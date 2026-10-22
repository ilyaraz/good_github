# Assemblers and linkers

Research date: **2026-10-09**

This selection covers native object-file linkers, textual machine-code assemblers, bank-aware cross-development toolchains, runtime assembly libraries, and one JVM bytecode assembler. It contains **23 distinct GitHub repositories**. For compiler or runtime monorepos, only the named assembly/linking subsystem is evaluated. The emphasis is on code an experienced engineer can study for concrete design decisions, rather than popularity or feature counts.

Criteria legend:

- **C1:** Difficult correctness: invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2:** Substantial reusable abstractions serving multiple use cases.
- **C3:** Real performance constraints addressed through an understandable architecture.
- **C4:** Sustained evolution supported by compatibility work, testing, or complexity management—not merely repository age.

The criteria below are engineering assessments grounded in the linked primary material. They are not claims that every component is exemplary, or that an assembler accepts untrusted input safely. Source links normally follow the inspected branch and can change. Historical documentation and official mirrors are identified explicitly; the list is not a maintenance ranking.

## Native linkers

### [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language/role:** C++; the **LLD** linker subsystem, counted once within the LLVM monorepo.

Study the relationship between symbol identity, lazy archive extraction, section ownership, and output layout. LLD also offers an instructive decision against excessive abstraction: its native ELF and COFF linkers share design ideas while deliberately sharing relatively little format-specific code.

- **C1:** The symbol table maintains one symbol object per name while resolution replaces its meaning in place. Defined, undefined, and lazy symbols have explicit conflict rules; the writer must assign non-overlapping output addresses. The design also explains why identical-code folding can violate observable function-address distinctions.
- **C3:** Lazy loading avoids reading section contents and relocations prematurely, while retained symbol handles avoid repeated name hashing. Archive symbols remain available for later extraction, reducing repeated archive scans. These mechanisms, and their semantic tradeoffs, are described in the [LLD design document](https://lld.llvm.org/NewLLD.html).

That document is the principal entry point. Its embedded-library contract explicitly assumes trustworthy object files; it should not be read as a hostile-input safety guarantee.

### [rui314/mold](https://github.com/rui314/mold)

**Language/role:** Rust on the inspected `main` branch; native Unix linker. Older descriptions of its C++ implementation do not describe the current source layout.

Study how an ordered sequence of passes can expose parallel work without making symbol and relocation results depend on scheduling.

- **C1:** The relocation pass documents a subtle ordering requirement: symbols eligible for promotion to dynamic relocations must be promoted across all sections before those sections are scanned. Otherwise classification depends on which section runs first. Symbol-version conflict checks and COMDAT resolution provide additional correctness boundaries.
- **C3:** Object relocation scanning uses Rayon parallel iteration, while the driver makes pass boundaries explicit. It also documents parallel unmapping to reduce process-exit cleanup costs. These are concrete mechanisms rather than an assumed speed advantage.

Entry points: [ELF pass implementations](https://github.com/rui314/mold/blob/main/elf/passes.rs) and [ELF driver](https://github.com/rui314/mold/blob/main/elf/driver.rs). The older, search-indexed `docs/design.md` was not usable as a current source and is not relied upon here.

### [wild-linker/wild](https://github.com/wild-linker/wild)

**Language/role:** Rust; ELF linker for Linux.

Wild is particularly useful for studying an explicit phase architecture coupled to differential testing. Its design separates input mapping, string merging, symbol indexing, resolution, layout, and writing; later phases borrow earlier results immutably.

- **C1:** Layout traverses relocation relationships to determine live sections and required GOT, symbol-table, and dynamic-relocation space before assigning addresses. The integration strategy compares links against GNU ld or LLD using `linker-diff`, then executes the linked programs.
- **C3:** Parallel iteration handles collection-oriented phases. Graph algorithms that do not fit that model use scoped tasks and explicit job coordination, rather than pretending all work is a simple parallel map.

Entry point: [DESIGN.md](https://github.com/wild-linker/wild/blob/main/DESIGN.md), which connects the phases, threading choices, and tests. Its inclusion does not imply complete compatibility with other ELF linkers.

### [golang/go](https://github.com/golang/go)

**Language/role:** Go; the **`src/cmd/link`** subsystem, not the entire language implementation.

Study a linker organized around a language-specific object format and compact symbol identities. The loader is a useful counterpoint to conventional object-oriented symbol graphs.

- **C1:** Content-addressed symbol deduplication must account for objects whose stored data omits trailing zeros: equal content hashes can accompany different declared sizes, so the loader selects the larger symbol. It also separates static, package, externally defined, and ABI-versioned names.
- **C3:** Global symbol indices, attribute bitmaps, separate value/section arrays, and selectively materialized external payloads make memory organization visible in the implementation. The study value is this explicit representation of a large symbol population, not an unverified throughput claim.

Entry point: [linker symbol loader](https://github.com/golang/go/blob/master/src/cmd/link/internal/loader/loader.go), especially `Loader`, `extSymPayload`, and `addSym`.

### [apple-oss-distributions/ld64](https://github.com/apple-oss-distributions/ld64)

**Language/role:** C++; Apple's official open-source distribution of the Darwin/Mach-O linker. Treat it as a published source distribution, not proof of parity with the newest Xcode linker.

Study the atom graph: an atom represents an indivisible piece of code or data, and fixups encode relationships between atoms. This makes otherwise disparate linker operations understandable as graph transformations.

- **C1:** Coalescing must preserve references when weak definitions, tentative definitions, or duplicate constants collapse into one atom. Optimization passes require a fully resolved graph; branch-island generation handles branches that cannot directly reach their targets.
- **C2:** Readers, resolution, graph passes, and output generation communicate through the atom/fixup model. The documented passes cover dead stripping, stubs, GOT entries, thread-local variables, and unwind information without requiring each pass to parse input files.

Entry point: [linker architecture document](https://github.com/apple-oss-distributions/ld64/blob/main/doc/design/linker.html). It is historical design material and is presented as such, rather than as a current feature matrix.

## General-purpose x86 assemblers

### [netwide-assembler/nasm](https://github.com/netwide-assembler/nasm)

**Language/role:** C implementation with substantial assembly tests and supporting generators; standalone x86 assembler.

Study how instruction-template matching, effective-address encoding, prefix rules, and output relocation policy interact. The implementation distinguishes errors such as incompatible operand sizes, CPU modes, masks, broadcasts, and immediate values instead of treating encoding as simple opcode lookup.

- **C1:** The encoder handles absolute versus relative addresses, output-width overflow, address-space wrapping in narrow modes, and cases where an address must remain a relocation instead of becoming raw bytes.
- **C2:** Instruction matching and sizing feed a shared output representation. The output-format interface supplies policies such as maximum address width and whether address records must be retained, allowing the assembler core to support multiple object formats.

Entry point: [assembler and output-encoding implementation](https://github.com/netwide-assembler/nasm/blob/master/asm/assemble.c). This is a good place to follow the boundary between ISA semantics and object-format semantics.

### [yasm/yasm](https://github.com/yasm/yasm)

**Language/role:** C; modular assembler supporting x86/AMD64, NASM/GAS syntax, and several object/debug formats. It is a separate rewrite, not a second listing of NASM.

Study an assembler that parses source once and performs later work over an in-memory representation. Its historical design document is unusually explicit about the boundaries between the frontend, `libyasm`, architecture modules, and output modules.

- **C1:** Bytecodes report dependent spans and thresholds for short/long encoding decisions. Length calculation and expansion callbacks make the consequences of moving labels and changing instruction sizes explicit.
- **C2:** The bytecode callback contract separates generic layout from instruction-specific behavior; parser, preprocessor, architecture, and object-format modules provide distinct extension points.

Entry points: [bytecode API](https://github.com/yasm/yasm/blob/master/libyasm/bytecode.h) and the author's [Design and Implementation of Yasm](https://www.tortall.net/projects/yasm/reference/design/design.pdf). The latter is dated 2010; no claim about present release cadence is inferred from it.

### [tgrysztar/fasm](https://github.com/tgrysztar/fasm)

**Language/role:** Assembly; flat assembler 1. The author identifies this as the official repository with source history reconstructed from preserved snapshots.

Study a self-hosted assembler whose resolution machinery is visible directly in assembly: pass state, symbol predictions, address spaces, and bounded retry behavior.

- **C1:** The core detects changed symbol predictions, requests another pass, and rejects assembly when the pass limit is exhausted. Symbol definition and address calculations include explicit overflow and redefinition paths. See [ASSEMBLE.INC](https://github.com/tgrysztar/fasm/blob/master/SOURCE/ASSEMBLE.INC).
- **C4:** The [dated change history](https://github.com/tgrysztar/fasm/blob/master/WHATSNEW.TXT) records continuing instruction additions and semantic corrections across years: intermediate-pass overflow behavior in 2021, relocatable-address fixes in 2023, and encoding/parser corrections through 2026. This is stronger evidence than the reconstructed start date alone.

The assembly implementation is compact but demands familiarity with its internal conventions; it is a specialist study choice.

## Banked, retro, and embedded toolchains

### [gbdev/rgbds](https://github.com/gbdev/rgbds)

**Language/role:** C++; Game Boy assembler/linker package. Relevant components are RGBASM and RGBLINK.

Study constrained placement in a machine with several memory-region types and banked address spaces. The linker represents free space per bank and handles sections with fixed addresses, fixed banks, or alignment constraints.

- **C1:** Placement checks both ends of a section against a free block, detects alignment wraparound, and terminates bank iteration correctly. These conditions are essential when addresses are narrow and some regions are banked while others are not.
- **C3:** The implementation uses first-fit decreasing placement and explains why only the earliest constraint-satisfying address within a free block needs testing. That is an understandable reduction of the placement search space.

Entry point: [linker section assignment](https://github.com/gbdev/rgbds/blob/master/src/link/assign.cpp), particularly `MemoryLocation`, `tryPlacingInBank`, and the section-placement routine.

### [cc65/cc65](https://github.com/cc65/cc65)

**Language/role:** C; **ca65 assembler and ld65 linker** within the 6502-family development-suite monorepo.

Study how relocatable assembly can serve machines with very different memory layouts without hard-coding each layout into the linker. Object files preserve expressions and source locations for deferred evaluation and diagnostics.

- **C1:** ld65 resolves expressions that cannot be completed during assembly and reports undefined symbols, range errors, and symbol-type mismatches at their originating source locations. Library groups are searched repeatedly until no more references can be satisfied.
- **C2:** Configuration files describe memory areas, segments, symbols, and output arrangements. The same linking machinery serves numerous 6502 systems and custom layouts, while ca65-produced modules and ar65 libraries provide reusable compilation units.

Entry point: [ld65 Users Guide](https://cc65.github.io/doc/ld65.html), especially its detailed workings and configuration sections. The compiler and platform libraries are outside this entry's evaluation.

### [vhelin/wla-dx](https://github.com/vhelin/wla-dx)

**Language/role:** C; multi-CPU cross assemblers plus WLALINK, including 65xx, Z80-family, Motorola, and other targets.

Study the distinction between CPU addresses, ROM banks, slots, and physical output placement. This toolchain is especially instructive when an ordinary flat address-space model is insufficient.

- **C1:** The linker documents precise interactions among fixed placement, bank-spanning sections, slot mappings, `AFTER` relationships, and offsets. A section's start bank and subsequent bank sequence must remain consistent with those constraints.
- **C2:** A shared link-file model handles object files, libraries, RAM sections, ROM sections, headers, and footers across the supported CPUs. Priority and size ordering are explicit policies rather than hidden platform-specific behavior.

Entry points: [linking documentation](https://wla-dx.readthedocs.io/en/latest/linking.html) and [linker output implementation](https://github.com/vhelin/wla-dx/blob/master/wlalink/write.c). The breadth comes from the shared placement model, not merely the CPU list.

### [dasm-assembler/dasm](https://github.com/dasm-assembler/dasm)

**Language/role:** C; macro assembler for several small 8-bit processor families.

Study the maintenance of a compact, established assembler while preserving accepted source behavior. Its error model distinguishes conditions such as unresolved sources, excessive passes, branch range failures, mismatched labels, and expression failures.

- **C1:** The main implementation buffers pass-dependent diagnostics until the relevant final pass and centralizes error descriptions and fatality decisions. See the [assembler driver](https://github.com/dasm-assembler/dasm/blob/master/src/main.c).
- **C4:** [NEWS](https://github.com/dasm-assembler/dasm/blob/master/NEWS) records changes across 2003–2026. The 2026 release explicitly preserves valid-source output while hardening malformed expressions, macro arguments, long lines, and zero alignment; older entries document numeric and compatibility repairs. This is a concrete evolution story, not an assertion that all old code is robust.

The useful lesson is how diagnostics and hardening coexist with long-lived assembly sources.

### [z00m128/sjasmplus](https://github.com/z00m128/sjasmplus)

**Language/role:** C++ implementation with assembly tests and Lua integration; Z80-family cross assembler.

Study a deliberately bounded three-pass assembler with rich macro processing and machine-aware memory facilities. Its manual describes exactly which state survives between passes.

- **C1:** The first two passes determine sizes and symbols; the third emits code and diagnoses symbols that still change. Symbol tables and Lua global state persist while other state is discarded. Text substitutions are iterative and have defined precedence, so macro semantics and convergence are part of correctness.
- **C2:** Macros, define arrays, modules, virtual-device memory, and relocation-data generation provide reusable mechanisms for different Z80 systems and output workflows, rather than a single fixed ROM format.

Entry point: [documentation source](https://github.com/z00m128/sjasmplus/blob/master/docs/documentation.xml), particularly “Assembling Process,” the substitution rules, and device/relocation directives. The documented pass limit is a meaningful restriction to understand before adopting complex metaprogramming patterns.

### [z88dk/z88dk](https://github.com/z88dk/z88dk)

**Language/role:** C/C++; **z88dk-z80asm**, the relocatable assembler, linker, and librarian inside the larger development kit.

Study a module-oriented toolchain serving a family of related CPUs and many machines. This is specifically z88dk's assembler, not an unrelated repository that happens to use the name `z80asm`.

- **C1:** Linking reconstructs modules, resolves expressions, and patches relocatable addresses. The relocation writer contains a concrete encoding edge case: a zero relocation distance cannot use the compact one-byte form and needs the longer representation.
- **C2:** Modules, libraries, sections, and external symbols support separate assembly and library extraction across CPU variants. The documented tool also exposes multiple floating-point data encodings and selectable synthetic instructions for different target environments.

Entry points: [module linker](https://github.com/z88dk/z88dk/blob/master/src/z80asm/src/c/modlink.c) and [official assembler guide](https://github.com/z88dk/z88dk/wiki/Tool---z80asm). The many unrelated compiler/runtime components are not counted separately.

## Cross-architecture and configurable assemblers

### [Kingcom/armips](https://github.com/Kingcom/armips)

**Language/role:** C++; assembler for ARM and MIPS platforms, with additional architecture hooks in the inspected core.

Study the separation between parsing, repeated validation, and final encoding in an assembler that can place code into existing binary layouts. Its command representation supports symbol output and temporary assembly listings as well as binary emission.

- **C1:** Validation repeats until layout stabilizes, with an explicit failure for an infinite validation loop. Allocation overlap is checked before final encoding; queued diagnostics can prevent output.
- **C3:** After validation, symbol output, temporary listing output, and encoding can run in parallel. A source comment explains the enabling invariant: these tasks read the same memory without mutating it. This is a particularly clear example of a performance feature resting on a correctness boundary.

Entry point: [core assembly pipeline](https://github.com/Kingcom/armips/blob/master/Core/Assembler.cpp), especially `encodeAssembly`.

### [mikeakohn/naken_asm](https://github.com/mikeakohn/naken_asm)

**Language/role:** C++; cross assembler spanning microcontrollers and larger ISAs, including MSP430, AVR, ARM, MIPS, and 68000.

Study how a common assembly context accommodates incompatible instruction syntaxes, address units, and encoding rules without hiding target-specific work.

- **C1:** The MSP430 backend performs operand-range checks, adjusts symbolic PC-relative values according to instruction length, and handles instructions starting off a 16-bit boundary. These are concrete examples of the numerical and alignment details each backend must preserve.
- **C2:** `AsmContext` supplies shared tokens, symbols, macros, memory, pass state, and CPU-selected callbacks for instruction parsing, directives, linking, and listings. `bytes_per_address` makes address-unit differences explicit.

Entry points: [assembly context](https://github.com/mikeakohn/naken_asm/blob/master/core/AsmContext.h) and [MSP430 encoder](https://github.com/mikeakohn/naken_asm/blob/master/asm/msp430.cpp). Backend breadth should not be mistaken for uniform completeness across every target.

### [hlorenzi/customasm](https://github.com/hlorenzi/customasm)

**Language/role:** Rust; assembler for user-defined instruction sets, including custom CPUs and virtual machines.

Study an instruction-definition language instead of a fixed set of built-in CPU backends. Rules map mnemonic patterns and typed operands to bit encodings; the repository's example uses signed 8-bit immediates and unsigned 16-bit branch addresses.

- **C1:** The engine resolves constants and conditional assembly before matching instructions, then performs bounded iterative resolution and checks output banks for overlap before building the final bit vector.
- **C2:** User-defined rules and banks sit above shared parsing, declaration, matching, resolution, diagnostics, and output stages. A `FileServer` interface also separates assembly from how source files are supplied.

Entry points: the [rule-definition example](https://github.com/hlorenzi/customasm/blob/main/README.md#example) and [assembly orchestration](https://github.com/hlorenzi/customasm/blob/main/src/asm/mod.rs). The latter is independent implementation evidence, not a second copy of the README.

## Runtime assembly libraries

### [asmjit/asmjit](https://github.com/asmjit/asmjit)

**Language/role:** C++; programmatic machine-code generation with assembler and higher-level emitters.

Study `CodeHolder` as the common representation between emission and executable placement. Its documented lifecycle distinguishes generated sections and labels from the final executable module.

- **C1:** Unbound labels carry unresolved fixups; relocation must account for the eventual base address and address-table entries. The API documents label-validity preconditions and explains why functions within one allocated module cannot be released independently.
- **C2:** Shared sections, labels, expressions, relocation records, logging, and error handlers support multiple emitters and multi-function modules. Higher-level function nodes also act as labels, connecting compiler-style emission to the same placement machinery.

Entry point: [CodeHolder API and implementation-facing documentation](https://github.com/asmjit/asmjit/blob/master/asmjit/core/code_holder.h). Its examples and invariants provide more architectural value than treating the library as a collection of instruction methods.

### [herumi/xbyak](https://github.com/herumi/xbyak)

**Language/role:** C++ header library; x86/x64 runtime assembler.

Study direct C++ instruction emission together with the often-overlooked lifecycle of a movable code buffer. The core exposes operands, labels, code generation, allocation, and memory-protection operations in one inspectable implementation.

- **C1:** Auto-growing buffers require jump-address recalculation. `ready()` rejects unresolved labels, while protection changes can fail explicitly. The allocator contract requires page-rounded storage because protection operates at page granularity.
- **C2:** `CodeGenerator`, `CodeArray`, typed operands, label management, and replaceable allocators separate reusable encoding and storage responsibilities. Callers can choose label/jump forms and finalize generated code for different embedding scenarios.

Entry point: [xbyak.h](https://github.com/herumi/xbyak/blob/master/xbyak/xbyak.h), especially `Allocator`, `CodeArray`, `Label`, and `CodeGenerator::ready`. `readyRE()` exists explicitly; the report does not assume read/execute-only permissions are the default.

### [CensoredUsername/dynasm-rs](https://github.com/CensoredUsername/dynasm-rs)

**Language/role:** Rust; assembly macros and runtime assembly support, with x86, x64, AArch64, and RISC-V runtime modules in the inspected tree.

Study the division between macro-generated emission calls and the runtime responsible for labels, relocations, and executable storage.

- **C1:** Executing through an `Executor` requires a read lock on the executable buffer; pointers must not outlive that guard. Relocation writes must preserve unrelated instruction bits and return an error when a value cannot be represented.
- **C2:** Runtime traits describe the macro interface, while an architecture implements the `Relocation` trait for its own encodings. Separate memory, label, and relocation components also support custom assembler implementations.

Entry points: [runtime and execution contract](https://github.com/CensoredUsername/dynasm-rs/blob/master/runtime/src/lib.rs) and [relocation abstraction](https://github.com/CensoredUsername/dynasm-rs/blob/master/runtime/src/relocations.rs). This is an independent Rust implementation inspired by DynASM, not another mirror of LuaJIT.

### [LuaJIT/LuaJIT](https://github.com/LuaJIT/LuaJIT)

**Language/role:** Lua preprocessor and C runtime; the **DynASM** subsystem. This is an official GitHub mirror, linked from the project's [download page](https://luajit.org/download.html).

Study how assembly preprocessing and a small runtime cooperate in a production code-generation system. The relevant unit is `dynasm/`, not the Lua language implementation as a whole.

- **C1:** The x86 runtime separates recording actions and estimated offsets, linking sections and shrinking branches, and final byte encoding. Forward-label offsets and short-branch range checks must remain consistent as layout shrinks.
- **C2:** Action lists, sections, labels, and architecture-specific runtime encoders provide a reusable boundary between assembly templates and the embedding application. The project explicitly describes DynASM as usable by other code-generation engines.

Entry points: [x86 runtime and its three passes](https://github.com/LuaJIT/LuaJIT/blob/v2.1/dynasm/dasm_x86.h) and [official DynASM documentation](https://luajit.org/dynasm.html). The official documentation acknowledges that source reading is necessary because the standalone manual is limited.

### [keystone-engine/keystone](https://github.com/keystone-engine/keystone)

**Language/role:** C/C++; embeddable multi-architecture textual assembler with language bindings.

Keystone is LLVM-derived, but has a substantive independent assembly-engine API and integration layer; it is included for that implementation, not counted as another LLVM mirror. Study how target machinery is packaged as a string-to-bytes service.

- **C1:** Assembly depends on architecture, mode, starting address, target parser/backend, and symbol resolution. The implementation creates an MC context, code emitter, streamer, and parser with explicit failure paths; the API exposes partial statement counts, errors, and caller-owned output memory.
- **C2:** A handle-based C API hides architecture-specific parser construction and accepts a symbol resolver, making the same engine usable through different host-language bindings and applications.

Entry points: [engine implementation](https://github.com/keystone-engine/keystone/blob/master/llvm/keystone/ks.cpp) and [public API contract](https://github.com/keystone-engine/keystone/blob/master/include/keystone/keystone.h). No current release-cadence or blanket thread-safety claim is inferred from its feature list.

## Bytecode assembly

### [Storyyeller/Krakatau](https://github.com/Storyyeller/Krakatau)

**Language/role:** Rust on the inspected `v2` branch; JVM classfile assembler/disassembler. The older Python decompiler is not the subject of this entry.

Study the difference between behavior-preserving assembly and exact binary reconstruction. The repository distinguishes readable disassembly from a round-trip mode intended to reproduce the original classfile bytes, including low-level encoding choices.

- **C1:** The assembly specification exposes details such as NaN payload syntax, explicit stack-map frames, wide instructions, switch tables, exception-handler labels, and constant-pool references. Exact reconstruction therefore involves numerical bit patterns and classfile structure, not just mnemonic translation.
- **C2:** The textual representation can express complete classes, code, attributes, annotations, and low-level references. It serves manual bytecode creation, binary inspection, modification, and round-trip workflows through one format.

Entry points: the repository's [mode descriptions](https://github.com/Storyyeller/Krakatau/blob/v2/README.md) and [assembly specification](https://github.com/Storyyeller/Krakatau/blob/v2/docs/assembly_specification.md). Its advertised Java 19 specification coverage is not generalized here to every later JVM revision.

## Coverage and search notes

Discovery used more than six distinct live-search formulations, covering: parallel ELF linkers; GNU assembler/linker mirrors; NASM/Yasm/fasm architecture; 6502/65816 and Z80/Game Boy toolchains; custom-ISA and microcontroller assemblers; JIT assembly libraries; Go's language-specific linker; Rust/RISC-V assemblers; JVM bytecode assembly; and Darwin/Mach-O/COFF linker design. Follow-up searches for smaller CPU communities and additional object formats increasingly returned already-covered projects, tutorials, unofficial mirrors, or projects requiring a separate depth assessment.

Every retained repository's canonical GitHub URL was opened or checked through the public GitHub API. Every entry also has an independently opened/read design document, implementation file, API contract, or specification beyond its repository overview. Public source-tree indexes were used to resolve changed paths. Where browser retrieval failed, public GitHub raw files were read directly; candidate code was not executed, dependencies were not installed, and repositories were not cloned. The output is a source-based selection guide, not a build or benchmark audit.

Important exclusions and limits:

- **GNU binutils/GAS/ld/gold:** the [GNU project page](https://www.gnu.org/software/binutils/) identifies Sourceware as the development repository. Several substantive GitHub mirrors were found, including RTEMS's mirror, but this search did not establish a GNU-endorsed GitHub mirror under the requested official-mirror standard. Their omission is a hosting/provenance limitation, not a quality judgment.
- **VIXL:** the [Linaro GitHub repository](https://github.com/Linaro/vixl) explicitly says maintenance moved to Arm GitLab and this tree is no longer updated. It was excluded under the moved-project rule.
- **Mirrors and historical material:** LuaJIT's upstream-linked GitHub mirror is retained and flagged; fasm's author-maintained reconstructed history and Apple's source-distribution model are identified. Yasm's old design document is used for architecture, not to assert current maintenance. No retained repository inspected through the API was marked archived.
- Assembly IDEs, assembly-program collections, tutorials, generated bindings without a substantive assembly engine, duplicate forks, and disassembler-only libraries were excluded. The selection intentionally includes less prominent implementations such as naken_asm, customasm, armips, and dynasm-rs alongside major toolchains.
- Dedicated GPU assemblers, mainframe toolchains, and proprietary linkers are not comprehensively covered. No numerical performance ranking is claimed. C4 is awarded only where dated evolution and concrete compatibility/correctness work were actually read; the other entries qualify through their stated technical criteria.
