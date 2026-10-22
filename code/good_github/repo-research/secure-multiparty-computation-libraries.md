# Secure multiparty computation libraries

Research date: **2026-10-09**

This report selects 22 substantive GitHub codebases for studying secure multiparty computation (MPC): general runtimes and compilers, circuit protocols, application-facing libraries, distributed homomorphic protocols, and secure machine learning. Two-party computation is included. For broader cryptographic monorepos, the relevant MPC subsystem is identified and the repository is counted once. Inclusion recognizes engineering material worth studying; it does not establish that every component is exemplary, audited, or suitable for deployment.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure modes.
- **C2 — Abstractions:** substantial reusable interfaces and components supporting multiple uses.
- **C3 — Performance architecture:** concrete computation, communication, or memory constraints addressed through understandable structure.
- **C4 — Evolution:** evidence across years of compatibility, testing, or complexity management, beyond repository age or recent activity.

## General runtimes and programming systems

### 1. [data61/MP-SPDZ](https://github.com/data61/MP-SPDZ)

**Language/role:** C++ runtimes and a Python-based compiler for a broad collection of MPC protocols.

Study how a compiler and virtual-machine boundary support secret sharing, garbled circuits, different arithmetic domains, and different corruption assumptions. The repository explains the distinction between compiling a high-level program and executing its arithmetic or Boolean bytecode. **C2:** the shared programming layer exposes reusable numerical and control-flow facilities across protocol implementations. **C3:** compiler round reduction and configurable preprocessing batches make communication and wasted offline work explicit engineering concerns. These are documented in the [repository architecture and usage guide](https://github.com/data61/MP-SPDZ).

**C1 and C4:** the [changelog](https://github.com/data61/MP-SPDZ/blob/master/CHANGELOG.md) records concrete correctness work across 2022–2026, including MAC-check omissions, threading interactions, truncation, platform compatibility, and compiler scalability. The July 2026 release discusses MAC-key commitments across threads/executions and additional Rep4 checks. This makes the history particularly useful for studying how protocol proofs interact with implementation state. The project explicitly cautions that its software has not undergone a production security review.

**Entry points:** repository guide; `CHANGELOG.md` linked above.

### 2. [lschoe/mpyc](https://github.com/lschoe/mpyc)

**Language/role:** Python framework for MPC with secure numbers and arrays; its documented basic setting is passive security with an honest majority.

MPyC is useful for studying a high-level language runtime that schedules communication while preserving familiar arithmetic and NumPy-style expressions. **C1:** the runtime tracks asynchronous secure objects and protocol execution; conversions, bit operations, and numeric ranges carry assumptions that callers must preserve. **C2:** secure scalar types, arrays, input/output operations, comparisons, and linear algebra are integrated into one programmable runtime. **C3:** the API exposes vectorized operations, and its inner-product documentation explains how a single resharing can replace repeated scalar resharing. These details are visible in the [runtime API and implementation documentation](https://lschoe.github.io/mpyc/mpyc.runtime.html).

The [repository](https://github.com/lschoe/mpyc) supplies the threat-model context and examples. Treat its Python-like surface as a secure computation system with explicit protocol and numeric semantics, rather than assuming ordinary Python execution behavior.

**Entry point:** `mpyc.runtime` documentation linked above, especially secure conversion, coroutine scheduling, and array operations.

### 3. [aicis/fresco](https://github.com/aicis/fresco)

**Language/role:** Java framework separating MPC applications from protocol suites and execution machinery.

FRESCO provides a particularly clear example of architectural seams. Its `SecureComputationEngine` combines a protocol suite, evaluator, resource pool, and network; applications use protocol builders and deferred results. **C2:** numeric and binary computation directories let application code depend on operations instead of a particular cryptographic realization. **C3:** the evaluator boundary accommodates batched evaluation, making scheduling a replaceable part of the system. The [quickstart architecture](https://fresco.readthedocs.io/en/latest/quickstart.html) explains these relationships with concrete interfaces.

**C1:** the [developer guide](https://github.com/aicis/fresco/blob/master/doc/source/developers.rst) describes protocol tests parameterized by evaluation strategy, network, preprocessing, and party count, with parties executed in separate threads. Reusing generic arithmetic tests across suites is useful evidence of how the framework checks that interchangeable implementations preserve behavior. Some documentation reflects older dependencies; use it to understand the architecture and check the source before relying on individual setup instructions.

**Entry points:** quickstart architecture; developer testing guide linked above.

### 4. [KULeuven-COSIC/SCALE-MAMBA](https://github.com/KULeuven-COSIC/SCALE-MAMBA)

**Language/role:** C++ MPC runtime, Python MAMBA programming/compiler layer, and compiler tooling including Rust. Included as a historical research system.

Study the integration of a bytecode machine with offline material production and online consumption. **C1:** the [official technical manual](https://nigelsmart.github.io/SCALE/Documentation.pdf) describes separate producers for checked triples, squares, bits, and input/output material, coordinated with online threads. Correct queue ownership, synchronization, and consumption of checked material are consequential invariants. **C3:** warmup, bounded queues, batching, and FHE worker pools expose the tradeoff between preprocessing throughput, startup delay, and memory use.

**C2:** the same programming system supports different sharing/access structures, including Shamir, replicated sharing, and more general monotone-span representations; an I/O abstraction separates application integration from protocol machinery. The manual also distinguishes setup procedures, so setup choices cannot be treated as security-neutral. The inspected manual is version 1.14, dated August 2021; this entry does not imply current maintenance.

**Entry point:** manual sections on preprocessing, threading, sharing structures, and the virtual machine; the repository provides the corresponding implementation.

## Mixed protocols and circuit execution

### 5. [encryptogroup/ABY](https://github.com/encryptogroup/ABY)

**Language/role:** C++ framework combining arithmetic sharing, Boolean sharing, and Yao circuits for two-party computation.

ABY is a compact way to study why different portions of one computation benefit from different representations. **C2:** its circuit and sharing layers make protocol conversion a reusable operation rather than an application-specific rewrite. **C1:** the [Sharing interface](https://encryptogroup.github.io/ABY/docs/class_sharing.html) separates preparation, setup completion, online preparation, local gate evaluation, interactive gate evaluation, and circuit-layer completion. Those boundaries expose the ordering and buffer-management obligations of a mixed-protocol engine. **C3:** distinguishing local from interactive work, together with precomputed oblivious transfer, supports batching and moving work out of the online phase, as described in the [repository guide](https://github.com/encryptogroup/ABY).

The generated interface documentation is older, so it is an architectural reading aid rather than a claim that every signature matches the latest branch. The project presents the implementation as experimental.

**Entry points:** `Sharing` class documentation; repository explanation of arithmetic/Boolean/Yao composition.

### 6. [encryptogroup/MOTION](https://github.com/encryptogroup/MOTION)

**Language/role:** C++ mixed-protocol framework for two or more parties.

MOTION extends the mixed-protocol design space beyond two parties. **C2:** its serialized communication interface separates protocols from particular messaging transports. Arithmetic and Boolean GMW, OT-based BMR, and conversions are organized as composable protocol machinery. **C3:** precomputed correlated oblivious transfers and conversion choices reduce work or rounds during online evaluation; the authors specifically describe a noninteractive conversion from BMR to arithmetic GMW. These architectural choices are explained in the [authors’ institutional publication record and abstract](https://pure.au.dk/portal/en/publications/motion-a-framework-for-mixed-protocol-multi-party-computation/).

The [core source tree](https://github.com/encryptogroup/MOTION/tree/dev/src/motioncore) separates communication, execution, multiplication triples, oblivious transfer, protocols, and secure types. This makes MOTION useful for tracing a secure operation down through preprocessing and transport without treating the framework as a single circuit evaluator. Its repository describes experimental software; the publication’s performance discussion is not used here as a cross-library ranking.

**Entry points:** `src/motioncore`; author architecture summary linked above.

### 7. [ladnir/aby3](https://github.com/ladnir/aby3)

**Language/role:** C++ three-party computation framework with arithmetic, matrix, machine-learning, and database-oriented components.

The implementation tutorial exposes a useful division between share creation/reconstruction (`Sh3Encryptor`), interactive operations (`Sh3Evaluator`), and dependency scheduling (`Sh3Runtime`). **C1:** asynchronous tasks must preserve dependencies and completion semantics; fixed-point operations add scale and approximation concerns. **C2:** the same underlying sharing and scheduling components support scalar arithmetic, matrices, and higher-level workloads. **C3:** the tutorial contrasts waiting for each operation with constructing independent work before driving completion, and explains why matrix operations avoid repeated scheduling overhead. See the substantive [ABY3 implementation tutorial](https://github.com/ladnir/aby3/blob/master/frontend/aby3Tutorial.cpp).

**Material limitation:** the [repository warning](https://github.com/ladnir/aby3) explicitly describes incomplete security features and a scheduler that can fail, and points readers toward MP-SPDZ for a better-supported implementation. Retain this as a research architecture case study, not as an unqualified deployment candidate.

**Entry point:** `frontend/aby3Tutorial.cpp`, particularly task composition and matrix/fixed-point examples.

### 8. [emp-toolkit/emp-sh2pc](https://github.com/emp-toolkit/emp-sh2pc)

**Language/role:** C++ semi-honest two-party garbled-circuit engine in the EMP ecosystem.

The inspected `main` branch uses `SH2PCSession`, context-bound wire values, and explicit input/reveal operations. **C1:** session ownership and output-recipient semantics are visible API concerns; a reveal can produce no value for a nonrecipient. **C2:** typed integers, bits, floating-point values, and reusable circuits share a context interface. **C3:** half-gate garbling and batched correlated OT address gate communication and input-wire transfer. The [repository API description](https://github.com/emp-toolkit/emp-sh2pc) explains these mechanisms and distinguishes the evolving main API from the legacy 0.3.x release line.

The [test build definition](https://github.com/emp-toolkit/emp-sh2pc/blob/main/test/CMakeLists.txt) separates two-process protocol tests from a compile-time session-concept check, while the [comparison example](https://github.com/emp-toolkit/emp-sh2pc/blob/main/test/test_example.cpp) shows typed party-owned inputs, public reveal, and explicit finalization. This is a useful implementation-scale entry point before exploring more elaborate MPC frameworks.

**Entry points:** session comparison example; test build definition linked above.

### 9. [emp-toolkit/emp-agmpc](https://github.com/emp-toolkit/emp-agmpc)

**Language/role:** C++ authenticated-garbling multiparty computation implementation, distinct from EMP’s semi-honest two-party engine.

Study the `CMPC` implementation and its division into function-independent preprocessing, function-dependent preparation, and online evaluation. **C1:** the code carries per-party MACs and keys alongside wire values, checks authenticated preprocessing, and validates exchanged input-mask information. These are concrete examples of the state and consistency obligations introduced by adversarial participants; reading them is not a security audit. **C3:** preprocessing phases separate reusable cryptographic work from circuit work, while thread-pool futures parallelize communication with multiple peers. Both are directly visible in [the main protocol implementation](https://github.com/emp-toolkit/emp-agmpc/blob/master/emp-agmpc/mpc.h).

**C2:** the same implementation consumes circuit descriptions and offers multiple input/output arrangements, including flexible input/output objects. The [source directory](https://github.com/emp-toolkit/emp-agmpc/tree/master/emp-agmpc) separates authenticated bits, preprocessing, network support, and the circuit engine. Shared EMP dependencies do not make this a duplicate of `emp-sh2pc`: its protocol and participant model are materially different.

**Entry points:** `emp-agmpc/mpc.h`; adjacent preprocessing and flexible-I/O components in the linked directory.

## Rust, browser, and Go integration designs

### 10. [GaloisInc/swanky](https://github.com/GaloisInc/swanky)

**Language/role:** Rust cryptographic workspace; relevant here are its MPC circuit, garbling, party, and communication components.

Swanky is valuable for studying how reusable cryptographic interfaces evolve under practical correctness pressure. **C2:** generic circuit construction supports different evaluators, including plaintext evaluation and analysis, while party abstractions avoid duplicating participant-specific logic. **C1:** the maintainers describe replacing a manually flushed channel interface that could hang with a channel abstraction that manages flushing. Authenticated garbling adds another backend without requiring each circuit to be rewritten. See the maintainers’ detailed [2026 architecture and evolution report](https://www.galois.com/articles/swanky-whats-new).

**C4:** that report traces engineering work from 2024 through 2026, including the 2025 separation between `core` and `edge`, documentation and test expectations, and API redesign. The [edge source tree](https://github.com/GaloisInc/swanky/tree/dev/edge) exposes research components without implying uniform stability. The repository explicitly frames the workspace as research software; count it once rather than counting its crates or unrelated proof-system components as separate MPC libraries.

**Entry points:** maintainer architecture report; `edge` source tree.

### 11. [tlsnotary/mpz2](https://github.com/tlsnotary/mpz2)

**Language/role:** Rust MPC libraries developed for TLSNotary. The former `ethereum/mpz` URL redirects to this canonical repository.

The project’s [design document](https://github.com/tlsnotary/mpz2/blob/dev/DESIGN.md) is unusually useful for understanding cryptographic protocol code embedded in an asynchronous application. **C1:** typestate, explicit protocol messages, lock discipline, and careful handling of CPU-intensive work address invalid transitions and executor stalls. **C2:** synchronous protocol cores are separated from asynchronous I/O, with transport- and executor-independent interfaces using typed message streams. **C3:** the design distinguishes cryptographic CPU work from asynchronous networking and discusses worker pools instead of allowing long computations to monopolize an executor.

The study value is in that separation of protocol logic, scheduling, and message transport. **Scope limitation:** the [repository](https://github.com/tlsnotary/mpz2) says these libraries are designed for TLSNotary and are not intended as a general public-use toolkit. Their interfaces are nevertheless substantive examples of reusable internal MPC abstractions; that is the basis for inclusion.

**Entry point:** `DESIGN.md`, especially core/I/O separation, typestate, and asynchronous execution.

### 12. [sine-fdn/tandem](https://github.com/sine-fdn/tandem)

**Language/role:** Rust malicious-secure two-party circuit engine with WebAssembly and HTTP integration components.

Tandem makes a protocol engine accessible as a nonblocking state machine. **C1:** contributor and evaluator states consume protocol messages and return successor states plus responses; circuit validation and protocol errors are explicit. **C2:** the core circuit engine deliberately leaves communication outside the crate, so applications can use different synchronous or asynchronous transports. Its circuit representation uses AND, XOR, and NOT gates, while adapters provide higher-level integration. The [crate API documentation](https://docs.rs/tandem/latest/tandem/) explains both the WRK17-based protocol construction and the message-driven API.

An experienced engineer can study how cryptographic round structure becomes an application-friendly interface without hiding the need to advance both parties consistently. The [repository](https://github.com/sine-fdn/tandem) contains the engine and its integration components; the inspected API documentation identifies version 0.3.0. No claim about current release cadence is inferred from the existence of that documentation.

**Entry point:** crate documentation, particularly contributor/evaluator transitions, messages, circuits, and errors.

### 13. [multiparty/jiff](https://github.com/multiparty/jiff)

**Language/role:** JavaScript MPC framework for browser and Node.js applications.

JIFF adds an application-integration perspective that native research engines often leave implicit. **C1:** secure-share promises, participant/session coordination, and preprocessing configuration must remain consistent despite asynchronous application behavior. The [introductory architecture tutorial](https://github.com/multiparty/jiff/blob/master/tutorials/1-intro.md) distinguishes a relay server from a server trusted to supply cryptographic material, and explains how preprocessing assumptions change the resulting trust model. **C2:** secret-share operations, extension hooks, and numeric extensions let web applications build on a common MPC API. **C3:** separating offline triple generation from online computation gives applications a concrete way to move expensive work before inputs arrive.

The [repository](https://github.com/multiparty/jiff) supplies the client/server architecture and extension model. Study how browser-oriented orchestration affects protocol composition, rather than assuming that a relay and a preprocessing provider have interchangeable security roles. The older tutorial is used for architectural evidence, not as a guarantee that its installation directions remain current.

**Entry point:** `tutorials/1-intro.md`, especially deployment roles and preprocessing choices.

### 14. [markkurossi/mpc](https://github.com/markkurossi/mpc)

**Language/role:** Go implementation of MPC tools, including the Go-like MPCL compiler and circuit execution machinery.

This is a useful smaller codebase for tracing source-language semantics into secure circuits. **C1:** the [compiler design](https://github.com/markkurossi/mpc/blob/master/compiler/README.md) explains the path from an abstract syntax tree through typed static single assignment to circuits. Secret-dependent branches require both paths to be represented, with merged values selected through multiplexers; integer widths and casts also affect circuit meaning. **C2:** the [repository](https://github.com/markkurossi/mpc) separates compiler, circuit parsing/evaluation, garbling, and oblivious-transfer functionality, making it possible to study or reuse parts below the language frontend.

The engineering lesson is how a familiar imperative language must be restricted and transformed when control flow cannot reveal private values. This is an experimental project: its own outstanding-work list includes incomplete security and implementation features. Its value here is the substantive independent compiler and protocol implementation, not a claim that all planned backends are complete.

**Entry point:** `compiler/README.md`, particularly SSA construction, branch merging, and type semantics.

## Protocol infrastructure and distributed homomorphic computation

### 15. [cryptobiu/libscapi](https://github.com/cryptobiu/libscapi)

**Language/role:** C++ secure-computation infrastructure spanning cryptographic primitives and interactive protocols.

libscapi is more than a binding around a single cryptographic package. Its [architecture introduction](https://biulibscapi.readthedocs.io/en/latest/intro.html) describes four layers: low-level primitives, noninteractive constructions, interactive protocols such as oblivious transfer and commitments, and higher-level secure computation such as Yao and GMW. **C2:** interchangeable interfaces and orthogonal communication/circuit facilities allow protocols to be assembled without tying each application to one primitive implementation. **C3:** the [repository](https://github.com/cryptobiu/libscapi) describes hardware intrinsics, pipelining, and communication optimizations within this layered organization.

Study where an abstraction remains cryptographically meaningful while still permitting specialized implementations beneath it. That makes this library complementary to compiler-centered systems: it exposes the construction materials from which an MPC engine is built. Its documentation includes older platform assumptions, so those instructions should not be mistaken for evidence of support for every current toolchain.

**Entry point:** architecture introduction, then the documented primitive, interactive-protocol, and circuit layers.

### 16. [alibaba-edu/mpc4j](https://github.com/alibaba-edu/mpc4j)

**Language/role:** Primarily Java, with native acceleration; a broad research library containing general two-/three-party circuit computation and reusable secure-protocol components.

Relevant modules include common circuits, RPC, cryptographic tools, preprocessing/correlations, `mpc4j-s2pc-aby`, and `mpc4j-s3pc-abb3`; the same infrastructure also supports private set operations and retrieval. **C2:** this organization lets researchers compare and compose protocols using shared support code. **C3:** Java SIMD and alternative Java/native implementations expose the tradeoff between portability and specialized computation. The [repository guide](https://github.com/alibaba-edu/mpc4j) discusses both architecture and platform constraints.

**C1:** the [changelog](https://github.com/alibaba-edu/mpc4j/blob/main/CHANGELOG.md) records rounding fixes, large-message handling, protocol input limits, RPC changes, and serialization compatibility. These are concrete numerical and systems failure modes beyond cryptographic algorithms. **Material limitation:** the repository explicitly assumes noncrashing nodes and a fully synchronized network; added RPC robustness should not be read as a complete crash-recovery model. Its DP-only components are outside this entry’s scope.

**Entry points:** repository module map and system-model discussion; `CHANGELOG.md`.

### 17. [tuneinsight/lattigo](https://github.com/tuneinsight/lattigo)

**Language/role:** Go lattice-cryptography library; included specifically for its multiparty homomorphic-encryption subsystem.

The relevant code supports distributed key generation, collective decryption/key switching, and interactive protocols over homomorphic schemes. **C2:** the [repository architecture](https://github.com/tuneinsight/lattigo) places multiparty protocols above reusable ring, RLWE, scheme, and circuit layers. This is useful for studying an MPC construction in which parties jointly operate a homomorphic key, rather than executing every operation through ordinary secret-sharing gates. It is not by itself a general network orchestration runtime.

**C1:** the [security documentation](https://github.com/tuneinsight/lattigo/security) explains noise and correctness considerations and gives an especially important implementation constraint: the documented multiparty protocols do not safely support generating/transmitting the same protocol share repeatedly through retries; countermeasures are not implemented. That constraint connects cryptographic security directly to application retry semantics. The documented passive-security assumptions also require attention before assigning stronger guarantees to a composed system.

**Entry points:** repository description of `multiparty`, `mpbgv`, and `mpckks`; security policy.

## Secure machine learning and GPU systems

### 18. [secretflow/spu](https://github.com/secretflow/spu)

**Language/role:** C++ secure processing runtime/compiler with Python integration, oriented toward privacy-preserving numerical and ML workloads.

SPU’s [runtime design](https://github.com/secretflow/spu/blob/main/docs/development/runtime.rst) provides a useful layered model: system services, cryptographic primitives and correlated preprocessing, online protocols, arithmetic/fixed-point operations, and higher-level operations. **C2:** a uniform virtual-machine interface hides heterogeneous party implementations and supports different physical arrangements of data providers and computing parties. **C1:** the separation between ring arithmetic, fixed-point interpretation, and higher operations makes numerical semantics an explicit runtime responsibility.

**C3:** the design discusses private/local operations and special treatment of zero shares to reduce communication during data input, rather than assuming every step should invoke a full interactive protocol. An experienced engineer can follow how compiler-facing operations meet cryptographic backends while placement and infeed costs remain visible. The [repository](https://github.com/secretflow/spu) is counted once; the surrounding SecretFlow ecosystem is not duplicated as a second implementation here.

**Entry point:** `docs/development/runtime.rst`, particularly layer boundaries, party layouts, and data infeed.

### 19. [mpc-msri/EzPC](https://github.com/mpc-msri/EzPC)

**Language/role:** Secure-computation compiler/tooling monorepo with C++ numerical libraries, Python tooling, and GPU-related components. The main focus here is SCI and its compiler integration.

The [SCI subsystem](https://github.com/mpc-msri/EzPC/tree/master/SCI) contains secure inference and floating-point computation machinery, with separate building blocks for comparisons, nonlinear operations, OT, garbling, and linear algebra using HE or OT. **C2:** those operator libraries can support generated model computations without making each model compiler implement cryptographic primitives. **C3:** distinct linear and nonlinear mechanisms expose why one protocol is not uniformly efficient for an entire neural network.

**C1:** the [floating-point library interface](https://raw.githubusercontent.com/mpc-msri/EzPC/master/SCI/src/library_float.h) makes mantissa/exponent sizes, signed integer widths, secret Boolean/fixed/float arrays, and conversions explicit. It then builds matrix, activation, convolution, and training operations on those types. This is concrete material for studying numerical representation boundaries; the interface alone does not establish full IEEE equivalence. Count SCI, model compilers, and related research systems in this repository as one codebase.

**Entry points:** SCI subsystem guide/source tree; `SCI/src/library_float.h`.

### 20. [facebookresearch/CrypTen](https://github.com/facebookresearch/CrypTen)

**Language/role:** Python/PyTorch-oriented encrypted tensor and neural-network framework. **Archived on May 13, 2025**, as marked on the repository.

CrypTen remains useful for studying the semantic gap between familiar tensor APIs and secure numerical computation. **C2:** `MPCTensor` supplies tensor operations and integrates with differentiation and model abstractions while managing arithmetic and binary sharing underneath. **C1:** the [MPCTensor documentation](https://crypten.readthedocs.io/en/latest/mpctensor.html) explains conversions and approximations: exponentiation by repeated squaring, logarithms through iterative methods, reciprocal iteration, and domain/accuracy parameters. These choices make numerical behavior and approximation cost visible instead of assuming native floating-point primitives.

**C3:** operations such as stable `log_softmax` illustrate how mathematical reformulation can avoid unnecessary work and improve numerical behavior in an encrypted setting. The archive status makes this a historical design reference, not evidence of an actively supported deployment path. The [repository](https://github.com/facebookresearch/CrypTen) and the separately inspected API documentation supply complementary status and implementation evidence.

**Entry point:** `MPCTensor` API, especially sharing conversion and approximate nonlinear functions.

### 21. [tf-encrypted/tf-encrypted](https://github.com/tf-encrypted/tf-encrypted)

**Language/role:** Python/TensorFlow secure-computation framework with cryptographic operations and multiple protocol implementations; Pond is the inspected subsystem.

Pond is useful for studying secure tensor computation inside a graph-oriented ML framework. **C1:** its implementation chooses fixed-point configurations and backing tensor factories together, checks configuration compatibility, and encodes values with explicit scaling. Device placement and the separation of public values from secret shares add further invariants. **C2:** protocol objects, public/private tensor types, factories, and triple sources are separate abstractions, allowing substantial reuse above the multiplication protocol. **C3:** the implementation uses vectorized secret sharing with Beaver triples supplied through a separate preprocessing/helper mechanism. These details are directly visible in [Pond’s implementation](https://github.com/tf-encrypted/tf-encrypted/blob/master/tf_encrypted/protocol/pond/pond.py).

The [repository](https://github.com/tf-encrypted/tf-encrypted) supplies the larger TensorFlow integration context. Do not generalize Pond’s helper-party assumptions to every protocol in the project, or infer current TensorFlow compatibility from the architectural study alone.

**Entry point:** `tf_encrypted/protocol/pond/pond.py`, particularly initialization, encoding, tensor factories, and triple-source integration.

### 22. [ucbrise/piranha](https://github.com/ucbrise/piranha)

**Language/role:** C++/CUDA platform for GPU-accelerated MPC and secure machine learning.

Piranha is a distinctive performance-architecture study because it separates device operations, MPC protocols, and applications. **C2:** its protocol layer accommodates different party-count/protocol families over a shared GPU computation substrate. **C3:** the authors describe GPU-resident integer buffers, vectorized operations, integer matrix multiplication, noncopying iterator views, and in-place computation to manage device memory. These are specific responses to GPU memory and data-movement constraints, explained in the [authors’ USENIX Security paper, especially sections 3–4](https://www.usenix.org/system/files/sec22-watson.pdf).

The [source tree](https://github.com/ucbrise/piranha/tree/main/src) makes the decomposition inspectable through `gpu`, `mpc`, `nn`, and test components. **Material limitation:** the repository explicitly presents a proof-of-concept implementation without a careful security review. The paper is used to understand structure and tradeoffs; its benchmark results are not reproduced or treated as a ranking against the other libraries here.

**Entry points:** architecture paper; `src` source tree.

## Coverage, search method, and limitations

Live web discovery used multiple distinct query families: general MPC libraries and frameworks; mixed arithmetic/Boolean/Yao computation; malicious authenticated garbling; honest-majority and replicated sharing; Python/Java/JavaScript runtimes; Rust protocol state machines; Go MPC compilers; secure floating-point and neural-network computation; GPU MPC; distributed homomorphic encryption; and historical SPDZ/SCALE systems. Follow-up searches targeted official design documents, runtime APIs, source files, test organization, changelogs, and repository status. Later queries largely returned the same substantive systems, narrow application artifacts, or overlapping research forks, giving diminishing returns for this selection.

Every retained canonical GitHub repository was opened, and at least one additional relevant primary source was opened and read. Sources include actual implementations, separate API/developer documentation, author-written architecture publications, and release histories. The old `ethereum/mpz` path was resolved to `tlsnotary/mpz2`; the original ABY3 implementation was verified under `ladnir/aby3`. No repository is counted twice, and EMP’s two entries implement materially different engines. Monorepos such as EzPC, Swanky, and mpc4j are each counted once.

Excluded from the selection were awesome-lists, teaching-only examples, generated bindings without substantial independent implementation, redundant forks/ancestors, standalone threshold-wallet/signature projects, enclave-only systems, and standalone FHE libraries without an inspected multiparty subsystem. Private-set and retrieval functionality is included only where it belongs to broader reusable MPC infrastructure. This is not an exhaustive census of historical MPC software or specialized threshold cryptography.

The criterion assignments are engineering judgments grounded in the cited mechanisms, not verified security certifications. No candidate code was installed, executed, or benchmarked. Some generated documentation and historical manuals predate current branches; those limits are called out, and no active-maintenance claim is inferred from repository availability. C4 is assigned only where inspected material supplies a sustained evolution narrative or dated changes together with concrete correctness/compatibility work. Archived and explicitly experimental systems remain useful study references, with their limitations stated rather than silently treated as deployment recommendations.
