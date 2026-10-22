# Executable loaders and binary format libraries

Research date: **2026-10-09**.

This report selects 25 GitHub repositories for studying the parsing, construction, modification, mapping, relocation, and linking of executable binaries. It covers ELF, PE/COFF, Mach-O, and WebAssembly, including executable metadata where it is part of those libraries. Runtime loaders, analysis-only loaders, and file-format libraries have different contracts; the descriptions distinguish them. Large repositories are counted once and scoped to the relevant subsystem.

The criteria below are engineering judgments grounded in the linked primary material, not claims that every component is exemplary, secure against arbitrary input, or suitable as a production dependency.

- **C1 — Correctness:** difficult invariants, concurrency, numerical or address semantics, malformed input, and failure handling.
- **C2 — Abstraction:** substantial reusable interfaces or representations supporting multiple applications.
- **C3 — Performance:** concrete time, allocation, memory, or I/O constraints addressed through an understandable design.
- **C4 — Evolution:** documented changes across years, together with compatibility work, tests, or complexity management. Age or recent activity alone does not qualify.

## Libraries spanning formats and runtime linking

### 1. [lief-project/LIEF](https://github.com/lief-project/LIEF)

**C++, with Python and Rust APIs — executable parsing, modification, and rebuilding.** Study how a common binary model coexists with format-specific rewriting rules. The repository covers ELF, PE, Mach-O, COFF, and Android formats; this selection concerns the open-source format libraries, not an assumption that all advertised Extended features are present in the repository.

- **C1:** PE import rewriting must preserve instruction references to existing IAT slots. The documented implementation relocates import headers, lookup tables, and names while retaining original IAT locations; removing an entry can require padding rather than shrinking the table. This is a concrete example of semantic invariants constraining serialization. [Import modification design](https://lief.re/doc/latest/formats/pe/modifications/imports.html)
- **C2:** The common concepts of sections, symbols, and entry points support inspection and rewriting through several language APIs, while builder configuration exposes operations with nonconservative layout effects. [Repository overview](https://github.com/lief-project/LIEF)

Start with the import modification design above, which explains both the algorithm and its unsupported operations.

### 2. [gimli-rs/object](https://github.com/gimli-rs/object)

**Rust — object-file and executable readers and writers.** Particularly useful for studying abstraction layers that preserve access to unusual format details. Supported read formats include ELF, Mach-O, PE/COFF, WebAssembly, XCOFF, and Unix archives; writing support is deliberately different for each format.

- **C2:** The `Object` trait supplies common section and symbol operations, while format-specific low-level APIs remain usable alongside it. Consumers can choose portability without losing access to raw structures. [Read API architecture](https://docs.rs/object/latest/object/read/index.html)
- **C3:** `ReadRef` supports both borrowed references into resident data and on-demand reads from storage. This makes avoiding copies and limiting I/O part of the parser interface rather than a separate implementation. [ReadRef contract](https://docs.rs/object/latest/object/read/trait.ReadRef.html)

The two linked API pages are the best entry points for comparing its unified interface with its storage abstraction.

### 3. [m4b/goblin](https://github.com/m4b/goblin)

**Rust — configurable native-binary parsers.** Study how one crate accommodates tooling, operating-system development, and constrained environments through feature selection and separate raw and interpreted representations.

- **C2:** Format and word-size features expose ELF, Mach-O, PE, TE, and archive support, including raw `repr(C)` definitions and configurations usable without the standard library. This supports consumers ranging from binary inspection tools to loaders. [Feature architecture](https://github.com/m4b/goblin)
- **C3:** Borrowed, endian-aware parsing limits copying, while ELF offers header-only and lazy construction paths so a consumer can choose which information to parse. These are explicit mechanisms, not a claim of benchmark superiority. [ELF parsing API](https://docs.rs/goblin/latest/goblin/elf/struct.Elf.html)

Start with the feature descriptions and `Elf::parse_header` / `Elf::lazy_parse` contracts.

### 4. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**C++ — JITLink and ORC ObjectLinkingLayer within the LLVM monorepo.** The relevant subsystem turns relocatable object files into executable memory. It is a strong study of runtime linking architecture rather than merely another compiler front end.

- **C1:** The generic link algorithm has distinct pruning, allocation, resolution, fixup, and finalization phases. Passes have phase-dependent constraints, failures propagate through the context, and finalization interacts with ORC's dependency tracking. [JITLink design](https://llvm.org/docs/JITLink.html)
- **C2:** `LinkGraph` represents content, symbols, and relocation edges across object formats. Plugins and replaceable memory managers let clients customize linking without duplicating each format backend. [Graph and plugin interfaces](https://llvm.org/docs/JITLink.html#linkgraph)
- **C3:** The design includes dead stripping, GOT/PLT relaxation, and continuations around potentially slow allocation, symbol lookup, and transfer operations. These mechanisms connect performance goals to explicit architectural stages. [Generic link algorithm](https://llvm.org/docs/JITLink.html#generic-link-algorithm)

Use the JITLink design document as the entry point; this entry counts LLVM only once.

## ELF and Mach-O specialists

### 5. [eliben/pyelftools](https://github.com/eliben/pyelftools)

**Python — ELF and DWARF parsing.** A useful example of translating specification-oriented binary structures into approachable high-level objects without making debug information inseparable from its container.

- **C1:** ELF loading includes section and segment interpretation and relocation of DWARF sections. The testing guide describes differential output checks against GNU `readelf` and reproducer unit tests for subtle DWARF behavior. [User guide](https://github.com/eliben/pyelftools/blob/main/doc/user-guide.md), [testing design](https://github.com/eliben/pyelftools/blob/main/doc/hacking-guide.md)
- **C2:** `ELFFile` accepts stream-like inputs, specialized section classes extend the generic section interface, and `DWARFInfo` can operate independently of ELF. [API layering](https://github.com/eliben/pyelftools/blob/main/doc/user-guide.md)
- **C4:** The changelog documents evolution from 2012 onward, including machine-dependent enum handling, compressed sections, DWARF5, and updated comparison tests. This establishes sustained compatibility work beyond repository age. [Change history](https://github.com/eliben/pyelftools/blob/main/CHANGES)

Start with the user and hacking guides.

### 6. [serge1/ELFIO](https://github.com/serge1/ELFIO)

**C++ — header-only ELF reader and producer; the repository also contains ARIO.** The selected subsystem is ELFIO. Study the difference between representing an ELF file and assigning a valid physical layout when writing it.

- **C1:** The writer computes segment alignment, orders overlapping section membership through its segment worklist, tracks generated sections, and separately lays out sections without segments. These are substantive layout invariants rather than header decoding alone. [ELF implementation](https://github.com/serge1/ELFIO/blob/main/elfio/elfio.hpp)
- **C2:** The `elfio` object provides sections, segments, headers, endian conversion, address translation, and an optional compression interface within a standalone library. Reading, generating, and modifying files share these representations. [Implementation and public interface](https://github.com/serge1/ELFIO/blob/main/elfio/elfio.hpp)

Start at `save`, `calc_segment_alignment`, and `layout_segments_and_their_sections` in the linked header.

### 7. [konrad-kruczynski/elfsharp](https://github.com/konrad-kruczynski/elfsharp)

**C# — managed ELF, UImage, and Mach-O readers.** A smaller alternative to compiler infrastructure, useful for studying typed binary models and stream ownership in a managed language.

- **C1:** The ELF implementation separates endian-aware reading, fields, string tables, sections, and segment headers. It explicitly records nonunique section names instead of silently treating the name index as one-to-one. [ELF implementation](https://github.com/konrad-kruczynski/elfsharp/blob/master/ELFSharp/ELF/ELF.cs)
- **C2:** Generic `ELF<T>` representations and the `IELF` interface expose typed and common views of sections, segments, machine flags, and entry points. [Typed API and parsing stages](https://github.com/konrad-kruczynski/elfsharp/blob/master/ELFSharp/ELF/ELF.cs)
- **C4:** The inspected 2020–2023 changelog records fixes for NOBITS sections, extended section numbering, big-endian Mach-O, and owned-stream cleanup after failed loads. The repository also identifies its test-binary corpus. [Changelog](https://github.com/konrad-kruczynski/elfsharp/blob/master/CHANGELOG.md)

The implementation and changelog are the entry points. The changelog's endpoint is not evidence of a current release cadence.

### 8. [blacktop/go-macho](https://github.com/blacktop/go-macho)

**Go — Mach-O parsing and creation, including platform runtime metadata.** Study how a format library extends beyond segment headers into information needed by Apple-platform analysis tools: Objective-C and Swift metadata, code signatures, and chained fixups.

- **C1:** Load-command decoding checks offsets before extracting names and reports command-specific errors. Swift decoding follows relative pointers and parent contexts while distinguishing descriptor kinds. [Mach-O parser](https://github.com/blacktop/go-macho/blob/master/file.go), [Swift metadata implementation](https://github.com/blacktop/go-macho/blob/master/swift.go)
- **C2:** A reusable `File` representation connects load commands and sections to runtime-language metadata and writing support. It extends Go's `debug/macho` use case substantially; it is not counted here as a second copy of the standard-library parser. [Project scope](https://github.com/blacktop/go-macho)

Start with `file.go` and then follow `swift.go` for a more specialized layer. Support for modern Objective-C metadata does not imply support for every historical ABI.

### 9. [Homebrew/ruby-macho](https://github.com/Homebrew/ruby-macho)

**Ruby — Mach-O and universal-binary inspection and modification.** Especially relevant to packaging tools that rewrite dylib identifiers, dependency paths, and rpaths.

- **C1:** Load-command insertion and replacement check the available header padding, update command counts and sizes, and preserve downstream offsets. The API documents when delaying field repopulation leaves an inconsistent object. [MachOFile implementation](https://raw.githubusercontent.com/Homebrew/ruby-macho/main/lib/macho/macho_file.rb)
- **C2:** Its structure DSL describes integer fields, strings, views, endianness, and serialization-related options, allowing many Mach-O structures to share the same representation machinery. [Structure DSL](https://github.com/Homebrew/ruby-macho/blob/main/machostructure-dsl-docs.md)

Those two files are useful entry points for contrasting declarative structure definitions with mutation invariants. The repository also explains why changing load commands invalidates signatures; its current overview includes ad-hoc signing support.

## PE and managed-executable libraries

### 10. [erocarrera/pefile](https://github.com/erocarrera/pefile)

**Python — PE inspection and limited modification.** Study a pragmatic parser designed to expose Windows header terminology while coping with unusual and malformed binaries.

- **C1:** `get_memory_mapped_image` distinguishes file offsets from virtual layout, optionally applies relocations, and permits limiting sections with extreme virtual addresses used to confuse analysis tools. Its documentation also makes the permanent effect of relocation explicit. [PE API](https://pefile.readthedocs.io/en/latest/modules/pefile.html)
- **C2:** The library exposes headers, sections, resources, imports, overlays, and address conversion through one reusable `PE` object, supporting analysis pipelines and file-inspection applications. [Repository capabilities and limitations](https://github.com/erocarrera/pefile)

Start with the PE API, especially mapped-image and RVA conversion methods. Modification does **not** automatically rearrange the file to make space for larger structures; that limit separates it from a rebuilding library.

### 11. [trailofbits/pe-parse](https://github.com/trailofbits/pe-parse)

**C/C++ — lightweight PE parsing library.** A focused example of putting input-access rules beneath format parsing rather than repeating pointer arithmetic throughout the parser.

- **C1:** `bounded_buffer` reads check offsets, widen arithmetic when checking multibyte accesses, and validate subviews using the remaining length. The implementation distinguishes owned file mappings from nonowning views. [Buffer implementation](https://raw.githubusercontent.com/trailofbits/pe-parse/master/pe-parser-library/src/buffer.cpp)
- **C2:** The parser converts file data into internal C++ container-backed representations and exposes a library API demonstrated by `dump-pe`; the bounded-buffer layer is reused across parsing operations. [Architectural overview](https://github.com/trailofbits/pe-parse)

Start with `buffer.cpp`, then use the repository's `dump-pe` example to trace how consumers traverse parsed information. The bounds-checking design is evidence of correctness work, not a proof that all malformed inputs are harmless.

### 12. [CasualX/pelite](https://github.com/CasualX/pelite)

**Rust — PE navigation with borrowed views and minimal allocation.** Study the separation between a file's on-disk organization and an image's loaded organization.

- **C1:** The `Pe` interface makes RVA, VA, file-offset conversion, minimum readable sizes, and alignment explicit. Directory access distinguishes an absent directory from corruption. [Pe trait](https://docs.rs/pelite/latest/pelite/pe64/trait.Pe.html)
- **C2:** `PeFile` and `PeView` implement a shared navigation interface, and wrapping types support 32-bit and 64-bit variants. [Crate architecture](https://docs.rs/pelite/latest/pelite/)
- **C3:** Memory-mapped inputs and borrowed views support the repository's zero-allocation reading goal. The address-conversion abstraction explains how this is achieved without requiring an eagerly allocated object for every structure. [Repository design](https://github.com/CasualX/pelite)

Start with the trait and crate documentation. Its inspected history includes ASLR-address and Rust compatibility fixes through 2025; this is not a promise of frequent releases. [History](https://github.com/CasualX/pelite/commits/master/)

### 13. [secana/PeNet](https://github.com/secana/PeNet)

**C# — native and managed PE parsing and analysis.** A useful study of separating storage choices from native headers, data directories, .NET structures, and signature-related interpretation.

- **C2:** `PeFile` composes specialized parser groups over `IRawFile`; buffer and stream constructors feed the same object model. Higher-level hashes and metadata are exposed through that model rather than separate command-line tools. [PeFile implementation](https://raw.githubusercontent.com/secana/PeNet/master/src/PeNet/PeFile.cs)
- **C3:** The parser-options documentation explains the memory and access tradeoffs among copied buffers, streams, and memory-mapped files. The implementation also caches derived values such as hashes. [Storage options](https://secana.github.io/PeNet/articles/parseroptions.html)

Start with those two sources. The options guide includes older examples: consult the implementation for exact current constructor and `TryParse` behavior, and distinguish modifications to a buffer from writes through a file-backed abstraction.

### 14. [Washi1337/AsmResolver](https://github.com/Washi1337/AsmResolver)

**C# — reading, constructing, and reconstructing native PE and .NET modules.** Study a layered binary writer that makes preservation policy explicit instead of treating serialization as the inverse of parsing.

- **C1:** `TemplatedPEFileBuilder` preserves existing sections and adds auxiliary sections when structures no longer fit. Import trampolines, TLS initialization, and relocation reconstruction illustrate how file layout and executable behavior interact. [PE building design](https://docs.washi.dev/asmresolver/guides/peimage/pe-building.html)
- **C2:** A tree of `ISegment` objects represents binary content; `SegmentBuilder` composes and aligns children, while virtual segments express differences between disk and memory sizes. Alternative builders share this infrastructure. [Segment architecture](https://docs.washi.dev/asmresolver/guides/core/segments.html)

The two guides are the entry points. The managed builder deliberately reconstructs a compact file, whereas the templated builder prioritizes preserving existing structure; neither policy should be assumed for the other.

### 15. [struppigel/PortEx](https://github.com/struppigel/PortEx)

**Java/Scala project targeting JVM applications — PE analysis with a malformation focus.** The verified canonical owner is `struppigel`; older references may use a previous owner name. Study how analysis-oriented parsing models what can actually be read from a suspicious file.

- **C1:** `SectionLoader` computes readable section extents using raw and virtual sizes, adjusted alignment, and low-alignment mode. It checks section validity against file extent instead of equating declared sizes with available bytes. [Section loading implementation](https://raw.githubusercontent.com/struppigel/PortEx/master/src/main/java/io/github/struppigel/parser/sections/SectionLoader.java)
- **C2:** The same loader mediates RVA conversion and specialized imports, exports, resources, relocations, and CLR structures. The library supplies structural anomaly analysis and extraction capabilities to separate CLI and GUI consumers. [Project overview](https://github.com/struppigel/PortEx)

Start with `SectionLoader`; its distinction between physical and virtual locations is more instructive than a feature checklist.

### 16. [jet2jet/pe-library-js](https://github.com/jet2jet/pe-library-js)

**TypeScript — PE parsing and generation for JavaScript applications.** A less prominent implementation worth comparing with native and managed-language libraries, particularly for packaging and resource-editing workflows.

- **C1:** `NtExecutable.from` validates DOS/NT headers, rejects unsupported symbol-table input, and rejects certificate-bearing executables unless an explicit option allows parsing them. Section handling accounts for alignment and empty raw data. These constraints make the accepted rewriting domain visible. [NtExecutable implementation](https://github.com/jet2jet/pe-library-js/blob/main/src/main/NtExecutable.ts)
- **C2:** The source separates executable and resource objects from typed format structures and binary-generation utilities; consumers operate on `ArrayBuffer`-style data rather than invoking platform tools. [Library organization](https://github.com/jet2jet/pe-library-js/tree/main/src/main)

Start with `NtExecutable.ts` and the adjacent resource layer. Parsing with `ignoreCert` is not evidence that an old signature remains valid after editing.

## Runtime and analysis loaders

### 17. [angr/cle](https://github.com/angr/cle)

**Python — analysis loader providing a simulated process-memory view.** CLE is not an operating-system mechanism for executing arbitrary loaded code. It loads binaries and dependencies into representations used by analysis consumers.

- **C1:** The loader manages architecture compatibility, rebasing, and nonoverlapping mappings. Its address-space allocator searches free gaps with progressively finer alignment and reports exhaustion; this is particularly relevant to small address spaces. [Loader implementation](https://raw.githubusercontent.com/angr/cle/master/cle/loader.py)
- **C2:** Format backends share a loader, memory representation, dependency handling, relocations, and TLS interfaces. ELF and PE parsers can be dependencies while CLE adds the independent process-level loading abstraction. [Backend and loader documentation](https://api.angr.io/projects/cle/en/latest/)

Start with `loader.py` and the documentation's backend interfaces. Support differs by backend; the README explicitly describes Mach-O support as limited.

### 18. [apple-oss-distributions/dyld](https://github.com/apple-oss-distributions/dyld)

**C++ and platform code — Apple's published dynamic-loader source distribution.** Treat this as Apple's source publication, not a claim that GitHub is the live internal development workflow. Study the `dyld` loader hierarchy and its relationship to cached loading state.

- **C1:** Loader state distinguishes weak or missing images, unload restrictions, pointer-authentication-aware references, and file validation using identity, timestamps, or code-directory hashes. These details constrain reuse of previously built loading information. [Loader interface and state](https://github.com/apple-oss-distributions/dyld/blob/main/dyld/Loader.h)
- **C2:** A common per-image `Loader` interface connects dependency search, symbol resolution, and mapped regions across several loader implementations. [Loader abstraction](https://github.com/apple-oss-distributions/dyld/blob/main/dyld/Loader.h)
- **C3:** The header explicitly distinguishes read-only memory-mapped `PrebuiltLoader` objects from allocated `JustInTimeLoader` objects and premapped images. That separation makes cached work and runtime work visible in the architecture.

Start with `dyld/Loader.h`; the repository's shared-cache and Mach-O directories provide the surrounding subsystem context.

### 19. [freebsd/freebsd-src](https://github.com/freebsd/freebsd-src)

**C and architecture-specific code — `libexec/rtld-elf` in the FreeBSD source tree.** This is the project's publish-only GitHub repository/mirror, as identified in its description. The selected subsystem is the ELF runtime linker, not the entire operating system.

- **C1:** Initialization can reenter loading through `dlopen`. `objlist_call_init` manages scanning and initialization state, while lookup and loading carry lock state and handle failure cleanup. TLS allocation, RELRO enforcement, and symbol versions add interacting correctness obligations. [Runtime linker implementation](https://raw.githubusercontent.com/freebsd/freebsd-src/main/libexec/rtld-elf/rtld.c)
- **C2:** Object dependency graphs, symbol-lookup requests, initialization lists, and loader APIs coordinate shared libraries across the process. They provide reusable internal structure around platform-specific relocation work. [Runtime linker implementation](https://raw.githubusercontent.com/freebsd/freebsd-src/main/libexec/rtld-elf/rtld.c)

Start with `dlopen_object`, `objlist_call_init`, and the symbol lookup helpers in `rtld.c`. This is a system-integrated loader, not a drop-in portable library.

### 20. [aosp-mirror/platform_bionic](https://github.com/aosp-mirror/platform_bionic)

**C/C++ and assembly — Android's dynamic linker within Bionic.** This is an official AOSP GitHub mirror. **The hosting organization is marked archived**, although substantive mirrored source remains available; it should not be presented as an actively maintained GitHub development venue. [Organization status](https://github.com/aosp-mirror)

- **C1:** The linker compatibility document explains dependency-search semantics, soname/path distinctions, symbol visibility, and rejection of text relocations. These are observable loading semantics that applications can accidentally depend on. [Linker changes and rationale](https://raw.githubusercontent.com/aosp-mirror/platform_bionic/main/android-changes-for-ndk-developers.md)
- **C4:** The same document tracks behavior across Android API generations and explains the policy of preserving or warning about older behavior below a target API threshold, then enforcing new rules above it. This is direct evidence of long-term compatibility management.
- **C3:** GNU symbol hashing and loading libraries directly from appropriately packaged APK contents are documented examples of lookup and loading costs shaping implementation choices.

Start with the linker changes document and the repository's maintainer overview. Only Bionic's `linker` subsystem is selected here.

### 21. [fancycode/MemoryModule](https://github.com/fancycode/MemoryModule)

**C — Windows EXE/DLL loading from a memory buffer.** A historical library implementation with an unusually compact path through the mechanics of loading. The inspected default-branch history ends in February 2019; retain it as a study reference without implying current Windows compatibility work. [History](https://github.com/fancycode/MemoryModule/commits/master/)

- **C1:** Loading connects base relocation, import resolution, section protection/discarding, TLS callbacks, and failure cleanup. The implementation runs TLS callbacks before the main entry path, making ordering constraints explicit. [Loader implementation](https://raw.githubusercontent.com/fancycode/MemoryModule/master/MemoryModule.c)
- **C2:** `MemoryLoadLibraryEx` accepts allocation and dependency-resolution callbacks, while export lookup supports names and ordinals. That is a reusable loader interface beyond the bundled demonstration. [Public API](https://raw.githubusercontent.com/fancycode/MemoryModule/master/MemoryModule.h)

Start with the implementation and header. This is not a claim of full equivalence to every service supplied by the Windows loader.

### 22. [weizhiao/Relink](https://github.com/weizhiao/Relink)

**Rust — ELF loader and runtime linker, published as `elf_loader`.** The canonical repository is now `Relink`; discovery results using `weizhiao/elf_loader` refer to this project. It covers shared objects, executable images, and selected relocatable-object targets, including `no_std` use cases.

- **C1:** `LinkContext` owns committed modules and dependency edges, and brands identifiers with a context identity to prevent accidental mixing of modules from different runtime/address-space contexts. [LinkContext design](https://docs.rs/elf_loader/latest/elf_loader/linker/struct.LinkContext.html)
- **C2:** Input, mapping, relocation, symbol scopes, dependency resolution, TLS, and observation hooks are separated into public modules. Consumers can supply policy for environments that do not match a conventional process-wide `dlopen`. [Crate architecture](https://docs.rs/elf_loader/latest/elf_loader/)

Start with the crate architecture and context contract. Documentation fetched during research spans published versions, so match API details to the chosen release. Architecture support is uneven: the repository explicitly distinguishes dynamic loading from object relocation and section-reordering support.

### 23. [erincandescent/elfload](https://github.com/erincandescent/elfload)

**C — compact embedded ELF loading library.** The smallest selection here, included for a distinct resource model rather than breadth or proven current maintenance. Its usefulness is in the callback-based mechanism and physical/virtual address separation.

- **C2:** An `el_ctx` holds loader state; the caller supplies positioned reads and allocation. Physical addresses are used for memory access while virtual addresses govern relocation, supporting loading before paging is enabled. [Context and address model](https://github.com/erincandescent/elfload)
- **C3:** The documented design intentionally minimizes cached binary metadata and rereads it as needed. The implementation's repeated program-header walks make the memory-versus-I/O tradeoff inspectable. [Loading and relocation implementation](https://raw.githubusercontent.com/erincandescent/elfload/master/elfload.c)

Start with the context description and `el_init` / `el_load` / `el_relocate`. The project explicitly lacks symbol resolution and dynamic linking. Current maintenance could not be established from the accessible history; no C4 or hostile-input-hardening claim is made.

### 24. [unikraft/app-elfloader](https://github.com/unikraft/app-elfloader)

**C — Linux ELF application loading within a Unikraft unikernel.** Study the boundary between loading a program image and providing the surrounding execution environment. The README documents static and dynamic PIE applications on x86-64; dynamic applications also use their conventional dynamic loader.

- **C1:** The implementation handles page-aligned mappings, the difference between file and memory segment sizes, anonymous zero-filled tails, and read failures. Its positioned-read loop retries interruption and rejects an unexpected end of file. [ELF loading implementation](https://raw.githubusercontent.com/unikraft/app-elfloader/staging/elf_load.c)
- **C2:** The implementation supports in-memory images and file-backed loading, with configuration-dependent mapping/read paths, allowing the same application loader to work with different Unikraft storage configurations. [Loader source](https://github.com/unikraft/app-elfloader/blob/staging/elf_load.c)

Start with `elf_load.c` and the repository's execution/debugging guide. The in-memory loading path rejects images requiring a program interpreter. This is a reusable application-loader component in the Unikraft environment, not an independent replacement for glibc's dynamic linker.

## Portable executable bytecode

### 25. [bytecodealliance/wasm-tools](https://github.com/bytecodealliance/wasm-tools)

**Rust — WebAssembly binary tooling libraries, especially `wasmparser` and validation.** The monorepo is counted once. This adds a portable executable format whose correctness obligations include typed instruction semantics rather than native relocation alone.

- **C1:** `Validator` carries module/component state and validates parser payloads against the WebAssembly specification. Its API explicitly separates receiving a function body from validating that body's contents and defines restrictions on resetting partially processed state. [Validator contract](https://docs.rs/wasmparser/latest/wasmparser/struct.Validator.html)
- **C2:** Parser events and validation are separate composable interfaces, so consumers can interleave their own work and inspect type information as validation progresses. [Parser API](https://docs.rs/wasmparser/latest/wasmparser/struct.Parser.html)
- **C3:** Both support incremental processing, and validation is designed to allow function bodies to be validated in parallel. The design avoids requiring every consumer to build a complete syntax tree before useful work begins.

Start with the parser and validator contracts. Parsing alone is not full semantic validation.

## Coverage, search method, and limits

Discovery used more than six distinct live search formulations, followed by repository opens and implementation/documentation inspection. Search angles included:

- Cross-format ELF/PE/Mach-O libraries and raw-versus-unified APIs.
- ELF runtime linking, relocations, and embedded loader callbacks.
- PE parsing, reconstruction, and malformed-file analysis in C++, C#, Java/Scala, and TypeScript.
- Python ELF/DWARF tooling and differential testing.
- Mach-O loading, Swift/Objective-C metadata, and Ruby packaging-oriented rewriting.
- Rust `no_std` loading and support for ARM, RISC-V, LoongArch, and Xtensa alongside x86.
- WebAssembly binary parsing, validation, and incremental/parallel processing.
- Smaller-language ecosystems and the availability/provenance of GNU/BSD format-library mirrors.

Later queries increasingly returned already identified libraries, thin inspection front ends, small experiments, or neighboring tooling. The final Ruby-focused follow-up added a distinct packaging community and language. Selection favors complementary mechanisms over listing every library implementing the same headers. Every retained repository's GitHub landing page was opened; each also has a separately opened primary implementation or technical-documentation source. Redirected names were resolved where observed.

Excluded were generic serialization frameworks, disassemblers without a selected format/loader subsystem, executable packers, injection demonstrations, tutorial-only loaders, thin platform-loading wrappers, and unverified personal mirrors. GNU BFD and elfutils are important neighboring libraries, but this search did not establish an appropriate official GitHub repository for inclusion; their omission is a hosting/evidence limitation, not a judgment of technical quality. Dedicated debug-only formats and complete language virtual machines were outside the chosen scope.

The report intentionally retains the historical MemoryModule implementation and labels the AOSP organization's archived status, FreeBSD's publish-only repository, and Apple's source distribution. It makes no general active-maintenance claim for the other selections. Some GitHub file views failed or exposed only partial source; successful raw-source or project-documentation reads supplied the substantive evidence instead. Documentation may describe a released version while a repository default branch has advanced, especially for Relink and PeNet. No candidate code was executed, no dependencies were installed, and no numerical performance comparisons were independently measured.
