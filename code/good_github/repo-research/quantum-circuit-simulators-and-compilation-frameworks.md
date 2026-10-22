# Quantum circuit simulators and compilation frameworks

Research date: **2026-10-09**.

This selection covers 26 GitHub repositories implementing quantum circuit representations, classical circuit simulators, circuit synthesis and optimization, hardware mapping, and quantum/classical compiler pipelines. It includes qubit and photonic circuits, from compact research implementations to large SDKs. The emphasis is on engineering mechanisms an experienced reader can study, rather than popularity or benchmark rankings. Monorepos are counted once; the relevant subsystem is identified below.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, input validation, or failure modes.
- **C2 — Abstractions:** substantial reusable interfaces and representations supporting different applications.
- **C3 — Performance:** concrete computational constraints addressed through an understandable architecture.
- **C4 — Evolution:** evidence across years of compatibility work, testing, or complexity management.

Criteria assignments are engineering judgments grounded in the linked implementation material. They are not claims that every component is exemplary. Canonical repository identities and archive flags were checked through GitHub pages or its public API. An unarchived repository should not be interpreted as a promise of active maintenance.

## Circuit frameworks and reusable compiler frontends

### 1. [Qiskit/qiskit](https://github.com/Qiskit/qiskit)

**Language / role:** Python and Rust; circuit SDK, particularly its transpiler and pass-management subsystem.

Study how a broad compiler exposes replaceable stages without making every internal pass part of the same extension contract.

- **C1:** Layout, routing, basis translation, and scheduling impose different constraints. The pass-manager API also explicitly warns that cached analysis can depend on both the input circuit and target; reusing it indiscriminately is incorrect.
- **C2:** `StagedPassManager` composes independent pass managers with pre/post hooks. External packages can supply stage implementations through entry points, allowing different compilation policies to share the surrounding pipeline.

Entry points: [staged pass-manager contract](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.StagedPassManager) and [transpiler stage plugin interface](https://quantum.cloud.ibm.com/docs/en/api/qiskit/transpiler_plugins).

### 2. [quantumlib/Cirq](https://github.com/quantumlib/Cirq)

**Language / role:** Python; circuit construction, transformation, simulation, and device-facing abstractions, principally `cirq-core`.

Study protocol-based extensibility: gates and operations expose capabilities rather than forcing every algorithm through one concrete gate hierarchy.

- **C1:** The protocol documentation distinguishes unitary effects, mixtures, Kraus channels, measurements, approximate equality, and equality up to global phase. Its unitary fallback behavior explicitly rejects objects that cannot supply a suitable matrix, decomposition, or application implementation.
- **C2:** Shared protocols such as `act_on`, `apply_unitary`, and `decompose` let custom operations participate in simulators and transformations. This is a useful example of separating mathematical capabilities from concrete object types.

Entry point: [protocol design and capability contracts](https://quantumai.google/cirq/build/protocols).

### 3. [qiboteam/qibo](https://github.com/qiboteam/qibo)

**Language / role:** Python; backend-independent circuit framework with an in-repository NumPy simulator.

Study the boundary between an algorithm-facing circuit model and execution implementations with materially different behavior.

- **C2:** Circuit and gate objects are backend agnostic; new implementations derive from `Backend` or the simulation-specific `Simulator`. Hamiltonians, evolution, and variational models reuse that boundary.
- **C1:** Backend choice affects state ownership: the documented qibojit integration updates initial states in place, so algorithms retaining those states must copy them explicitly. That is a concrete correctness contract for interchangeable execution backends.

Entry points: [code organization and extension interfaces](https://qibo.science/qibo/stable/developer-guides/general.html) and [backend semantics](https://qibo.science/qibo/stable/getting-started/backends.html). Accelerated qibojit kernels live in a separate repository; their implementation is not attributed to this one.

### 4. [QuantumBFS/Yao.jl](https://github.com/QuantumBFS/Yao.jl)

**Language / role:** Julia; compositional circuit and register framework, including its block libraries.

Study how multiple dispatch and a tree of quantum blocks support both matrix semantics and specialized execution.

- **C2:** Primitive and composite blocks share `AbstractBlock`; chains, tensor products, controlled operations, subroutines, and cached blocks compose into circuit trees.
- **C1:** The public `apply!` checks register/block sizes while extension authors implement `unsafe_apply!`. Parameterized primitive blocks must provide consistent hashing and equality for caching.
- **C3:** In-place application and cached matrix representations expose allocation and repeated-computation costs through explicit interfaces.

Entry point: [block hierarchy, extension contracts, and application methods](https://docs.yaoquantum.org/dev/man/blocks.html). GPU and tensor-network companion packages are not counted as separate Yao implementations here.

### 5. [ProjectQ-Framework/ProjectQ](https://github.com/ProjectQ-Framework/ProjectQ)

**Language / role:** Python and C++; compiler-engine pipeline and circuit simulator.

Study streaming compilation, where compiler engines process commands incrementally rather than requiring every transformation to own an entire circuit graph.

- **C2:** The framework composes compiler engines with simulation, resource-counting, and hardware backends.
- **C1:** Its local optimizer keeps per-qubit command pipelines. Before emitting a multi-qubit operation it must flush the preceding operations on the other participating qubits and avoid emitting that operation twice.
- **C3:** A configurable local cache bounds the optimization window; adjacent operations are merged or canceled before forwarding commands downstream.

Entry point: [local optimizer implementation](https://github.com/ProjectQ-Framework/ProjectQ/blob/develop/projectq/cengines/_optimize.py). The repository is unarchived; historical hardware examples in its README are not treated as verified current service availability.

### 6. [microsoft/qdk](https://github.com/microsoft/qdk)

**Language / role:** Rust, with Python and TypeScript integrations; Q# compiler, interpreter, and simulation tooling. Relevant subsystem: `source/compiler/qsc`.

Study a reusable compiler embedded in interactive tools and language integrations, particularly how diagnostics survive transitions between representations.

- **C1:** The compiler distinguishes frontend, pass, FIR-transformation, dependency-cycle, and OpenQASM errors. Target capability flags participate in compilation, and FIR diagnostics are mapped back through package identities to source information.
- **C2:** Package stores, dependency inputs, compile units, and reusable pass contexts provide several compiler entry points instead of coupling compilation to a single CLI invocation.

Entry point: [compiler orchestration and diagnostics](https://github.com/microsoft/qdk/blob/main/source/compiler/qsc/src/compile.rs). This is the modern QDK repository; deprecated Q# compiler/runtime repositories are not counted again.

## Dense, distributed, and accelerated simulation

### 7. [Qiskit/qiskit-aer](https://github.com/Qiskit/qiskit-aer)

**Language / role:** C++ and Python; simulation backend supporting several state representations and noise models.

Study how a common backend API exposes algorithm-specific accuracy and resource controls without pretending the methods are interchangeable in every case.

- **C1:** The API specifies which methods support measurement, reset, and noise. It documents failure cases for approximate stabilizer sampling on sparse output distributions and explicit MPS truncation controls.
- **C3:** Cache blocking partitions state data across GPUs or MPI processes; shot branching shares evolution until outcomes diverge. Parallel shots and parallel experiments also have documented resource restrictions.
- **C2:** `AerSimulator` provides one configurable interface over statevector, density-matrix, stabilizer, MPS, and other methods.

Entry point: [AerSimulator methods and execution options](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html).

### 8. [quantumlib/qsim](https://github.com/quantumlib/qsim)

**Language / role:** C++ and Python; statevector simulator with Cirq integration and hardware-specific kernels.

Study the relationship between circuit preprocessing and a memory-intensive numerical kernel.

- **C3:** Gate fusion reduces repeated state updates, while vectorized and threaded kernels address the cost of traversing the statevector. The source tree separates fusion, state storage, and simulator implementations.
- **C1:** The multi-qubit fuser documents ordering constraints for operations on the same qubits and prohibits crossing measurement or explicit time boundaries. Non-matrix operations require separate treatment.
- **C2:** The core library can be embedded independently of its Python integration.

Entry points: [multi-qubit fusion implementation](https://github.com/quantumlib/qsim/blob/main/lib/fuser_mqubit.h) and [kernel/state-space source tree](https://github.com/quantumlib/qsim/tree/main/lib).

### 9. [QuEST-Kit/QuEST](https://github.com/QuEST-Kit/QuEST)

**Language / role:** C++ implementation with C/C++ interfaces; statevector and density-matrix simulation across CPU, GPU, and distributed deployments.

Study a hardware-independent register abstraction whose implementation must manage synchronization, memory capacity, and communication costs.

- **C2:** The same `Qureg` interface supports different combinations of threading, GPU acceleration, and distribution, with deployment decisions made automatically or explicitly.
- **C1:** GPU dispatch and distributed workers can progress asynchronously; correct timing requires synchronization, and collective calculations establish necessary synchronization points.
- **C3:** The launch guide explains memory-bandwidth limits, NUMA tradeoffs, communication avoidance, and why small registers can disable distribution automatically.

Entry point: [execution, synchronization, and distribution guide](https://quest-kit.github.io/QuEST/md_docs_2launch.html). Some v4 documentation remains incomplete, which the project explicitly acknowledges.

### 10. [qulacs/qulacs](https://github.com/qulacs/qulacs)

**Language / role:** C++ and Python; noisy and parameterized circuit simulation with CPU, GPU, and MPI implementations.

Study how distributed state ownership changes APIs that appear simple in a single-process simulator.

- **C1:** MPI sampling must be invoked across ranks with consistent seeds. The documentation distinguishes local state fragments from global states and explains that random-state reproducibility changes with partition count.
- **C3:** The circuit optimizer can insert SWAP/FusedSWAP operations, optionally reorder gates, and reduce inter-rank communication.
- **C2:** Distributed execution extends the existing `QuantumState` and circuit-optimization interfaces rather than introducing a separate application model.

Entry point: [MPI API and optimization design](https://github.com/qulacs/qulacs/blob/main/README_MPI.md). The inspected guide explicitly disallows combining the MPI and GPU build options; support for each separately does not imply they compose.

### 11. [PennyLaneAI/pennylane-lightning](https://github.com/PennyLaneAI/pennylane-lightning)

**Language / role:** C++ and Python; PennyLane statevector and tensor-network simulator family, counted once.

Study a simulator boundary that converts high-level operations into specialized numerical calls while retaining a generic fallback.

- **C3:** The qubit state adapter selects specialized gates when available and otherwise applies dense or sparse matrices. It uses aligned allocations and distinct complex-precision state classes.
- **C1:** The same dispatch path must preserve adjoint flags, control values, wire mappings, and mid-circuit measurement-dependent behavior.
- **C2:** `LightningStateVector` derives from a shared base and separates managed state storage from measurement handling and operation dispatch.

Entry points: [state-vector adapter implementation](https://github.com/PennyLaneAI/pennylane-lightning/blob/main/pennylane_lightning/lightning_qubit/_state_vector.py) and [architecture overview](https://docs.pennylane.ai/projects/lightning/en/stable/arch/arch_overview.html). The implementation is the more detailed source for current dispatch behavior.

## Structured state representations and photonic circuits

### 12. [quantumlib/Stim](https://github.com/quantumlib/Stim)

**Language / role:** C++ and Python; stabilizer circuit simulation and detector-error-model tooling.

Study a deliberately restricted mathematical model optimized for repeated error-correction experiments.

- **C1:** Inverse stabilizer tableaus support measurement semantics, while Pauli-frame propagation produces samples relative to a reference trajectory. The restriction to stabilizer operations is essential; this is not an arbitrary non-Clifford simulator.
- **C3:** Reference-frame sampling avoids repeating full tableau simulation for every shot, and packed vector operations accelerate hot loops.
- **C2:** Circuits, tableaus, Pauli strings, samplers, and detector error models form reusable building blocks. The developer guide clearly separates Python/CLI compatibility promises from the unstable C++ interface and documents sanitizers and SIMD-specific tests.

Entry point: [developer contracts and testing architecture](https://github.com/quantumlib/Stim/blob/main/doc/developer_documentation.md); the repository README explains the simulation algorithms.

### 13. [jcmgray/quimb](https://github.com/jcmgray/quimb)

**Language / role:** Python; tensor-network library with a substantial quantum-circuit simulation subsystem.

Study simulation as query planning: the network needed for one amplitude or local expectation can differ dramatically from the network needed for a full state.

- **C2:** Circuit objects support amplitudes, expectations, reduced states, sampling, and access to the underlying tensor network, rather than exposing only a single simulation result.
- **C3:** The documented pipeline separates simplification, contraction-path search, slicing, and numerical contraction. Rehearsal methods expose contraction trees and memory requirements before expensive execution.
- **C1:** Local expectation calculations remove gates outside the relevant reverse lightcone using circuit structure; this optimization depends on preserving the correct ket/bra and index relationships.

Entry point: [circuit simulation architecture and cost planning](https://quimb.readthedocs.io/en/latest/circuit/circuit.html). The selection concerns circuit simulation, not every many-body feature in the monorepo.

### 14. [munich-quantum-toolkit/ddsim](https://github.com/munich-quantum-toolkit/ddsim)

**Language / role:** C++ and Python; decision-diagram circuit simulators built on MQT Core.

Study a compressed state representation whose usefulness depends on circuit structure and on the requested output.

- **C1:** The circuit simulator handles mid-circuit measurements and resets, which require different execution semantics from purely unitary evolution followed by terminal measurement.
- **C3:** With only terminal measurements, it evolves the decision diagram once and samples the final representation repeatedly. Requesting the complete statevector still incurs exponential output costs.
- **C2:** The project exposes circuit, unitary, hybrid, path-based, and noise-aware simulation variants, with Python/Qiskit-facing interfaces.

Entry point: [CircuitSimulator algorithm and dynamic-circuit examples](https://github.com/munich-quantum-toolkit/ddsim/blob/main/docs/simulators/CircuitSimulator.md). Compression is not a general guarantee of efficient simulation for arbitrary circuits.

### 15. [System-Verification-Lab/q-sylvan](https://github.com/System-Verification-Lab/q-sylvan)

**Language / role:** C/C++; quantum-specific extension of the parallel Sylvan decision-diagram library.

Study the interaction of canonical shared structure, complex weights, and memoized quantum operations. This contains substantive quantum simulation machinery beyond its inherited Sylvan base.

- **C1:** Simulator initialization selects weight-table tolerance and normalization strategy. Gate application distinguishes cached structural results from root amplitudes, which must be restored correctly when reusing results.
- **C3:** The implementation controls cache-access granularity and memoizes repeated gate applications on decision-diagram subgraphs.
- **C2:** It provides both QMDD/edge-valued and multi-terminal decision-diagram simulation, plus circuit-equivalence utilities.

Entry point: [quantum simulator and cache handling](https://github.com/System-Verification-Lab/q-sylvan/blob/master/src/qsylvan_simulator.c). Its README explicitly excludes custom QASM gate definitions and classical conditioning.

### 16. [NTU-ALComLab/SliQSim](https://github.com/NTU-ALComLab/SliQSim)

**Language / role:** C/C++; bit-sliced BDD circuit simulation and probability/statistics queries over CUDD.

Study an unusual numerical representation: integer bit slices are encoded as decision diagrams instead of storing one floating-point complex value per amplitude.

- **C1:** The interface exposes integer precision and overflow-triggered BDD allocation; disabling allocation can introduce numerical errors. Gate code also manages CUDD references explicitly while constructing and replacing Boolean functions.
- **C2:** Beyond sampling and statevector output, the query language supports Boolean events, Hamming weights, integer comparisons, Pauli expectations, and weighted combinations.
- **C3:** BDD reordering and bit-sliced state sharing address memory cost; targeted queries avoid requiring complete statevector output.

Entry point: [BDD gate implementation](https://github.com/NTU-ALComLab/SliQSim/blob/master/src/gates.cpp); the repository README documents query semantics and overflow controls. Its supported gate set is explicitly limited.

### 17. [XanaduAI/strawberryfields](https://github.com/XanaduAI/strawberryfields)

**Language / role:** Python; continuous-variable photonic circuit framework and Gaussian, Fock, and bosonic simulators. **Archived on January 16, 2026; retained as a historical engineering study.**

Study the numerical and abstraction differences between finite-dimensional qubits and truncated optical modes.

- **C1:** The Fock backend documents tensor index ordering, ket-versus-density-matrix representations, and cutoff-dependent numerical inaccuracies, including a specific caveat for cubic phase gates.
- **C2:** A backend adapter implements the common API while a separate circuit object carries out mathematical state updates.
- **C3:** The simulator preserves a pure-state representation as long as possible; switching to mixed states increases tensor rank. The cutoff makes the accuracy/memory tradeoff explicit.

Entry point: [Fock backend implementation contract](https://strawberryfields.readthedocs.io/en/latest/code/api/strawberryfields.backends.FockBackend.html). The GitHub archive banner takes precedence over older contribution text still present in the documentation.

## Synthesis, hardware compilation, and hybrid program lowering

### 18. [Quantinuum/tket](https://github.com/Quantinuum/tket)

**Language / role:** C++ and Python; circuit compiler core and `pytket` bindings.

Study compiler composition with explicit contracts about what each transformation requires, preserves, and invalidates.

- **C1:** Passes carry preconditions and postconditions expressed as predicates. The manual explains why routing can invalidate gate-set or measurement constraints, and how pass combinators use these conditions to check composition.
- **C2:** Predicates, pass combinators, and `CompilationUnit` are reusable infrastructure. Initial and final qubit maps track permutations introduced by transformations, so subsequent circuits and measurements can be aligned correctly.

Entry point: [compiler predicates, composition, and qubit maps](https://docs.quantinuum.com/tket/user-guide/manual/manual_compiler.html). Canonical identity was additionally verified with the [GitHub repository API](https://api.github.com/repos/Quantinuum/tket) after browser-reader failures.

### 19. [BQSKit/bqskit](https://github.com/BQSKit/bqskit)

**Language / role:** Python; quantum synthesis and compilation framework. OpenQASM benchmark data should not be confused with the implementation language.

Study a compiler whose optimization work is itself a parallel computational workload.

- **C2:** Passes implement asynchronous `run(circuit, data)` methods; workflow-scoped `PassData` carries target models and communication between passes.
- **C1:** Pass objects are intended to remain immutable after construction. Work sent to the multiprocessing runtime must be serializable and importable by workers, avoiding hidden mutable state and worker-only failures.
- **C3:** Runtime handles expose mapping, submission, waiting, and cancellation. Attached execution serves one machine, while detached managers support distribution across machines.

Entry points: [custom pass contracts](https://bqskit.readthedocs.io/en/latest/guides/custompass.html) and [compiler runtime architecture](https://bqskit.readthedocs.io/en/latest/source/runtime.html).

### 20. [zxcalc/pyzx](https://github.com/zxcalc/pyzx)

**Language / role:** Python; ZX-calculus circuit rewriting, optimization, extraction, and equivalence tools.

Study optimization that temporarily leaves the circuit representation and must reconstruct an executable circuit afterward.

- **C1:** Simplification changes a graph while preserving its quantum meaning. Verification can compare tensors up to global phase or simplify one circuit composed with the other's adjoint; the latter is a method with practical limits, not an unconditional equivalence oracle.
- **C2:** Circuit/graph conversion, rewrite strategies, extraction, phase-polynomial optimization, and routing can be combined independently.
- **C3:** The documentation distinguishes T-count improvement from the potentially high CNOT cost of extraction and offers phase teleportation when preserving circuit structure matters.

Entry point: [simplification, verification, and extraction tradeoffs](https://pyzx.readthedocs.io/en/stable/notebooks/simplify.html).

### 21. [softwareQinc/staq](https://github.com/softwareQinc/staq)

**Language / role:** C++17 with Python bindings; source-to-source circuit optimization, synthesis, and mapping.

Study a compiler that transforms OpenQASM syntax trees while retaining source structure, with algorithms organized into distinct mapping, synthesis, and optimization modules.

- **C2:** The library separates device descriptions, initial layout, routing, circuit synthesis, and generic AST substitution.
- **C1:** Clifford/rotation algebra and topology-constrained synthesis must preserve circuit semantics. The changelog records a concrete interoperability issue: differing gate-phase conventions between OpenQASM and Qiskit.
- **C4:** Dated releases from 2019 through 2024 document parser extraction, testing/CI migrations, platform fixes, and an explained header-layout change for consistent installed and non-installed builds.

Entry points: [library architecture](https://github.com/softwareQinc/staq/wiki/Library-structure) and [versioned evolution](https://github.com/softwareQinc/staq/blob/main/CHANGES.md). The older wiki's paths predate the documented `include/staq` reorganization.

### 22. [quil-lang/quilc](https://github.com/quil-lang/quilc)

**Language / role:** Common Lisp; optimizing Quil compiler, with reusable `cl-quil` library and CLI/RPC interfaces.

Study how a dynamic-language implementation separates language processing from the process and network interfaces used by clients.

- **C1:** Parsing includes definition-resolution rules and post-parse transforms for gate-loop validation, circuit expansion, and type checking. Ambiguous memory and gate definitions have explicit handling.
- **C2:** `cl-quil` supplies the parsing/compilation library; `quilc` exposes it through command-line and RPC operation. The repository describes `compiler-hook` constructing a control-flow graph before optimization.

Entry point: [parser orchestration and semantic transforms](https://github.com/quil-lang/quilc/blob/master/src/cl-quil.lisp). The canonical owner is `quil-lang`; older Rigetti references are not listed as separate projects.

### 23. [QuTech-Delft/OpenQL](https://github.com/QuTech-Delft/OpenQL)

**Language / role:** C++ and Python; retargetable circuit compiler extending down to control-architecture assembly/microcode.

Study resource-constrained scheduling beyond the simple rule that two gates cannot occupy the same qubit simultaneously.

- **C1:** Shared instruments may allow simultaneous operations only when their functions, start times, and durations agree. Mapping and scheduling must honor those constraints while overlapping swaps with other work.
- **C2:** Platform descriptions configure reusable resource types, instrument connectivity, and architecture-specific variants. Compatibility desugaring converts older specialized resource formats into the generalized model.
- **C3:** Resource-aware routing uses available parallelism to improve execution schedules while preserving physical feasibility.

Entry point: [scheduler resource model and compatibility rules](https://openql.readthedocs.io/en/latest/gen/reference_resources.html).

### 24. [NVIDIA/cuda-quantum](https://github.com/NVIDIA/cuda-quantum)

**Language / role:** C++, Python, and MLIR/TableGen; CUDA-Q compiler and runtime for hybrid quantum/classical programs.

Study a full lowering pipeline whose compiler and simulation runtime can be understood as separate layers.

- **C1:** The Quake dialect supports memory and value semantics for qubits. The C++ runtime disallows copying qubits through a deleted copy constructor, enforcing a language constraint using existing compiler diagnostics.
- **C2:** The architecture separates the Clang AST bridge, Quake/CC dialects, transformation and conversion passes, and QIR runtime. An extensible `CircuitSimulator` interface sits beneath QIR execution.
- **C3:** CPU and GPU simulator implementations can serve the same runtime contract, while modular tools expose compilation stages independently.

Entry point: [compiler/runtime architecture and source map](https://github.com/NVIDIA/cuda-quantum/blob/main/Overview.md).

### 25. [PennyLaneAI/catalyst](https://github.com/PennyLaneAI/catalyst)

**Language / role:** Python, C++, and MLIR/TableGen; JIT compiler for hybrid quantum programs.

Study how automatic differentiation, classical control flow, and quantum circuit transformations share an intermediate representation.

- **C1:** Quantum operations consume and produce qubit state values in SSA form; lowering removes these bookkeeping values while preserving operation dataflow. Gradient transformations must also handle classical instructions and control flow, subject to documented limitations.
- **C2:** Quantum and gradient dialects, verifiers, canonicalizers, conversions, and standalone compiler tools separate representation, transformation, and execution concerns.
- **C3:** Compiling the hybrid workflow into native code addresses repeated Python execution overhead; the architecture also distinguishes optimization in tensor form from later bufferization.

Entry points: [compiler IR and source organization](https://docs.pennylane.ai/projects/catalyst/en/stable/modules/mlir.html) and [end-to-end architecture](https://docs.pennylane.ai/projects/catalyst/en/latest/dev/architecture.html).

### 26. [openqasm/qe-compiler](https://github.com/openqasm/qe-compiler)

**Language / role:** C++ and MLIR/TableGen; IBM-origin Quantum Engine compiler framework for OpenQASM 3 and real-time control systems. **Archived; historical implementation.**

Study the gradual conversion of mutable classical variables into dataflow suitable for optimizing dynamic quantum circuits.

- **C1:** The variable-lowering design explains measurement-conditioned gates, symbol-based loads/stores, alias assumptions, and why remaining control-flow cases retain memory operations. It explicitly describes partial rather than complete SSA promotion.
- **C2:** QUIR, OQ3, Pulse, and QCS dialects separate abstraction levels. Hardware-specific targets extend the framework; the repository supplies a mock target rather than a complete hardware compiler.

Entry points: [variable-lowering design](https://github.com/openqasm/qe-compiler/blob/main/docs/variable-lowering.rst) and [archive/identity metadata](https://api.github.com/repos/openqasm/qe-compiler). Old `qss-compiler` names remain in documentation; it also records incomplete documentation and variable-scoping limitations.

## Coverage and search notes

Discovery used more than six distinct live-search formulations, including statevector/tensor-network/decision-diagram simulators; MPI and GPU implementations; stabilizer and error-correction simulation; Julia and Rust quantum tooling; MLIR and OpenQASM 3 dynamic-circuit compilation; topology-aware synthesis and mapping; ZX rewriting; Common Lisp/Quil compilation; photonic Gaussian/Fock simulation; and FPGA/distributed simulator alternatives. Searches were followed by repository-page or API verification and additional primary documentation/source inspection for every retained repository. Public GitHub raw files were used when the browser reader could not load implementation pages. No candidate code was executed and no dependencies were installed.

The final searches mostly returned already represented architecture families, wrappers, or narrower research prototypes. Strawberry Fields was added because photonic state representations supplied a distinct missing family, extending the selection to 26. Smaller substantive implementations such as SliQSim, Q-Sylvan, staq, and quilc balance the larger SDKs. Q-Sylvan is included for its separate quantum implementation, not merely for inherited decision-diagram infrastructure.

Tutorial simulators, visual circuit demos without comparable implementation depth, repository lists, and thin bindings were excluded. General quantum dynamics, tensor algebra, chemistry packages, standalone error decoders, and analog-only simulators were not included merely because they are adjacent to quantum computing. Deprecated Q# repositories and merged Qulacs variants were not counted separately. This is not exhaustive coverage of quantum compilation research or every accelerator-specific simulator.

Limitations: the review inspected selected architectural paths rather than auditing entire codebases, reproducing benchmarks, or proving transformations correct. Documentation can lag implementation; the report identifies particularly relevant historical or incomplete material. Archive status is explicit for qe-compiler and Strawberry Fields. No numerical speedup rankings or blanket maintenance claims are made. Performance and correctness criteria describe concrete engineering problems and mechanisms, not independent verification that every implementation solves them without defects.
