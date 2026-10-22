# Smart contract virtual machines and verification tools

Research date: **2026-10-09**.

This guide selects 24 GitHub repositories implementing smart contract execution engines, language safety machinery, formal or symbolic verification, static analysis, and property-based security testing. It covers both standalone tools and explicitly identified subsystems of larger repositories. The emphasis is on engineering decisions worth studying: transaction rollback, numerical semantics, host boundaries, reusable analysis representations, resource accounting, and tractable exploration of adversarial programs. Inclusion is a reasoned assessment of the cited material, not a claim that every component is exemplary or that any tool establishes complete contract security.

**Criteria legend**

- **C1 — Difficult correctness:** invariants, numerical semantics, concurrency, adversarial inputs, or failure behavior.
- **C2 — Reusable abstractions:** substantial interfaces, intermediate representations, engines, or frameworks supporting multiple uses.
- **C3 — Performance with structure:** concrete measures addressing execution or analysis costs while retaining understandable architecture.
- **C4 — Sustained evolution:** multi-year development with evidence of compatibility work, testing, or deliberate complexity management.

Each heading links to a verified canonical repository. The implementation and documentation links within each entry are suggested reading entry points. Maintenance statements are limited to evidence inspected on the research date; an entry without an archival label is not a guarantee of ongoing maintenance.

## Execution engines and host boundaries

### [bluealloy/revm](https://github.com/bluealloy/revm)

**Rust — embeddable EVM and framework for customized execution.** Study how a consensus-sensitive interpreter can expose customization without making database access, transaction handling, tracing, and opcode execution one inseparable layer.

- **C1:** Journaled state and execution/commit separation make rollback an explicit concern. The changelog records concrete failures involving memory out-of-gas, failed contract creation warming accounts, and journal finalization, rather than merely asserting correctness. See the [architecture](https://bluealloy.github.io/revm/architecture.html) and [changelog](https://github.com/bluealloy/revm/blob/main/CHANGELOG.md).
- **C2:** Context, database, instruction, precompile, handler, and inspector interfaces allow different hosts and EVM variants to reuse the execution machinery. The architecture explains their responsibilities and composition.
- **C4:** The changelog spans 2022–2026 and documents consensus fixes, framework reorganizations, API compatibility classifications, migrations, and receipt-root validation in blockchain tests. It provides unusually concrete evidence of managing evolution across protocol and library changes.

### [ipsilon/evmone](https://github.com/ipsilon/evmone)

**C++ — standalone EVM implementing the EVMC interface.** Its baseline and advanced interpreters make this a useful comparison of inexpensive startup against more aggressive bytecode analysis.

- **C1:** The [gas calculation design](https://github.com/ipsilon/evmone/blob/master/docs/efficient_gas_calculation_algorithm.md) explicitly reasons about exceptional termination, stack underflow/overflow, dynamic gas, and instructions that observe remaining gas. It also identifies observable tracing differences introduced by checking some failures earlier.
- **C3:** Basic-block analysis precomputes static gas charges and stack requirements, reducing repeated checks during execution. Dynamic charges remain separate, and gas-observing instructions receive corrections. This is a concrete optimization with its semantic obligations explained alongside the algorithm.
- **C2:** The [repository overview](https://github.com/ipsilon/evmone) describes an EVMC-compatible engine, allowing hosts to integrate the VM through a defined boundary rather than incorporating a complete blockchain client.

### [ethereumjs/ethereumjs-monorepo](https://github.com/ethereumjs/ethereumjs-monorepo)

**TypeScript — the `packages/vm` execution subsystem and its companion EVM/state packages.** Counted once as a monorepo. Study transaction orchestration separately from individual EVM instructions and persistent state management.

- **C1:** The [VM package documentation](https://github.com/ethereumjs/ethereumjs-monorepo/tree/master/packages/vm) walks through balance and nonce checks, intrinsic gas, access-list preparation, execution, refunds, receipts, and checkpoint/commit/revert behavior. These are consensus obligations surrounding the interpreter, not just opcode semantics.
- **C2:** VM, EVM, state manager, blockchain, and protocol configuration have separate interfaces. The package explains injected implementations and selecting historical hardfork rules through `Common`, making the code useful for simulation and custom execution environments.
- **C4:** The same documentation records the 2023 module-format transition and 2025 removal of Node-specific primitives, alongside hardfork-specific testing and fixture execution. These are concrete examples of preserving usability while changing packaging and protocol behavior.

### [CosmWasm/cosmwasm](https://github.com/CosmWasm/cosmwasm)

**Rust — Wasm contract runtime and contract-facing libraries; focus on `packages/vm`.** The cache implementation is a particularly instructive boundary between consensus execution, expensive compilation, and machine-local resources.

- **C1:** [`cache.rs`](https://github.com/CosmWasm/cosmwasm/blob/main/packages/vm/src/cache.rs) validates Wasm before compilation, checks loaded code against its checksum, and separates locks around shared cache state and instantiation. Its unsafe-construction documentation explicitly states the trust assumption for compiled artifacts on disk; it also warns that cache statistics must not influence consensus behavior.
- **C2:** The cache is parameterized over backend API, storage, and querier implementations, supporting different host environments through explicit interfaces.
- **C3:** Pinned-memory, ordinary memory, and filesystem cache tiers avoid repeating compilation while keeping instantiation and artifact management distinct. Study the actual cache lifecycle and error paths rather than assuming that a Wasm sandbox alone solves all isolation concerns.

### [stellar/rs-soroban-env](https://github.com/stellar/rs-soroban-env)

**Rust — Soroban host, guest interface, and shared environment definitions.** This repository is useful for studying how an SDK-visible value model maps onto an isolated Wasm runtime.

- **C1:** The [guest interface specification](https://github.com/stellar/rs-soroban-env/blob/main/docs/GUEST_INTERFACE.md) explains tagged values, host-owned object handles, bounds-checked guest memory access, and the distinction between recoverable contract errors and unrecoverable host failures. Budget exhaustion cannot simply be caught by the contract and ignored.
- **C2:** A common environment interface is implemented differently for host and guest execution. It supports native host tooling and Wasm contract bindings while preventing guest values from becoming arbitrary host pointers.
- **C3:** The interface includes bulk memory operations that reduce repeated boundary crossings. The useful architectural lesson is how representation and API granularity affect both isolation and execution cost, not an unverified throughput claim.

### [FuelLabs/fuel-vm](https://github.com/FuelLabs/fuel-vm)

**Rust — register-based VM for Fuel scripts, contracts, and predicates.** Study how a VM's execution context and transaction types constrain the operations available to its interpreter.

- **C1:** The [interpreter implementation](https://raw.githubusercontent.com/FuelLabs/fuel-vm/master/fuel-vm/src/interpreter.rs) keeps registers, memory, call frames, receipts, transaction state, and gas parameters together behind controlled access. The [repository's testing examples](https://github.com/FuelLabs/fuel-vm) include opcode tests and a memory-overflow reproducer, exposing failure semantics as a first-class concern.
- **C2:** Generic storage, memory, transaction, and verification components support multiple transaction forms without duplicating the entire execution engine. This is a useful contrast with the stack-based EVM model.
- **C3:** The interpreter explicitly caches storage slots for repeated accesses and tracks the associated execution context. The relevant study question is how caching interacts with protocol accounting and transaction-local state.

### [starkware-libs/cairo-vm](https://github.com/starkware-libs/cairo-vm)

**Rust — Cairo execution engine used in the provable-program and Starknet ecosystem.** This entry concerns execution and trace machinery; it should not be mistaken for a complete cryptographic proof verifier.

- **C1:** [`vm_core.rs`](https://github.com/starkware-libs/cairo-vm/blob/main/vm/src/vm/vm_core.rs) distinguishes field elements from relocatable addresses, deduces operands under instruction constraints, and checks assertion and return-address consistency. Its tests exercise inconsistent memory and arithmetic or addressing failures.
- **C2:** Builtin runners, hint processing, segmented memory, and optional execution traces are separate concepts. Their interaction makes the code useful for understanding how a VM supports proof-oriented execution without embedding every operation directly into one instruction loop.
- **C3:** The same implementation contains instruction caching and selectively enabled trace collection, showing how ordinary interpreter costs coexist with the additional artifacts needed by proving workflows.

### [neo-project/neo-vm](https://github.com/neo-project/neo-vm)

**C# — embeddable stack VM for Neo smart contracts.** Study a managed-language runtime that makes limits, object lifetimes, and host extensibility explicit.

- **C1:** [`ExecutionEngine.cs`](https://raw.githubusercontent.com/neo-project/neo-vm/master/src/Neo.VM/ExecutionEngine.cs) manages invocation contexts, reference counting, execution limits, and transitions into a fault state. Context unloading and exception handling show how failures interact with runtime object lifetimes.
- **C2:** The engine accepts a jump table, limit configuration, and reference-counter implementation, and exposes instruction/context hooks. These boundaries allow instruction dispatch and host integration to vary without rewriting the core execution lifecycle.

The [repository overview](https://github.com/neo-project/neo-vm) supplies the contract-VM context; the execution engine is the more useful starting point for evaluating its actual architecture.

## Language safety and formally specified runtimes

### [aptos-labs/aptos-core](https://github.com/aptos-labs/aptos-core)

**Rust — specifically the Move bytecode verifier and Move Prover under `third_party/move`.** Counted once; the networking and consensus portions of this large monorepo are outside this entry's scope. Study the distinction between admitting safe bytecode and proving a user-specified functional property.

- **C1:** The [bytecode verifier design](https://github.com/aptos-labs/aptos-core/blob/main/third_party/move/move-bytecode-verifier/README.md) describes control-flow, stack/type, resource, and reference checks. Abstract interpretation computes fixed points over control-flow joins; mutation-based tests exercise invalid programs.
- **C2:** The [prover driver](https://github.com/aptos-labs/aptos-core/blob/main/third_party/move/move-prover/src/lib.rs) composes compiler/model construction, a stackless-bytecode pipeline, translation to Boogie, and backend execution. Verification targets, backend options, and diagnostics are coordinated separately from the bytecode admission checks.

This is a substantial language-tooling implementation inside a chain repository, not merely a client SDK or a set of contract examples.

### [Zilliqa/scilla](https://github.com/Zilliqa/scilla)

**OCaml — Scilla language implementation, checker, and interpreter. Historical: GitHub reports archival on August 27, 2025.** It remains useful for studying a smart contract language designed around restricted effects and analyzable control flow.

- **C1:** The [checker documentation](https://scilla.readthedocs.io/en/latest/scilla-checker.html) describes separate checks for algebraic data types, types, exhaustive/reachable patterns, event consistency, and payment acceptance. Its cashflow analysis is an analysis aid; the documentation does not justify treating its output as a complete financial safety proof.
- **C2:** The implementation description explains representation and syntax functors carrying successive annotations through compiler passes. This is a concrete example of reusing an AST family while allowing each analysis to attach the information it needs.

Use the checker architecture as a historical design study. The [repository's archival notice](https://github.com/Zilliqa/scilla) precludes presenting it as an actively maintained choice for a new deployment.

### [BlockstreamResearch/simplicity](https://github.com/BlockstreamResearch/simplicity)

**Haskell, C, and Rocq/Coq — a typed combinator language, formal models, and execution implementations for blockchain contracts.** Study the relationship between a small semantic core and practical execution machinery.

- **C1:** The [Bit Machine formalization](https://github.com/BlockstreamResearch/simplicity/blob/master/Coq/Simplicity/BitMachine.v) models read/write frames, nonempty stacks, state shapes, space accounting, and compositional execution properties. These are explicit machine invariants, not informal assertions that a language is “safe.”
- **C2:** Typed combinators and a separately modeled machine provide a shared foundation for reference interpretation, formal reasoning, and implementation work.
- **C3:** The official [jets design discussion](https://blog.blockstream.com/simplicity-jets-release/) explains substituting recognized expressions with efficient native implementations. The semantic identity of the substituted program is central to the optimization. This does not imply that every surrounding native component has been formally verified.

## Symbolic execution and formal verification

### [argotorg/hevm](https://github.com/argotorg/hevm)

**Haskell — concrete and symbolic EVM execution, assertions, and equivalence checking.** This separately evolved implementation is counted once, without also counting its dapptools ancestry.

- **C1:** The [symbolic execution guide](https://hevm.dev/symbolic.html) explains symbolic calldata and storage, path exploration, solver queries, and counterexamples. Empty versus abstract initial storage changes what a successful check means; assertion settings also affect which violations are sought.
- **C2:** Concrete execution, symbolic checking, and equivalence-oriented workflows share an EVM model, making the repository useful for studying an execution engine reused across several forms of analysis.
- **C3:** The guide describes exploring branches before postcondition queries and selectively querying branch feasibility around repeated execution. These choices expose the tradeoff between solver overhead and path explosion instead of hiding it behind a generic “fast verification” claim.

### [a16z/halmos](https://github.com/a16z/halmos)

**Python — symbolic testing for EVM contracts using Solidity/Foundry-style tests.** Study the translation from a familiar testing interface into symbolic machine state and solver constraints.

- **C1:** The [symbolic VM implementation](https://raw.githubusercontent.com/a16z/halmos/main/src/halmos/sevm.py) handles bit-vector arithmetic, symbolic balances, memory/calldata representations, and exceptional execution. Expensive mathematical and hash operations introduce modeling choices that matter to the interpretation of results.
- **C2:** Byte-vector operations, calldata handling, contract models, cheatcodes, and execution state have separate abstractions. The [FAQ](https://github.com/a16z/halmos/wiki/FAQ) explains how users construct external state and mock dependencies through that framework.

The FAQ also discusses symbolic storage expressions and timeout-sensitive exploration. These are useful boundaries to study: successful symbolic tests depend on the modeled environment, abstractions, and exploration settings, rather than constituting an unrestricted proof about every deployed interaction.

### [runtimeverification/evm-semantics](https://github.com/runtimeverification/evm-semantics)

**K and Python — KEVM, an executable formal definition of EVM behavior.** Study how one semantic specification can support both execution and deductive reasoning.

- **C1:** The [EVM semantics source](https://github.com/runtimeverification/evm-semantics/blob/master/kevm-pyk/src/kevm_pyk/kproj/evm-semantics/evm.md) explicitly separates machine-local state, transaction substate, and world state. Stack, memory, gas, logs/refunds, accessed accounts, original storage, and transient storage occupy distinct parts of the configuration, making rollback and instruction rules inspectable.
- **C2:** The [repository documentation](https://github.com/runtimeverification/evm-semantics) describes concrete execution through K's LLVM backend and symbolic reasoning through its Haskell backend. Gas schedules and supporting data domains are factored separately from the main rules.

This is a useful foundation for comparing executable specifications with hand-written interpreters. Its existence does not establish that every client implementation or every contract has been proved equivalent to the specification.

### [runtimeverification/kontrol](https://github.com/runtimeverification/kontrol)

**Python and K — a contract verification workflow integrating Foundry projects with KEVM.** Although it builds on KEVM, its proof lifecycle and orchestration are substantive enough to study separately.

- **C1:** [`prove.py`](https://github.com/runtimeverification/kontrol/blob/master/src/kontrol/prove.py) handles constructors, setup, and test proofs as distinct stages and rejects failed prerequisite setup proofs. This matters because an invalid initial-state argument can undermine the interpretation of a later property check.
- **C2:** Proof graphs, versioned artifacts, test digests, and reusable function summaries make verification incremental and compositional. The driver shows how a semantic engine becomes a practical verification tool with diagnosable intermediate results.
- **C3:** Proof tasks can be distributed across workers, while summaries avoid repeatedly exploring the same behavior. Read this implementation for the dependencies and invalidation rules around those optimizations, not as evidence of a universal speedup.

### [argotorg/solidity](https://github.com/argotorg/solidity)

**C++ — specifically the compiler's SMTChecker and SMT support libraries.** Counted once as a compiler monorepo. Study verification coupled to a production language frontend, including the cost of approximating language features.

- **C1:** The [SMTChecker documentation](https://docs.soliditylang.org/en/latest/smtchecker.html) explains CHC-based reasoning about contract state across transactions and external/reentrant calls. It distinguishes proved properties, potential counterexamples, unsupported features, and solver-unknown results. Abstraction can yield false positives.
- **C2:** [`SMTEncoder.h`](https://github.com/argotorg/solidity/blob/develop/libsolidity/formal/SMTEncoder.h) provides common AST traversal, symbolic context, variable handling, and branch/SSA machinery for verification encodings. This separates substantial reusable lowering logic from particular verification engines and targets.

The inspected development documentation marks the BMC engine deprecated. Readers should follow the documented engine/version semantics rather than assume older SMTChecker tutorials describe the current compiler.

### [microsoft/verisol](https://github.com/microsoft/verisol)

**C# — Solidity verification through translation to Boogie. Historical: the README states no active maintenance since 2021; GitHub reports archival on June 11, 2026.** Its value here is the inspectable translation architecture.

- **C1:** [`RevertLogicGenerator.cs`](https://github.com/microsoft/verisol/blob/master/Sources/SolToBoogie/RevertLogicGenerator.cs) models reversion through shadow state and separate success/failure procedure behavior. It illustrates why proving contract properties requires modeling transaction failure, not merely translating arithmetic expressions.
- **C2:** [`BoogieTranslator.cs`](https://github.com/microsoft/verisol/blob/master/Sources/SolToBoogie/BoogieTranslator.cs) coordinates desugaring, declaration collection, inheritance/state resolution, constructor and function translation, dispatch, harness generation, and modification analysis. The intermediate verification language decouples Solidity lowering from the backend prover.

Read it as a historical example of a multipass verification compiler. The [maintenance notice](https://github.com/microsoft/verisol) is material to any attempt to use it with contemporary Solidity.

### [ConsenSysDiligence/mythril](https://github.com/ConsenSysDiligence/mythril)

**Python — EVM security analysis using the LASER symbolic execution engine.** Study a search-oriented analyzer whose core is configurable independently of individual vulnerability detectors.

- **C1:** [`svm.py`](https://github.com/ConsenSysDiligence/mythril/blob/develop/mythril/laser/ethereum/svm.py) tracks global/world states across transaction execution and distinguishes contract creation from execution against supplied states. Multiple transactions and exceptional states make reachable attack behavior more complex than inspecting a single function in isolation.
- **C2:** Search strategies, depth and transaction limits, dynamic loading, and hooks for transactions, instructions, and state transitions are separate extension points. This lets detector plugins consume a general symbolic engine.
- **C3:** Configurable exploration strategies and time/depth limits address state-space cost explicitly. Those limits also constrain findings: absence of a reported vulnerability is not a completeness result.

### [trailofbits/manticore](https://github.com/trailofbits/manticore)

**Python — general symbolic execution framework, specifically its Ethereum backend. Historical: archived June 24, 2026; the repository states that internal development and maintenance have ended.** Its other platform backends are outside this entry's scope.

- **C1:** The [Ethereum implementation](https://github.com/trailofbits/manticore/blob/master/manticore/ethereum/manticore.py) builds symbolic calldata and addresses, constrains account choices, and manages EVM world state across explored paths. Its treatment of symbolic buffers and machine-width indices makes numerical modeling visible.
- **C2:** `ManticoreEVM` layers account, ABI, transaction, and detector facilities over a common symbolic execution base. It is useful for studying how a reusable exploration framework acquires domain-specific concepts without replacing its whole core.

Some hash-modeling modes explicitly trade soundness for tractability; configuration matters. The [repository notice](https://github.com/trailofbits/manticore) and these modeling boundaries make this an architectural reference rather than an implied current maintenance recommendation.

## Static analysis and stateful property testing

### [crytic/slither](https://github.com/crytic/slither)

**Python — Solidity/Vyper analysis framework with detectors and an intermediate representation.** Study reusable dataflow infrastructure through a concrete vulnerability family rather than treating the detector catalog as the architecture.

- **C1:** The [reentrancy analysis base](https://github.com/crytic/slither/blob/master/slither/detectors/reentrancy/reentrancy.py) tracks reads, writes, callbacks, value transfers, and events across control-flow predecessors. Ordering before and after calls is central to distinguishing dangerous state interactions.
- **C2:** Its abstract state and merge/fixed-point machinery support several reentrancy detectors, while the broader [framework](https://github.com/crytic/slither) exposes reusable representations and custom analyses. The code shows how related checks share analysis rather than repeatedly walking syntax independently.

The reentrancy implementation describes its heuristic nature. Its engineering interest lies partly in managing practical false-positive/false-negative tradeoffs; it should not be represented as a sound proof system for arbitrary reentrancy properties.

### [crytic/tealer](https://github.com/crytic/tealer)

**Python — static analysis of Algorand TEAL programs and transaction groups.** This adds a different execution and authorization model to an otherwise EVM-heavy analysis ecosystem.

- **C1:** The [transaction-context dataflow implementation](https://github.com/crytic/tealer/blob/main/tealer/analyses/dataflow/transaction_context/generic.py) combines local constraints with forward and backward propagation. It explicitly handles subroutine call/return matching so that analyses do not casually merge impossible execution paths.
- **C2:** A generic framework defines domains of possible transaction-field values, joins/intersections, and fixed-point computation. Detectors can reuse this infrastructure for transaction authorization conditions instead of implementing a separate simulator for each check.

The [repository documentation](https://github.com/crytic/tealer) supplies the TEAL and group-analysis context. Study the dataflow layer to understand how field constraints become detector evidence; a clean result remains bounded by supported analyses and their models.

### [eth-sri/securify2](https://github.com/eth-sri/securify2)

**Python and Soufflé Datalog — context-sensitive Solidity security analysis. Historical research implementation:** the documented setup targets Solidity 0.5.x, and the README limits input to flattened contracts. Contemporary Solidity compatibility was not established.

- **C1:** The [Datalog dataflow analysis](https://github.com/eth-sri/securify2/blob/master/securify/staticanalysis/souffle_analysis/analysis-dataflow.dl) propagates dependencies through arguments, returns, and storage across calling contexts. It distinguishes possible dependence from stronger derivation conditions, including uniqueness conditions on incoming edges and preceding stores.
- **C2:** The [fact encoder](https://github.com/eth-sri/securify2/blob/master/securify/staticanalysis/factencoder.py) translates a control-flow IR into reusable relations for assignments, branches, calls, storage, and source locations. Security patterns sit above shared relational analyses rather than being coupled directly to parser nodes.

This is a substantive alternative to symbolic execution and imperative detector frameworks. The [documented toolchain limitations](https://github.com/eth-sri/securify2) are part of the selection, not hidden by its inclusion.

### [crytic/echidna](https://github.com/crytic/echidna)

**Haskell — ABI-driven, stateful property fuzzing for EVM contracts.** Study not only input generation and shrinking, but also how a long-running campaign coordinates workers and reports reproducible failures.

- **C1:** The [repository overview](https://github.com/crytic/echidna) describes transaction-sequence generation, properties, corpus reuse, and shrinking. [`Worker.hs`](https://github.com/crytic/echidna/blob/master/lib/Echidna/Worker.hs) makes concurrent failure handling concrete through worker events, STM channels, stop coordination, and replay/shrink notifications.
- **C2:** Fuzzing and symbolic workers share event and lifecycle abstractions, separating campaign execution from consumers of progress and failure information.
- **C3:** Parallel exploration and coverage feedback address campaign cost, but concurrency brings its own correctness obligations. The [changelog](https://github.com/crytic/echidna/blob/master/CHANGELOG.md) records listener-startup, shrinking-trace, corpus-distribution, and memory-management fixes, giving useful examples of those obligations in practice.

Fuzzing discovers counterexamples; passing a finite campaign does not prove an invariant universally.

### [crytic/medusa](https://github.com/crytic/medusa)

**Go — parallel, coverage-guided EVM contract fuzzer backed by go-ethereum.** Study the explicit campaign lifecycle and the boundary between a simulated chain, mutation engine, and property checks.

- **C1:** The [fuzzing lifecycle](https://github.com/crytic/medusa/blob/master/docs/src/testing/fuzzing_lifecycle.md) describes deployment of an initial state, stateful transaction sequences, property checks during execution, and state reset between sequences. This makes the assumed starting environment and order-dependent failures inspectable.
- **C2:** The [repository's API overview](https://github.com/crytic/medusa) exposes chain access, hooks, and events for custom testing workflows. It also warns that the Go API is developing and can introduce breaking changes.
- **C3:** Workers explore sequences in parallel; new bytecode coverage causes useful sequence prefixes to enter the corpus for later mutation. This is a concrete feedback mechanism for spending test effort, distinct from merely increasing random input volume.

## Coverage, search method, and limitations

Discovery used live web searches followed by opened GitHub repository pages and implementation files or primary documentation. Distinct search formulations covered EVM interpreter architecture and gas optimization; formal EVM semantics and equivalence checking; Wasm metering and host isolation; Move bytecode verification and proving; Cairo/Fuel/Neo execution; Scilla and TEAL analysis; stateful fuzzing; Solidity-to-Boogie and SMT verification; Simplicity's Bit Machine and jets; and Datalog-based Solidity analysis. Follow-up searches explored less familiar OCaml and Michelson tools as well as the established Ethereum projects. Later searches increasingly returned already examined projects, predecessor implementations, or tools outside the category; Securify2 added a final distinct relational-analysis architecture.

The resulting selection spans Rust, C++, TypeScript, C#, OCaml, Haskell, Python, Go, K, Rocq/Coq, and Datalog, with both small research implementations and subsystems of large production repositories. EVM tools remain the largest group because they expose a particularly broad set of independently inspectable analysis architectures. Monorepos are counted once; closely related projects are retained separately only where their implementation contributes a distinct engine or substantial orchestration layer, as with KEVM and Kontrol. Historical Move repositories and hevm's ancestry are not additional entries.

Excluded material includes tutorials, awesome lists, contract application examples, generated wrappers, hosted-service clients without the underlying verification engine, and general blockchain repositories without a sufficiently specific relevant subsystem. Michelson searches led to work such as [Mi-Cho-Coq's primary GitLab repository](https://gitlab.com/nomadic-labs/mi-cho-coq/); an appropriate substantive official GitHub mirror was not established, so it is outside this GitHub-only selection.

Every retained repository had its canonical GitHub page opened and at least one additional substantive source or documentation page read. Sources establish architectural facts; the choice of what an engineer can profitably study is an inference from those facts. No candidate repository was cloned, built, or executed, and no benchmark or security guarantee was independently reproduced. Branch-linked sources can change. Archived and historically constrained tools are labeled explicitly, while C4 is used selectively where inspected material demonstrates evolution and compatibility/testing work rather than merely an old creation date. Formal proofs, symbolic tests, heuristic findings, bytecode admission checks, and finite fuzzing campaigns provide different kinds of evidence and are not interchangeable.
