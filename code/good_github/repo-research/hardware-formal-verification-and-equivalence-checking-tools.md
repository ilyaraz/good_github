# Hardware formal verification and equivalence checking tools

Research date: **2026-10-09**.

This report selects 23 GitHub repositories for studying formal reasoning about digital hardware: RTL and netlist equivalence, temporal property checking, architectural refinement, symbolic hardware analysis, verified hardware languages, arithmetic circuits, and masking security. It includes implementation frameworks and reusable proof infrastructure, not just command-line solvers. General-purpose theorem provers appear only where a substantial hardware-specific subsystem is identified. Isla covers architectural memory-model analysis rather than RTL equivalence. Historical research implementations are retained when their engineering ideas remain useful, with their status stated explicitly.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, numerical or HDL semantics, adversarial behavior, or failure modes.
- **C2 — Reusable abstractions:** substantial interfaces, representations, libraries, or frameworks supporting multiple designs or verification tasks.
- **C3 — Performance and structure:** concrete measures to control proof cost, memory, or execution time within an understandable architecture.
- **C4 — Sustained evolution:** years of development supported by compatibility work, testing, or explicit complexity management; age alone does not qualify.

The criteria assessments are engineering judgments grounded in the linked material. They are not claims that every component is equally exemplary, that proofs are assumption-free, or that the tools were executed during this research.

## RTL flows and equivalence checking

### 1. [YosysHQ/yosys](https://github.com/YosysHQ/yosys)

**Language/role:** C++ with Python tooling; synthesis infrastructure containing formal preparation, SAT/SMT support, and equivalence passes. The relevant subsystem is the formal/equivalence machinery, not the entire synthesis suite.

Study how an extensible compiler representation becomes a verification platform: passes manipulate RTLIL and expose individual equivalence obligations as `$equiv` cells. This makes the relationship between synthesis transformations and subsequent proof unusually visible.

- **C1:** The temporal induction implementation handles undefined values, assumptions, and collective versus individual obligations. Its help text explicitly states the limited equivalence notion being proved: non-divergence after a sufficiently long equal-output prefix. That boundary is valuable material for understanding why reset alignment cannot be silently assumed. [Implementation and command semantics](https://github.com/YosysHQ/yosys/blob/main/passes/equiv/equiv_induct.cc).
- **C2:** The pass-oriented architecture permits reusable elaboration, transformations, and proof steps to be assembled into different flows; the repository README describes extending it with additional passes.
- **C4:** Verified releases span [0.9 in August 2019](https://github.com/YosysHQ/yosys/releases/tag/yosys-0.9) through [0.69 in September 2026](https://github.com/YosysHQ/yosys/releases/tag/v0.69). The [changelog](https://github.com/YosysHQ/yosys/blob/main/CHANGELOG) records solver compatibility updates, formal-property preservation fixes, fuzz-comparison support, and coordinated command changes affecting SBY.

### 2. [YosysHQ/sby](https://github.com/YosysHQ/sby)

**Language/role:** Python; SymbiYosys, the orchestration layer for Yosys-based formal verification.

The interesting engineering lies in translating a declarative verification job into model preparation, engine execution, and interpretable results. This is a substantial proof-flow frontend whose correctness responsibilities include clocks, task configuration, and solver outcomes.

- **C1:** Its configuration distinguishes bounded safety, unbounded safety, liveness, and cover generation, with explicit depth semantics and multiclock modeling. Expected outcomes distinguish failure, unknown, timeout, and tool error. [Job format and semantics](https://github.com/YosysHQ/sby/blob/main/docs/source/reference.rst).
- **C2:** Tagged tasks can share source lists and scripts while varying implementation combinations, properties, engines, and options. The same reference documents a common interface to multiple backend families.
- **C3:** Multiple engines can compete to finish a job, while an optional wait mode checks consistency across their results; timeouts and engine-specific bounds expose resource control without embedding it in each design.

### 3. [YosysHQ/eqy](https://github.com/YosysHQ/eqy)

**Language/role:** Python and C++; equivalence checking frontend using Yosys and backend proof strategies.

Study the decomposition of a large equivalence problem into signal matching, fragments, partitions, and local proof strategies. EQY is especially instructive about what “equivalent” means when synthesis can resolve unknowns and don't-care values.

- **C1:** EQY defines asymmetric safe-replacement equivalence: its reference design uses three-valued semantics, while the implementation uses two-valued semantics with unconstrained choices for unknowns. The documentation explains both the preservation argument and its limitations. [X-propagation semantics](https://github.com/YosysHQ/eqy/blob/main/docs/source/xprop.rst).
- **C2/C3:** Matching and partition rules expose reusable controls for grouping related state, preventing unsuitable cut boundaries, and merging dependent partitions. These are concrete mechanisms for making proofs tractable across different circuit organizations. [Partition configuration](https://github.com/YosysHQ/eqy/blob/main/docs/source/config.rst).

### 4. [keplertech/kepler-formal](https://github.com/keplertech/kepler-formal)

**Language/role:** C++ with Python interfaces; combinational and sequential equivalence for gate-level and RTL designs, including Naja interchange inputs.

This is a useful contemporary complement to the Yosys ecosystem. Its documentation exposes the actual correspondence-learning algorithm and the assumptions attached to initialization, rather than treating equivalence as an opaque command.

- **C1:** Register correspondences guessed from names or shared drivers become usable invariants only after base and inductive checks. Candidate removal triggers renewed proof rounds because weakening the hypotheses can invalidate earlier reasoning. [Internal relation learning](https://github.com/keplertech/kepler-formal/blob/main/docs/sec-internal-relations.md).
- **C3:** That same implementation description explains structural expression numbering, partitioned SAT queries, variables allocated on first use, and counterexample replay that eliminates multiple bad candidates. These are identifiable memory and search-cost controls, not merely speed claims.
- **C2:** The tool supports several design input paths and explicit reset configuration. Its [reset bootstrap semantics](https://github.com/keplertech/kepler-formal/blob/main/docs/sec-reset-bootstrap.md) specify post-reset constraints and check whether the initial output-equality assumption is satisfiable. LEC's naming/boundary restrictions and SEC's input-matching requirements still matter; this entry does not claim universal equivalence coverage.

### 5. [berkeley-abc/abc](https://github.com/berkeley-abc/abc)

**Language/role:** Primarily C; logic synthesis and formal verification engine, including combinational and sequential equivalence infrastructure.

Study the interaction between compact circuit graphs, simulation, SAT sweeping, and reusable verification managers. ABC is particularly useful for engineers interested in algorithms below the RTL frontend.

- **C1/C3:** The equivalence core separates SAT, simulation, sweeping, and correspondence parameters. Conflict limits, solver recycling, bounded refinement rounds, and counterexample-bearing graph results make the practical cost of equivalence reasoning visible. [CEC core](https://github.com/berkeley-abc/abc/blob/master/src/proof/cec/cecCore.c).
- **C2:** ABC can be embedded as a library as well as used interactively or in batches. Its documented frame lifecycle supports independent sessions and explicitly identifies concurrency restrictions: a frame cannot be shared concurrently, and some older commands still use shared process state. [Embedding and build guide](https://github.com/berkeley-abc/abc/blob/master/README.md).

### 6. [fvmformal/fvm](https://github.com/fvmformal/fvm)

**Language/role:** Python with VHDL/PSL collateral; Formal Verification Methodology and toolchain orchestration. **Official substantive GitHub mirror:** the repository identifies [GitLab](https://gitlab.com/fvmformal/fvm) as its development/issue location.

Study how a VHDL-oriented formal workflow exposes design configurations, clocks, resets, cutpoints, and blackboxes through a common framework. Its property-generation component gives this project more substance than a collection of example command scripts.

- **C1/C2:** `drom2psl` translates structured timing diagrams into temporal properties, with documented distinctions between overlapping implication, non-overlapping implication, and simultaneous sequences. Its datatype and repetition conventions show the semantic obligations of a property authoring abstraction. [Translation rules](https://github.com/fvmformal/fvm/blob/main/doc/sphinx/source/drom2psl.rst).
- **C3:** The methodology explains how cutpoints, module abstraction, and counter abstraction change the problem, including when freeing a signal makes a property harder to prove. It maps those ideas to concrete framework APIs. [Proof complexity techniques](https://github.com/fvmformal/fvm/blob/main/doc/sphinx/source/complexityreduction.rst).

## Property-checking engines and transition systems

### 7. [stanford-centaur/pono](https://github.com/stanford-centaur/pono)

**Language/role:** C++ with Python bindings; extensible SMT-based model checker with hardware input flows.

Study the separation between transition-system representation and solving strategy. Pono is the successor to CoSA, but is a distinct implementation, not a second listing of the same code.

- **C2:** Its `TransitionSystem` interface distinguishes state, input, initial conditions, functional updates, invariants, and named witness terms. Copying into another solver has an explicit term-translation boundary. These abstractions support multiple frontends and verification algorithms. [Core interface](https://github.com/stanford-centaur/pono/blob/main/core/ts.h).
- **C1:** The interface guards illegal next-state references and repeated next-state assignments. More subtly, the project documents how solver-owned terms, Boolean/one-bit-vector aliasing, and on-the-fly rewriting can change an unrolling computation if handled incorrectly. [Solver semantic pitfalls](https://github.com/stanford-centaur/pono/blob/main/gotchas.md).

### 8. [aman-goel/avr](https://github.com/aman-goel/avr)

**Language/role:** C++ with Python drivers; Abstractly Verifying Reachability, a word-level property checker using equality abstraction.

AVR provides an alternative to immediately reducing every hardware problem to Boolean logic. Study how an abstract counterexample is represented, inspected, and refined against more concrete reasoning.

- **C1:** The refinement implementation tracks predicates, word-level terms, uninterpreted-function structure, and concrete versus abstract assignments. It exposes the difficult boundary between a genuine reachable violation and an artifact of abstraction. [CEGAR implementation](https://github.com/aman-goel/avr/blob/master/src/reach/reach_cegar.cpp).
- **C3:** The Proof Race driver runs multiple configurations under time and memory budgets and preserves the winning invariant or witness. The documented result taxonomy also separates safety, violation, and resource/error exits. [Architecture, outputs, and Proof Race](https://github.com/aman-goel/avr/blob/master/README.md).

This is research software with project-specific license terms; no claim of current support or universal solver interoperability is made.

### 9. [gipsyh/rIC3](https://github.com/gipsyh/rIC3)

**Language/role:** Rust; hardware model checker for AIGER/BTOR inputs and RTL project flows.

Study a modern IC3 implementation organized around frames, proof obligations, SAT interfaces, abstraction, and generalization. The repository contains the checking algorithms themselves, not just a Rust wrapper around an external checker.

- **C1:** The IC3 state explicitly owns frame solvers, a proof-obligation queue, restoration information, and the largest completed depth. A reached search bound is represented as unknown with a depth, rather than silently converted to an unbounded proof. [IC3 implementation](https://github.com/gipsyh/rIC3/blob/master/src/ic3/mod.rs).
- **C3:** The implementation exposes generalization and abstraction choices as validated configurations, while the tool offers both a portfolio and single-engine execution. The architecture separates these choices from the transition-system representation. [Modes and input flow](https://github.com/gipsyh/rIC3/blob/master/README.md).

The README specifically warns that its CIll development branch is unstable and paused; that warning should not be generalized into a claim that every rIC3 component has the same status.

### 10. [diffblue/hw-cbmc](https://github.com/diffblue/hw-cbmc)

**Language/role:** C++; repository containing EBMC and HW-CBMC. Counted once, with EBMC's hardware property-checking implementation as the principal entry point.

Study temporal-property lowering and the boundary between bounded counterexample search and inductive proof. The repository supports Verilog/SystemVerilog, NuSMV, and netlist inputs, rather than requiring a single hardware DSL.

- **C1:** The induction engine separately checks the base and step cases, refuses to prove a property whose base case failed, and turns a satisfiable induction step into an inconclusive result. Unsupported assumptions also affect whether an apparent refutation can be trusted. [Induction implementation](https://github.com/diffblue/hw-cbmc/blob/main/src/ebmc/k_induction.cpp).
- **C2/C3:** The same implementation shares transition systems, property objects, and solver factories while optionally reducing each query to the cone of influence of both the property and its assumptions. This is a concrete reuse and performance boundary.
- **Complexity-management evidence:** The [changelog](https://github.com/diffblue/hw-cbmc/blob/main/CHANGELOG) records fixes involving strong/weak SVA sequences, `$past`, four-valued operations, and unsupported temporal assumptions. These entries make useful regression-study targets; release counts alone are not used here to award C4.

### 11. [Boolector/boolector](https://github.com/Boolector/boolector)

**Language/role:** C/C++; the **BtorMC hardware model-checking subsystem** within Boolector. **Archived:** the README explicitly says maintenance has stopped and identifies Bitwuzla as Boolector's SMT-solver successor.

This entry is included for BtorMC, not merely because a general SMT solver can serve hardware tools. It offers a compact view of constructing a word-level transition system directly through a library API.

- **C1:** The API separates state initialization, next-state functions, bad-state properties, and invariant constraints; it offers both bounded model checking and k-induction, plus time-indexed counterexample assignments. [Model-checker API](https://github.com/Boolector/boolector/blob/master/src/boolectormc.h).
- **C2:** Independent model-checker instances, configurable options, callbacks at explored bounds, and integration with the underlying Boolector term API provide reusable building blocks for custom checking applications.

The [repository guide](https://github.com/Boolector/boolector/blob/master/README.md) identifies the BtorMC binaries and archive status. It does not establish that Bitwuzla is a drop-in replacement for the entire model-checking subsystem.

### 12. [cristian-mattarei/CoSA](https://github.com/cristian-mattarei/CoSA)

**Language/role:** Python; CoreIR Symbolic Analyzer, an SMT-based hardware checker. **Historical implementation:** GitHub metadata showed its last push in October 2020; Pono explicitly identifies itself as the next generation.

CoSA remains useful for studying how to compose frontends, symbolic transition systems, properties, and equivalence encodings in a relatively accessible language.

- **C1:** Its miter builder renames both systems, translates assumptions and lemmas, controls symbolic initialization, and constructs input/state/output relations. The code makes the distinction between nondeterministic behavior and matched-state assumptions visible. [Miter construction](https://github.com/cristian-mattarei/CoSA/blob/master/cosa/encoders/miter.py).
- **C2:** Multiple input formats feed shared invariant, LTL, equivalence, parameter, and fault-analysis workflows. This is useful evidence of a common symbolic representation serving more than one verification mode. [Supported workflows and examples](https://github.com/cristian-mattarei/CoSA/blob/master/README.rst).

Treat its documented dependency versions as historical, not as a verified present-day installation recipe.

## Processor, SoC, and architecture reasoning

### 13. [YosysHQ/riscv-formal](https://github.com/YosysHQ/riscv-formal)

**Language/role:** Verilog/SystemVerilog and Python; reusable RISC-V processor formal-verification framework.

Study the interface between microarchitectural implementation and architectural observations. RVFI lets processor-independent instruction models and consistency checks operate across differently organized cores.

- **C1:** The interface specifies retirement ordering, causality, traps, register values, byte-masked memory effects, and rollback behavior. These are semantic contracts that a simple instruction-result comparison would miss. [RVFI specification](https://github.com/YosysHQ/riscv-formal/blob/main/docs/source/rvfi.rst).
- **C2:** A core wrapper, configuration, and generated checks connect a new processor to the shared models. [Integration procedure](https://github.com/YosysHQ/riscv-formal/blob/main/README.md).
- **C3:** RVFI documents alternative arithmetic operations used to make surrounding control/bypass proofs tractable when multiplication or division is too costly. This abstraction does **not** prove the real arithmetic unit; the distinction is essential when studying coverage.

The project describes its interfaces as work in progress, and the RVFI document also contains proposed extensions. Proposed features should not be read as implemented coverage.

### 14. [PrincetonUniversity/ILAng](https://github.com/PrincetonUniversity/ILAng)

**Language/role:** C++; instruction-level abstraction library and verification-target generation for SoCs and accelerators.

Study refinement across abstraction levels: an architectural operation may require many implementation cycles, so direct cycle-for-cycle equality is often the wrong specification.

- **C2:** The ILA representation organizes states, inputs, initialization, fetch/valid predicates, decoded instructions, update functions, child abstractions, and instruction sequencing. It is a reusable modeling layer rather than a model of one processor. [ILA object model](https://github.com/PrincetonUniversity/ILAng/blob/master/include/ilang/ila/instr_lvl_abs.h).
- **C1:** Verification targets take explicit variable mappings and refinement conditions. Configuration addresses reset assumptions, memory abstraction, updated-state checks, candidate invariant validation, and overconstraint checking. These expose the proof obligations introduced when relating an ILA to RTL. [Target-generation interface](https://github.com/PrincetonUniversity/ILAng/blob/master/include/ilang/vtarget-out/vtarget_gen.h).

The repository was not archived when checked, but the latest push metadata was July 2024; this is not an assertion of ongoing support for every listed backend.

### 15. [rems-project/isla](https://github.com/rems-project/isla)

**Language/role:** Rust with OCaml adapters; symbolic execution of Sail ISA specifications and axiomatic relaxed-memory checking.

This is the architectural edge of the category: it analyzes formally specified hardware behavior rather than comparing RTL implementations. Study how detailed instruction semantics can be combined with a separate concurrency model.

- **C1:** `isla-axiomatic` asks whether concurrent litmus-test outcomes are allowed, with additional mechanisms for instruction-fetch events and address translation. The manual explains why initializing registers before a model's setup code can differ from initializing them at the intended execution point. [Axiomatic checking semantics](https://github.com/rems-project/isla/blob/master/doc/axiomatic.adoc).
- **C2:** The project separates a symbolic execution library, a cat-to-SMT translator, litmus processing, Sail integration, and architecture configuration. Arm and RISC-V models can use the same engine and analysis interfaces. [Architecture and project structure](https://github.com/rems-project/isla/blob/master/README.md).

Its result is about the selected formal ISA and memory model; it is not by itself a proof that a physical processor implements them.

## Symbolic circuit analysis and proof-assistant frameworks

### 16. [TeamVoss/VossII](https://github.com/TeamVoss/VossII)

**Language/role:** C/C++ implementation, the functional language `fl`, and Tcl/Tk tooling; hardware verification suite with symbolic trajectory evaluation.

VossII offers a distinct architecture from SAT/SMT command pipelines: binary decision diagrams are built into a lazy, statically typed language used to describe circuits and properties.

- **C1:** The FSM/trajectory structures explicitly represent antecedents, consequents, weakening, temporal events, trajectory validity, and assertion results. This is useful for studying the semantics and bookkeeping of symbolic circuit evaluation. [FSM and STE representation](https://github.com/TeamVoss/VossII/blob/master/src/bin/fl/fsm.h).
- **C2:** The same environment supports circuit import, symbolic manipulation, simulation, and visual debugging. The [tutorial's circuit-analysis section](https://github.com/TeamVoss/VossII/blob/master/doc/fl_tutorial/index.html) connects Verilog import, FSM construction, STE, and signal inspection, providing a practical route into the implementation.

The suite includes much more than Verilog examples; repository language totals should not be mistaken for the implementation language of the verification engine.

### 17. [acl2/acl2](https://github.com/acl2/acl2)

**Language/role:** Common Lisp/ACL2; specifically the **SV, VL, and SVTV hardware-analysis libraries in the Community Books**. The monorepo is counted once.

Study a hardware semantics embedded in a theorem prover and connected to automated Boolean reasoning. The relevant SV subsystem spans expression evaluation, sound rewriting, module composition, SystemVerilog translation, symbolic test vectors, and waveform debugging.

- **C1:** SV gives four-valued vectors explicit semantics, handles multiply driven wires during module compilation, and links symbolic expressions to GL/FGL reasoning. It illustrates how language semantics and proof automation meet. [SV architecture and semantics](https://github.com/acl2/acl2/blob/master/books/centaur/sv/top.lisp).
- **C2/C3:** The same document explains the change from bit-level ESIM expressions to vector-level SV expressions. Avoiding per-bit symbols and repeated structures reduces translation, traversal, and memoization costs while preserving shared analysis interfaces. This is unusually concrete architectural justification for a performance-driven representation change.

The [repository guide](https://github.com/acl2/acl2/blob/master/README.md) distinguishes this canonical development repository from the separate official stable-release fork; they are not listed as independent projects.

### 18. [sifive/Kami](https://github.com/sifive/Kami)

**Language/role:** Coq with Haskell simulation support; hardware specification, implementation, and refinement proofs. **Historical:** GitHub metadata showed its last push in August 2020.

The README identifies this as SiFive's rewrite of the earlier MIT Kami. Only this implementation is retained here, avoiding two entries for closely related framework lineages.

- **C1:** Correctness is trace inclusion between implementations and specifications. The inspected proof relates a two-step counter implementation to a one-rule specification through an explicit state invariant and a stuttering step. [Refinement proof example](https://github.com/sifive/Kami/blob/master/Tutorial/TacticsEx.v).
- **C2:** Parameterized hardware generators, typed action syntax, module semantics, and reusable tactics allow proof over families of designs rather than a single fixed-width netlist. The shared syntax serves both circuit generation and reasoning. [Semantics and framework design](https://github.com/sifive/Kami/blob/master/README.adoc).

The small counter proof is an entry into a substantial framework, not the reason for retaining a tutorial repository. The documentation itself acknowledges incomplete proof guidance.

### 19. [mit-plv/koika](https://github.com/mit-plv/koika)

**Language/role:** Coq/Rocq and OCaml, with C++ simulation output; rule-based hardware language, formal semantics, and verified circuit compilation.

Study how hardware can execute multiple rules in a cycle while retaining a serializable reasoning model. The project is explicitly a research prototype and documents limitations in its optimizer.

- **C1:** The one-rule-at-a-time proof connects scheduler execution, read/write logs, state commitment, and a sequence of individual rule executions. This directly addresses the semantic risk introduced by concurrent rule scheduling. [Machine-checked theorem](https://github.com/mit-plv/koika/blob/master/coq/OneRuleAtATime.v).
- **C2:** The framework provides typed syntax, reference interpretation, a verified compiler, an embedded DSL, and separate simulation/synthesis outputs. Parameterized rules and schedulers apply beyond the included pipelined RISC-V example. [Language and compiler overview](https://github.com/mit-plv/koika/blob/master/README.rst).

Its value is the connection between reusable design abstractions and their formal semantics; generated RTL quality should be evaluated separately for a particular design.

### 20. [project-oak/silveroak](https://github.com/project-oak/silveroak)

**Language/role:** Coq with Haskell infrastructure; Cava hardware DSL and verification of structural circuits. **Archived** GitHub research repository.

Silver Oak complements rule-based languages with a structural, combinator-oriented approach suitable for datapaths and cryptographic peripherals. Study how circuit construction preserves sharing while supporting different interpretations.

- **C2:** Cava parameterizes circuit definitions over a typeclass, uses a monad to preserve sharing, and separates typed signals, circuit structure, simulation, and netlist generation. Its vector combinators make hardware families reusable without discarding structural control. [Cava reference](https://github.com/project-oak/silveroak/blob/main/docs/reference.md).
- **C1:** The project places circuit specifications, implementations, and proofs within Coq, including work on OpenTitan-style cryptographic peripherals. Crucially, it explicitly limits its verification claim to circuits rather than the complete Cava-to-SystemVerilog compiler infrastructure. [Verification scope and design rationale](https://github.com/project-oak/silveroak/blob/main/README.md).

That compiler trust boundary and archived status are material limitations. This is a selection for studying proof-oriented hardware design, not a claim of an entirely verified production toolchain.

## Arithmetic and hardware-security specialists

### 21. [d-kfmnn/amulet2](https://github.com/d-kfmnn/amulet2)

**Language/role:** C++ with GMP; algebraic verification and certification of signed and unsigned multiplier circuits represented as AIGs.

Study a specialized alternative to general-purpose SAT equivalence. AMulet2 makes the circuit-to-polynomial reduction and the generation of independently checkable proof material accessible in a compact codebase.

- **C1:** The verification routine reduces a specification polynomial, validates the shape of a nonzero remainder before constructing a counterexample, and distinguishes malformed slicing results from a valid incorrect-multiplier witness. [Verification routine](https://github.com/d-kfmnn/amulet2/blob/main/src/polynomial_solver.cpp).
- **C3:** The pipeline removes internal XOR gates, attempts XOR-based slicing, falls back to input-cone slicing, and eliminates recognized Booth structure before reduction. These are explicit tactics for controlling algebraic expression growth.
- **C2:** Separate substitution, verification, and certification modes expose reusable stages and proof outputs. The [usage and version notes](https://github.com/d-kfmnn/amulet2/blob/main/README.md) also document polynomial-memory changes and slicing bugs found through fuzzing and delta debugging.

This is a multiplier specialist, not a general RTL equivalence checker.

### 22. [Chair-for-Security-Engineering/SILVER](https://github.com/Chair-for-Security-Engineering/SILVER)

**Language/role:** C++ verification framework with bundled C dependencies; statistical-independence and leakage verification for masked circuit implementations.

Study security properties that functional equivalence does not establish. SILVER interprets circuit signals with reduced ordered binary decision diagrams and checks whether observations reveal secret-dependent information under specified probing models.

- **C1:** The framework distinguishes ordinary and robust security models and several notions of non-interference, as well as output-sharing uniformity. Its worked example shows that a circuit can satisfy one notion and fail another. [Models and usage](https://github.com/Chair-for-Security-Engineering/SILVER/blob/master/README.md).
- **C2:** A shared graph representation and parse/elaborate pipeline feed separate probing, NI, SNI, PINI, and uniformity checkers, with probing order and model choices exposed explicitly. [Verification interface](https://github.com/Chair-for-Security-Engineering/SILVER/blob/master/inc/Silver.hpp).
- **C3:** The documented Sylvan integration exposes core and memory budgets for the BDD workload. No numerical speedup claim is needed to identify this resource-conscious design.

Security results depend on correct secret/share annotations and the selected leakage model.

### 23. [isec-tugraz/rebecca](https://github.com/isec-tugraz/rebecca)

**Language/role:** Python with Z3 and Yosys-derived netlists; formal analysis of masked hardware in the presence of glitches. **Historical research republication:** the README says this is the original EUROCRYPT 2018 tool code republished with license declarations; it is not counted alongside the original repository.

Study a contrasting security encoding to SILVER's decision-diagram approach. REBECCA propagates symbolic share/mask information through a circuit graph and asks whether a bounded set of observations violates the separation condition.

- **C1:** The checker maintains distinct stable and transient variables, constrains probe activation by the requested security order, and uses different transfer rules for linear gates, nonlinear gates, and registers. This makes glitch modeling and mask cancellation concrete. [Z3 encoding](https://github.com/isec-tugraz/rebecca/blob/master/Z3Checker.py).
- **C2:** Circuit topology, user labeling, security order, observation mode, and independence/security checks are separated as inputs to a reusable checker rather than hard-coded to a single gadget. [Workflow and republication status](https://github.com/isec-tugraz/rebecca/blob/master/README.md).

Interpret conclusions under its documented abstraction and labeling scheme; no active-maintenance claim is made.

## Search coverage and limitations

Discovery used more than six distinct formulations, including broad hardware formal/equivalence tools; RTL model checking and Yosys flows; word-level BTOR2/AVR/BtorMC engines; Rust hardware checkers; HW-CBMC and cross-level checking; CoSA/ILAng SoC abstractions; RISC-V/RVFI frameworks; Coq/Kami/Kôika hardware reasoning; symbolic trajectory evaluation and VossII; algebraic multiplier verification; masked-hardware leakage/glitch analysis; and VHDL/PSL methodologies. Later broad SMT/framework and VHDL searches mostly returned already-covered infrastructure, tutorial collections, simulation tools, or adjacent projects, with FVM adding a substantive final perspective.

Every retained canonical repository URL was checked through GitHub's API via the GitHub connector. Repository READMEs and additional primary documentation or source files were opened and read; each entry links substantive semantics, architecture, or implementation evidence. Archive flags and push metadata were checked, but recent pushes were not treated as proof of maintenance quality. GitHub metadata supplied the historical status notes; explicit project statements establish Boolector's retirement, FVM's mirror status, and REBECCA's republication. No candidate code was executed, dependencies installed, or large repositories cloned.

The selection intentionally excludes simulation-only frameworks such as UVVM/OSVVM, standalone HDL parsers and synthesis backends without their own relevant proof subsystem, generic SAT/SMT solvers merely used as dependencies, awesome-lists, tutorial-only repositories, and processor implementations that only consume the listed tools. Boolector is the explicit exception to the generic-solver exclusion because its repository contains BtorMC. Yosys, ACL2, and HW-CBMC are each counted once despite containing multiple relevant components. Alternative Kami lineages and competition snapshots/forks of the same model checker were not inflated into separate entries.

The research is strongest on digital functional verification, architectural semantics, arithmetic, and masking security. It does not claim comprehensive coverage of analog/mixed-signal formal methods, proprietary signoff tools, or every research artifact. Historical toolchains may need dependency work, and formal guarantees remain relative to the frontend semantics, initial-state/environment assumptions, abstraction choices, and trusted backend components. Those limits are part of selecting a codebase to study.
