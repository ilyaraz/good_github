# In-kernel virtual machines and verification toolchains

Research date: **2026-10-09**.

This report selects **19 repositories** implementing kernel extension virtual machines, their admission checks and JITs, or tools that specify, verify, optimize, and test those components. The core is BPF/eBPF, with DTrace DIF and kernel Lua providing alternative designs. Embedded operating-system VMs and off-kernel verification infrastructure are included where their connection is explicit. General hypervisors, ordinary eBPF applications, and generic static-analysis frameworks without a concrete connection to these VMs are outside the scope.

Each numbered heading identifies one repository; large operating-system trees count once. The linked implementation files and design documents within each entry are suggested reading entry points. Criterion assignments are engineering judgments grounded in those sources, not certifications of correctness or security.

## Criteria

- **C1 — Difficult correctness:** invariants, concurrency, arithmetic semantics, adversarial programs, or failure handling are central to the implementation.
- **C2 — Reusable abstractions:** substantial interfaces, intermediate representations, semantic models, or runtime mechanisms support multiple uses.
- **C3 — Performance with structure:** execution or analysis costs are addressed through identifiable architectural mechanisms.
- **C4 — Sustained evolution:** years of change accompanied by compatibility, testing, or complexity-management evidence. Age, stars, and recent pushes alone do not qualify.

## Kernel and embedded runtimes

### 1. [torvalds/linux](https://github.com/torvalds/linux)

**Language / role:** C and architecture-specific assembly; the BPF interpreter, verifier, maps, helpers, and native JITs within the Linux monorepo.

This is the central study target for the contract between untrusted bytecode, a static admission checker, and privileged execution. Focus on the BPF subsystem rather than attempting to treat the whole kernel as one VM implementation.

- **C1:** The [verifier documentation](https://github.com/torvalds/linux/blob/master/Documentation/bpf/verifier.rst) explains pointer provenance, signed and unsigned bounds, tracked unknown bits, stack initialization, pointer spills, nullable references, and reference release obligations. Packet bounds established on one pointer can affect related pointers, making alias identities and state refinement particularly instructive.
- **C2 and C3:** The [BPF design Q&A](https://github.com/torvalds/linux/blob/master/Documentation/bpf/bpf_design_QA.rst) explains why the register and C calling convention, typed helper calls, and maps form the extension interface, and how that convention supports efficient native calls after JIT compilation. These mechanisms serve networking, tracing, and security hooks.

Some answers in the design Q&A preserve historical limitations; do not use its loop discussion as a current feature matrix. The value here is the documented architectural reasoning.

### 2. [microsoft/ebpf-for-windows](https://github.com/microsoft/ebpf-for-windows)

**Language / role:** C/C++; Windows kernel hosting, verification integration, maps, extension interfaces, and native eBPF compilation.

Study how a VM ecosystem is adapted to a different kernel and code-integrity model. Its Windows hosting and compilation machinery is substantive even though PREVAIL and uBPF are reused dependencies.

- **C1:** [Epoch-based memory management](https://github.com/microsoft/ebpf-for-windows/blob/main/docs/EpochBasedMemoryManagement.md) specifies ownership of per-CPU state, deferred reclamation, participant enter/exit, and forwarding an exit to the original CPU when a thread migrates. The distinction between globally published epochs and per-CPU cached epochs exposes concrete lifetime and concurrency invariants.
- **C2:** [Native code generation](https://github.com/microsoft/ebpf-for-windows/blob/main/docs/NativeCodeGeneration.md) separates ELF verification, instruction-to-C translation, native compilation, driver linking, and signing. Metadata tables and the Network Module Registrar connect compiled programs to maps and helpers. This is a reusable deployment pipeline for several program types, with HVCI compatibility shaping its architecture.

The native-generation document explicitly marks some BTF function-import structures as proposals; those portions should not be mistaken for the implemented interface.

### 3. [NetBSD/src](https://github.com/NetBSD/src)

**Language / role:** C and Lua; classic BPF JIT and kernel Lua facilities in the NetBSD source tree. **Official automatic CVS conversion mirror:** the repository warns that commit links can change and directs development to NetBSD infrastructure.

This offers both a smaller packet-filter VM and a general scripting runtime in one operating-system context.

- **C1:** [`sys/net/bpfjit.c`](https://github.com/NetBSD/src/blob/trunk/sys/net/bpfjit.c) checks allocation-size overflow, terminal return encoding, initialization requirements, and compatibility with the interpreter's acceptance rules. Its treatment of preinitialized external memory and A/X register initialization is a useful example of preserving interpreter semantics through compilation.
- **C3:** The same implementation divides instructions into basic blocks, computes initialization masks and code-generation hints, and emits native code through SLJIT. These explicit passes connect safety analysis to reduced execution work.
- **C2:** [`sys/modules/lua/lua.c`](https://github.com/NetBSD/src/blob/trunk/sys/modules/lua/lua.c) supplies a separate study path: named Lua states, module management, locked state queues, and controls over bytecode loading and instruction counts. It is an in-kernel scripting facility, not an eBPF-style static verifier.

### 4. [illumos/illumos-gate](https://github.com/illumos/illumos-gate)

**Language / role:** C; DTrace's DIF bytecode validator and interpreter within illumos. **Official read-only mirror:** the repository identifies `code.illumos.org` as the authoritative repository.

DTrace is a useful counterpoint to eBPF: inspect how a purpose-built tracing instruction set divides work between load-time validation and fault-aware execution.

- **C1:** [`dtrace.c`](https://github.com/illumos/illumos-gate/blob/master/usr/src/uts/common/dtrace/dtrace.c) contains `dtrace_difo_validate` and `dtrace_dif_emulate`. Validation constrains opcodes, register references, reserved bits, final returns, and forward-only branch targets; interpretation handles runtime faults such as division by zero through per-CPU fault state.
- **C2:** [`sys/dtrace.h`](https://github.com/illumos/illumos-gate/blob/master/usr/src/uts/common/sys/dtrace.h) defines the DIF instruction representation, integer and tuple registers, probe identities, and tracing interfaces. A common bytecode format represents predicates and actions bound to different providers, separating the tracing language from individual instrumentation sources.

These are subsystem entry points; this selection does not assess unrelated illumos components.

### 5. [luainkernel/lunatik](https://github.com/luainkernel/lunatik)

**Language / role:** C, Lua, and shell tooling; Lua runtime environments and bindings for scripting the Linux kernel.

Study the difficult boundary between a garbage-collected language and kernel object lifetimes, execution contexts, and module unloading. Its purpose is broader kernel scripting; inclusion does not imply the same untrusted-program security model as eBPF.

- **C1:** The [C API](https://github.com/luainkernel/lunatik/blob/master/doc/capi.md) specifies reference counts, object closure, module ownership, and deferred release when final reference drops occur in atomic context. Softirq and hardirq classes select atomic allocation and appropriate spinlock behavior, while process-context objects use different locking and allocation rules.
- **C2:** The same API defines reusable object classes and monitored methods, allowing bindings to expose kernel facilities through a shared lifecycle mechanism. The [integration-test guide](https://github.com/luainkernel/lunatik/blob/master/tests/README.md) makes the breadth concrete: map operations, sockets, probes, runtime management, and kernel/userspace interoperability receive behavior-specific tests in KTAP format.

### 6. [future-proof-iot/Femto-Container](https://github.com/future-proof-iot/Femto-Container)

**Language / role:** C with Python tooling; an eBPF-derived VM for embedded software modules. **Historical research implementation:** the README calls the API unstable, and repository metadata records its latest push in April 2022.

This is the embedded-OS edge of the category. The authors' [Femto-Containers paper](https://arxiv.org/abs/2106.12553) explicitly describes RIOT integration and evaluation on Arm Cortex-M, ESP32, and RISC-V. It provides a compact implementation to compare with the much larger Linux runtime.

- **C1 and C3:** [`src/jumptable.c`](https://github.com/future-proof-iot/Femto-Container/blob/main/src/jumptable.c) combines read/write region checks with a computed-goto instruction dispatcher and macros for related 32-bit and 64-bit operations. This exposes the cost and correctness tradeoff of dynamic isolation on constrained processors; it is not evidence that all safety properties have been proved.
- **C2:** [`src/bpf.c`](https://github.com/future-proof-iot/Femto-Container/blob/main/src/bpf.c) separates VM setup and execution from a region abstraction covering stack, writable data, read-only data, context, and additional host-supplied memory. Different applications can supply their own context and permitted regions without changing instruction dispatch.

### 7. [iovisor/ubpf](https://github.com/iovisor/ubpf)

**Language / role:** C; embeddable userspace eBPF interpreter and JIT infrastructure, also reused by the Windows eBPF ecosystem.

This is explicitly an off-kernel companion, included for its runtime/verifier integration and direct reuse in kernel VM tooling. Count this implementation once, not again through repositories that vendor it.

- **C1:** [Using verified programs](https://github.com/iovisor/ubpf/blob/main/docs/VerifiedPrograms.md) documents a concrete integration hazard: a verifier can assume a non-null, structured context in `r1`, while a runtime caller supplies no context. Acceptance is meaningful only when runtime inputs satisfy the verifier's assumptions.
- **C2:** The [public VM API](https://github.com/iovisor/ubpf/blob/main/vm/inc/ubpf.h) exposes VM lifecycle, interpreter/JIT execution, configurable stack and call limits, external-stack JIT entry points, and execution profiles. It provides a clear place to study how an embeddable execution engine exposes safety choices and host responsibilities.

## Static analysis, formal semantics, and verified compilation

### 8. [vbpf/prevail](https://github.com/vbpf/prevail)

**Language / role:** C++; PREVAIL, an abstract-interpretation-based eBPF verifier. This is the canonical repository, including references that still use the former `ebpf-verifier` name.

Study how pointer types, relational numeric facts, and byte-addressed stack state are combined into a reusable analyzer, with a distinct pipeline from the Linux verifier.

- **C1:** [`EbpfDomain`](https://github.com/vbpf/prevail/blob/main/src/crab/ebpf_domain.hpp) couples type/numeric state with an optional stack domain and explicitly documents their shared bottom-state invariant. It also handles overlapping stack byte ranges, pointer offsets, map dimensions, and loop-counter bounds.
- **C2 and C3:** The [architecture document](https://github.com/vbpf/prevail/blob/main/docs/architecture.md) separates ELF decoding, control-flow construction, instruction transformers, assertion checking, and result generation. Weak topological ordering and widening/narrowing organize fixpoint computation, while explicit assertions separate safety properties from transfer semantics.

The [changelog](https://github.com/vbpf/prevail/blob/main/CHANGELOG.md) documents concrete soundness repairs, including ALU32/JMP32 width mismatches and stale type-dependent facts. Those repairs are valuable study material, not a reason to assume every current operator is sound.

### 9. [bpfverif/agni](https://github.com/bpfverif/agni)

**Language / role:** Python, C++/LLVM infrastructure, and SMT; automated checking of the Linux eBPF verifier's value-tracking analysis.

Agni checks the analyzer rather than merely submitting programs to it. Its scope is arithmetic and branch-related abstract operators and domain synchronization, not a proof of the whole kernel verifier.

- **C1:** [`wf_soundness.py`](https://github.com/bpfverif/agni/blob/main/bpf-verification/src/wf_soundness.py) constructs concrete and abstract register states, constrains concrete inputs to lie within abstract bounds, relates 32-bit views to 64-bit values, and searches for violated output properties. This makes abstract-operator soundness a concrete solver obligation.
- **C2:** The [project workflow](https://github.com/bpfverif/agni/blob/main/README.md) separates extraction of SMT encodings from kernel C/LLVM, modular operator checking, and counterexample-program synthesis. Its configurable instruction sets and kernel-commit inputs let the same machinery investigate multiple operators and kernel revisions; the documented `BPF_SYNC` step matters because cross-domain refinement is part of the contract.

### 10. [uw-unsat/jitterbug](https://github.com/uw-unsat/jitterbug)

**Language / role:** Racket/Rosette specifications, C JIT implementations, and SMT; formal checking and synthesis for Linux BPF JITs. **Historical research tool:** repository metadata records the latest push in July 2023.

Read this for the difference between proving bytecode safe and proving that native code implements that bytecode. The repository's [project description](https://github.com/uw-unsat/jitterbug/blob/master/README.md) connects the tool to RISC-V, Arm, and x86 JIT fixes and optimizations.

- **C1:** [`per-insn.rkt`](https://github.com/uw-unsat/jitterbug/blob/master/racket/lib/spec/per-insn.rkt) checks live-register agreement, memory traces, tail-call counts, target invariants, and the mapping between BPF and native program counters. It separately checks that unresolved call addresses do not change emitted-code length and invalidate branch offsets.
- **C2 and C3:** Its target descriptor abstracts instruction emission, target execution, register mapping, stack usage, and architecture invariants. The documented synthesis workflow reuses that contract to search for RV32 instruction sequences, connecting correctness specifications to native-code optimization.

Proof results apply to the modeled targets, assumptions, and versions—not automatically to today's entire Linux JIT collection.

### 11. [uw-unsat/serval](https://github.com/uw-unsat/serval)

**Language / role:** Racket/Rosette; reusable symbolic execution and specification infrastructure used by BPF JIT verification. **Historical research framework:** metadata records the latest push in April 2022, despite older documentation describing this branch as actively developed.

Serval merits a separate entry from Jitterbug because it supplies general machine semantics, memory abstractions, and proof interfaces; Jitterbug supplies the specialized JIT correctness obligations.

- **C1:** [`serval/bpf.rkt`](https://github.com/uw-unsat/serval/blob/master/serval/bpf.rkt) models the BPF CPU, registers, program counter, call state, tail-call count, and memory-manager interface. These state components make instruction-level reasoning sensitive to more than the final return value.
- **C2:** The [framework guide](https://github.com/uw-unsat/serval/blob/master/serval/guide/scribble/serval.scrbl) documents reusable overflow predicates, disjoint memory blocks, bug conditions, refinement, noninterference, and symbolic case splitting. BPF, RISC-V, x86, and LLVM semantics can share those facilities.

The tutorial and SOSP artifact snapshots are not counted as additional projects.

### 12. [future-proof-iot/CertFC](https://github.com/future-proof-iot/CertFC)

**Language / role:** Coq/Rocq and C; CertrBPF's verified embedded rBPF verifier and interpreter. **Historical research artifact:** metadata records the latest push in September 2022.

This complements Femto-Container with a mechanized refinement development rather than another ordinary copy of its runtime. Study how executable semantics, an extraction-oriented model, and a CompCert Clight implementation are related.

- **C1:** [`isolation/Isolation1.v`](https://github.com/future-proof-iot/CertFC/blob/master/isolation/Isolation1.v) proves preservation of register and memory invariants through interpreter steps. It also exposes explicit axioms about external calls preserving invariants: those host-call assumptions are part of the trusted boundary and should accompany any safety claim.
- **C2:** The [architecture and proof workflow](https://github.com/future-proof-iot/CertFC/blob/master/README.md) separates syntax/semantics, verifier invariants, optimized synthesis models, extraction, equivalence proofs, and implementation simulation. Its small Clight logic and decomposition into isolation, equivalence, and simulation make the proof infrastructure useful beyond reading one interpreter loop.

The proof applies to the represented embedded ISA and environment assumptions, not the full contemporary Linux helper and program-type ecosystem.

### 13. [OpenSourceVerif/linux-ebpf-semantics](https://github.com/OpenSourceVerif/linux-ebpf-semantics)

**Language / role:** Rocq/Coq with an OCaml validation frontend; mechanized semantics and trace validation for the Linux eBPF core ISA. Research code, not an in-kernel admission checker.

This newer project is useful for understanding where an ISA's mathematical model must specify details that host C arithmetic or informal prose can obscure.

- **C1:** [`ebpfBinSem.v`](https://github.com/OpenSourceVerif/linux-ebpf-semantics/blob/main/theories/ebpfBinSem.v) explicitly models 32/64-bit operand interpretation, division by zero, signed minimum divided by minus one, modulo behavior, and masked shifts. Its immediate-shift discussion records an assumption supplied by Linux's verifier.
- **C2:** The [theory layout](https://github.com/OpenSourceVerif/linux-ebpf-semantics/blob/main/theories/README.md) separates reusable syntax, state, decoding, and semantics from interpreter validation and OCaml extraction. The repository describes checking traces from Linux BPF selftests against the reference interpreter. Auxiliary concurrency modules are built but explicitly are not dependencies of that extracted validator; this distinction limits what validation results establish.

### 14. [smartnic/superopt](https://github.com/smartnic/superopt)

**Language / role:** C++ and Z3; the K2 eBPF superoptimizer implementation. **Historical research code:** metadata records the latest push in June 2023.

Study an optimizer whose search must respect both program behavior and the safety constraints of kernel extensions. The separate SIGCOMM artifact is supporting documentation, not an additional selected repository.

- **C1:** [`src/verify/validator.cc`](https://github.com/smartnic/superopt/blob/master/src/verify/validator.cc) checks candidate safety before equivalence, constructs shared-input constraints, extracts counterexamples, and distinguishes solver `unknown` from a successful proof. It also exposes implementation limitations, such as special handling of pointer-valued outputs.
- **C3:** The validator supports bounded optimization windows, canonicalized equivalence caches, and counterexample reuse to reduce solver work. The authors' [artifact guide](https://github.com/smartnic/sigcomm21_artifact/blob/master/README.md) connects those mechanisms to stochastic search, instruction-count optimization, and experiments on kernel/Cilium packet-processing programs.

No published speedup is generalized here; the interesting engineering is how expensive proof checks are integrated into a search loop.

## Conformance, fuzzing, and independent oracles

### 15. [Alan-Jowett/bpf_conformance](https://github.com/Alan-Jowett/bpf_conformance)

**Language / role:** C++ and assembly-like test data; cross-implementation BPF ISA conformance testing.

This is a compact way to study whether runtimes agree about the meaning of an instruction. Conformance results are distinct from memory-safety verification.

- **C1:** The [high-divisor regression](https://github.com/Alan-Jowett/bpf_conformance/blob/main/tests/div32-high-divisor.data) distinguishes 32-bit operand truncation from an incorrect 64-bit division: a divisor with nonzero high bits must still yield the specified 32-bit result. The surrounding corpus exercises shifts, endianness, overflow, memory operations, and exceptional arithmetic.
- **C2:** The [runner/plugin protocol](https://github.com/Alan-Jowett/bpf_conformance/blob/main/README.md) passes bytecode or ELF and initial memory to an external process and collects either `r0` or an execution error. Its plugin and static-library interfaces support Linux, uBPF, Windows/bpf2c, rbpf, and other engines without embedding every engine into the harness.

The project's use of Linux as a reference is a testing policy, not proof that Linux or every passing implementation is correct in all contexts.

### 16. [google/buzzer](https://github.com/google/buzzer)

**Language / role:** Go with native syscall/FFI support; a strategy-oriented Linux eBPF fuzzing toolchain.

Study how to make the oracle more informative than a kernel crash. Buzzer can compare the verifier's reported register assumptions with values observed during execution.

- **C1:** The [architecture document](https://github.com/google/buzzer/blob/main/docs/architecture/architecture.md) describes a verifier-log strategy that records runtime register values and checks them against abstract predictions, plus a pointer-arithmetic strategy probing map-access behavior. These target disagreement between accepted abstract states and actual execution.
- **C2:** The same design separates control, instruction generation, kernel execution, strategy interfaces, and coverage metrics. New generation and detection policies can share syscall handling and observability. The [project README](https://github.com/google/buzzer/blob/main/README.md) links specific verifier bug reports attributable to the framework, providing concrete context for the architecture.

The generic framework is the selection target; individual vulnerability demonstrations are not separate entries.

### 17. [trusslab/brf](https://github.com/trusslab/brf)

**Language / role:** Go and C; BPF Runtime Fuzzer, a substantive Syzkaller-based research implementation. **Historical artifact:** metadata records the latest push in May 2024.

BRF addresses the difficulty of reaching the runtime at all: random programs often fail verification or never get attached and triggered. Its modifications are the reason to retain it separately from generic Syzkaller.

- **C1:** The [project description](https://github.com/trusslab/brf/blob/dev/README.md) explains semantic- and dependency-aware generation for components protected by the verifier. The goal includes creating the prerequisite kernel objects and trigger syscalls, not simply mutating instruction bytes.
- **C2:** [`prog/brf.go`](https://github.com/trusslab/brf/blob/dev/prog/brf.go) maintains helper, program-type, and context-access descriptions and composes open, load, attach, and test-run calls. Its generation/mutation pipeline explicitly repairs reference and spinlock usage. These shared descriptions and lifecycle steps support different BPF program types and fuzzing inputs.

This is version-sensitive research infrastructure; its setup documentation does not establish turnkey support for every current kernel.

### 18. [blocksecteam/BpfChecker](https://github.com/blocksecteam/BpfChecker)

**Language / role:** C++ and Rust; differential-testing infrastructure for eBPF runtimes. **CCS 2024 research artifact:** metadata records the latest push in December 2024.

This is an adjacent toolchain entry: the project includes an instrumented Windows/uBPF VM path, while the documented demo targets Solana rBPF. It is useful for studying transferable runtime-testing machinery, not as evidence that Solana is an in-kernel VM.

- **C1:** The [project description](https://github.com/blocksecteam/BpfChecker/blob/main/README.md) defines the interpreter/JIT differential-testing target. Inspection of [`ubpf_runner/runner_fuzzer.cpp`](https://github.com/blocksecteam/BpfChecker/blob/main/ubpf_runner/runner_fuzzer.cpp) reveals a material limitation: that path runs verification and both execution modes but comments out its result-comparison checks. Do not assume every bundled runner has the advertised differential oracle enabled.
- **C2:** [`bpf_ir/ir/BasicBlock.h`](https://github.com/blocksecteam/BpfChecker/blob/main/bpf_ir/ir/BasicBlock.h) models mutable instruction sequences, explicit terminators, successors, and address calibration before branch offsets are emitted. That IR underpins reusable generation and mutation across runtime targets instead of relying solely on unconstrained byte mutation.

### 19. [rs3lab/veritas](https://github.com/rs3lab/veritas)

**Language / role:** Dafny, Go, C/C++; Beacon fuzzing and the SpecCheck specification-based oracle for Linux's eBPF verifier.

Study how to compare verifier decisions with an independently expressed safety model, including programs the kernel rejects. This is research infrastructure with a modified Syzkaller component, not a replacement kernel verifier.

- **C1:** [`ebpf-dafny-spec/spec.dfy`](https://github.com/rs3lab/veritas/blob/master/ebpf-dafny-spec/spec.dfy) models register types, stack slots, pointer metadata, contexts, maps, arithmetic, and operation preconditions/postconditions. It contains axiomatized ghost methods and documented unfinished questions; the specification is an oracle with assumptions, not itself a proof that Linux implements every modeled rule.
- **C2 and C3:** The [architecture and evaluation guide](https://github.com/rs3lab/veritas/blob/master/readme.md) separates generation, translation of a concrete BPF program into Dafny, safety checking, and comparison with the kernel. It also exposes experiments for state sampling and per-stage verification cost, making oracle throughput an explicit design concern.

The documented evaluation is resource-intensive and nondeterministic. No experiments were rerun for this report, and the reported performance is not independently confirmed here.

## Search coverage and limitations

Discovery used more than six distinct live-web query formulations, including abstract-interpretation eBPF verifiers; BPF JIT refinement and synthesis; verifier range/tnum soundness; differential fuzzing and runtime reachability; ISA conformance; Coq/Rocq interpreter proofs; eBPF superoptimization; NetBSD BPF JIT and kernel Lua; DTrace DIF; and in-kernel WebAssembly. Follow-up searches for newer formal semantics and Rust verification led to the Rocq semantics repository and cross-runtime testing work. Later searches increasingly returned the same verifier/fuzzer families, generic eBPF applications, or much less complete prototypes.

Canonical URLs, branches, archive flags, and historical push dates were checked through GitHub repository pages or the GitHub API. Each selected repository received an additional opened primary-source inspection, including substantive code or architectural documentation. No selected repository was marked archived at inspection; this does not establish active maintenance. Historical push dates above describe metadata only. C4 was deliberately not awarded merely because a repository is old or has tests; the entries qualify through the more directly inspected C1–C3 evidence.

Coverage includes classic BPF and eBPF, DTrace DIF, Lua, embedded Arm/ESP32/RISC-V deployments, and JIT reasoning for multiple native architectures. The implementation and specification languages include C, C++, Lua, Go, Rust, Python, Racket/Rosette, Rocq/Coq, OCaml, and Dafny. Production kernel subsystems and small research tools are intentionally distinguished.

Important exclusions and boundaries:

- General KVM/Xen-style hardware virtualization and generic proof assistants are outside this category. Ordinary loaders, observability products, networking applications, and tutorial repositories were not added merely for using eBPF.
- PREVAIL forks, copied Linux trees, Serval tutorial/artifact snapshots, and the K2 packaging repository were not counted as independent implementations. Jitterbug/Serval and Femto-Container/CertFC remain separate because they contain different substantive runtime, specification, or proof infrastructure.
- The inspected [kernel-wasm prototype](https://github.com/wasmerio/kernel-wasm) was not retained: its repository documents incomplete functionality and unresolved security review, and metadata records a last push in February 2020. The search therefore does not claim broad coverage of production kernel WebAssembly runtimes.
- Off-kernel uBPF and BpfChecker are explicitly bounded companion entries. Most verification tooling runs outside the kernel; inclusion depends on the runtime, verifier, or ISA it investigates, not the process in which the tool itself executes.
- This was read-only research. No candidate code was run, dependencies installed, benchmark reproduced, or formal development rechecked. In particular, axioms, host-call contracts, supported instruction subsets, and historical kernel versions limit proof and testing claims. The report is a selection guide to concrete engineering problems, not a claim that every component is uniformly exemplary.
