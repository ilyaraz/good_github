# Zero-knowledge proof systems

Research date: **2026-10-09**.

This selection covers 24 GitHub repositories implementing reusable zero-knowledge proof systems, their circuit and protocol frameworks, and virtual machines with a zero-knowledge proving path. It spans pairing-based SNARKs, PLONK-family systems, polynomial IOPs, folding, range proofs, and interactive protocols. Monorepos count once, with the relevant subsystem identified. Several entries are research implementations or historical designs; inclusion is an engineering study recommendation, not a security audit or a claim that every component is exemplary. A proof of correct execution is not automatically zero knowledge: configuration and final-wrapper boundaries are called out below.

Criteria used in the selection:

- **C1 — Difficult correctness:** mathematical invariants, adversarial inputs, protocol state, numerical semantics, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting different statements, applications, or protocol instantiations.
- **C3 — Performance with structure:** explicit responses to computation, memory, communication, or proof-size constraints within an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, migrations, or complexity management. Repository age alone does not qualify.

The criteria assessments are grounded engineering judgments based on the linked primary material. Each repository page and at least one additional implementation or documentation source were opened and read.

## R1CS, pairing-based SNARKs, and circuit libraries

### 1. [scipr-lab/libsnark](https://github.com/scipr-lab/libsnark)

**C++; foundational research library for preprocessing SNARKs and reductions.** Study how a large cryptographic library separates constraint languages, reductions, proof systems, and reusable gadgets. Its R1CS, BACS, USCS, and other interfaces offer more architectural variety than a single Groth16 implementation. The repository explicitly describes research code and implementation limitations; treat it as a historical engineering reference rather than an assurance of production suitability.

- **C1:** The R1CS verifier API distinguishes strong input consistency, requiring the prescribed number of public inputs, from weak consistency, permitting a shorter input padded with zeroes. Proof objects also expose group-element well-formedness checks. These are concrete examples of seemingly small API choices changing statement semantics.
- **C2:** Curve-parameterized proof systems sit below reductions and gadget libraries, allowing multiple statement representations to share proving machinery. Processed verification keys further separate one-time preparation from repeated verification.

Entry point: [R1CS preprocessing-SNARK interfaces, proof validation, and verifier variants](https://raw.githubusercontent.com/scipr-lab/libsnark/master/libsnark/zk_proof_systems/ppzksnark/r1cs_ppzksnark/r1cs_ppzksnark.hpp). The repository overview maps the wider reduction and gadget layers.

### 2. [zkcrypto/bellman](https://github.com/zkcrypto/bellman)

**Rust; circuit construction and Groth16 proving library.** A relatively focused codebase for studying the boundary between a developer's circuit description and the backend that allocates variables and enforces equations. Generic field/group interfaces and basic Boolean and numeric gadgets make the abstractions useful beyond a single application.

- **C1:** Circuit synthesis explicitly represents missing assignments, division failures, unsatisfied constraints, and unconstrained variables. Public input allocation is distinct from auxiliary allocation, so the statement boundary appears in the API rather than being implicit in a witness array.
- **C2:** `Circuit::synthesize` targets a `ConstraintSystem`; the same description can serve parameter generation and proving. Namespaced constraint systems organize complex gadget composition, with scope cleanup handled by the namespace wrapper.

Entry point: [the circuit, constraint-system, namespace, and error interfaces](https://raw.githubusercontent.com/zkcrypto/bellman/main/src/lib.rs). Start here before the Groth16 backend to understand what information the frontend promises to supply.

### 3. [arkworks-rs/groth16](https://github.com/arkworks-rs/groth16)

**Rust; generic Groth16 implementation in the arkworks ecosystem.** Useful for studying a narrowly scoped proving backend that composes with a broader algebra and constraint ecosystem. The repository labels the implementation an academic proof of concept, so its value here is architectural and algorithmic.

- **C2:** `Groth16` is parameterized by both a pairing engine and an R1CS-to-QAP reduction. Its implementation of the common `SNARK` trait separates generation, proving, verification, and constraint-side verification without fixing one curve or reduction strategy.
- **C3:** Verification distinguishes ordinary from prepared verification keys and can reuse prepared public inputs. The verifier combines pairing work through a multi-Miller loop followed by final exponentiation, exposing expensive operations and reusable preparation explicitly.

Entry points: [generic backend and module boundaries](https://raw.githubusercontent.com/arkworks-rs/groth16/master/src/lib.rs), and [prepared-key/input verification implementation](https://raw.githubusercontent.com/arkworks-rs/groth16/master/src/verifier.rs). These support the abstraction and performance criteria without assuming that genericity alone establishes input safety.

### 4. [Consensys-Incorporated/gnark](https://github.com/Consensys-Incorporated/gnark)

**Go; circuit framework with Groth16 and PLONK backends.** The former `Consensys/gnark` repository URL resolves to this owner. Study the effort required to make ordinary-looking programming operations mean precise finite-field constraints across different proving backends.

- **C1:** The frontend documents checked versus unchecked division, Boolean assertions, and backend-dependent behavior around zero denominators. `MulAcc` may mutate its accumulator representation, and callers must use the returned value. These contracts expose both algebraic and aliasing pitfalls that circuit authors must understand.
- **C2:** A shared frontend API supports distinct constraint representations and proof backends, while backend-specific operations are separated so portable circuits need not depend on them. The repository also contains reusable circuit components and end-to-end testing infrastructure.

Entry point: [frontend arithmetic, assertion, and backend-extension contracts](https://raw.githubusercontent.com/Consensys/gnark/master/frontend/api.go). This verified raw source still uses the former owner spelling; the heading uses the resolved canonical repository URL. Serialized artifacts should not be assumed stable across versions merely because the Go API looks familiar.

### 5. [iden3/snarkjs](https://github.com/iden3/snarkjs)

**JavaScript/WebAssembly; proving, verification, and setup tooling.** This is substantive proof-system tooling for browser and Node environments, including Groth16, PLONK, and FFLONK workflows. It is useful for studying how algebraic backends meet JSON inputs, binary circuit artifacts, command-line workflows, and multiparty setup transcripts.

- **C1:** The Groth16 verifier converts external numeric representations, rejects public signals outside the scalar field, checks curve-point validity, and only then evaluates the multiexponentiation and pairing equation. Setup contribution and artifact verification add another adversarial-data boundary in the wider toolchain.
- **C2:** The project provides programmatic and command-line interfaces over several proof systems, with shared setup and artifact workflows usable from different execution environments. Its worker and memory configuration also make browser constraints visible rather than hiding them behind a single opaque call.

Entry point: [Groth16 verification implementation](https://raw.githubusercontent.com/iden3/snarkjs/master/src/groth16_verify.js). The repository's workflow documentation provides the complementary setup, browser, and artifact context.

### 6. [scipr-lab/dizk](https://github.com/scipr-lab/dizk)

**Java/Apache Spark; distributed zkSNARK research system.** A historical academic implementation worth reading for distributed algebra and memory management, rather than treating it as a currently supported deployment recommendation. It includes serial and distributed versions of core polynomial and multiscalar operations.

- **C1:** The distributed prover must preserve the association between witness indices and proving-key queries through Spark joins. Its debug path checks QAP witness and degree conditions, making the algebraic invariants behind distributed data transformations inspectable; those checks are not a claim of unconditional runtime validation.
- **C3:** Partition-aware joins and distributed multiscalar multiplication place expensive work in the dataflow, while explicit `unpersist` calls release constraints and key material after the stages that need them. This makes the interaction between proof construction and cluster memory particularly instructive.

Entry point: [distributed prover implementation](https://raw.githubusercontent.com/scipr-lab/dizk/master/src/main/java/zk_proof_systems/zkSNARK/DistributedProver.java). Compare its orchestration with the serial/distributed module map in the repository overview.

## PLONK-family systems and application-scale proving backends

### 7. [zcash/halo2](https://github.com/zcash/halo2)

**Rust; Halo 2 proving system and circuit infrastructure.** This entry is the Zcash implementation, not a separate listing of downstream forks. Study how proof encoding, transcript construction, circuit knowledge, and batching are designed together rather than as unrelated serialization concerns.

- **C1:** `TranscriptRead` and `TranscriptWrite` couple serialization with absorption into the Fiat–Shamir transcript. The design explains why treating a proof as an opaque byte stream helps prevent accidentally omitting proof elements from challenge derivation.
- **C2:** The transcript interfaces separate proof-system logic from concrete readers, writers, and transcript implementations. Circuit-known dimensions guide decoding, while support for multiple instances permits shared proof components rather than requiring each circuit instance to invent an independent format.

Entry point: [proof encoding and transcript implementation design](https://zcash.github.io/halo2/design/implementation/proofs.html). This is especially valuable for engineers designing protocols whose verifier must reconstruct exactly the prover's challenge schedule.

### 8. [dusk-network/plonk](https://github.com/dusk-network/plonk)

**Rust; PLONK with custom gates and BLS12-381/KZG.** Study both circuit engineering and the compatibility cost of changing a cryptographic implementation. The project supports constrained allocation-oriented builds as well as standard-library parallelism; its own documentation also discusses security and timing limitations.

- **C1:** The changelog records concrete correctness boundaries: shifted-wire blinding, canonical encodings, rejection of trailing data and invalid cached polynomials, and binding public-input rows during compilation. These are useful examples of soundness and privacy depending on serialization and circuit metadata, not just the main algebraic equation.
- **C4:** The inspected history spans 2020–2026 and documents testing expansion, reorganizations, breaking API changes, and circumstances requiring circuit-key regeneration. This is direct evidence of managing compatibility and correctness over time, rather than an inference from repository age.

Entry point: [detailed changelog, including the 2026-10-08 release and earlier migration history](https://raw.githubusercontent.com/dusk-network/plonk/master/CHANGELOG.md). Read it alongside the repository overview to understand which interfaces and artifacts a change can invalidate.

### 9. [EspressoSystems/jellyfish](https://github.com/EspressoSystems/jellyfish)

**Rust; cryptographic monorepo, especially `jf-plonk`, `jf-relation`, and polynomial commitments.** The relevant subsystem implements PLONK-family proofs while keeping constraint arithmetization, commitments, and transcript machinery as separate concepts. Its engineering interest is the interface between reusable cryptographic components and application-level claims.

- **C1:** The universal-SNARK API permits additional application data to initialize the transcript, but its documentation explicitly distinguishes binding that data from verifying its meaning. Local testing SRS generation is also separated from ordinary production-facing operations. Both boundaries prevent an API feature from being mistaken for a stronger security guarantee.
- **C2:** `UniversalSNARK` associates proof, key, and SRS types, accepts an `Arithmetization`, and parameterizes transcript and randomness requirements. This supports interchangeable circuit descriptions and protocol plumbing without collapsing all responsibilities into a single circuit class.

Entry points: [proof-system API](https://jellyfish.docs.espressosys.com/jf_plonk/proof_system/index.html) and [its trait implementation source](https://jellyfish.docs.espressosys.com/src/jf_plonk/proof_system/mod.rs.html). Count the monorepo once, rather than treating each crate as an independent project.

### 10. [o1-labs/proof-systems](https://github.com/o1-labs/proof-systems)

**Primarily Rust, with OCaml/WebAssembly integration; Mina's Kimchi and shared cryptographic components.** Focus on Kimchi and its polynomial-commitment, curve, and hash infrastructure. The book is explicitly a work in progress and may not describe every deployed Mina detail; the repository's APIs follow that application's needs.

- **C1:** Kimchi combines gate equations, copy constraints, and lookup constraints into polynomial identities. The overview explains quotient construction and randomized aggregation, making the obligations that must survive circuit-to-polynomial translation concrete.
- **C2:** Custom-gate arguments, permutation and lookup arguments, and polynomial commitments are organized as separable layers. An experienced reader can study how many constraint families share the same proof machinery while retaining their own algebraic responsibilities.

Entry point: [Kimchi architecture overview](https://o1-labs.github.io/proof-systems/kimchi/overview/). The [book introduction](https://o1-labs.github.io/proof-systems/) supplies its scope and documentation caveat. This entry does not count related implementations or the surrounding blockchain as separate proof-system repositories.

### 11. [AztecProtocol/aztec-packages](https://github.com/AztecProtocol/aztec-packages)

**C++ proving backend within a larger monorepo; Barretenberg, particularly Ultra Honk.** Study the explicit circuit-builder → preprocessing → sumcheck → commitment-opening pipeline. The relevant code is in `barretenberg`; the older standalone repository is not counted separately.

- **C1:** ZK flavors coordinate witness masking, disabled rows, sumcheck masking, and masked polynomial openings. The design also distinguishes public-input transcript binding from enforcement through the permutation argument, and maps relation, transcript, memory, and ZK-boundary tests.
- **C2:** A compile-time flavor selects fields, relations, polynomial layout, commitment scheme, and transcript. Shared preprocessing and commitment components support ordinary, recursive, and folding-related configurations.
- **C3:** Prover-side relation skipping avoids work on inactive selectors while leaving verifier checks intact. The backend also provides circuit-level diagnostics and CPU/memory profiling facilities.

Entry points: [Ultra Honk architecture, ZK mechanisms, and test map](https://github.com/AztecProtocol/aztec-packages/tree/next/barretenberg/cpp/src/barretenberg/ultra_honk), and [Barretenberg build, debugging, and profiling guide](https://github.com/AztecProtocol/aztec-packages/tree/next/barretenberg). Base and ZK flavors are distinct; inclusion does not imply every internal proof hides its witness.

## Polynomial IOPs, transparent constructions, and binary fields

### 12. [0xPolygonZero/plonky2](https://github.com/0xPolygonZero/plonky2)

**Rust; recursive PLONK/FRI system, with the related `starky` subsystem.** The repository explicitly declares Plonky2 deprecated and directs users toward Plonky3. Retain it as a historical design study, not a maintenance recommendation. It is a distinct implementation, not a duplicate listing of Plonky3.

- **C1:** `CircuitConfig` exposes zero knowledge as an explicit setting: the standard recursion configuration disables it, while a separate ZK configuration enables it. This is a concrete lesson in separating recursive proof capability from witness privacy.
- **C2:** Common circuit data, prover-only data, and verifier-only data are separate types, with serialization interfaces for gates and witness generators. Their separation makes the trust and reuse boundaries inspectable.
- **C3:** Prover data can retain precomputed low-degree extensions, explicitly exchanging memory for proving work while keeping verifier material separate.

Entry point: [circuit configuration and circuit-data implementation](https://raw.githubusercontent.com/0xPolygonZero/plonky2/main/plonky2/src/plonk/circuit_data.rs). The repository notice establishes its deprecated status.

### 13. [Plonky3/Plonky3](https://github.com/Plonky3/Plonky3)

**Rust; modular polynomial-IOP/STARK toolkit, including a hiding FRI commitment implementation.** Its inclusion concerns actual hiding machinery as well as reusable proof components; some examples and configurations are explicitly non-ZK. Study the obligations imposed when adding privacy to an otherwise valid polynomial proof.

- **C1:** `HidingFriPcs` requires an appropriately hiding underlying commitment layer and cryptographic randomness. Its implementation accounts for the information exposed by openings and FRI queries, and shares an atomic single-use marker across cloned prover data to prevent reuse of masking material.
- **C2:** The hiding PCS composes generic field, transform, commitment, and randomness components. The larger toolkit exposes choices of finite fields, hashes, polynomial commitments, and arithmetic implementations rather than baking one proof stack into every application.

Entry point: [hiding FRI PCS implementation and its security contracts](https://raw.githubusercontent.com/Plonky3/Plonky3/main/fri/src/hiding_pcs.rs). Read the caller requirements before assuming a composition of individually useful components is zero knowledge.

### 14. [scipr-lab/libiop](https://github.com/scipr-lab/libiop)

**C++; research framework implementing Aurora, Ligero, Fractal, and shared IOP machinery.** A useful historical counterpart to contemporary Rust toolkits: it separates interactive oracle protocols, low-degree testing, and conversion to noninteractive proofs. The repository explicitly cautions that it is research software without the review needed to infer production safety.

- **C1:** The protocol mediator registers oracle domains, degree bounds, index status, and zero-knowledge requirements. A registration state machine and typed handles make transcript construction and permitted oracle access explicit invariants.
- **C2:** Real and virtual oracles let protocol components describe derived polynomial information without every construction owning its own transcript engine. Encoded protocols, low-degree tests, and the BCS transformation can be composed above that shared layer.
- **C3:** The interface includes coset-grouped queries, connecting the abstract oracle model to fewer Merkle authentication operations and smaller query representations.

Entry point: [IOP mediator, oracle metadata, handles, and registration interfaces](https://raw.githubusercontent.com/scipr-lab/libiop/master/libiop/iop/iop.hpp). Zero knowledge is a protocol/configuration choice, not a blanket property of every IOP instantiated through this library.

### 15. [binius-zk/binius64](https://github.com/binius-zk/binius64)

**Rust; binary-field proving infrastructure, including the Iron Spartan zero-knowledge system.** The architecture document distinguishes the word-oriented Binius64 argument from Iron Spartan's ZK construction over a binary extension field. This entry specifically includes Iron Spartan and the shared implementation substrate; the distinction matters more than the repository's broad zkSNARK label.

- **C2:** Shared field arithmetic, mathematical routines, and transcripts support separate frontend, prover, and verifier layers. Iron Spartan has its own sparse-constraint frontend and proving/verification components, allowing the binary-field infrastructure to serve more than one relation model.
- **C3:** The architecture deliberately keeps verifier arithmetic simple and scalar while concentrating packed arithmetic, SIMD, and parallel work in the prover. Dependency direction prevents the verifier from pulling in prover complexity; tests that need both sit on the prover side.

Entry point: [architecture document covering the two systems, dependency rules, and optimization boundaries](https://raw.githubusercontent.com/binius-zk/binius64/main/ARCHITECTURE.md). This is particularly instructive for balancing an aggressively optimized prover against a smaller verification implementation.

## Sumcheck, folding, and incremental verification

### 16. [microsoft/Spartan](https://github.com/microsoft/Spartan)

**Rust; transparent R1CS proof-system research implementation.** Study the original Spartan implementation's decomposition of a statement proof into polynomial commitments, zero-knowledge sumcheck, and smaller equality/product proofs. The repository warns that it is research code and has not been audited; no current maintenance guarantee is inferred.

- **C1:** The R1CS proof joins two masked sumcheck phases with commitment consistency, equality, and product proofs. Public inputs enter the transcript, and a separate random tape supplies blinding. These connections show where individually correct subprotocols must agree on the same claims.
- **C2:** Sumcheck, witness commitments, and auxiliary proof primitives remain recognizable components rather than being flattened into one verifier equation. The R1CS layer supplies a reusable statement representation for different computations.

Entry point: [R1CS proof construction and verification](https://raw.githubusercontent.com/microsoft/Spartan/master/src/r1csproof.rs). Its sparse-matrix operations and timing boundaries also provide concrete performance study material, without relying on the repository's headline benchmark comparisons.

### 17. [microsoft/Nova](https://github.com/microsoft/Nova)

**Rust; folding-based incremental verifiable computation and compressed proofs.** Study how repeated state transitions become a recursively accumulated object and then a final succinct proof. The repository supports multiple curve cycles and commitment/compression choices, so setup assumptions must be evaluated for the selected backend rather than generalized across the project.

- **C1:** Public parameters tie the two engines' base and scalar fields together, construct augmented circuits, check their expected public-input structure, and bind parameters through a digest. These constraints expose how recursive consistency depends on more than a single step circuit being satisfiable.
- **C2:** A generic `StepCircuit` is separate from curve engines, commitment sizing, recursive state, and compressed-proof choices. This makes application logic reusable across the accumulation and final-proof layers.

Entry point: [Nova public parameters and recursive proof implementation](https://raw.githubusercontent.com/microsoft/Nova/main/src/nova/mod.rs). The repository overview explains its zero-knowledge randomization and compression choices; an intermediate folding object should not automatically be treated as a private final proof.

### 18. [privacy-ethereum/sonobe](https://github.com/privacy-ethereum/sonobe)

**Rust; modular folding/IVC framework, currently presented as an alpha rewrite.** This is the canonical repository reached from the former `privacy-scaling-explorations` owner. Its current support table is narrower than the older project's collection of examples: Nova/CycleFold and the listed implemented components should not be conflated with pending protocols.

- **C1:** The current IVC API tracks circuit-state shape, including dynamic dimensions. Dummy synthesis must match real proving shape, and preprocessing capacity must cover later instances. Older design documentation separately explains why raw IVC output needs randomization to obtain zero knowledge.
- **C2:** Application transition circuits, folding-to-IVC compilers, the stateful IVC interface, and final deciders are separated. This allows studying how a framework coordinates application state with protocol-specific accumulation and final proof generation.

Entry points: [current `sonobe-ivc` API and state-shape contracts](https://docs.rs/sonobe-ivc/latest/sonobe_ivc/), and [older Nova zero-knowledge design explanation](https://sonobe.pse.dev/usage/nova-zk.html). The latter is conceptual/historical evidence, not a promise that its examples match the rewritten API. Alpha APIs remain unstable.

## Virtual machines with zero-knowledge proving paths

### 19. [risc0/risc0](https://github.com/risc0/risc0)

**Rust and C++/GPU components; RISC-V zkVM, proof backend, and recursion infrastructure.** Count the monorepo once. Study how instruction execution, memory consistency, public output, and program identity are translated into the statements a verifier actually checks.

- **C1:** The documented protocol separates main and auxiliary traces, uses randomized consistency checks for memory and lookup obligations, and binds execution to the program image. Random noise is part of the documented hiding construction; the public journal remains deliberately public.
- **C2:** Ordinary guest programs, host-side receipt verification, the lower-level proof system, and recursive proof machinery are distinct layers. This supports many computations without requiring each application to implement a polynomial protocol.
- **C3:** The protocol documentation explains specialized handling of expensive operations, including bigint advice checked through randomized algebraic identities, rather than expressing all such work through the same instruction-level constraints.

Entry point: [proof-system sequence and explanation of trace, consistency, and hiding mechanisms](https://github.com/risc0/risc0/blob/main/website/docs/proof-system/proof-system-sequence-diagram.md). Treat this design document as an implementation guide, not a guarantee that every detailed circuit choice remains identical across releases.

### 20. [succinctlabs/sp1](https://github.com/succinctlabs/sp1)

**Primarily Rust, with accelerated prover components; general-purpose zkVM.** The current Hypercube documentation is a useful study of sharded execution, polynomial commitments, memory arguments, and recursive proof aggregation. The security model explicitly states that individual STARK proofs are not zero knowledge; privacy is supplied by the Groth16 or PLONK wrapping path.

- **C1:** Execution shards must agree on memory across shard boundaries, not merely pass local instruction checks. The security documentation also distinguishes the proved program's behavior from application safety and lists assumptions for the final proof system.
- **C3:** The Hypercube architecture separates zerocheck, LogUp GKR, Jagged commitments, and Basefold, then combines shard proofs through recursion. These named stages make scaling and compression choices inspectable instead of presenting the zkVM as a single compiler operation.

Entry points: [Hypercube proof-system architecture](https://docs.succinct.xyz/docs/sp1/hypercube/), and [security model, including the precise zero-knowledge boundary](https://docs.succinct.xyz/docs/sp1/security/security-model). This entry includes a substantive execution-proof implementation, not merely its use of an external final SNARK backend.

## Range proofs, composable Sigma protocols, and VOLE-based systems

### 21. [dalek-cryptography/bulletproofs](https://github.com/dalek-cryptography/bulletproofs)

**Rust; Ristretto range proofs, aggregation, and multiparty proving.** Study how a compact algebraic protocol becomes a composable API with explicit round structure. The optional R1CS functionality is documented as experimental; it should not be assigned the same stability expectations as the range-proof interfaces.

- **C1:** The multiparty range-proof API represents successive party and dealer states as different types. Advancing a round consumes the prior state, reducing opportunities to reorder steps or reuse values that belong to an earlier challenge.
- **C2:** The same range-proof framework supports local aggregation and multiparty construction. Message types separate commitments, challenges, and proof shares, while transcript-based composition allows a range statement to participate in a larger application protocol.

Entry points: [multiparty range-proof protocol and typestate API](https://doc-internal.dalek.rs/bulletproofs/range_proof_mpc/index.html), and [implementation notes](https://doc-internal.dalek.rs/bulletproofs/notes/index.html). These are useful for studying protocol misuse prevention without mistaking type safety for a complete cryptographic proof.

### 22. [GaloisInc/swanky](https://github.com/GaloisInc/swanky)

**Rust; secure-computation monorepo, including VOLE-based zero-knowledge engines.** Focus on Diet Mac'n'Cheese and related ZK components rather than counting every MPC primitive as a proof system. The repository distinguishes supported core components from experimental edge components; the inspected Diet Mac'n'Cheese code is in `edge`.

- **C2:** Its evaluator accepts SIEVE circuit representations and separates party-generic execution, authenticated field operations, conversion machinery, RAM support, and sVOLE generation. This is a substantially different reuse model from arithmetic-circuit-to-SNARK compilation.
- **C3:** The implementation exposes threaded sVOLE and field-dependent LPN parameter choices. Comments explain why smaller parameters can reduce memory and improve extension work for larger fields, making performance choices traceable to the protocol layer they affect.

Entry point: [Diet Mac'n'Cheese evaluator, module boundaries, and parameter selection](https://raw.githubusercontent.com/GaloisInc/swanky/dev/edge/diet-mac-and-cheese/src/lib.rs). The repository's research-software and core/edge distinctions limit any inference about deployment readiness.

### 23. [emp-toolkit/emp-zk](https://github.com/emp-toolkit/emp-zk)

**C++; interactive Boolean/arithmetic ZK with reusable memory and set gadgets.** The inspected repository presents a new alpha session API alongside an older engine lineage. Study the lifecycle of authenticated computation and the point at which provisional results become verified results.

- **C1:** `ZKSession` owns the engine and exposes explicit finalization. Its contract states that revealed values are provisional until final checks complete; copying is disabled, and role/context/I/O assumptions are guarded. Correct teardown therefore belongs to the proof's trust boundary, not just resource hygiene.
- **C2:** Explicit sessions, contexts, and typed wire values replace reliance on a global backend and support reusable Boolean and arithmetic gadget code. Expected-work budgets distinguish prepaid correlation generation from streaming when the amount of work is unknown.

Entry point: [Boolean session ownership, finalization, and API contracts](https://github.com/emp-toolkit/emp-zk/blob/main/emp-zk/emp-zk-bool/zk_session.h). The repository labels the current API alpha and explains that older published performance tables concern the earlier engine; those numbers are not attributed to this implementation.

### 24. [spring-epfl/zksk](https://github.com/spring-epfl/zksk)

**Python; composable Sigma-protocol and noninteractive-proof framework.** A smaller research project that broadens the list beyond succinct circuit proofs. Study its expression language for discrete-log relations, conjunctions, disjunctions, simulation, and Fiat–Shamir proofs. The repository positions it for prototyping, not mission-critical use.

- **C1:** The documentation distinguishes sharing the same secret object from supplying two secret objects with equal values: only the former requests an equality relation. It also documents restrictions on secrets shared across OR boundaries and compatibility of group orders, exposing composition hazards directly.
- **C2:** Statement expressions can be combined into AND/OR trees and used through interactive, simulated, or noninteractive interfaces. This makes it possible to reuse proof primitives while inspecting how composition changes their security obligations.

Entry point: [usage and composition guide, including secret identity and validity restrictions](https://zksk.readthedocs.io/en/latest/usage.html). Its value is the transparent treatment of protocol composition, rather than proving large general-purpose computations.

## Coverage, search process, and limitations

Discovery used more than six meaningfully different live-search angles: pairing/R1CS libraries across C++, Go, and JavaScript; PLONK and Halo implementations; STARK/FRI and low-degree-testing frameworks; sumcheck/GKR and binary-field systems; Nova-style folding and final deciders; distributed Java/Spark proving; zkVM architectures; VOLE/MPC-derived ZK; and composable Sigma/range-proof libraries. Follow-up searches targeted source trees, verifier code, transcript designs, hiding modes, tests, changelogs, and canonical owner changes. Later queries increasingly rediscovered the same backends, wrappers, and application integrations, so the selection stopped at 24 distinct repositories rather than padding it with near-duplicates.

The resulting set includes established ecosystems and less prominent projects such as DIZK, libiop, Dusk PLONK, Jellyfish, and zksk. It covers local and distributed proving, native and browser execution, recursive and nonrecursive systems, and both succinct and interactive constructions. The criteria emphasize different strengths: for example, DIZK's distributed memory/dataflow, Bulletproofs' protocol-state types, Plonky3's hiding contracts, and Dusk's documented compatibility history.

Canonical repository pages were opened, including the owner redirects for gnark and Sonobe. Each retained project also has an independently inspected primary source beyond the root README; raw source files were used where GitHub's rendered view was unreliable. Monorepo subsystems and closely related crates are not counted separately. Plonky2's deprecation, Sonobe's rewrite, experimental Swanky components, and EMP's engine-version distinction are explicitly retained in the descriptions.

Important exclusions include awesome-lists, tutorials, generated wrappers, circuit-language compilers without a retained proof backend, and application-only integrations. Winterfell, Jolt, Expander, and other adjacent candidates surfaced during discovery but are not included here because their relevant privacy paths and second-source evidence were not verified to the same depth in this search; this is not a finding that they lack zero-knowledge capability. The former standalone Barretenberg location is not an additional project entry. No fork is counted merely for having a different owner.

This was read-only source and documentation research: no candidate code was executed, no benchmark claims were reproduced, and no security audit was performed. Links target the inspected branches or documentation channels rather than immutable snapshots, so interfaces can change. Maintenance is not inferred from stars, a recent push, or an old creation date. C4 is asserted only where the inspected history directly shows sustained testing and compatibility work; historical research implementations remain useful study material without being represented as maintained production choices.
