# Program verification and contract checking tools

Research date: **2026-10-09**.

This selection covers 25 GitHub codebases implementing deductive program verification, bounded model checking, symbolic execution, or executable design-by-contract checks. It includes verification languages, reusable verification backends, language-specific tools, and runtime libraries. These approaches provide different guarantees: a runtime check covers an execution, symbolic exploration may be incomplete, and a proof depends on its specification, supported semantics, and trusted components. The entries identify engineering material worth studying rather than certify every component of a project.

## Criteria legend

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or subtle failure modes.
- **C2 — Reusable abstractions:** substantial components or interfaces supporting multiple programs, domains, or analysis strategies.
- **C3 — Performance and structure:** explicit responses to real analysis or execution costs, with understandable architectural boundaries.
- **C4 — Sustained evolution:** years of development accompanied by compatibility, testing, or complexity-management evidence. Neither repository age nor a recent commit is sufficient.

Each entry justifies at least two criteria. An omitted criterion is unassessed, not a negative judgment. Language labels distinguish implementation languages from languages being checked. Repository headings link to canonical pages that were opened during research; the additional links are inspected primary documentation or source entry points.

## Verification languages and reusable proof infrastructure

### 1. [dafny-lang/dafny](https://github.com/dafny-lang/dafny)

**Language/role:** C# implementation; verification-aware language, verifier, and compiler.

Dafny is useful for studying how contracts, heap specifications, loop invariants, and termination arguments become automated proof obligations while the same source language remains executable. Its Boogie translation makes proof-search control concrete: recursive functions receive a fuel argument, recursive unfolding consumes fuel, and opaque definitions are exposed through explicit mechanisms. This separates mathematical meaning from how aggressively the solver unfolds definitions. [Boogie compilation design](https://github.com/dafny-lang/dafny/blob/master/docs/Compilation/Boogie.md).

- **C1:** Specifications include mutation boundaries and termination, requiring coordinated reasoning about heap state, recursion, and logical assumptions.
- **C2:** A common specification language and verification pipeline support multiple compiler targets and reusable verified libraries.
- **C3:** Fuel and opacity constrain unfolding; the release notes also document assertion isolation, proof-complexity reporting, and fixes to IDE caching and memory consumption. These are specific responses to expensive and unstable verification workloads. [Release notes](https://raw.githubusercontent.com/dafny-lang/dafny/master/RELEASE_NOTES.md).

**Study entry points:** the compilation design and release notes above. The latter also records soundness fixes and migration-sensitive changes; a successful historical proof should not be treated as independent of tool version.

### 2. [boogie-org/boogie](https://github.com/boogie-org/boogie)

**Language/role:** C#; intermediate verification language and verification-condition generator.

Boogie exposes the boundary between a source-language frontend and automated theorem proving. Frontends encode programs using procedures, assertions, assumptions, maps, contracts, and invariants; Boogie produces solver obligations. An engineer can study the benefits and responsibilities of using a shared logical intermediate representation instead of embedding a separate verifier into every compiler.

- **C1:** The representation distinguishes mathematical integers and reals from fixed-width bitvectors, and distinguishes required preconditions from assumed axioms. The language reference discusses inconsistent assumptions, a crucial boundary: an inconsistent encoding can make obligations vacuous.
- **C2:** Source-language-independent procedures, maps, framing clauses, and solver integration provide reusable verification infrastructure rather than a checker for one application.

**Study entry point:** [language reference](https://boogie-docs.readthedocs.io/en/latest/LangRef.html), especially types, procedure contracts, and inconsistent assumptions. This reference explicitly labels itself out of date and contains unfinished sections; use it for the inspected semantic concepts and consult the repository for current implementation details. It is not evidence that every documented interface remains current.

### 3. [FStarLang/FStar](https://github.com/FStarLang/FStar)

**Language/role:** F* and OCaml; proof-oriented programming language with extraction.

F* makes specifications part of the type system. It is a strong study choice for connecting dependent function types, refinements, SMT automation, and executable programs. Its tutorial gives actual introduction and elimination rules: constructing a refined value requires proving the predicate, while using it as its base type can forget that refinement. [Refinements and dependent functions](https://fstar-lang.org/tutorial/book/part1/part1_getting_off_the_ground.html).

- **C1:** Refinement obligations express constraints that ordinary types cannot, with proof obligations dependent on particular values and function arguments.
- **C2:** First-class dependent functions and refinement types compose across libraries; the repository integrates verification with extraction to executable target languages.

**Study entry point:** the tutorial chapter above, followed through to its specification examples. The engineering lesson is how a language assigns obligations to type formation, function application, and value construction, rather than merely attaching assertions to existing syntax. Extraction and external dependencies remain relevant parts of the overall assurance boundary.

### 4. [epfl-lara/stainless](https://github.com/epfl-lara/stainless)

**Language/role:** Scala; deductive verifier for a supported Scala subset.

Stainless offers an instructive division of responsibility: its transformations and contract/termination reasoning sit above the reusable Inox solver infrastructure. Its imperative-language documentation explains how mutation can be translated into functional updates, with restrictions on aliasing used to make that translation tractable. It also distinguishes current state from pre-state through `old`. [Imperative programs](https://epfl-lara.github.io/stainless/imperative.html).

- **C1:** Mutable objects, pre-state references, and termination create obligations beyond checking expression types. The documented alias restrictions expose where sound translation depends on accepted language constructs.
- **C2:** A layered transformation pipeline handles functional and imperative source constructs while delegating logical queries to Inox.

**Study entry point:** the imperative translation guide above. The repository explains the current Scala 3 focus and identifies v0.9.8.7 as the final Scala 2-compatible release. The inspected imperative guide has an older version banner, so its transformation explanation should not be mistaken for a complete current compatibility matrix. GitHub is identified as the primary repository, with GitLab as its mirror.

### 5. [ucsd-progsys/liquidhaskell](https://github.com/ucsd-progsys/liquidhaskell)

**Language/role:** Haskell; refinement-type checking integrated into GHC.

LiquidHaskell is particularly useful for studying integration with a real compiler and module system. Its repository describes a GHC plugin that works with unoptimized Core and serializes lifted specifications into interface files. Abstract and bounded refinements let specifications describe families of data structures and higher-order relationships rather than isolated predicates. [Specification guide](https://ucsd-progsys.github.io/liquidhaskell/specifications/).

- **C1:** Refinement constraints and constructor-established datatype invariants require logical reasoning beyond ordinary Haskell typing. The guide explicitly distinguishes local datatype invariants from an older, unsound global-invariant mechanism.
- **C2:** Measures, abstract refinements, and reusable specifications compose with functions and datatypes across module boundaries.
- **C3:** The plugin architecture stores specification payloads in GHC interface files and uses fingerprints to participate in recompilation decisions, addressing repeated verification work within an existing build model. [Compiler integration explanation](https://github.com/ucsd-progsys/liquidhaskell#readme).

**Study entry points:** the specification guide and the repository’s plugin architecture discussion. Pay attention to the compiler representation selected for checking and to how specification dependencies are made visible to incremental builds.

## Heap ownership, concurrency, and mainstream-language contracts

### 6. [viperproject/silicon](https://github.com/viperproject/silicon)

**Language/role:** Scala; symbolic-execution backend for the Viper verification language.

Silicon is a focused backend, distinct from frontends that translate particular programming languages into Viper. Its repository demonstrates shared-state reasoning with fractional permissions and lock invariants. The central operations are technically revealing: `inhale` adds permissions and assumptions, while `exhale` checks required facts and permissions before consuming resources. [Permission transfer semantics](https://viper.ethz.ch/tutorial/permissions-inhale-exhale.html).

- **C1:** Heap access and concurrency require accounting for resources, not just proving value predicates. Fractional access supports shared reads while exclusive write permissions constrain mutation.
- **C2:** The same permission-transfer primitives represent procedure calls, loop invariants, and synchronization encodings, making the backend usable by multiple language frontends.

**Study entry point:** the inhale/exhale tutorial above, read alongside Silicon’s repository example. It shows why a verifier must track both logical facts and authority to access memory. The tutorial describes shared Viper semantics; the selected repository is specifically the Silicon implementation of symbolic verification over that language.

### 7. [viperproject/gobra](https://github.com/viperproject/gobra)

**Language/role:** Scala; verifier for annotated Go, translating to Viper.

Gobra shows how a language frontend maps Go concepts into a permission-based verification system. Its tutorial covers function contracts, predicates for structured heap resources, and interfaces, and explicitly describes modular checking: a caller uses a callee’s specification rather than repeatedly analyzing its implementation. [Gobra tutorial](https://github.com/viperproject/gobra/blob/master/docs/tutorial.md).

- **C1:** The intended checks include memory safety, absence of certain runtime failures, data-race freedom, and functional partial correctness for supported concurrent Go programs.
- **C2:** Contracts and predicates encapsulate implementation details, while the Viper translation can use Silicon or Carbon as backends. Interface specifications and implementation proofs extend modular reasoning across Go abstractions.

**Study entry point:** the tutorial above. Its treatment of trusted or bodyless methods is especially valuable: their contracts enter the proof as assumptions, making the trusted boundary visible. The repository calls Gobra a prototype; this is a study recommendation for a substantial research implementation, not a claim of complete Go support or termination proof for every accepted program.

### 8. [verifast/verifast](https://github.com/verifast/verifast)

**Language/role:** Primarily OCaml; separation-logic verification for C, Java, and Rust.

VeriFast combines symbolic verification with user-defined predicates, inductive datatypes, recursive pure functions, and lemma functions. These mechanisms allow heap structures and ownership protocols to be described independently of individual clients. It is also unusually useful for studying how a verifier documents its own assumptions and known gaps.

- **C1:** Its central problems include ownership, shared mutable state, concurrent resource protocols, and the relationship between source semantics and compiler behavior.
- **C2:** Abstract predicates and reusable lemmas provide modular proof interfaces for data structures and APIs instead of requiring every client to reason about their representation.

**Study entry point:** [soundness boundaries](https://github.com/verifast/verifast/blob/master/soundness.md). This document records concrete issues involving C strict aliasing, compilation-unit assumptions, Java exceptions, and other corner cases. Those details make the project useful for analyzing the limits of a trusted frontend and symbolic semantics. The repository describes a research prototype; the presence of documented soundness issues is material and rules out presenting verification as an unconditional guarantee.

### 9. [OpenJML/OpenJML](https://github.com/OpenJML/OpenJML)

**Language/role:** Java; JML specification checking integrated with a Java compiler codebase.

The relevant subsystem is OpenJML’s verification implementation and its tests, within a repository containing substantial OpenJDK-derived code. Count this monorepo once, rather than treating the inherited JDK as a second verification project. OpenJML is useful for studying how Java mutation, arithmetic, and method contracts become modular proof obligations.

- **C1:** The frame-condition tutorial combines arithmetic overflow preconditions with pre-state values and restrictions on assignments. Assigning the same value still violates a frame that forbids writing that location.
- **C2:** JML method specifications summarize permitted effects and results, allowing callers to reason without inlining method bodies. Array ranges and object-field frames make the interface applicable to many mutable APIs.

**Study entry point:** [frame conditions](https://www.openjml.org/tutorial/FrameConditions). It explains the permissive default frame, intersection of multiple frame clauses, and why missing effect specifications make apparently simple caller assertions unprovable. These are concrete lessons in specification design and modularity, not just annotation syntax.

### 10. [KeYProject/key](https://github.com/KeYProject/key)

**Language/role:** Java; deductive verification and symbolic reasoning for Java/JML.

KeY exposes proof obligations through Java dynamic logic and combines automation with interactive proof development. The repository separates core reasoning, utilities, UI, and optional extensions; it also identifies uses of the core for symbolic execution and test generation. This makes it a useful larger codebase for studying the boundary between proof machinery and user interaction.

- **C1:** Its contract obligations combine normal and exceptional behavior, termination, postconditions, frame conditions, and class invariants. Loop annotations guide proofs across repeated state changes.
- **C2:** A reusable reasoning core supports multiple applications and extensions; contract-based proof construction separates program semantics from UI and proof-search presentation.

**Study entry point:** [proving contracts](https://keyproject.github.io/key-docs/quicktour/proving/), alongside the module overview in the repository. The quick tour explains how contract clauses contribute to the formula being proved. It carries a documentation-status caveat, so its conceptual account is stronger evidence here than its exact menu names or screenshots. No claim of complete Java-language coverage is implied.

### 11. [AdaCore/spark2014](https://github.com/AdaCore/spark2014)

**Language/role:** Ada and OCaml; SPARK verification tools, including GNATprove and GNAT2Why.

SPARK offers a concrete compiler-to-prover architecture: flow analysis checks initialization and dependencies, GNAT2Why translates proof obligations, and Why3 dispatches them to provers. The quality-assurance documentation goes beyond a test-suite claim: it discusses Coq realizations of base theories, control of solver versions, and safeguards against inconsistent function axioms. [Verification architecture and QA](https://docs.adacore.com/live/wave/spark2014/html/spark2014_ug/en/appendix/quality_assurance.html).

- **C1:** Initialization, parameter/global effects, bitvectors, floating-point theories, and axiom consistency are explicit correctness concerns. Function axioms are constrained to relevant call contexts, and nonreturning functions require special handling.
- **C2:** Compiler analysis, logical translation, and solver orchestration form separate reusable layers serving many SPARK programs.

**Study entry point:** the architecture/QA appendix above. It connects proof-theory design with regression suites, compiler tests, and integration testing. The repository notes that development branches can require matching GNAT development versions; public release branches are the more appropriate reference for reproducible toolchain combinations.

## Model checking, abstract interpretation, and symbolic execution

### 12. [diffblue/cbmc](https://github.com/diffblue/cbmc)

**Language/role:** C++; bounded checking for C/C++, with related CProver tools and JBMC in the same repository.

CBMC is a strong study target for lowering realistic program semantics into solver formulas. The shared GOTO representation contains explicit control flow, guards, declarations, lifetime endings, and nondeterministic values; transformations remove higher-level side effects and insert checks. [GOTO-program architecture](https://diffblue.github.io/cbmc/group__goto-programs.html).

- **C1:** Bounds, pointer validity, assertions, and related runtime errors require precise treatment of memory and machine-level values. Loop unwinding and analysis bounds must be understood when interpreting results.
- **C2:** Language-independent GOTO programs support instrumentation, transformations, serialization, and multiple frontends. The relevant abstraction is the CProver representation, not merely one command-line executable.
- **C3:** Lazy GOTO models convert methods on demand rather than eagerly materializing unreachable code; serialization also shares repeated expression structures and strings.

**Study entry point:** the GOTO-program documentation above. It makes representation choices and resource costs visible in the same architectural layer. CBMC and JBMC are counted together because the repository and major infrastructure are shared.

### 13. [esbmc/esbmc](https://github.com/esbmc/esbmc)

**Language/role:** C++; SMT-based bounded model checking with multiple language frontends.

ESBMC’s architecture follows a readable pipeline: frontend AST, GOTO representation, symbolic execution with loop/recursion unwinding, SSA constraints, then SMT solving. Its documentation distinguishes bounded exploration from k-induction, which can establish properties beyond a fixed unwind depth when the required obligations succeed. [Architecture](https://github.com/esbmc/esbmc/blob/master/ARCHITECTURE.md).

- **C1:** Its C/C++ checking includes numerical semantics and concurrency concerns, with the repository describing pthread interleavings, deadlock and race checks, bitvectors, and floating-point reasoning.
- **C2:** Frontend translation and backend solver interfaces share a common intermediate pipeline, allowing different source languages and SMT engines to participate.
- **C3:** The repository explains lazy interleaving exploration as an alternative to placing all interleavings in one formula, exposing a real state-space-management decision.

**Study entry point:** the architecture document above, supplemented by the repository’s concurrency explanation. The value is in seeing how verification modes alter the exploration and proof strategy. A bounded result should not be silently interpreted as an unbounded correctness theorem.

### 14. [sosy-lab/cpachecker](https://github.com/sosy-lab/cpachecker)

**Language/role:** Java; configurable program analysis for software verification. **Official read-only GitHub mirror.**

CPAchecker is especially valuable for studying analysis composition. Its central interface separates abstract domains, transfer relations, merge operators, stopping conditions, precision adjustment, and initial states. These are substantive algorithmic extension points rather than a collection of loosely connected command-line tools. [ConfigurableProgramAnalysis interface](https://raw.githubusercontent.com/sosy-lab/cpachecker/main/src/org/sosy_lab/cpachecker/core/interfaces/ConfigurableProgramAnalysis.java).

- **C1:** Correct abstract reachability depends on how transfer, merge, and stopping operations approximate concrete behavior; precision adjustment makes the soundness/precision boundary explicit.
- **C2:** The CPA interface permits reusable analyses and combinations of analyses, with specifications and counterexample reporting around the common engine.

**Study entry points:** the interface above and [developer documentation](https://raw.githubusercontent.com/sosy-lab/cpachecker/main/doc/Developing.md). The latter describes static checks, unit testing, and large regression campaigns across configurations. This supports studying how a configurable verifier controls combinatorial integration complexity, without inferring reliability merely from project age. The GitHub mirror remains a substantive source tree; its read-only status is explicit, not evidence of abandonment.

### 15. [ultimate-pa/ultimate](https://github.com/ultimate-pa/ultimate)

**Language/role:** Java; verification framework containing Automizer, Taipan, GemCutter, and related tools.

Ultimate is one monorepo with multiple analysis strategies. Its repository explains Automizer’s trace abstraction, Taipan’s combination of abstract interpretation and trace abstraction, and GemCutter’s concurrent-program exploration. Study it to see how specialized verification algorithms share parsers, intermediate representations, analysis infrastructure, and witness handling.

- **C1:** Trace infeasibility, invariant discovery, and concurrent interleavings create distinct proof obligations. GemCutter’s commutativity-based reduction addresses the difficulty of exploring equivalent thread schedules.
- **C2:** Toolchains explicitly compose plugins. The usage guide gives a pipeline from C translation through procedure inlining and control-flow construction to trace abstraction and witness printing.
- **C3:** Configurable abstraction and partial-order reduction address state-space size; the usage guide also exposes floating-point overapproximation and its effect on possible `UNKNOWN` results.

**Study entry point:** [toolchains and analysis settings](https://github.com/ultimate-pa/ultimate/wiki/Usage). The architecture separates input, plugin sequence, and preferences, making precision/performance decisions inspectable. The project identifies its tools as evolving research software; the named tools are not counted as independent repositories.

### 16. [seahorn/seahorn](https://github.com/seahorn/seahorn)

**Language/role:** C++ with Python orchestration; LLVM-based verification using constrained Horn clauses.

SeaHorn has a particularly clear three-stage architecture. A frontend prepares LLVM bitcode, a middle layer encodes program semantics and proof obligations as constrained Horn clauses, and a backend combines automated reasoning with abstract interpretation. Its official architecture description identifies PDR/IC3-style solving and Crab-generated invariants. [Architecture and reasoning components](https://seahorn.github.io/).

- **C1:** Safety invariants and termination arguments require reasoning about unbounded behavior rather than only executing test inputs. The architecture also describes ranking-function synthesis and validation for termination work.
- **C2:** The LLVM-to-Horn-clause boundary separates program translation from reasoning, allowing different semantic encodings, precision choices, and solving components.

**Study entry point:** the project’s architecture overview above. It is a good route into understanding why intermediate logical representations matter: the frontend’s operational details and the backend’s proof algorithms can evolve around an explicit contract. The repository and site describe several analysis modes; inclusion does not assert that every mode supports every C construct equally.

### 17. [klee/klee](https://github.com/klee/klee)

**Language/role:** C++; LLVM symbolic execution and counterexample/test generation.

KLEE is useful for studying the architecture needed when solver queries dominate an analysis. Its solver chain is a sequence of decorators that can transform, cache, validate, or forward queries. Independence analysis partitions unrelated constraints; counterexample caching reuses satisfying assignments rather than only exact query results. [Solver-chain design](https://klee-se.org/docs/solver-chain/).

- **C1:** Symbolic execution must preserve the relationship between execution-state expressions and solver semantics. Assignment validation and cross-checking with another solver are explicit mechanisms for detecting mismatches.
- **C2:** Common solver interfaces let caching, validation, independence handling, and alternative solver backends be composed without embedding each concern in the execution engine.
- **C3:** Query caching, counterexample reuse, and constraint independence directly reduce expensive solver work while keeping these optimizations structurally separate.

**Study entry point:** the solver-chain documentation above. It explains both optimization and validation in the same pipeline. KLEE’s practical exploration limits mean that failure to find a counterexample is not, by itself, proof that all possible executions satisfy the property.

### 18. [OCamlPro/owi](https://github.com/OCamlPro/owi)

**Language/role:** OCaml; WebAssembly analysis and multicore symbolic execution.

Owi brings a less common architecture to this selection: programs from several source languages are compiled to Wasm and checked through shared execution semantics, including cross-language programs. Its current repository distinguishes the main bug-finding engine from experimental abstract-interpretation-based proof work.

- **C1:** The symbolic choice implementation maintains path conditions, checks feasibility, and constructs models for traps or failed assertions. These are concrete correctness responsibilities at the boundary between execution and SMT solving.
- **C2:** A shared Wasm layer and OCaml library support different source languages and integration into other tools; symbolic choice packages state, failure, and branching into a reusable computation abstraction.
- **C3:** The implementation schedules branches with priorities and slices path conditions before solver checks, exposing how parallel exploration and query size are managed. [Symbolic choice implementation](https://github.com/OCamlPro/owi/blob/main/src/symbolic/symbolic_choice.ml).

**Study entry points:** that source file and [developer/testing guide](https://github.com/OCamlPro/owi/blob/main/HACKING.md), which describes Cram tests, documentation tests, fuzzing, coverage, and profiling. Do not conflate its experimental proof direction with completeness of symbolic exploration.

## Rust verification approaches

### 19. [model-checking/kani](https://github.com/model-checking/kani)

**Language/role:** Rust; bit-precise model checking, using CBMC as a backend.

Kani connects Rust compiler semantics, verification harnesses, and a bounded checking engine. Its repository identifies checks for undefined behavior, panics, assertions, and related safety properties. This is a distinct Rust compiler integration and user model, despite sharing a solver backend with CBMC.

- **C1:** Unsafe operations, machine arithmetic, and Rust runtime failures require precise lowering rather than an approximate source-level simulation.
- **C2:** A driver, compiler extension, and harness/API layer organize compilation, nondeterministic inputs, and individual proof targets into reusable components.
- **C3:** The project’s engineering account explains replacing an intermediate JSON conversion with direct GOTO binary serialization, plus field-sensitive constant propagation for unions. These attack conversion and formula costs at identifiable layers. [Architecture and optimization case study](https://model-checking.github.io/kani-verifier-blog/2023/08/03/turbocharging-rust-code-verification.html).

**Study entry point:** that technical article. It is explicitly a 2023 implementation case study, not a current benchmark claim. It also reports uneven workload effects, a useful reminder that a verifier optimization can improve some programs while regressing others.

### 20. [verus-lang/verus](https://github.com/verus-lang/verus)

**Language/role:** Rust; deductive verification for a supported Rust subset.

Verus is particularly interesting where ownership reasoning must connect to concurrent protocols. Its tokenized state-machine machinery turns abstract transitions into ghost token types that verified implementation code manipulates. The method requires choosing an abstraction and then connecting concrete operations to it; the tool does not infer that connection automatically. [State-machine approach](https://verus-lang.github.io/verus/state_machines/high-level-idea.html).

- **C1:** Tracked resources and state-machine invariants express ownership and synchronization obligations beyond ordinary Rust borrowing.
- **C2:** Tokenization strategies are reusable proof abstractions. The map strategy creates key/value tokens, consumes tokens on removal, and requires key absence on insertion; generated exchange functions connect abstract updates to typed token operations. [Map tokenization semantics](https://verus-lang.github.io/verus/state_machines/strategy-map.html).

**Study entry points:** those two state-machine chapters. They explain a concrete bridge from global logical state to locally held capabilities. The repository describes a verifier under development with language-support limitations; this is not a claim that arbitrary existing Rust programs can be verified unchanged.

### 21. [creusot-rs/creusot](https://github.com/creusot-rs/creusot)

**Language/role:** Rust; deductive verification using Why3 infrastructure.

Creusot presents a distinctive treatment of mutable borrowing: a borrow is represented using its current value and a predicted final value, with a resolution constraint when the borrow ends. This supports a functional logical encoding of mutation. Its architecture also separates executable Rust, obtained after borrow checking, from Pearlite specification expressions. [Architecture](https://raw.githubusercontent.com/creusot-rs/creusot/master/ARCHITECTURE.md).

- **C1:** Correctness depends on connecting aliasing, borrow lifetimes, and future values to the source program’s actual mutation behavior. Arithmetic and panic-related obligations add further semantic constraints.
- **C2:** Proc-macro specification extraction, separate representations for program/specification terms, logical library specifications, and Why3 translation provide reusable verification layers.

**Study entry point:** the architecture document above, especially borrow encoding and the executable/specification frontend distinction. It is useful for comparing how a verifier can exploit a language’s existing ownership discipline rather than reproduce a general unrestricted heap model. Some sections discuss unfinished or evolving implementation details; treat the document as an explanation of design, not a promise that every planned feature is supported.

## Executable contracts and dynamic-language symbolic checking

### 22. [pschanely/CrossHair](https://github.com/pschanely/CrossHair)

**Language/role:** Python; symbolic execution for Python contracts and behavioral analysis.

CrossHair follows an unusual path: it executes functions using proxy objects that carry symbolic expressions, rather than first translating the entire function’s AST into another language. When a symbolic boolean is needed for a branch, its implementation consults the solver, chooses a feasible result, and adds the corresponding constraint. [Execution architecture](https://crosshair.readthedocs.io/en/latest/how_does_it_work.html).

- **C1:** The checker must reconcile Python operations and control flow with symbolic values and solver constraints, including the exact point where a symbolic expression becomes a branch decision.
- **C2:** Symbolic proxies and execution machinery can serve contract checking, counterexample generation, and comparison of function behavior through a shared mechanism.

**Study entry point:** the architecture explanation above. The implementation lesson is how host-language dispatch can provide a symbolic interpreter while leaving much ordinary execution intact. Exploration and supported-operation limits remain material: an unreported failure does not establish a universal proof of the Python program.

### 23. [Parquery/icontract](https://github.com/Parquery/icontract)

**Language/role:** Python; runtime preconditions, postconditions, and class invariants.

icontract is a compact but substantive choice for studying contract composition in a dynamic object model. Its implementation documentation describes storing multiple conditions on one checking wrapper, finding wrappers through decorator chains, and maintaining class-invariant metadata. [Implementation details](https://icontract.readthedocs.io/en/latest/implementation_details.html).

- **C1:** Invariant timing and reentrancy are correctness problems: checks must avoid examining partly initialized objects or recursively triggering themselves. The documented function- and instance-level guards make those concerns explicit.
- **C2:** Contract inheritance and shared checking wrappers support reusable class interfaces and stacked conditions without turning each decorator into an independent checking mechanism.

**Study entry point:** the implementation guide above. It offers specific lessons about Python wrappers, object lifecycle, and inherited specifications, with a much smaller conceptual footprint than a theorem prover. These are executable checks on exercised executions; integration with symbolic or generated testing does not turn the runtime library itself into a proof system.

### 24. [life4/deal](https://github.com/life4/deal)

**Language/role:** Python; executable contracts with linting and testing integrations.

deal extends contracts beyond values to exceptions and side effects. The runtime implementation holds preconditions, postconditions, result-dependent conditions, permitted exceptions, and effect patching in a common contract object, then builds separate wrappers for synchronous functions, coroutines, and generators. [Runtime contract implementation](https://raw.githubusercontent.com/life4/deal/master/deal/_runtime/_contracts.py).

- **C1:** Exception-sensitive cleanup matters: patched effects must be restored even when the wrapped body fails. Contract failures and exceptions from the function body follow distinct paths; validation also needs protection against recursively checking itself.
- **C2:** Shared contract metadata supports several calling protocols and connects executable specifications to the repository’s broader lint/test workflows.

**Study entry point:** the runtime source above, particularly wrapper selection and the `try`/`finally` boundaries around execution. This is a concrete example of making a declarative API survive Python’s multiple execution protocols. Separate verification integrations should be assessed on their own supported semantics; their existence is not evidence that every deal contract is statically proved.

### 25. [boostorg/contract](https://github.com/boostorg/contract)

**Language/role:** C++; generic runtime design-by-contract library within the Boost ecosystem.

Boost.Contract is useful for studying contracts in the presence of C++ object lifetime, exceptions, inheritance, and template-based APIs. Its overview explains preconditions, postconditions, old values, exception guarantees, and invariant checking, including how inherited contracts must preserve substitutability. [Contract programming semantics](https://www.boost.org/doc/libs/latest/libs/contract/doc/html/boost_contract/contract_programming_overview.html).

- **C1:** Constructors, destructors, exceptions, recursive checks, and overridden methods make checking order part of correctness. Contract inheritance weakens acceptable preconditions and strengthens promised postconditions.
- **C2:** The library supplies reusable mechanisms for functions and class hierarchies rather than project-specific assertions.
- **C3:** The documentation discusses old-value copying, function-object costs, suppression of nested checks, synchronization, and selective disabling of checks. These expose the cost model and configurable tradeoffs rather than promising free instrumentation.

**Study entry point:** the overview above. Count this focused library once, not the whole Boost organization. Its runtime guarantees concern checks that are enabled and reached; they do not establish that all executions satisfy the contracts.

## Coverage, search method, and limitations

Discovery used more than six distinct live-search formulations, with repeated targeted follow-ups. The search angles included general deductive verification and intermediate verification languages; C/C++ bounded checking and pthread interleavings; separation logic and permission-based Go/C verification; Java JML and frame conditions; Scala/Haskell refinements; F* dependent specifications; Ada proof-tool architecture; Rust model checking and ownership-based deductive verification; LLVM/Horn-clause and abstract-interpretation frameworks; Python/C++ runtime contracts; and Wasm symbolic execution. Later searches for smaller projects, architecture documents, mirrors, and runtime implementation internals produced mostly overlap, with Owi supplying a distinct Wasm-centered design.

For every retained repository, the canonical GitHub page and at least one additional primary source were opened and read. The evidence includes implementation files, logical encoding descriptions, interface definitions, developer/testing guides, and technical project documentation. Performance criteria refer to identifiable engineering mechanisms, not unverified speedup claims. C4 was not assigned merely from age, release counts, or activity timestamps; the selected entries already satisfy at least two more directly documented criteria.

Generic SMT solvers and general-purpose proof assistants were excluded as foundational dependencies rather than the direct program-checking tools sought here. Tutorial-only projects, lists, thin integrations, and duplicate monorepo subsystems were also excluded. [Frama-C’s GitHub snapshot](https://github.com/Frama-C/Frama-C-snapshot) was inspected but excluded: its own notice says development moved and that releases from version 21 onward are absent. CPAchecker remains included because its explicitly identified read-only GitHub mirror contains the substantive implementation. Boogie-based frontends, Viper frontends/backends, and Kani/CBMC are separate implementations with distinct abstraction responsibilities, not duplicate forks.

This was read-only source/documentation research: no candidate was cloned, built, benchmarked, or tested. Some documentation is historical or incomplete, and the relevant entries identify that limitation. Unless an entry explicitly states a checked status, inclusion should not be read as a claim about present support commitments or maintenance cadence. The suggested study value is an engineering inference from the cited structures; it is not a comparative audit of soundness, usability, or production readiness.
