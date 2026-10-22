# Security protocol verification tools

Research date: **2026-10-09**.

This selection covers GitHub implementations of symbolic protocol analyzers, computational security proof frameworks, and reusable systems for connecting protocol security arguments to source code or binaries. It includes 16 repositories across Haskell, C, Rust, OCaml, Maude, Standard ML, F*, Rocq/Coq, and Go verification tooling. General-purpose theorem provers and cryptographic libraries appear only as dependencies. Research artifacts qualify when they contain substantial reusable verification machinery, rather than just models of one protocol.

The criteria describe what makes each codebase worth studying; they do not certify its soundness or the security of every supported protocol. Verification results depend on the modeled adversary, assumptions, bounds, and trusted components. Maintenance is not inferred from stars, repository age, or a recent push.

## Criteria legend

- **C1 — Difficult correctness:** nontrivial invariants, concurrency, adversarial behavior, semantic preservation, or failure modes.
- **C2 — Reusable abstractions:** substantial modeling languages, proof interfaces, libraries, or composition mechanisms that serve multiple protocols.
- **C3 — Performance with structure:** explicit treatment of search explosion or verification cost through understandable algorithms and architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management, beyond creation dates.

## Symbolic search and equivalence

### 1. [tamarin-prover/tamarin-prover](https://github.com/tamarin-prover/tamarin-prover)

**Language/role:** Haskell, with Maude-backed equational reasoning; symbolic protocol proof and attack search.

Tamarin is a strong starting point for understanding how a protocol language, adversary theory, constraint solver, and interactive proof strategy fit together. Its multiset-rewriting model distinguishes linear state from persistent facts and records actions for temporal security claims. The [introductory model](https://tamarin-prover.com/manual/master/book/003_example.html) explicitly models key compromise and checks executability alongside secrecy, making vacuous proofs a concrete engineering concern.

- **C1:** Freshness, compromise, state consumption, and temporal authentication must agree across operational rules and trace formulas; the example shows how changing the compromise conditions changes the claim.
- **C2:** Facts, rules, action traces, and reusable lemmas support many stateful protocols. SAPIC integration belongs to this repository and is not counted separately.
- **C3:** Precomputation separates raw from refined sources. Inductively proved source lemmas eliminate partial deconstructions before later proofs, addressing a documented cause of nontermination.

**Entry points:** [Precomputation and source-lemma architecture](https://tamarin-prover.com/manual/master/book/009_precomputation.html); [change history](https://github.com/tamarin-prover/tamarin-prover/blob/develop/CHANGES), including parser round-trip regressions, tactic changes, and integration work.

### 2. [cascremers/scyther](https://github.com/cascremers/scyther)

**Language/role:** C analysis engine with a Python GUI; symbolic security-protocol analysis.

Scyther exposes a comparatively direct implementation of protocol role instances, intruder actions, and causal search. Its Arachne engine is useful for studying how an analyzer represents partially constructed executions and tries to explain received terms through earlier events, rather than treating attack search as an opaque solver call.

- **C1:** The engine constructs role runs and receive goals, unifies terms, and explores causal bindings while rejecting invalid ordering. Explicit intruder roles cover atomic knowledge, encryption, and decryption.
- **C2:** Protocol roles, claims, terms, and bindings are shared abstractions across the analyzer; heuristics and pruning are separated from the core search operations.
- **C4:** The changelog records releases from 2008 onward, language and role-restriction fixes, the 2020 Python 2-to-3/wx migration, and 2026 build and test automation. This is evidence of compatibility and complexity management across years.

**Entry points:** [Arachne search implementation](https://github.com/cascremers/scyther/blob/main/src/arachne.c); [changelog](https://github.com/cascremers/scyther/blob/main/CHANGELOG.md).

### 3. [mitre/cpsa](https://github.com/mitre/cpsa)

**Language/role:** Haskell; Cryptographic Protocol Shapes Analyzer. The repository identifies this line as experimental CPSA 4, a refactoring of CPSA 2, distinct from CPSA 3.

CPSA starts with a partial participant view and searches for essentially different executions, or shapes, that could explain it. It offers an instructive alternative to process-calculus and multiset-rewriting analyzers: strands and skeletons organize the search around causal protocol behavior.

- **C1:** Reduction must preserve the meaning of skeletons while distinguishing realized executions from unresolved obligations. The implementation treats bound exhaustion separately from successful analysis.
- **C2:** Protocol roles, skeletons, algebraic terms, and rules form reusable modeling machinery rather than a collection of protocol-specific checks.
- **C3:** The reduction engine maintains previously seen preskeletons, checks strong isomorphism with unrealized-node information, and uses parallel mapping in search. These mechanisms target redundant exploration within an explicit search structure.

**Entry point:** [Reduction engine](https://github.com/mitre/cpsa/blob/master/src/CPSA/Reduction.hs), especially the seen-state representation, isomorphism checks, and breadth/step loops. The repository overview explains the CPSA 4 scope and modeling additions.

### 4. [DeepSec-prover/deepsec](https://github.com/DeepSec-prover/deepsec)

**Language/role:** OCaml; trace- and session-equivalence verification for finite protocol processes with supported destructor rewrite theories.

DeepSec is particularly useful for studying privacy properties that compare executions, rather than asking only whether an attacker learns a secret. Its tutorial develops anonymity examples in which decryption failure and observable branches matter.

- **C1:** Equivalence checking must account for adversarial observations and destructor failures. Session equivalence is stronger than trace equivalence; the manual explicitly explains why a failed session-equivalence check need not establish a trace-equivalence attack.
- **C2:** A process language and user-defined, subterm-convergent destructor systems support multiple protocols and primitive models.
- **C3:** Worker distribution and partial-order reduction address interleaving growth. The manual states the structural conditions for reductions, including determinacy and channel restrictions; changing channel visibility can also change the security question.

**Entry points:** [Modeling, equivalence, and distributed-search tutorial](https://deepsec-prover.github.io/manual/html/tutorial.html); [changelog](https://github.com/DeepSec-prover/deepsec/blob/master/changelog). The inspected changelog ends with version 2.0.2 in July 2020; it is not evidence of current maintenance.

### 5. [symbolicsoft/verifpal](https://github.com/symbolicsoft/verifpal)

**Language/role:** Rust in the inspected current repository; accessible protocol modeling and bounded symbolic attack analysis.

Verifpal is valuable for examining the boundary between usable modeling and precisely delimited search guarantees. Its current analysis documentation describes scenario expansion, principal-local state, execution, attacker deduction, and active substitutions as separate stages.

- **C1:** A substituted input must be derivable earlier in the same execution. Candidate knowledge gathered across runs proposes further executions; it does not by itself justify an attack. Goal-directed candidates are replayed before being reported as failures.
- **C2:** Principal instances, local slots, primitive operations, and security queries provide reusable protocol abstractions, with slot metadata tracking origin and attacker influence.
- **C3:** Finite relevant-term bases, lazy term construction, and goal-directed search control cost. The documented bounds and heuristics also limit completeness.

**Entry point:** [Analysis architecture and limitations](https://verifpal.com/docs/analysis/). A passing query means no attack was found under the configured analysis; it is not an unbounded proof, and the documentation does not promise exhaustive search even within every stated bound.

### 6. [canhminhdo/par-maude-npa](https://github.com/canhminhdo/par-maude-npa)

**Language/role:** Maude; a parallel Maude-NPA research extension associated with WRLA 2022.

This is a substantive specialized implementation, not a second listing of unchanged upstream Maude-NPA. The repository decomposes backwards search into successor generation, subsumption within a layer, subsumption against history, and final filtering. It parallelizes the first three stages using a manager and worker interpreters.

- **C1:** The implementation must collect complete batches before changing levels, update search history consistently, and distinguish discovery of an initial state from continued exploration. The manager's state machine makes those ordering obligations visible.
- **C3:** Separate batching controls for simulation, jobs, and history work expose load-balancing decisions. The manager coordinates queues, interpreter loading, reductions, and result counts rather than simply launching independent whole-tool processes.

**Entry points:** [Manager/worker implementation](https://github.com/canhminhdo/par-maude-npa/blob/master/parallel-maude-npa.maude); [architecture and parameter guide](https://github.com/canhminhdo/par-maude-npa/blob/master/README.md). Treat it as a research extension with its own environment assumptions; no current support or numerical speedup is asserted here.

### 7. [darrenldl/ProVerif-ATP](https://github.com/darrenldl/ProVerif-ATP)

**Language/role:** OCaml, Python, and JavaScript; modified ProVerif, automated-theorem-prover integration, and attack-trace narration. **Archived historical project**, associated with CADE 2019.

This is an independent research extension of ProVerif 2.00, not the official upstream ProVerif repository. It is worth studying for the semantic difficulties in exporting a protocol analyzer's internal logic to another prover. The README warns that the main branch may not build and that some changes have uncertain safety.

- **C1:** The TPTP exporter documents an important name-distinctness issue: omitted inequalities between free or constant names can prevent discovery of attacks involving inequality guards. Its repair makes a concrete semantic obligation visible at a tool boundary.
- **C2:** The modified exporter, external-prover orchestration, and trace narration connect reusable protocol input and logical backends. This is more substantial than a command-line wrapper, although its historical status limits practical deployment value.

**Entry point:** [TPTP export design and correctness issue](https://github.com/darrenldl/ProVerif-ATP/blob/master/doc/proverif/tptp_export.md). Read together with the repository's branch/build warnings before attempting reuse.

## Computational proofs and compositional frameworks

### 8. [squirrel-prover/squirrel-prover](https://github.com/squirrel-prover/squirrel-prover)

**Language/role:** OCaml; interactive computational security reasoning with symbolic protocol descriptions.

Squirrel connects protocol processes and trace reasoning to probabilistic security assumptions. It is useful for engineers interested in proof automation that retains computational meaning, including indistinguishability arguments and explicit probability bounds.

- **C1:** The current change history describes concrete reachability judgments, bound distribution between subgoals, exact rewrite requirements, and proof-term bound weakening. These are semantic obligations, not merely user-interface features.
- **C2:** Reusable theories, process descriptions, proof tactics, and cryptographic games separate general reasoning infrastructure from individual protocol proofs. Paired terms support reasoning about related systems.

**Entry points:** [Protocol and proof tutorial](https://squirrel-prover.github.io/documentation/tutorial.html); [current change history](https://github.com/squirrel-prover/squirrel-prover/blob/master/CHANGES.md). The latter explicitly deprecates the older `ddh`, `xor`, and `enckp` tactics because of soundness issues, directing users toward game-based `crypto` reasoning. Historical examples therefore require attention to the checker version and migration notes.

### 9. [EasyCrypt/easycrypt](https://github.com/EasyCrypt/easycrypt)

**Language/role:** OCaml; a proof assistant for probabilistic programs and cryptographic security arguments.

EasyCrypt is broader than protocol verification, but its adversarial games and relational reasoning provide substantial reusable infrastructure for that task. A productive way into the codebase is to follow how one sampling tactic behaves under several program logics rather than starting with a large completed proof.

- **C1:** The `rnd` tactic documentation distinguishes ordinary, probabilistic, relational, and expectation reasoning. Relational sampling needs distribution relationships such as bijective couplings, while one-sided sampling has losslessness obligations. These conditions prevent seemingly intuitive game transformations from silently changing probability semantics.
- **C2:** Shared tactic machinery works across multiple judgments, while probabilistic programs, modules, and cryptographic libraries support reusable constructions and adversary reasoning. The repository includes larger cryptographic examples beyond elementary sampling.

**Entry point:** [Sampling tactic semantics](https://github.com/EasyCrypt/easycrypt/blob/main/doc/tactics/rnd.rst). The repository overview also documents the Why3/solver integration and supported tool versions; those dependencies are part of reproducing proofs, not evidence that every configured solver combination is interchangeable.

### 10. [easyuc/EasyUC](https://github.com/easyuc/EasyUC)

**Language/role:** OCaml and EasyCrypt; a domain-specific language, interpreter, and proof framework for universal composability.

EasyUC adds substantial protocol-composition machinery above EasyCrypt and therefore warrants its own entry. Its functionality addresses, interfaces, simulators, and message-driven control flow organize real/ideal security arguments. The implementation is especially useful for studying how a domain-specific frontend can reject invalid interactions before generating proof obligations.

- **C1:** The modeling discipline constrains message routing and transfer of control: a component cannot arbitrarily send twice without regaining control, and environment/adversary routing is checked. These constraints matter to the UC execution model.
- **C2:** Interface composition, parameterized functionality units, interpretation, and generated EasyCrypt developments support reusable real/ideal constructions. Generated clone parameters and axioms remain obligations for the proof author.

**Entry point:** [UC DSL implementation and examples guide](https://github.com/easyuc/EasyUC/blob/master/uc-dsl/README.md), including unit restrictions and the SMC examples. The guide labels translation functionality as work in progress; generation should not be equated with automatic completion of a security proof.

### 11. [SSProve/ssprove](https://github.com/SSProve/ssprove)

**Language/role:** Rocq/Coq Gallina; foundational, modular proofs of probabilistic cryptographic programs and protocols.

SSProve is worth reading for its package algebra. Interfaces, imports, exports, local state, and package composition turn game-based proof steps into reusable mathematical operations. Its examples include Sigma protocols and Schnorr alongside constructions such as KEM–DEM and secret sharing.

- **C1:** The code language includes probabilistic sampling, mutable state, assertions, and failure represented through subdistributions. Relational proofs must preserve the relevant state invariants and account for differences in adversarial advantage.
- **C2:** Linking connects compatible imports and exports, whereas parallel composition requires compatible state and disjoint interfaces. Validity predicates and reduction lemmas expose the side conditions behind modular proof reuse.

**Entry points:** [Code and proof-library documentation](https://github.com/SSProve/ssprove/blob/main/DOC.md); [package algebra and example map](https://github.com/SSProve/ssprove/blob/main/README.md). Consult the documented assumptions of individual developments rather than interpreting “foundational” as a claim that every example avoids additional axioms.

## Connecting security arguments to implementations

### 12. [secure-foundations/owl](https://github.com/secure-foundations/owl)

**Language/role:** Haskell verifier with Rust/Verus-related code generation; a research language for computationally secure protocol programming.

Owl combines information-flow and refinement-style reasoning with cryptographic operations. Its current KDF design is a particularly revealing case study: names derived from keys need a coherent global interpretation across sites, indices, and recursive ratchets.

- **C1:** KDF checking must reconcile aliasing, key cycles, corruption, and derived-name distinctness with explicit cryptographic assumptions. The design document traces these obligations into parsing, typing, and SMT components.
- **C2:** KDF scopes group related derivation rules, and indexed derived names let multiple protocol steps share a structured account of key derivation rather than duplicating ad hoc checks.

**Entry point:** [Current KDF scopes design](https://github.com/secure-foundations/owl/blob/main/docs/kdf-scopes.md). **Material limitation:** its soundness discussion documents unresolved gaps involving corruption flows and derived/base-name distinctness, including an insecure accepted example. This entry recommends studying the implementation and its explicit design problems; it does not endorse the current checker as blanket security assurance.

### 13. [REPROSEC/dolev-yao-star](https://github.com/REPROSEC/dolev-yao-star)

**Language/role:** F*, with extraction support; the DY* framework for symbolic verification of executable protocol programs.

This repository contains the framework associated with EuroS&P 2021 and multiple protocol developments, including Signal and key-exchange examples. It is useful for studying how a typed cryptographic API can enforce a symbolic security discipline while leaving protocol code executable. Treat this repository as a research development; this report does not establish that it is the latest DY* line.

- **C1:** Secrecy labels account for principals, sessions, versions, and corruption. Flow checks and timestamp-sensitive validity contracts connect message handling to what may already be known by an attacker.
- **C2:** Encryption, signing, and MAC interfaces are parameterized by usage predicates. Shared labels and abstract operations let protocol-specific policies build on a common security API rather than reproducing the adversary model.

**Entry points:** [Labeled cryptographic API](https://github.com/REPROSEC/dolev-yao-star/blob/master/LabeledCryptoAPI.fsti); [secrecy labels and flow interface](https://github.com/REPROSEC/dolev-yao-star/blob/master/SecrecyLabels.fsti). These interfaces expose proof contracts, corruption relationships, and deliberate control of SMT matching.

### 14. [arthuraa/cryptis](https://github.com/arthuraa/cryptis)

**Language/role:** Rocq/Coq; cryptographic separation logic built on Iris.

Cryptis connects symbolic cryptography to reasoning about stateful, concurrent programs. Its repository maps a progression from protocol proofs to authenticated connections, RPC, and a store, making it useful for studying how security facts become reusable program specifications. It also explores session-typed reasoning through Actris.

- **C1:** Public attacker knowledge interacts with heap invariants, ghost state, and cryptographic term structure. The core public-knowledge development uses monotonicity, persistence, and fixed-point reasoning rather than treating secrecy as a standalone Boolean property.
- **C2:** Reusable cryptographic predicates and connection specifications support layered application proofs. The examples include Needham–Schroeder–Lowe and ISO Diffie–Hellman, with higher-level components building on their specifications.

**Entry point:** [Core public-knowledge logic](https://github.com/arthuraa/cryptis/blob/master/cryptis/core/public.v). Use the repository's example map to follow the protocol-to-application layers. Its OPAQUE and TLS 1.3 developments are explicitly described as partial; they are not evidence of complete verification of those protocols.

### 15. [viperproject/SecurityProtocolImplementations](https://github.com/viperproject/SecurityProtocolImplementations)

**Language/role:** Go with Gobra specifications, plus a C/VeriFast prototype; reusable implementation-verification libraries in a CCS 2023 research artifact.

The relevant subsystem is `ReusableVerificationLibrary`, not merely the bundled protocol case studies. It connects ordinary concurrent implementations to a shared symbolic execution trace through local snapshots and parameterized trace invariants. The repository demonstrates reuse for NSL, Diffie–Hellman, and WireGuard, and separately instantiates the approach for C.

- **C1:** The trace manager synchronizes local snapshots with a shared history while preserving permission and trace invariants. Its event-logging contract deliberately promises an event at the participant's snapshot, not at the latest global position: another participant or the attacker may extend the trace after unlocking.
- **C2:** A `TraceContext` supplies protocol-dependent conditions, while common operations log messages, events, corruption, publication, and nonce creation. This separates reusable concurrency/proof machinery from protocol-specific lemmas.

**Entry points:** [Trace-manager implementation and contracts](https://github.com/viperproject/SecurityProtocolImplementations/blob/main/ReusableVerificationLibrary/tracemanager/manager.gobra); [library source tree](https://github.com/viperproject/SecurityProtocolImplementations/tree/main/ReusableVerificationLibrary). This is a reproducible research artifact, not a claim of an independently maintained production verification SDK.

### 16. [FaezehNasrabadi/CryptoBAP](https://github.com/FaezehNasrabadi/CryptoBAP)

**Language/role:** Standard ML and HOL4 within a HolBA-based tree; a bridge from binary analysis to symbolic protocol verification.

The relevant subsystem is `HolBA/src/tools/parallelcomposition`; the enclosing repository counts once. CryptoBAP connects binary intermediate representations, symbolic execution, composition with an attacker, and SAPIC model generation. It offers a different engineering perspective from a protocol DSL: the challenge is preserving security-relevant observations while extracting a model from implementation behavior.

- **C1:** Its SAPIC translator recursively returns both translated terms and HOL theorems, including cases for constants, casts, arithmetic, and memory-related expressions. The surrounding development supplies labeled transition systems and refinement machinery for the binary-to-model connection.
- **C2:** Reusable transition-system composition, adversary components, symbolic execution, and translation support multiple protocol analyses, rather than embedding one protocol's attack search directly in the binary analyzer.

**Entry points:** [SAPIC translation library](https://github.com/FaezehNasrabadi/CryptoBAP/blob/main/HolBA/src/tools/parallelcomposition/translateTosapic/translate_to_sapicLib.sml); [pipeline and subsystem guide](https://github.com/FaezehNasrabadi/CryptoBAP/blob/main/README.md). Extraction is not the entire security proof: cryptographic assumptions and desired properties still have to be supplied to the resulting model.

## Coverage, search method, and limitations

Discovery used more than six distinct live search formulations, including general GitHub security-protocol provers; symbolic reachability and equivalence tools; Maude-NPA parallel narrowing; ProVerif extensions and source mirrors; computational game proofs and universal composability; F* protocol verification and DY*; Iris/Gobra/VeriFast implementation verification; and HOL4 binary-to-protocol extraction. Follow-up searches targeted specific tools, architecture documents, source trees, changelogs, and examples. Later queries increasingly returned already covered projects, teaching material, protocol-only artifacts, and peripheral integrations rather than additional substantial tool implementations.

Every numbered repository's canonical GitHub page was opened, and at least one additional primary document or implementation source was read. The linked implementation and design entry points—not search snippets or star counts—support the selection. Some GitHub browser views failed to load and the public API became rate-limited; public raw files and official documentation supplied the substantive evidence instead. No candidate was built, installed, or executed. Criterion assignments and study recommendations are grounded judgments from the cited materials, not independent proofs or benchmark reproductions.

The GitHub-only requirement leaves significant ecosystem gaps. This search did not establish suitable official substantive GitHub mirrors for upstream [ProVerif](https://bblanche.gitlabpages.inria.fr/proverif/) or [CryptoVerif](https://bblanche.gitlabpages.inria.fr/cryptoverif/); their omission is not a quality judgment. ProVerif-ATP is explicitly a historical derivative, not a substitute source of current upstream releases. The parallel Maude-NPA extension is likewise distinguished from upstream Maude-NPA. SAPIC is counted with Tamarin, and general engines such as Rocq, F*, Gobra, VeriFast, and SMT solvers are not inflated into separate protocol-tool entries.

Model collections, tutorials without reusable machinery, editor integrations, generated wrappers, awesome-lists, and ordinary cryptographic implementations were excluded. Some retained projects are academic artifacts with narrow environment assumptions; archival and known correctness limitations are stated where established. Absence of an archival label is not an assertion of active support. Links to development branches describe the inspected state and can change. This is a diverse selection guide, not an exhaustive census or a claim that every component is uniformly exemplary.
