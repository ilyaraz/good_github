# Logic synthesis and hardware compilation tools

Research date: **2026-10-09**.

This selection covers 25 repositories for Boolean optimization and technology mapping, hardware compiler infrastructure, high-level synthesis (HLS), hardware-language elaboration, and synthesizable HDL frontends. It includes FPGA, ASIC-oriented, and emerging-technology flows. Frontends and hardware construction languages qualify when their implementation performs substantial semantic analysis, elaboration, or lowering into hardware representations; their entries distinguish that role from downstream synthesis. Pure simulators, physical-design-only tools, IP collections, and flow wrappers are outside this selection.

The criteria below are judgments grounded in the linked implementation and documentation, not certifications of correctness or uniform code quality. Repository headings link to the verified GitHub repositories; the additional links are reading entry points.

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or failure modes require careful handling.
- **C2 — Reusable abstractions:** substantial representations, interfaces, or components support multiple uses.
- **C3 — Performance and structure:** real execution-time, circuit area, timing, bandwidth, or resource constraints are addressed through understandable architecture.
- **C4 — Sustained evolution:** evidence across years includes compatibility work, testing, or explicit complexity management; age alone is insufficient.

## Logic synthesis, mapping, and architecture-aware optimization

### [YosysHQ/yosys](https://github.com/YosysHQ/yosys)

**C++ — RTL synthesis framework.** Yosys is a strong starting point for studying how HDL semantics become an optimizable netlist without forcing every frontend and backend to share a source language. Its RTLIL representation retains processes and memories before lowering them into simpler hardware structures.

- **C1:** RTLIL processes represent decision trees and synchronization rules, including assignment priority and asynchronous reset behavior. Preserving these distinctions while converting processes into multiplexers and storage is a concrete correctness problem. The [RTLIL representation guide](https://yosyshq.readthedocs.io/projects/yosys/en/latest/yosys_internals/formats/rtlil_rep.html) explains the relevant structures and lowering responsibilities.
- **C2:** The same guide describes a hierarchy of designs, modules, cells, wires, processes, and memories, with `SigSpec` representing constants and arbitrary signal fragments. This common representation makes frontend elaboration, transformation passes, and output backends independently reusable.

### [berkeley-abc/abc](https://github.com/berkeley-abc/abc)

**C — logic synthesis and equivalence verification.** ABC is useful for studying the interaction between a compact graph representation, aggressive structural optimization, technology mapping, and formal reasoning. Its standalone repository is counted separately from projects that embed it.

- **C1:** Sequential equivalence depends on input sequences and initial states, while retiming must respect structural constraints on register placement. The project author's [ABC design and command manual](https://people.eecs.berkeley.edu/~alanmi/abc/abc.htm) also explains simulation/SAT-based functional reduction, making the correctness burden more concrete than a claim of Boolean simplification.
- **C2:** AIG-based network manipulation provides shared machinery for synthesis and verification, while specialized representations support other operations. The same manual explains this organization and its command-level composition.
- **C3:** DAG-aware rewriting, balancing, refactoring, and mapping expose competing area and delay objectives through identifiable algorithms. The linked manual is a **legacy architectural source**; its old benchmark results are not treated as current performance evidence.

### [lsils/mockturtle](https://github.com/lsils/mockturtle)

**C++17 — generic logic-network and synthesis library.** This is particularly useful for engineers designing algorithms that should operate across AIGs, majority-inverter graphs, and other network representations without duplicating the algorithm for every storage format.

- **C2:** Its [design philosophy](https://mockturtle.readthedocs.io/en/latest/philosophy.html) separates network interfaces, concrete implementations, algorithms, and specialized implementations. Algorithms state their required network operations, checked at compile time; network-specific specialization can coexist with generic implementations.
- **C4:** The [changelog](https://mockturtle.readthedocs.io/en/latest/changelog.html) documents releases in 2019, 2021, and 2022, including network fuzz testing in v0.2 and testcase minimization in v0.3. Those additions show sustained investment in finding and reducing synthesis failures, rather than merely an old repository creation date.

The architectural lesson is how to preserve representation independence while still allowing implementation-specific optimization and debugging tools.

### [cda-tum/fiction](https://github.com/cda-tum/fiction)

**C++17, with Python bindings — synthesis and physical design for field-coupled nanotechnologies.** Fiction broadens the selection beyond conventional CMOS and FPGA targets. Study its translation from logic networks into clocked gate layouts and technology-specific implementations; it is a research design framework, not evidence of production silicon performance.

- **C1:** The [exact physical-design documentation](https://fiction.readthedocs.io/en/latest/algorithms/exact.html) describes constraints for clocking, synchronization, crossings, and I/O placement, along with timeout and unsupported-fanin cases. Logical equivalence alone is insufficient when the generated layout must also satisfy these physical rules.
- **C2:** Algorithms accept network and gate-layout types satisfying common interfaces, while the repository separates gate layouts from technology-specific gate libraries. This permits multiple logic representations and physical technologies.
- **C3:** The exact flow incrementally searches layout sizes using SMT. Its documented tradeoff between parallel search and sharing information across incremental solver calls is a concrete example of optimizer runtime shaping the architecture.

### [verilog-to-routing/vtr-verilog-to-routing](https://github.com/verilog-to-routing/vtr-verilog-to-routing)

**C/C++, Python — FPGA CAD monorepo; relevant subsystem: synthesis and architecture-dependent partial mapping.** Counted once, including its Parmys and Odin II components. The [Odin II documentation](https://docs.verilogtorouting.org/en/latest/odin/) explicitly marks Odin II deprecated and identifies Parmys, using Yosys elaboration, as the default frontend. Odin remains a useful historical implementation to study.

- **C1:** The [Odin developer guide](https://docs.verilogtorouting.org/en/latest/odin/dev_guide/contributing/) traces per-module AST construction, elaboration, connected-netlist construction, and simulation. It requires bug-reproducing benchmarks in regression tests, connecting semantic transformations to executable checks.
- **C2:** The documented mapping boundary consumes a separate FPGA architecture description. The same logical operation can therefore be implemented with soft logic or available hard blocks, rather than baking one target device into the frontend.
- **C3:** Partial mapping explicitly chooses between LUT logic and architecture-provided hard resources. The historical guide exposes this decision at a clear stage in the compilation flow; its source filenames should not be assumed to describe modern Parmys internals.

## Compiler infrastructure and intermediate representations

### [llvm/circt](https://github.com/llvm/circt)

**C++/MLIR — hardware compiler infrastructure.** Relevant subsystems include the HW/Comb/SV dialects and scheduling library. This monorepo is counted once. CIRCT is a useful study in sharing hardware representations across source languages while preserving backend-specific detail.

- **C2:** The [HW dialect rationale](https://circt.llvm.org/docs/Dialects/HW/RationaleHW/) separates structural modules, instances, and types from combinational operations and SystemVerilog-specific constructs. Parameter representation and module interfaces are designed to support analyses across module boundaries.
- **C1:** The [scheduling infrastructure](https://circt.llvm.org/docs/Scheduling/) distinguishes checking that an input problem is well formed from verifying that a computed schedule satisfies constraints. Dependencies include SSA relationships and explicit auxiliary edges, such as memory ordering.
- **C3:** Specialized scheduling problems represent shared operators, cyclic execution, modulo scheduling, and chaining. These give resource and latency constraints explicit homes instead of hiding them in one scheduler's control flow.

### [google/xls](https://github.com/google/xls)

**C++, with DSLX and Python infrastructure — optimizing hardware compiler and toolchain.** XLS is useful for studying how functional and communicating-process representations move through optimization, cycle scheduling, and RTL generation. The [project documentation](https://google.github.io/xls/) identifies the IR, optimization, scheduling, code-generation, interpreter, JIT, and solver components.

- **C1:** The [pipeline scheduling design](https://google.github.io/xls/scheduling/) accounts for causality, I/O constraints, and process-state backedges. A scheduler must preserve these relationships while inserting pipeline boundaries; infeasible constraints are a meaningful compilation failure.
- **C3:** Scheduling balances clock period, pipeline stages, and register cost. The design describes difference constraints and a progression from determining a feasible clock to minimizing register usage, making the relationship between circuit objectives and optimization machinery inspectable.
- **C2:** A shared IR supports both execution-oriented tools and synthesis passes. This makes XLS valuable for comparing alternate implementations of semantics and for studying a compiler with multiple consumers of the same representation.

### [calyxir/calyx](https://github.com/calyxir/calyx)

**Rust — compiler infrastructure for accelerator construction.** Calyx makes control and datapath structure explicit rather than requiring every source language to invent its own RTL sequencing conventions. Engineers can study components, primitive interfaces, guarded assignments, and the compilation of structured control.

- **C1:** The [language reference](https://docs.calyxir.org/lang/ref.html) specifies assignment-guard restrictions, group completion, and the requirement to keep `go` asserted until `done`. Parallel control also has timing rules that differ from assuming every component starts in the same cycle. These are substantive concurrency and handshake invariants.
- **C2:** Cells and wires describe structure, groups package operations, and control constructs compose those operations through sequencing, parallelism, and invocation. The same reference supplies a compact interface between frontend languages and reusable lowering passes; the repository separately organizes frontend, IR, and optimization crates.

## High-level synthesis and accelerator compilation

### [EPFL-LAP/dynamatic](https://github.com/EPFL-LAP/dynamatic)

**C++/MLIR — dynamically scheduled HLS.** Dynamatic is a contrasting study to statically scheduled pipelines: it compiles C/C++ into dataflow hardware with distributed control. Memory dependencies, buffering, and backpressure make its compiler architecture especially instructive.

- **C1:** The [release engineering notes](https://github.com/EPFL-LAP/dynamatic/releases) describe memory-dependence analysis, distinct memory-controller and load-store-queue operations, and pass infrastructure with configurable pre/post semantic verification. These address ordering and IR-validity obligations during transformations.
- **C2:** The same notes document the separation of dependence tagging, memory-interface tagging, and interface placement, with shared abstractions for logical memory ports. This is concrete evidence of decomposing a complicated compiler subsystem into reusable passes.
- **C3:** Buffer placement uses optimization models incorporating channel delays, while memory analysis can reduce load-store-queue requirements. Study how the dataflow organization exposes performance choices through explicit IR operations and optimization stages.

### [ferrandi/PandA-bambu](https://github.com/ferrandi/PandA-bambu)

**C++ — C/C++ high-level synthesis within the PandA framework.** Bambu offers a substantial implementation of the classical scheduling, allocation, and binding problems. Its value is the connection between compiler analysis and the construction of actual datapaths, controllers, and memory interfaces.

- **C2:** The [Bambu architecture description](https://panda.deib.polimi.it/?page_id=31) explains distinct front-, middle-, and backend classes and representations, including SSA-derived control/data/program-dependence graphs. The [HLS source subtree](https://github.com/ferrandi/PandA-bambu/tree/main/src/HLS) exposes scheduling, binding, memory, and allocation boundaries.
- **C3:** Resource-constrained scheduling considers critical paths; binding uses compatibility relationships while accounting for multiplexers and interconnect; register allocation reuses storage across nonoverlapping live ranges. These are specific area/timing tradeoffs, not generic optimization claims.
- **C1:** The architecture distinguishes statically resolved memory accesses from dynamic accesses requiring interconnection logic. Preserving pointer-dependent access behavior and respecting live ranges are correctness obligations visible at the same boundaries used for optimization.

### [UCLA-VAST/AutoSA](https://github.com/UCLA-VAST/AutoSA)

**C/C++, Python — polyhedral compilation to systolic-array implementations.** AutoSA is a specialized but substantive compiler for loop-based computations. Its generated HLS code relies on downstream HLS tooling for RTL; it should not be confused with a complete standalone replacement for that backend.

- **C1:** The [array optimization tutorial](https://autosa.readthedocs.io/en/latest/tutorials/optimize_array.html) connects space-time transformations to dependence distances and derives communication groups from read, flow, and output dependencies. Loop transformations and transfer elimination must preserve these relationships.
- **C3:** The same document explains array partitioning, latency hiding, SIMD vectorization, hierarchical I/O clustering, data packing, and double buffering. These address on-chip capacity, compute utilization, fanout, and communication bandwidth through separate, understandable stages.

The distinctive reading opportunity is the compiler's treatment of communication as a generated architecture in its own right: the processing elements are only part of the result.

### [cornell-zhang/allo](https://github.com/cornell-zhang/allo)

**Python/C++/MLIR — accelerator programming and composable optimization.** Allo is useful for studying the separation between a kernel's algorithm and its hardware schedule, especially when independently optimized kernels are combined. The FPGA/HLS path is the relevant category fit; not every supported or proposed backend is a hardware-synthesis backend.

- **C2:** The [schedule-composition guide](https://cornell-zhang.github.io/allo/gallery/dive_03_composition.html) builds schedules for component kernels and composes them into a parent design. Template instance identifiers allow different instances to receive different schedules, making reuse more substantial than text substitution.
- **C3:** The worked implementation uses loop reordering, local buffering, and pipelining before composition. These transformations expose memory organization and parallel execution as explicit scheduling decisions, with generated IR available for inspection.

Study this codebase when interested in reusable optimization interfaces and how they survive module composition; the cited examples establish mechanisms, not general speedup guarantees.

## Hardware languages, elaboration, and RTL construction

### [chipsalliance/chisel](https://github.com/chipsalliance/chisel)

**Scala — hardware construction language and elaboration compiler.** Chisel is useful for studying the boundary between a general-purpose host language and a hardware-specific type and elaboration system. Its repository describes the progression from the public API through builder state and an intermediate representation to emission and downstream CIRCT processing.

- **C1:** The [width-inference specification](https://www.chisel-lang.org/docs/explanations/width-inference) explains how operation rules and connections determine widths, including inference across module instantiations and errors when widths remain unknown. Integer widths are circuit semantics, not merely storage hints.
- **C2:** Parameterized generators, structured hardware data, and reusable interfaces share the same elaboration machinery. The repository's architecture description helps locate the compiler boundary beneath these user-facing abstractions.

Chisel's elaboration implementation is the focus here. Low-level transformations performed by CIRCT belong to the separate CIRCT entry rather than being attributed wholesale to Chisel.

### [SpinalHDL/SpinalHDL](https://github.com/SpinalHDL/SpinalHDL)

**Scala — RTL construction and netlist compilation.** SpinalHDL is an instructive alternative for studying an extensible elaborated netlist and the ordering of compiler phases. It describes hardware directly; it is not a C-to-hardware HLS system.

- **C2:** The [compiler data-model documentation](https://spinalhdl.github.io/SpinalDoc-RTD/master/SpinalHDL/Developers%20area/spinalhdl_datamodel.html) describes mutable graph structures, traversal/remapping APIs, and hooks for inserting custom phases. These are reusable mechanisms for implementing design-wide transformations.
- **C1:** Phase placement imposes invariants. In particular, transformations inserted after width inference must supply widths for newly introduced nodes. The same guide explains how transformations interact with the compiler's existing checks and phases, making it useful for studying the correctness hazards of extending a mutable IR.

The engineering lesson is the coupling between a pass's insertion point and the properties it may assume or must preserve.

### [clash-lang/clash-compiler](https://github.com/clash-lang/clash-compiler)

**Haskell — functional hardware compiler.** Clash is a substantial case study in turning a typed functional language into structural hardware, rather than interpreting functions as software instructions on a processor.

- **C1:** The [architecture document](https://github.com/clash-lang/clash-compiler/blob/master/ARCHITECTURE.md) describes normalization into a hardware-compatible form, including administrative normalization and rejection of recursive call graphs that cannot become finite hardware. Engineers can inspect where general functional-language expressiveness meets synthesis restrictions.
- **C2:** The compiler separates GHC input handling, Clash Core, normalization using rewrite combinators, netlist generation, and HDL backends. This makes rewrite strategies and backend-independent lowering concrete reusable abstractions.

The same document discusses isolating GHC-version-specific code and caching generated results. Those are useful complexity-management details, but this entry does not infer a C4 qualification merely from their presence or the repository's age.

### [amaranth-lang/amaranth](https://github.com/amaranth-lang/amaranth)

**Python — hardware description, elaboration, simulation, and build integration.** Amaranth is particularly useful for examining an HDL whose numerical and assignment semantics deliberately differ from ordinary Python and from some Verilog expectations.

- **C1:** The [language guide](https://amaranth-lang.org/docs/amaranth/latest/guide.html) specifies shapes, signedness, expression widths, and assignment truncation. It also explains per-bit driver restrictions across clock domains and priority among assignments within a domain. These rules directly affect generated circuit behavior.
- **C2:** Shape- and value-casting protocols allow user-defined abstractions to participate in the same expression and elaboration system. Structured data and domain-aware construction therefore extend the language through shared interfaces rather than independent code generators.

An experienced engineer can study how precise bit-vector semantics, host-language integration, and extensibility are kept compatible, including edge cases such as zero-width values and excessively wide variable shifts.

### [B-Lang-org/bsc](https://github.com/B-Lang-org/bsc)

**Haskell, with C++ simulation infrastructure — Bluespec compiler.** BSC offers a distinctive concurrency model based on guarded rules, with both Verilog and Bluesim consumers. The [developer guide](https://github.com/B-Lang-org/bsc/blob/main/DEVELOP.md) maps the compiler and test infrastructure.

- **C1:** The comments and types in [AScheduleInfo.hs](https://github.com/B-Lang-org/bsc/blob/main/src/comp/AScheduleInfo.hs) distinguish rules whose `CAN_FIRE` predicates are disjoint from rules whose `WILL_FIRE` predicates are exclusive because scheduling prevents simultaneous firing. Confusing those notions can change generated behavior.
- **C2:** The schedule-information representation collects rule/method uses, resource allocation, conflicts, and scheduling relationships for multiple backends. The same exclusivity information informs Verilog multiplexing decisions and Bluesim scheduling logic.
- **C3:** The source explains when exclusivity permits avoiding priority multiplexers and when simulation can shortcut conflict checks. This ties a precise semantic distinction to both circuit structure and simulator work.

### [janestreet/hardcaml](https://github.com/janestreet/hardcaml)

**OCaml — hardware construction and compilation library.** Hardcaml is a useful library-oriented comparison with standalone HDL compilers: ordinary OCaml programs build circuit graphs that become RTL or simulation models.

- **C1:** The [circuit documentation](https://github.com/janestreet/hardcaml/blob/master/docs/circuits.md) describes constructing circuits by walking from outputs, detecting combinational loops, rejecting invalid port names, and discovering inputs. It also explains the consequence of an unconnected node: it is absent from the reachable circuit.
- **C2:** `Circuit.t` packages named interfaces and reachable logic for subsequent consumers. This common representation connects reusable circuit generators with RTL production and simulation, rather than requiring separate implementations for each use.

The same guide's identifier-normalization facility is useful for studying reproducible generated RTL. Engineers should pay particular attention to the distinction between the graph a host-language program constructs and the graph reachable from a circuit's declared outputs.

### [sylefeb/Silice](https://github.com/sylefeb/Silice)

**C++ — compiler for a hardware language with algorithmic control and explicit timing.** Silice provides a useful middle ground between manually encoding state machines and delegating all scheduling to HLS. Its repository describes algorithms, pipelines, per-cycle logic, and integration with Verilog modules.

- **C2:** Those constructs give different hardware behaviors a common compilation model while preserving module-level composition. The [coding and implementation guidelines](https://github.com/sylefeb/Silice/blob/master/learn-silice/Guidelines.md) connect source constructs to generated control and datapath structure.
- **C3:** The guidelines explain how state boundaries affect register generation, multiplexing, combinational depth, and achievable clock timing. The compiler can remove unnecessary flip-flops, but source sequencing still controls meaningful hardware costs.

Study how explicit timing boundaries become finite-state-machine states and how registered interfaces alter cycle-level behavior. The documentation is candid about tradeoffs; this selection makes no claim that the generated designs universally outperform handwritten RTL.

### [pymtl/pymtl3](https://github.com/pymtl/pymtl3)

**Python — multi-level hardware modeling with RTL translation and import passes.** PyMTL3 belongs here through its elaboration and translation system, rather than through simulation alone. It is useful for studying a compiler embedded in a modeling and verification workflow.

- **C2:** The [translation guide](https://pymtl3.readthedocs.io/en/latest/ref/passes-translation-intro.html) defines the translatable structural and behavioral subset and uses pass metadata to control translation. Components, interfaces, and elaborated parameters provide the reusable input structure.
- **C1:** The [Verilog import guide](https://pymtl3.readthedocs.io/en/latest/ref/passes-import-intro.html) explains placeholder replacement and translation followed by re-import for simulation. Keeping the component interface stable allows the same test harness and cases to exercise both Python execution and generated Verilog, directly targeting translation discrepancies.

This is a testing mechanism, not a proof of equivalence. The boundary between unrestricted Python modeling and the supported RTL subset is central to understanding the implementation.

### [spade-lang/spade](https://github.com/spade-lang/spade)

**Rust — typed HDL compiler with explicit pipelines. Official read-only GitHub mirror.** The opened repository identifies its upstream as Codeberg; the GitHub tree retains substantive compiler crates and architecture documentation. It is included as a mirror, not as an independently developed fork.

- **C1:** The project's [pipeline explanation](https://spade-lang.org/) shows latency encoded in pipeline declarations, automatic insertion of intermediate registers, and diagnostics for consuming nested-pipeline results too early. This makes signal alignment a compiler-checked property.
- **C2:** The [compiler architecture](https://github.com/spade-lang/spade/blob/main/ARCHITECTURE.md) separates AST, scoped HIR, flattened MIR, type inference, and Verilog code generation into crates. It also describes globally identified names and source-location propagation, useful abstractions for maintaining semantic information across lowering.

The architecture document contains some forward-looking passages; only its described representation and pass structure are used here. Spade is an HDL with explicit hardware timing, not a general C-like HLS compiler.

## HDL frontends and semantic translation

### [ghdl/ghdl](https://github.com/ghdl/ghdl)

**Primarily Ada — VHDL frontend and toolchain; relevant subsystem: experimental synthesis.** GHDL is included specifically for its synthesis frontend, not simply because it is a simulator. Its [synthesis documentation](https://ghdl.github.io/ghdl/using/Synthesis.html) explicitly labels synthesis experimental/work in progress and describes an unoptimized netlist intended for downstream tools.

- **C1:** The documentation explains semantic issues around generated simplified VHDL, including shift behavior for invalid values and options governing assertion/assumption handling. Preserving or deliberately translating those meanings is a concrete frontend obligation.
- **C2:** Synthesis reuses the VHDL frontend and can emit simplified VHDL or Verilog; the documented Yosys connection translates the internal representation through an integration layer. This makes the frontend useful independently of a particular simulator or final technology mapper.

Engineers can study shared language infrastructure serving execution and synthesis, while keeping the experimental status and downstream optimization dependency explicit.

### [MikePopoloski/slang](https://github.com/MikePopoloski/slang)

**C++ — reusable SystemVerilog parsing, elaboration, and analysis frontend.** Slang is a compiler building block for hardware tools, not a complete gate-level optimizer. Its separation of syntactic, semantic, and analysis stages is especially useful when embedding language support in other applications.

- **C1:** The [architecture overview](https://www.sv-lang.com/overview.html) explains error-recovering parsing and the lifetime relationship between source storage and string views. It also describes resolving names, types, parameters, and instance hierarchies during compilation: correctness extends well beyond accepting grammar productions.
- **C2:** Lexing, preprocessing, parsing, syntax trees, compilation, and analysis are separately usable layers. Expensive analyses live behind `AnalysisManager` rather than being inseparable from basic parsing and elaboration.
- **C3:** Shared source storage and delayed analysis are explicit architectural choices that control memory ownership and avoid unnecessary work for clients needing only part of the frontend.

### [chipsalliance/Surelog](https://github.com/chipsalliance/Surelog)

**C++/ANTLR — SystemVerilog preprocessing, parsing, elaboration, and UHDM production.** Surelog is valuable for studying both source-language complexity and a persistent interchange boundary between an HDL frontend and downstream tools.

- **C1:** The [preprocessor design](https://github.com/chipsalliance/Surelog/blob/master/PREPROCESSOR.md) treats preprocessing as grammar-driven processing and records nested macro/include contexts. Preserving source locations through expansion is necessary for correct diagnostics and downstream interpretation.
- **C2:** Preprocessed content and provenance can be serialized; elaboration exports UHDM for consumers using a shared design representation and APIs. This separates language handling from the applications built on the elaborated result.
- **C3:** The repository documents multithreaded parsing and a low-memory multiprocess mode. Together with persistent intermediate data, these expose concrete scaling strategies for large source collections; they do not establish any unmeasured speedup.

Study the provenance structures alongside the exported model: persistence is only useful when source identity and semantic meaning survive the boundary.

### [zachjs/sv2v](https://github.com/zachjs/sv2v)

**Haskell — synthesizable SystemVerilog-to-Verilog conversion.** Sv2v is a substantial semantic lowering tool, especially relevant when downstream synthesis accepts a narrower language. Its supported subset and documented exclusions matter; it should not be treated as an unrestricted replacement for a complete SystemVerilog implementation.

- **C2:** [Convert.hs](https://github.com/zachjs/sv2v/blob/master/src/Convert.hs) composes transformations through common phase types, separates initial/main/final stages, and repeats the main conversion sequence until convergence. Engineers can study how interacting feature-lowering passes are organized without a single monolithic rewrite.
- **C1:** The [test-suite description](https://github.com/zachjs/sv2v/blob/master/test/README.md) explains running paired SystemVerilog and reference-Verilog cases through shared testbenches and comparing logs and waveform outputs. It also describes error-location tests and checking generated output for unwanted remaining constructs.

These tests target semantic and diagnostic regressions. Simulation comparisons cover exercised behaviors, and some cases are compile-only; they are not exhaustive equivalence proofs.

## Coverage, search process, and limitations

Discovery used live web searches across more than six materially different angles: Boolean/AIG/MIG synthesis and technology mapping; Yosys/ABC-style synthesis architecture; MLIR and hardware compiler IRs; static versus dynamic HLS; polyhedral systolic-array generation; Scala/Haskell/OCaml/Python hardware languages; Rust pipeline languages; SystemVerilog and VHDL synthesis frontends; emerging nanotechnology synthesis; and FPGA architecture-dependent mapping. Follow-up searches targeted architecture documents, scheduling and memory representations, test suites, release notes, and historical alternatives. Later queries mostly returned overlapping projects, narrower experiments, or adjacent tooling, although they also surfaced Spade's substantive official mirror.

Every retained GitHub repository page was opened, and each entry has additional primary material that was opened and read rather than relying on search snippets. The selection spans compiler frameworks, focused libraries, research compilers, and language implementations, with C/C++, Rust, Scala, Haskell, OCaml, Python, and Ada represented. A repository is counted once: CIRCT dialects and VTR synthesis components are not separate entries, and embedded copies of ABC are not additional projects.

Excluded scope includes pure simulators, placement/routing-only systems, orchestration-only bundles, tutorials, generated wrappers, and hardware IP without a substantive compiler. The stale CIRCT-HLS integration repository was not substituted for the underlying CIRCT implementation. Other discoverable research compilers remain outside this curated selection; omission is not a judgment that they fail the criteria.

Maintenance is not inferred from stars, creation dates, or a recent push. Spade is labeled as a mirror, Odin II as a deprecated historical subsystem, and GHDL synthesis as experimental. ABC's legacy manual and versioned documentation elsewhere can lag source trees; they support architectural study, not a promise about every current option or path. No candidate was cloned, built, executed, benchmarked, or formally audited. Claims about useful engineering lessons and satisfaction of the criteria are grounded in the cited mechanisms; they do not assert that every component is exemplary, that all translations are proven correct, or that documented optimization choices deliver universal performance gains.
