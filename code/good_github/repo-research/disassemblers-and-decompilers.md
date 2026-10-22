# Disassemblers and decompilers

Research date: **2026-10-09**.

This selection covers **27 GitHub repositories** implementing machine-instruction decoding, disassembly and semantic lifting, native-code decompilation, or bytecode-to-source reconstruction. It includes reusable engines, complete analysis platforms, and specialist embedded, GPU, and virtual-machine implementations. In larger repositories, the relevant subsystem is identified. The linked implementation files and technical documents are suggested starting points for study.

The criteria describe engineering substance, not a guarantee that recovered source is correct or that every component is exemplary. Statements about what an engineer can learn are grounded assessments of the cited implementations. No candidate code was executed, and project benchmark claims were not independently reproduced. Links generally follow the default development branch inspected on the research date, which can differ from a released version.

**Criteria legend**

- **C1:** Difficult correctness involving invariants, concurrency, numerical semantics, adversarial input, or failure handling.
- **C2:** Substantial reusable abstractions supporting multiple architectures, consumers, or analysis tasks.
- **C3:** Concrete performance or resource constraints addressed through understandable architectural choices.
- **C4:** Sustained evolution supported by compatibility work, testing, or deliberate complexity management; repository age alone does not qualify.

## Native decompilers and binary-analysis platforms

### 1. [NationalSecurityAgency/ghidra](https://github.com/NationalSecurityAgency/ghidra)

**Language/role:** Java and C++; integrated disassembler and native decompiler, with SLEIGH processor specifications.

Study the boundary between processor semantics and architecture-independent analysis, particularly the C++ decompiler under `Ghidra/Features/Decompiler`. This is a large-system example of making a common analysis engine work across different register layouts, address spaces, and instruction sets.

- **C1:** P-code makes operand sizes, overlapping storage, signed versus unsigned interpretation, and instruction effects explicit. These are necessary semantic distinctions when translating machine operations into higher-level expressions. The [SLEIGH and P-code specification](https://ghidra.re/ghidra_docs/languages/html/sleigh.html) explains those invariants rather than merely listing supported CPUs.
- **C2:** `ArchitectureCapability` provides executable-format recognition and construction hooks; `Architecture` owns the loader, translator, symbols, and output-language components for a processor/compiler combination. The [architecture interfaces](https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/Features/Decompiler/src/decompile/cpp/architecture.hh) expose the extension boundaries clearly.

### 2. [radareorg/radare2](https://github.com/radareorg/radare2)

**Language/role:** C; command-line reverse-engineering framework with extensive disassembly and instruction-analysis support.

The useful study target is the architecture-plugin/session layer, rather than treating every external decompiler plugin as part of this repository. Its interfaces reveal how a command-oriented application can expose low-level machinery to many callers.

- **C2:** `RArchPlugin` supplies decoding, encoding, register descriptions, lifecycle callbacks, and semantic integration, while `RArchSession` holds configuration and plugin-specific state. The [architecture header](https://github.com/radareorg/radare2/blob/master/libr/include/r_arch.h) separates reusable architecture services from the interactive shell.
- **C3:** The same header's decode masks let callers request basic operation information, disassembly text, operands, or ESIL semantics selectively. Stateful cross-instruction decoding is an explicit option excluded from the ordinary all-fields mask. This makes both analysis cost and state requirements visible in the API.
- **C1:** The [regression-test guide](https://github.com/radareorg/radare2/blob/master/test/README.md) specifies instruction-byte/assembly checks, including endianness and expected-broken cases, alongside unit and fuzzing infrastructure. These are concrete mechanisms for managing decoder correctness across architectures.

### 3. [rizinorg/rizin](https://github.com/rizinorg/rizin)

**Language/role:** C; disassembly and binary-analysis framework, originating as a radare2 fork.

Retained separately because RzIL is substantive architectural evolution, not a repackaged interface. Study how a C implementation introduces stronger semantic structure while retaining an extensible analysis platform.

- **C1:** RzIL distinguishes statically typed intermediate-language values, pure expressions, and state-changing effects. Its design discusses bitvector widths, concatenation, and the limits of enforcing those rules in C. This directly addresses ambiguity in the earlier ESIL representation. See the [RzIL design document](https://github.com/rizinorg/rizin/blob/dev/doc/rzil.md).
- **C2:** The same document defines a shared expression/effect vocabulary and VM state made of variables and memories. Processor-specific lifting can therefore feed common semantic consumers. It also explains which ideas were adapted from BAP Core Theory and where the implementation deliberately differs.

The [repository overview](https://github.com/rizinorg/rizin/blob/dev/README.md) confirms the fork provenance and native/bytecode disassembly scope. Neither Rizin nor radare2 is counted through its GUI or language bindings again.

### 4. [angr/angr](https://github.com/angr/angr)

**Language/role:** Primarily Python; binary-analysis platform with a native-code decompiler.

Focus on `angr/analyses/decompiler` and its AIL pipeline. It is especially useful for studying how decompilation composes existing analyses instead of implementing an isolated byte-to-text transformation.

- **C1:** The documented pipeline deals with indirect branches and jump tables, stack-pointer values, calling conventions, reaching definitions, variable recovery, and type constraints before structuring control flow. Each addresses information absent from raw instruction text. See the [decompiler analysis-pass guide](https://docs.angr.io/en/latest/analyses/decompiler.html).
- **C2:** Block-level AIL simplification, whole-function simplification, call-site construction, region identification, and code generation are separate stages. The same guide maps the responsibilities and dependencies, making this a useful example of reusable analyses feeding a higher-level consumer.

The [repository overview](https://github.com/angr/angr/blob/master/README.md) explicitly includes disassembly, lifting, and decompilation; inclusion is not based solely on angr's symbolic-execution capabilities.

### 5. [uxmal/reko](https://github.com/uxmal/reko)

**Language/role:** C#; retargetable native executable decompiler, available through front ends and a .NET API.

Study how processor, operating-environment, and executable-format knowledge are kept outside the central analysis pipeline. Reko offers a useful managed-language comparison with Ghidra and LLVM-based decompilers.

- **C1:** The [decompilation-process guide](https://github.com/uxmal/reko/blob/master/doc/guide/reko.md) explains recursive scanning, instruction-to-RTL translation, control-flow construction, and the failure to discover code behind unresolved indirect transfers. It explicitly distinguishes heuristic recovery from information established by traversal.
- **C2:** The [design documentation](https://github.com/uxmal/reko/wiki/Design) separates loaders, processor architectures, platforms, the loaded program model, and later analysis. Architecture-specific endianness and instruction rewriting are abstracted behind those components rather than embedded throughout the core.

The design wiki is older documentation; it is most useful as a conceptual map, not as installation guidance for current releases.

### 6. [avast/retdec](https://github.com/avast/retdec)

**Language/role:** C++; LLVM-based retargetable machine-code decompiler.

Study the conversion between executable addresses, decoded machine instructions, LLVM blocks, and high-level output. This is the original Avast repository; similarly named downstream projects are not treated as the same implementation.

- **C1:** The [library implementation](https://github.com/avast/retdec/blob/master/src/retdec/retdec.cpp) verifies a newly created LLVM module before pass initialization and reconstructs machine-level edges across synthetic IR blocks. Its explicit MIPS delay-slot and ARM conditional-transfer handling illustrates why an IR graph cannot simply be mistaken for the original instruction graph.
- **C2:** That implementation connects decoding, configuration providers, and `llvmir2hll` behind a library interface. The [changelog](https://github.com/avast/retdec/blob/master/CHANGELOG.md) documents the v5 transition from script orchestration to an embeddable library.
- **C4:** The changelog covers releases from 2017 through 2022 and subsequent development fixes, with linked regressions for damaged executable files, decoder changes, compiler compatibility, and dependency migrations. This supports historical evolution without implying a rapid current release cadence.

### 7. [BoomerangDecompiler/boomerang](https://github.com/BoomerangDecompiler/boomerang)

**Language/role:** C++; native-code-to-C decompiler; historical continuation of the original Boomerang project.

Useful for studying an explicit pass-oriented decompiler with procedure-level state, SSA transformations, and interprocedural recursion. The repository describes itself as a fork of the earlier SourceForge implementation.

- **C1:** [`ProcDecompiler.cpp`](https://github.com/BoomerangDecompiler/boomerang/blob/develop/src/boomerang/decomp/ProcDecompiler.cpp) tracks procedure status, prevents repeated traversal of already decompiled procedures, and handles callees discovered only after further analysis. Call-graph cycles and changing information make ordering part of correctness.
- **C2:** [`PassManager.cpp`](https://github.com/BoomerangDecompiler/boomerang/blob/develop/src/boomerang/passes/PassManager.cpp) registers dedicated passes for dominators, phi placement, renaming, call arguments, stack-pointer preservation, type analysis, and leaving SSA. These provide an accessible map of reusable compiler-style machinery applied in reverse.

**Status:** Historical study candidate. [GitHub metadata](https://api.github.com/repos/BoomerangDecompiler/boomerang) reported the last push in December 2020 and `archived: false`; that is not evidence of active maintenance.

### 8. [revng/revng](https://github.com/revng/revng)

**Language/role:** C++ and Python; LLVM/QEMU-based binary-analysis and decompilation framework.

Study incremental code discovery and the separation between analysis models and generated artifacts. The code-discovery explanation is unusually concrete about why apparently local CFG changes require reanalysis.

- **C1:** The [code-discovery design](https://docs.rev.ng/developer-manual/code-discovery/) explains the mutual dependency between lifting and indirect-branch resolution. It tracks newly found targets, growing successor sets, and invalidation caused by newly recognized non-returning calls, with a termination argument based on bounded monotone changes.
- **C3:** Expensive value analysis runs over a backward-expanded region of changed code instead of repeatedly processing the entire program. The same document explains the scope and the need to preserve calling context.
- **C2:** The [pipeline reference](https://docs.rev.ng/references/pipeline/) separates transforming pipes, cached savepoints, containers, model-refining analyses, and requested artifacts. Disassembly, CFGs, and C output share earlier work through explicit pipeline branches.

### 9. [cea-sec/miasm](https://github.com/cea-sec/miasm)

**Language/role:** Python with native support components; multiarchitecture assembler/disassembler and semantic-analysis framework.

Miasm belongs here through its decoding and instruction-semantics implementation; it should not be mistaken for a complete C-source decompiler. Study the transition from machine instructions to expressions and parallel assignments.

- **C1:** [`AssignBlock` in the IR implementation](https://github.com/cea-sec/miasm/blob/master/miasm/ir/ir.py) models simultaneous assignments, checks source/destination widths, expands partial-register writes, and rejects overlapping concurrent writes to the same bits. This preserves semantics such as register exchange that sequential assignments would change.
- **C2:** The [technical examples](https://github.com/cea-sec/miasm/blob/master/README.md) show the `Machine` abstraction selecting decoders and lifters, with shared IR consumed by read/write analysis, emulation, and symbolic execution. The same representation supports several analysis tasks after disassembly.

### 10. [BinaryAnalysisPlatform/bap](https://github.com/BinaryAnalysisPlatform/bap)

**Language/role:** OCaml with native backends; disassembly, semantic lifting, and binary-analysis infrastructure.

The relevant subsystem is `lib/bap_disasm`. BAP is an informative contrast to C APIs because its interfaces express capability and state constraints in types.

- **C1:** The [basic disassembler interface](https://github.com/BinaryAnalysisPlatform/bap/blob/master/lib/bap_disasm/bap_disasm_basic.mli) parameterizes instructions by available assembly and classification information. Accessors require the corresponding capability, while decoding exposes invalid-input callbacks and typed errors. The [recursive disassembler interface](https://github.com/BinaryAnalysisPlatform/bap/blob/master/lib/bap_disasm/bap_disasm_rec.mli) distinguishes disassembly failures from lifting failures.
- **C2:** Those interfaces support registered backends, custom decoders, stateful stepping and jumping, configurable branch/root discovery, and reusable CFG output. The repository's `disassemble`, `objdump`, and `mc` tools are different consumers of that infrastructure.

## Instruction-decoding libraries and specialist disassemblers

### 11. [capstone-engine/capstone](https://github.com/capstone-engine/capstone)

**Language/role:** C with many bindings; architecture-neutral instruction-disassembly engine.

Study the boundary between upstream-derived instruction machinery and a stable consumer-facing representation. The inspected `next` branch includes newer architecture and testing work that may differ from stable releases.

- **C2:** The [architecture document](https://github.com/capstone-engine/capstone/blob/next/docs/ARCHITECTURE.md) separates LLVM-derived decoding from mapping into `cs_insn`. The mapping layer supplies Capstone identifiers, operand forms, and access details while hiding the decoder's `MCInst` representation.
- **C1:** The [testing guide](https://github.com/capstone-engine/capstone/blob/next/tests/README.md) distinguishes YAML checks of instruction text and operand details from older crash-only tests. It also explains limitations when importing LLVM cases with different CPU-feature settings; the existence of tests is not presented as complete coverage.
- **C4:** The [changelog](https://github.com/capstone-engine/capstone/blob/next/ChangeLog) spans releases from 2014 onward and records API migrations, a RISC-V compatibility macro, operand-width corrections, and sanitizer-related fixes. This is concrete evidence of evolution and compatibility management.

### 12. [zyantific/zydis](https://github.com/zyantific/zydis)

**Language/role:** C; x86/x86-64 decoder, formatter, and encoder library.

Study the API design for callers that need instruction boundaries, full operands, or re-encoding at different costs.

- **C1:** The [decoder API](https://github.com/zyantific/zydis/blob/master/include/Zydis/Decoder.h) makes input-buffer length and operand-array capacity explicit. The [re-encoding fuzz target](https://github.com/zyantific/zydis/blob/master/tools/ZydisFuzzReEncoding.c) exercises decoding followed by conversion into an encoder request across machine and decoder modes.
- **C2:** Instruction decoding and operand decoding can be invoked separately or combined, giving instrumentation, disassembly, and code-generation clients a shared decoded-instruction model.
- **C3:** The repository documents allocation-free operation; the decoder interface supports that with caller-provided instruction and operand storage and optional operand work. This is a concrete resource-control design, not a reproduced throughput ranking.

### 13. [icedland/iced](https://github.com/icedland/iced)

**Language/role:** Rust, C#, and Java implementations plus bindings; x86/x64 decoding, formatting, and encoding.

Study the Rust decoder's low-level bounds discipline alongside its higher-level instruction-relocation machinery.

- **C1:** [`decoder.rs`](https://github.com/icedland/iced/blob/master/src/rust/iced-x86/src/decoder.rs) states pointer-order and overflow invariants and caps instruction reads at the architectural length limit, including pathological prefix streams. It distinguishes invalid encodings from exhausted input.
- **C2:** [`block_enc.rs`](https://github.com/icedland/iced/blob/master/src/rust/iced-x86/src/block_enc.rs) moves instruction blocks, resolves targets, rejects duplicate nondefault instruction addresses, and rewrites out-of-range branches. Decoded instructions thus support rewriting and instrumentation as well as text output.
- **C3:** The decoder uses precomputed handler tables and borrowed input; the block encoder preallocates from instruction counts and uses a sorted target index. These expose the costs and invariants behind the project's performance goals without relying on its benchmark headline.

### 14. [intelxed/xed](https://github.com/intelxed/xed)

**Language/role:** C with Python generation tools; Intel's x86 encoder/decoder library.

Study detailed instruction metadata rather than just opcode names. XED is particularly useful for understanding how disassembly consumers distinguish syntax, instruction-set membership, and actual operand effects.

- **C1:** The [technical API manual source](https://github.com/intelxed/xed/blob/main/docsrc/xed-doc-top.txt) explains conditional operand reads/writes, including the distinction between merging and zeroing masks. It also describes CPUID support as groups of required records, avoiding an oversimplified single-feature-bit interpretation.
- **C2:** Decoded-instruction and encoder-request objects share operand-value fields while exposing different additional information. The same manual covers registers, flags, effective-address calculation, instruction forms, and formatting, making the decoder useful to many analysis and transformation consumers.

The [build overview](https://github.com/intelxed/xed/blob/main/README.md) documents decoder-only/encoder-only configurations and string reduction. These are useful integration options; no numerical performance comparison is asserted here.

### 15. [iximeow/yaxpeax-arm](https://github.com/iximeow/yaxpeax-arm)

**Language/role:** Rust; ARMv7, Thumb/Thumb-2, and AArch64 decoders within the yaxpeax architecture ecosystem.

A smaller implementation worth studying for explicit architectural edge cases and reusable decoding traits.

- **C1:** The [ARMv7 implementation](https://github.com/iximeow/yaxpeax-arm/blob/no-gods-no-/src/armv7.rs) distinguishes exhausted input, invalid operands/opcodes, undefined instructions, and unpredictable encodings. Its shared instruction model retains Thumb-origin information rather than conflating instruction modes.
- **C2:** The repository documents `InstDecoder` entry points, integration with `yaxpeax-arch`, and `no_std` operation, supporting both ordinary analysis programs and constrained environments.
- **C1, testing evidence:** The [Thumb differential test implementation](https://github.com/iximeow/yaxpeax-arm/blob/no-gods-no-/differential-tests/tests/differential-v7-thumb.rs) normalizes register aliases and operand syntax for decoder comparison. Its exceptions and unfinished cases are themselves useful lessons in the limits of differential testing.

**Limitations:** The README explicitly lists incomplete ARMv7 NEON, SVE/SVE2, strict unpredictable-encoding handling, and exhaustive testing. Do not read the broad architecture names as complete ISA coverage.

### 16. [envytools/envytools](https://github.com/envytools/envytools)

**Language/role:** Primarily C; NVIDIA hardware research toolkit, specifically its `envydis` disassembler/assembler subsystem.

Study decoding when instruction sets are incompletely documented and differ across GPU engines and generations. This repository contributes shader and firmware-microcode coverage beyond conventional desktop CPUs.

- **C1:** The [internal decoder design](https://github.com/envytools/envytools/blob/master/envydis/dis-intern.h) tracks which opcode bits have been consumed and highlights unexplained bits. It explicitly states the table-termination invariant: decode tables need a fallback or exhaustive matching because their scan does not independently check table length.
- **C2:** Hierarchical decode tables combine masks, feature/program-type constraints, and reusable operand operations. The [envydis guide](https://github.com/envytools/envytools/blob/master/docs/envydis/index.rst) documents selection across shader ISAs, Falcon firmware, hardware sequencers, and other microcode, including per-ISA completeness ratings.

**Status:** Historical specialist reference, not a promise of support for current NVIDIA generations. The README identifies GitHub as canonical; [metadata](https://api.github.com/repos/envytools/envytools) reported the last push in October 2023 and no archive flag.

### 17. [tgtakaoka/libasm](https://github.com/tgtakaoka/libasm)

**Language/role:** C++; embeddable assembler/disassembler library for retro CPUs and microcontrollers.

This small-environment design is a useful counterpoint to workstation-scale frameworks. Targets include 6502, 8051, Z80, Motorola families, DSPs, and less familiar processors; supported hosts include Arduino and desktop systems.

- **C2:** [`Disassembler`](https://github.com/tgtakaoka/libasm/blob/main/src/dis_base.h) separates architecture-specific decoding from CPU configuration, symbolic names, numeric formatting, and memory delivery. Its public decode call accepts a memory abstraction, instruction object, optional symbol table, and caller-owned output buffer.
- **C3:** The [base implementation](https://github.com/tgtakaoka/libasm/blob/main/src/dis_base.cpp) places option strings in program memory with `PROGMEM` and formats operands into a buffer with an explicit capacity. Those choices directly address scarce embedded RAM while preserving common formatting and option machinery.
- **C1:** That implementation validates instruction addresses against the selected CPU configuration and propagates formatting errors through the instruction's error state, connecting resource limits to observable failure handling.

## JVM, Android, and .NET decompilers

### 18. [skylot/jadx](https://github.com/skylot/jadx)

**Language/role:** Java; Android DEX-to-Java decompiler with command-line, library, and GUI consumers.

Study the progression from register instructions through blocks, SSA, inferred types, and structured regions. The `jadx-core` implementation is the main interest here, rather than Android resource extraction alone.

- **C1:** [`SSATransform`](https://github.com/skylot/jadx/blob/master/jadx-core/src/main/java/jadx/core/dex/visitors/ssa/SSATransform.java) places phi nodes using liveness and dominance frontiers, renames values, and includes special handling for assignments inside `try` regions. These are concrete obstacles to reconstructing Java variables from reused DEX registers.
- **C2:** [`Jadx.java`](https://github.com/skylot/jadx/blob/master/jadx-core/src/main/java/jadx/core/Jadx.java) assembles reusable visitors into distinct restructure, simple, and fallback pipelines. Instruction, block, and region representations make the staging explicit, with optional debugging graphs at intermediate points.

**Limitation:** The project explicitly warns that complete successful decompilation is not guaranteed. Its fallback modes are part of the design, not evidence that every input can be reconstructed as idiomatic Java.

### 19. [Vineflower/vineflower](https://github.com/Vineflower/vineflower)

**Language/role:** Java; Java/JVM-language decompiler descended from Fernflower and continued through the Quiltflower lineage.

Study the unusually readable account of structuring arbitrary bytecode control flow into Java. This is retained as a substantive evolving implementation; its ancestor forks are not separately counted.

- **C1:** The [architecture guide](https://github.com/Vineflower/vineflower/blob/master/ARCHITECTURE.md) explains exception-range repair, irreducible-flow handling, `finally` deduplication, and preservation of explicit branch targets before labels can be simplified. It also distinguishes SSA from assignment-and-usage versioning during expression reduction.
- **C2:** Instruction sequences, CFG basic blocks, statement graphs, and expression trees form successive representations, each with dedicated processors. That separation supports different compiler patterns and JVM inputs while sharing control-flow and expression machinery.

The [project overview](https://github.com/Vineflower/vineflower/blob/master/README.md) documents library/CLI use, multithreaded decompilation, modern Java constructs, and precise fork provenance. Architecture explanations are more valuable here than unverified comparisons of output quality.

### 20. [leibnitz27/cfr](https://github.com/leibnitz27/cfr)

**Language/role:** Java; Java class-file and JAR decompiler.

Study both bytecode reconstruction and the separation between an engine's file acquisition and output policy. CFR also documents a useful distinction between regression expectations and semantic ground truth.

- **C1:** The [processed instruction graph](https://github.com/leibnitz27/cfr/blob/master/src/org/benf/cfr/reader/bytecode/analysis/opgraph/Op02WithProcessedDataAndRefs.java) carries stack and exception information and interprets `invokedynamic` bootstrap arguments, including marker interfaces and variable-argument signatures. Reconstructing lambdas therefore involves metadata and type constraints beyond recognizing one opcode.
- **C2:** [`CfrDriver`](https://github.com/leibnitz27/cfr/blob/master/src/org/benf/cfr/reader/api/CfrDriver.java) accepts replaceable class-file sources, fallback sourcing, output sinks, and options. Consumers can integrate the same engine with files, archives, or custom class providers.

The README explains its expected-output test suite and explicitly says those expected results are not a correctness oracle. The API likewise identifies interfaces that are not promised stable.

### 21. [icsharpcode/ILSpy](https://github.com/icsharpcode/ILSpy)

**Language/role:** C#; .NET IL disassembler and C# decompiler, with a reusable `ICSharpCode.Decompiler` engine.

Study reconstruction that must preserve C# binding semantics as well as control flow. The engine is worth examining independently of the desktop UI.

- **C1:** The [architecture document](https://github.com/icsharpcode/ILSpy/blob/master/doc/DecompilerArchitecture.html) explains resolver-checked output, invariant checks between transforms, recovery of async/iterator state machines, and fallback when a transformation cannot recognize an input safely. Emitting a plausible method call is insufficient if overload resolution changes its target.
- **C2:** The [ILAst description](https://github.com/icsharpcode/ILSpy/blob/master/doc/ILAst.txt) replaces the evaluation stack with explicit variables and typed instruction trees. The architecture then separates IL transforms, C# AST construction, AST transforms, and text output, shared by library, CLI, and UI consumers.
- **C3:** The architecture documentation makes concurrency ownership explicit: a decompiler instance is not thread-safe, so parallel project decompilation uses separate instances. This is a useful example of choosing an understandable unit of parallel work.

## Python, Lua, Flash, WebAssembly, and EVM

### 22. [rocky/python-uncompyle6](https://github.com/rocky/python-uncompyle6)

**Language/role:** Python; cross-version Python bytecode and source-fragment decompiler.

Study grammar-based reconstruction and mapping recovered source ranges back to bytecode offsets. Fragment decompilation makes this useful beyond whole-file recovery, including debugger displays.

- **C1:** [`parser.py`](https://github.com/rocky/python-uncompyle6/blob/master/uncompyle6/parser.py) builds grammar rules according to opcode argument counts and parser/version context, instead of assuming one permanent Python bytecode grammar. This addresses changing stack-machine encodings and ambiguous source constructs.
- **C2:** [`fragments.py`](https://github.com/rocky/python-uncompyle6/blob/master/uncompyle6/semantics/fragments.py) extends the source walker with offset-indexed source spans. The tree/walker separation supports complete source generation and localized source explanations from the same reconstruction.

**Limitations:** The README describes input bytecode support through Python 3.8. Its branches that run on newer Python interpreters do not imply support for decompiling those interpreters' bytecode. Broader input compatibility should be checked explicitly before selecting it.

### 23. [zrax/pycdc](https://github.com/zrax/pycdc)

**Language/role:** C++; Python bytecode disassembler `pycdas` and decompiler `pycdc`, also known as Decompyle++.

A useful independent contrast to uncompyle6's grammar-based approach: study direct stack simulation and construction of a source AST in a standalone native implementation.

- **C1:** [`ASTree.cpp`](https://github.com/zrax/pycdc/blob/master/ASTree.cpp) maintains operand-stack histories and nested block state, including exception-table-driven regions. Its handling of conditionals and exception entries shows why source recovery cannot be a linear opcode substitution.
- **C2:** [`bytecode.cpp`](https://github.com/zrax/pycdc/blob/master/bytecode.cpp) maps version-specific opcode numbers into shared opcode identities and handles differences in instruction/argument encoding. The common bytecode layer serves both disassembly and AST reconstruction.

**Limitation:** Supporting every Python version is a stated goal, not a verified completeness result. Version tables and individual fixtures do not demonstrate correct decompilation of every construct in those versions.

### 24. [viruscamp/luadec](https://github.com/viruscamp/luadec)

**Language/role:** C; Lua bytecode disassembler and decompiler, descended from LuaDec and LuaDec51.

Study a compact, procedural implementation of register-to-expression reconstruction, nested-function handling, and checking generated output by recompiling it.

- **C1:** [`decompile.c`](https://github.com/viruscamp/luadec/blob/master/luadec/decompile.c) reconstructs nested loop and Boolean-expression structures and includes a mode that recompiles decompiled functions for instruction comparison. The README shows separate outcomes for compilation failure and mismatched instruction sequences; this is useful validation evidence, not a general equivalence proof.
- **C2:** Shared Lua `Proto` objects and constant/operand helpers support complete and selected nested-function workflows. [`disassemble.c`](https://github.com/viruscamp/luadec/blob/master/luadec/disassemble.c) demonstrates the same function-selection and constant-rendering machinery in the lower-level disassembler.

**Status/limits:** A legacy study candidate. Lua 5.1 is the main target; 5.2 and 5.3 are explicitly experimental. [Metadata](https://api.github.com/repos/viruscamp/luadec) reported the last push in February 2024 and no archive flag. Earlier ancestor repositories are not counted separately.

### 25. [jindrapetrik/jpexs-decompiler](https://github.com/jindrapetrik/jpexs-decompiler)

**Language/role:** Java; Flash SWF/ActionScript decompiler and editor; focus on `libsrc/ffdec_lib`.

Study decompilation embedded in a larger binary-format editing library. Flash adds a different mix of bytecode, exception handling, resource structures, and round-trip editing requirements.

- **C1:** [`AVM2Graph.java`](https://github.com/jindrapetrik/jpexs-decompiler/blob/master/libsrc/ffdec_lib/src/com/jpexs/decompiler/flash/abc/avm2/graph/AVM2Graph.java) extends the common graph machinery with AVM2 exception entries and distinct stack-based, register-based, and inlined `finally` patterns. This is substantial source reconstruction, not just SWF resource extraction.
- **C2:** The [library guide](https://github.com/jindrapetrik/jpexs-decompiler/blob/master/libsrc/ffdec_lib/README.md) exposes SWF parsing, typed tags, modification tracking, saving, and decompilation as a separately usable library. Its requirement to mark modified tags shows a concrete persistence invariant for consumers.
- **C4:** The [multiyear changelog](https://github.com/jindrapetrik/jpexs-decompiler/blob/master/CHANGELOG.md) records ongoing compatibility and reconstruction fixes, including switch breaks inside loops, `if`/`switch` confusion, and obfuscated-name debugging. This supports evolution well beyond the age of the Flash ecosystem itself.

### 26. [WebAssembly/wabt](https://github.com/WebAssembly/wabt)

**Language/role:** C++; WebAssembly binary toolkit, specifically `wasm-objdump`, `wasm2wat`, and their binary-reading infrastructure.

Study specification-oriented disassembly and serialization with clear malformed-input handling. The monorepo is counted once; its JavaScript packaging is not a separate decoder implementation.

- **C1:** [`binary-reader.cc`](https://github.com/WebAssembly/wabt/blob/main/src/binary-reader.cc) handles prefixed opcodes, LEB128 operands, section boundaries, and bounded reads with explicit errors. The [test guide](https://github.com/WebAssembly/wabt/blob/main/test/README.md) documents invalid-input cases, expected diagnostics, sanitizer configurations, and binary/text/binary round trips.
- **C2:** The reader infrastructure serves dumping, text conversion, validation, and other tools. The testing guide shows the same fixtures and runner composing several of those consumers, including generated binaries and specification-test inputs.

**Important scope correction:** `wasm-decompile` was [removed in June 2026](https://github.com/WebAssembly/wabt/pull/2769). This entry is for the current disassembly infrastructure; old descriptions that still advertise that decompiler are stale.

### 27. [Jon-Becker/heimdall-rs](https://github.com/Jon-Becker/heimdall-rs)

**Language/role:** Rust; EVM bytecode disassembly, CFG recovery, and Solidity-like/Yul decompilation.

Study contract-bytecode analysis where function selectors, ABI reconstruction, and VM hard-fork semantics are central. This supplies a different machine model from native CPUs and conventional language bytecode.

- **C1:** The [control-flow implementation](https://github.com/Jon-Becker/heimdall-rs/blob/main/crates/decompile/src/core/control_flow.rs) prunes constant branches only after checking trace completeness. It protects against losing shared continuations or the only path exposing a return used for ABI recovery, and includes tests beside those rules.
- **C2:** The [decompiler orchestrator](https://github.com/Jon-Becker/heimdall-rs/blob/main/crates/decompile/src/core/mod.rs) composes a hard-fork-aware VM, disassembler, selector discovery, symbolic traces, analyzers, and source/ABI output. Callers can request different higher-level products from the common analysis.
- **C3:** Symbolic execution is given explicit deadlines, and later per-function trace analyses are composed asynchronously. These mechanisms expose limits and work boundaries; they do not establish universal scalability or complete path coverage.

## Coverage and search notes

Discovery used more than six distinct live-search formulations, followed by repository/API verification and direct reading of technical primary sources. Search angles included native decompiler pipelines; x86 decoder libraries; ARM, Thumb, RISC-V, and other processor backends; OCaml and Python lifting frameworks; JVM/Android decompilation; .NET reconstruction; Python and Lua bytecode; Flash; WebAssembly; NVIDIA shader/microcode ISAs; EVM; and embedded/retro processors. Targeted follow-ups looked for architecture documents, regression suites, API contracts, and feature removals. The last expansion added libasm for its embedded resource model. Final follow-ups also surfaced additional x86 engines, generated ARM decoders, and language ports. Their architecture and role coverage largely overlapped this selection, so they did not receive full second-source verification and remain outside the report.

The selection deliberately extends slightly beyond the 15–25 guide to preserve those specialist domains. It includes both large platforms and smaller substantive libraries. ARM, MIPS, PowerPC, RISC-V, DSP, and legacy-CPU coverage is often inside a shared framework rather than represented by a separate repository for every backend. Java, C#, OCaml, Python, Rust, and C/C++ implementations provide materially different architectural approaches.

Canonical GitHub identities were checked using repository pages or the public API. Additional source files or technical documentation were read for every retained project; raw copies of the same README were not counted as independent evidence. GitHub metadata was available for the first 26 candidates; libasm was verified through its repository page and directly fetched implementation files after the unauthenticated API reached its rate limit. None of the metadata-checked repositories was archived. Historical inactivity is nevertheless called out for Boomerang, envytools, and LuaDec. No entry relies on an unofficial mirror, and no commercial engine is represented by a repository containing only its SDK or plugins.

Excluded from the retained list were GUI-only wrappers, generated bindings, MCP adapters, curated lists, decompiler-comparison harnesses, and emulator-first projects where disassembly was incidental. Search results included several RetDec forks; the original Avast implementation was selected without assuming downstream claims applied upstream. Fernflower-family ancestors and LuaDec ancestors were not duplicated. Rizin was retained alongside radare2 because its documented semantic-language redesign provides distinct material. Newer experimental and model-driven decompilation projects were encountered but not given entries without equally strong inspected implementation evidence; that is a verification limit, not a judgment that the entire research direction lacks value.

This is a selection guide, not an exhaustive inventory or benchmark. Test descriptions, source invariants, and changelogs support the stated criteria; they do not prove semantic equivalence for arbitrary binaries. No star-count threshold, unsupported speed ranking, or assumption that a recent push establishes sustained maintenance was used.
