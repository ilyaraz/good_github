# Circuit and mixed-signal simulators

Research date: **2026-10-09**.

This selection covers circuit-solving engines and reusable circuit-modeling libraries: SPICE-style numerical simulation, analog/digital interaction, RF harmonic balance, superconducting electronics, power converters, symbolic linear analysis, and audio-rate circuit emulation. It includes 17 repositories, counting each monorepo once and naming its relevant subsystem. Schematic editors, simulator-launching wrappers, pure digital HDL simulators, and generic signal-processing libraries are outside this report's core scope.

Criteria are judgments grounded in the linked implementation material, not certifications of numerical accuracy or uniformly exemplary code. Repository pages or GitHub API metadata were checked, and additional primary implementation or design material was read for every entry. None of the retained repositories was marked archived when checked; historical and early-release code is identified separately. No candidate code was executed or benchmarked.

## Criteria legend

- **C1 — Difficult correctness:** numerical semantics, circuit invariants, convergence, event ordering, adversarial input, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces for devices, circuits, analyses, solvers, or model composition.
- **C3 — Performance with structure:** concrete responses to computational or memory constraints, expressed through identifiable architectural mechanisms.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management; age and recent activity alone do not qualify.

## General numerical engines and mixed-signal foundations

### 1. [Xyce/Xyce](https://github.com/Xyce/Xyce)

**Language/role:** C++; parallel SPICE-compatible analog circuit engine, with multiple analysis types and external coupling interfaces.

Study how a large simulator separates numerical infrastructure from device loading and analysis control. The nonlinear solver manager connects analysis, topology, equation loading, linear systems, time integration, and parallel execution through explicit interfaces.

- **C2:** The [nonlinear solver manager](https://github.com/Xyce/Xyce/blob/master/src/NonlinearSolverPKG/N_NLS_Manager.h) exposes solver/preconditioner factories, distinct analysis options, sensitivity calculations, and initialization contracts. This is a substantial extension boundary rather than a single hard-coded Newton loop.
- **C3:** The [project description](https://github.com/Xyce/Xyce#readme) explains the MPI-based design and use of Trilinos/KLU. The manager additionally exposes matrix-free operation and separate linear-solver configuration, making performance choices visible in the architecture.

Additional context: the [regression-testing guide](https://github.com/Xyce/Xyce/blob/master/test/ReadMe_RegressionTesting.txt) describes CTest integration and dependency-sensitive test selection, but also warns about tests interfering when run concurrently. The README documents a public-history restart after release 7.9; commit-count comparisons would therefore be misleading.

### 2. [gnucap/gnucap](https://github.com/gnucap/gnucap)

**Language/role:** C++; modular mixed-signal simulator with partial Verilog-AMS support. **Provenance:** read-only GitHub mirror under the project organization; its contribution guide directs development interactions to Savannah/Codeberg.

Study a small simulation core extended by dynamically loaded devices, languages, and commands. The [README](https://github.com/gnucap/gnucap#readme) explains the library/front-end/plugin split; the [component interface](https://github.com/gnucap/gnucap/blob/develop/include/e_compon.h) shows shared model data, parameter processing, and transient evaluation/review/acceptance hooks.

- **C2:** Device models, input languages, and simulation commands are extension points around `libgnucap`, allowing different front ends and independently distributed plugins.
- **C4:** The [NEWS history](https://github.com/gnucap/gnucap/blob/develop/NEWS) records 2023–2026 work on expression semantics, transient QA, matrix interfaces, event handling, and the move to case-sensitive input. The README gives a compatibility invocation for older SPICE behavior. The [test guide](https://github.com/gnucap/gnucap/blob/develop/tests/README) explains reference-output regressions and explicitly distinguishes floating-point differences from meaningful failures.

This is especially useful for studying the costs of evolving a public device interface while maintaining language compatibility.

### 3. [wrcad/xictools](https://github.com/wrcad/xictools)

**Language/role:** Primarily C++; select the **`wrspice/` simulator subsystem** of the XicTools monorepo, not the layout editor or extraction utilities.

WRspice offers a substantial SPICE-derived implementation, including specialized superconducting-device work. Study how numerical failure handling and legacy interfaces accumulate within a long-lived simulator.

- **C1:** [`sCKT::NIiter`](https://github.com/wrcad/xictools/blob/master/wrspice/src/ckt/niiter.cc) coordinates device loading, convergence state, sparse-matrix setup/reordering, and floating-point exception checks. It also preserves clearly marked experimental alternatives, useful for distinguishing production mechanisms from abandoned numerical ideas.
- **C4:** The [4.3 release notes](https://github.com/wrcad/xictools/blob/master/wrspice/docs/wrs4.3) document changes across 2020, 2021, 2024, and 2026, including Windows infrastructure, GTK/Qt migration, accepted keyword compatibility, and numerical bug fixes. These are concrete maintenance decisions, not just evidence of an old origin.

The same notes label the newer FastLin solver infrastructure **alpha-level**; it should not be mistaken for an established performance guarantee.

### 4. [SpiceSharp/SpiceSharp](https://github.com/SpiceSharp/SpiceSharp)

**Language/role:** C#; embeddable SPICE simulation framework for .NET.

Study how a simulator becomes a reusable object model. An entity creates behaviors appropriate to a simulation; the simulation then works with those behaviors and shared simulation states rather than continuously querying the original circuit objects.

- **C2:** The [flow architecture](https://github.com/SpiceSharp/SpiceSharp/blob/master/articles/structure/flow.md) separates entities, parameter sets, model/instance relationships, and temperature, biasing, convergence, and time behaviors. This permits device implementations to participate in several analyses without putting every operation into one component class.
- **C1:** The [transient-analysis design](https://github.com/SpiceSharp/SpiceSharp/blob/master/articles/structure/transient.md) explains timestep changes driven by truncation error, failed nonlinear convergence, and source breakpoints. Integration methods are supplied as simulation state, and irreducibly small steps have an explicit failure exception.

These two documents are particularly clear entry points for engineers designing plugin-style numerical libraries.

## Programmatic and symbolic circuit modeling

### 5. [ahkab/ahkab](https://github.com/ahkab/ahkab)

**Language/role:** Python with NumPy/SciPy/SymPy; SPICE-like numerical and symbolic circuit simulation. **Status:** historical implementation; the checked [master history](https://github.com/ahkab/ahkab/commits/master/) ends in March 2019, and the README still highlights the 2015 release.

Study a comparatively approachable implementation of the mathematics shared by larger SPICE engines, including operating points, transient integration, and periodic steady state.

- **C1:** [`transient.py`](https://github.com/ahkab/ahkab/blob/master/ahkab/transient.py) explicitly decomposes the differential circuit equation into static MNA, nonlinear, time-varying, and dynamic terms. It supports alternative differentiation formulas and local-truncation-error step control.
- **C2:** The [programmatic circuit/analysis interface](https://github.com/ahkab/ahkab#usage) separates circuit construction from analysis requests; transient analysis can also accept previously constructed matrices. The library therefore supports scripted experiments and repeated analyses, beyond reading one netlist and exiting.

Its [changelog](https://github.com/ahkab/ahkab/blob/master/CHANGELOG.md) is useful supplementary reading on semantic compatibility: AC results changed from angular frequency to hertz, with migration instructions. Treat dependency and packaging guidance as historical.

### 6. [CedarEDA/CedarSim.jl](https://github.com/CedarEDA/CedarSim.jl)

**Language/role:** Julia, with SPICE/Spectre and Verilog-A parsing; compiler-based analog simulation integrated with differential-equation tooling.

Study circuit specialization and the boundary between a modeling language and a numerical compiler. **Status:** the public README describes an unstable early release; the checked [main history](https://github.com/CedarEDA/CedarSim.jl/commits/main/) ends in August 2024. This report does not infer ongoing development from the README's prospective language.

- **C2:** The [device implementation guide](https://github.com/CedarEDA/CedarSim.jl/blob/main/docs/src/devices.md) builds devices from branch relations, named variables, and differential equations, including additional internal state. Julia-defined devices can participate in imported SPICE circuits.
- **C3:** [`circuitodesystem.jl`](https://github.com/CedarEDA/CedarSim.jl/blob/main/src/circuitodesystem.jl) distinguishes `DefaultSim` from `ParamSim`: only selected parameters remain changeable, allowing other values to become compiler constants. This makes the flexibility/specialization tradeoff concrete.

The README also documents substantial compilation latency and incomplete model/dialect coverage; the device guide warns that its internal API and accepted Julia subset are not stable specifications.

### 7. [mph-/lcapy](https://github.com/mph-/lcapy)

**Language/role:** Python/SymPy; symbolic linear circuit analysis, with an explicitly experimental time-stepping simulator.

Study how circuit equations retain distinctions between DC, phasor, Laplace, noise, and initial-value interpretations. This is the symbolic-analysis edge of the category, rather than a general nonlinear SPICE replacement.

- **C1:** [`mna.py`](https://github.com/mph-/lcapy/blob/master/lcapy/mna.py) documents when solutions are causal or only valid after the initial instant, and requires superposition for mixed source domains. It also allocates branch-current unknowns for controlled sources and rejects undefined controlling elements.
- **C2:** The [circuit and network API](https://github.com/mph-/lcapy#readme) accepts both netlists and compositional one-port networks, exposing node voltages, component currents, and transformed expressions through reusable objects.

For comparison with symbolic solving, [`simulator.py`](https://github.com/mph-/lcapy/blob/master/lcapy/simulator.py) implements backward-Euler/trapezoidal companion models. Its explicit initial-value TODOs are a reason to keep the experimental numerical path distinct from the mature-looking symbolic interface.

## RF and superconducting circuit simulation

### 8. [ra3xdh/qucsator_rf](https://github.com/ra3xdh/qucsator_rf)

**Language/role:** C++; Qucs-derived RF/microwave circuit kernel used with Qucs-S. Only this continuation of the Qucs solver family is counted here.

Study a frequency-domain-oriented component architecture and harmonic balance implementation, rather than treating RF simulation as a minor option on a transient solver.

- **C1:** [`hbsolver.cpp`](https://github.com/ra3xdh/qucsator_rf/blob/develop/src/hbsolver.cpp) separates linear/nonlinear circuit portions, identifies their boundary nodes, transforms nonlinear currents and charges with FFTs, constructs a frequency-domain Jacobian, and checks balance during iteration.
- **C2:** [`circuit.h`](https://github.com/ra3xdh/qucsator_rf/blob/develop/src/circuit.h) supplies common device hooks for S-parameters, DC, AC, noise, transient, and harmonic-balance analyses, with per-device matrix allocation and operating-point state.

The [continuation's release notes](https://github.com/ra3xdh/qucsator_rf/blob/develop/NEWS.md) show substantive separate evolution: S-matrix transformation fixes, radial-stub work, transmission-line model corrections, and converter changes. The original Qucs monorepo and Qucs-S GUI are not additional entries.

### 9. [JoeyDelp/JoSIM](https://github.com/JoeyDelp/JoSIM)

**Language/role:** C++; transient superconducting-circuit simulator, exposed as a CLI and `libjosim`.

Study how the choice of state variable changes a simulator. JoSIM supports voltage-domain MNA and modified nodal **phase** analysis for Josephson-junction circuits, using the phase/voltage relationship to derive different component stamps.

- **C1:** The [technical discussion](https://github.com/JoeyDelp/JoSIM/blob/master/docs/tech_disc.md) derives BDF2-based stamps and shows why a phase-domain capacitor needs additional history. It also explains hierarchical parameter processing and validation of mutually coupled inductors.
- **C3:** The same guide describes assembling sparse storage from component contributions, using KLU, and retaining only requested output traces. Transmission lines require extra retained histories, illustrating a concrete exception to the memory-saving strategy.

Start with that guide and the [component-stamp reference](https://github.com/JoeyDelp/JoSIM/blob/master/docs/comp_stamps.md). The documented scope is transient analysis; the guide explicitly says its parallel CLI option was a reservation for future work in the described version, not evidence of parallel speedup.

### 10. [kpobrien/JosephsonCircuits.jl](https://github.com/kpobrien/JosephsonCircuits.jl)

**Language/role:** Julia; nonlinear frequency-domain Josephson-circuit simulation, harmonic balance, scattering parameters, and noise.

Study the distinction between solving a pumped nonlinear operating point and linearizing around it for small-signal conversion and amplification. The [project explanation](https://github.com/kpobrien/JosephsonCircuits.jl#readme) describes flux-basis modified nodal equations, analytic Jacobians, and adjoint noise calculations.

- **C1:** The [Newton implementation](https://github.com/kpobrien/JosephsonCircuits.jl/blob/main/src/solvers/newton.jl) treats Anderson history ordering, rank-deficient histories, non-finite corrections, and real-valued acceleration coefficients for an antilinear complex update. These are unusually concrete numerical-semantics study material.
- **C3:** That implementation preallocates history/QR buffers and reuses sparse factorization structure; its KLU path explicitly checks reused pivots. The architecture makes allocation, ordering, and factorization reuse inspectable rather than hiding them behind a performance claim.

The README warns of breaking changes. Its example timings are workload-specific and are not generalized here into comparisons with other simulators.

### 11. [acl2/acl2](https://github.com/acl2/acl2)

**Language/role:** ACL2/Common Lisp; select **`books/projects/vwsim/`**, an RSFQ/Josephson circuit simulator within the ACL2 monorepo.

Study a circuit tool whose intermediate representation is a collection of symbolic equations amenable to logical reasoning. The [VWSIM implementation map](https://github.com/acl2/acl2/blob/master/books/projects/vwsim/README) distinguishes hierarchical/flat HDLs, sparse equation construction, evaluators, and the simulation loop.

- **C1:** [`vw-flatten-top-sort.lisp`](https://github.com/acl2/acl2/blob/master/books/projects/vwsim/vw-flatten-top-sort.lisp) combines netlist flattening and symbol rewriting with guards and supporting theorems. Correctness obligations are present in the implementation, not only in prose.
- **C2:** Separate circuit representations, a SPICE translation path, symbolic terms, and optimized/unoptimized evaluators support repeated circuit construction and analysis. The optimized evaluator is designed to evaluate shared subterms once, according to the implementation map.

**Boundary of the guarantees:** the [VWSIM documentation](https://github.com/acl2/acl2/blob/master/books/projects/vwsim/vwsim-doc.lisp) acknowledges Common Lisp floating-point routines outside the fully modeled logic, and the README identifies an unverified solver boundary and skipped proofs. This is not an end-to-end verified floating-point simulator.

## Interactive, embedded, and power-electronics engines

### 12. [pfalstad/circuitjs1](https://github.com/pfalstad/circuitjs1)

**Language/role:** Java compiled for the browser with GWT; interactive analog/digital circuit simulation. The original Java applet and browser-port lineage are documented in the README; alternate copies are not counted separately.

Study numerical simulation under an interactive editing loop. Its [internals guide](https://github.com/pfalstad/circuitjs1/blob/master/INTERNALS.md) relates element stamping, Newton linearization, wire connectivity, and timestep updates to actual implementation methods.

- **C1:** Nonlinear device updates limit voltage changes to avoid exponential overflow; `doStep()` contributes both matrix changes and convergence decisions. Changes to connectivity trigger a new circuit analysis.
- **C3:** The engine reuses LU factorization for linear circuits and collapses wire-connected points into a single node instead of spending extra matrix rows on every wire. The guide explains why these choices reduce repeated work and matrix size.

Use the guide alongside the [client source tree](https://github.com/pfalstad/circuitjs1/tree/master/src/com/lushprojects/circuitjs1/client), particularly the circuit-element, matrix, and simulation classes. It is a substantial solver implementation despite its educational presentation.

### 13. [mamedev/mame](https://github.com/mamedev/mame)

**Language/role:** C++; select the **`src/lib/netlist/` mixed-signal circuit engine** inside MAME, not the emulator as a whole.

Study analog/digital interaction under emulation-time constraints. The [netlist design document](https://github.com/mamedev/mame/blob/master/src/lib/netlist/documentation/mainpage.dox.h) distinguishes rail outputs, high-impedance inputs, and finite-impedance terminals, inserting proxy devices at analog/logic boundaries.

- **C1:** Those distinct connection semantics and automatic boundary proxies make mixed-signal assumptions explicit. The [solver scheduler](https://github.com/mamedev/mame/blob/master/src/lib/netlist/solver/nld_solver.cpp) manages queued solver times, rescheduling, and subsequent input updates.
- **C3:** The [frontier documentation](https://github.com/mamedev/mame/blob/master/src/lib/netlist/FAQ.md) explains splitting a network into smaller solver regions at suitable impedance transitions, including the limited-feedback assumption. The scheduler also contains a deliberately disabled parallel path because it reduced performance in the tested applications.

This is valuable material on accuracy/performance tradeoffs in deployed emulation; the documented circuit approximations should not be confused with universal SPICE model fidelity.

### 14. [geckocircuits/GeckoCIRCUITS](https://github.com/geckocircuits/GeckoCIRCUITS)

**Language/role:** Java; power-electronics simulator coupling electrical, control, and thermal networks. The README identifies this as the official GitHub continuation maintained by an original author.

Study simulation workloads where switching repeatedly returns a system to previously encountered matrices, alongside interactions between domains.

- **C2:** [`SimulationsKern.java`](https://github.com/geckocircuits/GeckoCIRCUITS/blob/main/src/main/java/ch/technokrat/gecko/geckocircuits/circuit/SimulationsKern.java) maintains separate electrical/thermal matrices and control-network machinery, with explicit mappings between network quantities and control elements. This supports multiple converter and coupled-system configurations.
- **C3:** [`LUDecompositionCache.java`](https://github.com/geckocircuits/GeckoCIRCUITS/blob/main/src/main/java/ch/technokrat/gecko/geckocircuits/circuit/LUDecompositionCache.java) reuses factorizations for recurring switched-converter matrices and tracks access, capacity, and memory. Its hash-based identification and eviction policy are concrete design choices worth scrutinizing.

**Limitation:** the [README](https://github.com/geckocircuits/GeckoCIRCUITS#tests) explicitly says legacy tests were disabled because of environment-dependent failures. Selection here rests on reusable modeling and workload-driven architecture, not an assertion of strong current test coverage.

## Audio-rate circuit-modeling libraries

### 15. [HSU-ANT/ACME.jl](https://github.com/HSU-ANT/ACME.jl)

**Language/role:** Julia; analog circuit modeling and emulation, particularly nonlinear audio circuits.

Study automatically deriving a nonlinear state-space model from a programmatically connected circuit, then choosing a solution strategy for repeated input samples. The [circuit construction example](https://github.com/HSU-ANT/ACME.jl#first-steps) provides the front end; [`solvers.jl`](https://github.com/HSU-ANT/ACME.jl/blob/main/src/solvers.jl) exposes the numerical strategy.

- **C1:** Newton iteration is wrapped by a homotopy solver that retries along intermediate parameter values. The implementation handles the case where floating-point arithmetic leaves no representable intermediate value, instead of assuming unlimited refinement.
- **C2:** `SimpleSolver`, `HomotopySolver`, and `CachingSolver` compose through a shared nonlinear-solver contract; convergence, extrapolation origins, and tolerances remain accessible through the wrappers.
- **C3:** The caching wrapper stores difficult solved points in a k-d tree to improve later starting guesses, while the source explicitly warns that populating the cache can initially cost more than it saves.

The combination is particularly useful for studying robustness versus per-sample cost without assuming that plain Newton iteration always converges.

### 16. [Chowdhury-DSP/chowdsp_wdf](https://github.com/Chowdhury-DSP/chowdsp_wdf)

**Language/role:** C++; header-only wave digital filter library for real-time circuit models.

This belongs here because it models connected circuit elements and their wave-port interactions, rather than providing unrelated audio effects. Study the relationship between circuit topology, numerical type, and low-level execution strategy.

- **C2:** The [library examples](https://github.com/Chowdhury-DSP/chowdsp_wdf#readme) compose resistors, capacitors, sources, polarity changes, and adaptors into reusable models. Numeric templates allow the same circuit description to process scalar or SIMD batches.
- **C3:** [`rtype_detail.h`](https://github.com/Chowdhury-DSP/chowdsp_wdf/blob/main/include/chowdsp_wdf/rtype/rtype_detail.h) implements padded/aligned storage and SIMD scattering-matrix multiplication, with scalar fallback paths and compile-time port dimensions. This directly addresses work performed for each sample or collection of voices.

Those two entry points connect the user-facing model composition to the performance-critical kernel. No speedup factor is inferred from the presence of vectorization.

### 17. [RT-WDF/rt-wdf_lib](https://github.com/RT-WDF/rt-wdf_lib)

**Language/role:** C++/Armadillo; wave digital circuit modeling with arbitrary topologies and multiple/multiport nonlinearities. **Status:** historical research library; the checked [master history](https://github.com/RT-WDF/rt-wdf_lib/commits/master/) ends in November 2017.

Study a more explicitly object-oriented WDF architecture than the templated library above, particularly the interface between a circuit tree and a nonlinear multiport root.

- **C2:** [`rt-wdf.h`](https://github.com/RT-WDF/rt-wdf_lib/blob/master/Libs/rt-wdf/rt-wdf.h) separates tree initialization, port adaptation, root-matrix construction, input/output access, and sample-by-sample wave propagation. Users specialize a tree while reusing its execution protocol.
- **C1:** [`rt-wdf_nlSolvers.cpp`](https://github.com/RT-WDF/rt-wdf_lib/blob/master/Libs/rt-wdf/rt-wdf_nlSolvers.cpp) assembles nonlinear device residuals and Jacobians and iterates under tolerance and iteration-budget constraints, with previous-state initialization.

The inspected loop proceeds to output calculation after exhausting its iteration budget; this makes convergence/failure semantics a useful review topic, not a reason to assume every returned sample has converged. The older research implementation is retained for its substantive architecture, not current maintenance.

## Coverage, search process, and limitations

Discovery used more than six distinct formulations, including general SPICE engines; mixed-signal/SystemC-AMS frameworks; Python, Julia, Rust, and C# implementations; RF/microwave harmonic balance; browser and real-time circuit simulation; power electronics; superconducting/Josephson devices; wave digital audio models; and ACL2/formal circuit simulation. Targeted searches for ACME, CedarSim, JoSIM, GSEIM, GeckoCIRCUITS, WRspice, MAME netlists, and Lcapy expanded the list beyond the best-known SPICE programs. Follow-up searches increasingly returned the same engines, wrappers, teaching implementations, or copies; the formal-methods angle supplied the final distinct addition, VWSIM.

Verification used live web search, direct repository pages or GitHub API responses, and direct reads of source files and project documentation. GitHub's unauthenticated API quota was exhausted during metadata collection, so remaining checks used public GitHub pages and raw source files. Branch paths were taken from inspected inventories. Canonical owner/repository URLs are the linked headings; source links are moving branch references, not immutable snapshots.

Important selection boundaries:

- **ngspice:** omitted from the retained GitHub list because its [official download page](https://ngspice.sourceforge.io/download.html) identifies SourceForge as upstream and explicitly describes the linked current GitHub/GitLab copies as externally maintained. An official substantive GitHub mirror was not established in this search. This is a provenance limitation, not a judgment against ngspice's engineering quality.
- **SystemC AMS:** the [official overview](https://systemc.org/overview/systemc-ams/) points to COSEDA's proof-of-concept distribution. A current official GitHub implementation was not verified, and plain SystemC's discrete-event kernel was not substituted for its AMS extension.
- **Unavailable candidates:** the discovered `dan-fritchman/Spice21` and `gseim/gseim` repository URLs returned HTTP 404 during direct verification. Search-index descriptions were insufficient to retain them. Rust searches also returned experimental ports and small implementations; language diversity was not padded with an unverified substitute.
- **Related projects:** Qucs-S, PySpice-style interfaces, schematic tools, model collections, and Verilog-A compilers were not counted as separate solving engines. Only one Qucs solver continuation and one CircuitJS lineage were retained. MAME, XicTools, and ACL2 each count once for their specifically identified circuit subsystems.

The criteria indicate fruitful areas for experienced engineers to study. They do not establish whole-project correctness, production readiness, maintained dependency compatibility, or comparative performance. Documented limitations and historical status are part of the selection guide.
