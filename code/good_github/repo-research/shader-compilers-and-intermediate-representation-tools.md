# Shader compilers and intermediate representation tools

Research date: 2026-10-09.

This selection covers 23 GitHub repositories implementing shader languages, shader compilation and translation, shader-oriented intermediate representations, reflection, and compiler testing. It includes graphics and Vulkan compute shaders, plus production rendering languages. For larger repositories, only the named shader subsystem is evaluated. Historical implementations are included when they offer substantial, distinctive engineering material; their status is explicit. This is a guide to code worth studying, not a certification of correctness or a recommendation that every component is ready for production.

**Criteria legend:** **C1** — difficult correctness involving semantic invariants, concurrency, numerical behavior, malformed inputs, or failure modes. **C2** — substantial reusable abstractions supporting multiple uses. **C3** — concrete performance constraints addressed through understandable architecture. **C4** — sustained evolution with evidence of compatibility, testing, or complexity management. The criterion assessments below are grounded engineering judgments drawn from the linked primary material; they are not benchmark results.

## Language front ends and shader composition

### 1. [KhronosGroup/glslang](https://github.com/KhronosGroup/glslang)

**Language/role:** C++; reference GLSL/ESSL validation, AST construction, reflection, and SPIR-V generation.

Study how one compiler keeps language versions, profiles, shader stages, and target environments distinct while sharing its parser infrastructure. The repository describes separate front-end, AST-to-SPIR-V, and reflection components. Its HLSL front end is **deprecated as of April 2026**, so that component should be approached as legacy material. [Component and status documentation](https://github.com/KhronosGroup/glslang#glslang-components-and-status).

- **C1:** The compiler interface explicitly protects process-wide initialization state with a mutex and distinguishes language/profile/SPIR-V environments when creating parse contexts. These are real embedding and semantic invariants, beyond parsing a grammar.
- **C2:** Language-specific built-ins and parse contexts feed a shared intermediate representation and compiler/linker interface; validation, reflection, and code generation are separable uses.

**Implementation entry point:** [ShaderLang.cpp](https://raw.githubusercontent.com/KhronosGroup/glslang/main/glslang/MachineIndependent/ShaderLang.cpp), including initialization, parse-context construction, and version/profile indexing.

### 2. [microsoft/DirectXShaderCompiler](https://github.com/microsoft/DirectXShaderCompiler)

**Language/role:** C++; HLSL compiler, DXIL tooling, and SPIR-V generation, with a substantive LLVM/Clang-derived implementation.

Study the boundary between a source-language compiler and a driver-facing binary contract. DXC lowers higher-level HLSL constructs into DXIL, while separately exposing compilation, assembly, disassembly, linking, and validation components. [Repository overview](https://github.com/microsoft/DirectXShaderCompiler#features-and-goals).

- **C1:** DXIL restricts LLVM IR and couples instructions, metadata, shader models, and validation rules. Shader-model, DXIL, and bitcode versions are separate compatibility dimensions.
- **C2:** The high-level IR, lowering optimizer, linker, and validator form reusable components around a documented producer/consumer contract rather than a single executable-only pipeline.

**Design entry point:** [DXIL specification](https://raw.githubusercontent.com/microsoft/DirectXShaderCompiler/main/docs/DXIL.rst), especially the compilation diagram, versioning rules, and lowering of matrices, aggregates, and shader interfaces. This repository is counted separately from upstream LLVM because its shader implementation and evolution are substantive.

### 3. [shader-slang/slang](https://github.com/shader-slang/slang)

**Language/role:** C++; modular shading language and compiler supporting multiple target formats.

Slang is particularly useful for studying how shader specialization and composition become first-class compiler concepts. Its compilation guide distinguishes source units, translation units, serialized IR modules, entry points, targets, and host-visible parameter layouts. [Compilation model and API guide](https://github.com/shader-slang/slang/blob/master/docs/user-guide/08-compiling.md).

- **C1:** Host code and generated kernels must agree on target-dependent parameter layout and resource bindings. The compiler also separates source semantic checking from target capabilities and floating-point options.
- **C2:** Modules can be serialized and loaded from IR, while compilation sessions support multiple targets and application-specific compilation policies. This is substantial infrastructure for assembling large shader systems.

**Additional design entry point:** [Interfaces design](https://github.com/shader-slang/slang/blob/master/docs/design/interfaces.md), which explains the connection between generics, interface requirements, static specialization, and resource binding. It is a design document, so proposed details should be distinguished from the current user guide.

### 4. [gfx-rs/wgpu](https://github.com/gfx-rs/wgpu)

**Language/role:** Rust; the relevant subsystem is **Naga**, the shader translator and shared IR inside the wgpu monorepo.

Study an IR that deliberately separates pure expressions from statements with effects and structured control flow. This makes evaluation order explicit while allowing multiple shader front ends and back ends to share one module representation. The monorepo counts once; the former standalone Naga repository is not an additional entry.

- **C1:** Expression scope and evaluation time are documented invariants. Loads must observe the correct stores, derivatives must remain in suitable uniform control flow, and function-call results become available at their corresponding statements.
- **C2:** `Module`, typed arenas, functions, entry points, expressions, and statements provide reusable compiler structures shared across translation paths.
- **C3:** Back ends use expression reference counts and sensitivity to evaluation timing to decide when temporary values must be materialized, combining efficient output with semantic constraints.

**Implementation/design entry point:** [Naga IR definitions and explanatory module documentation](https://raw.githubusercontent.com/gfx-rs/wgpu/trunk/naga/src/ir/mod.rs).

### 5. [google/dawn](https://github.com/google/dawn)

**Language/role:** C++; **Tint** WGSL compiler subsystem. **Official GitHub mirror** of the Dawn repository hosted on googlesource.

Tint is a good comparison with Naga because its IR design explicitly responds to the cost and complexity of repeatedly rebuilding AST and semantic structures. Its mutable IR has blocks, values, instructions, and normalized structured control flow. [IR design](https://raw.githubusercontent.com/google/dawn/main/docs/tint/ir.md).

- **C1:** Terminator rules, transform capabilities, and IR validation make internal invariants explicit. The design distinguishes debug-time internal validation from production behavior.
- **C2:** Common transformations and backend-specific lowering share a module representation and builder; AST/IR conversion supports incremental replacement of older transformations.
- **C3:** In-place transforms address documented AST-reconstruction overhead, while normalizing loops reduces the number of forms each transformation must handle.

**Verification entry point:** [Tint testing guide](https://github.com/google/dawn/blob/main/docs/tint/testing.md), covering unit tests, complete translation flows, and shader validation/execution through the WebGPU CTS.

### 6. [google/angle](https://github.com/google/angle)

**Language/role:** Primarily C++; **shader compiler/translator** within the ANGLE graphics implementation. GitHub mirror of the Chromium-hosted project.

Study how compiler passes mediate between WebGL/ESSL semantics and the behavior of different native back ends. ANGLE documents using its shader compiler as both validator and translator, including transformations for driver quirks. [Shader translation context and upstream hosting](https://github.com/google/angle#angle---almost-native-graphics-layer-engine).

- **C1:** The compiler enforces expression-complexity limits and validates transformations; its pipeline also addresses initialization, indirect indexing, and platform-specific loop behavior. These are practical correctness concerns for browser-supplied shaders.
- **C2:** The compiler context, call-dependency analysis, common tree operations, and target-specific transformations separate shared language handling from backend adaptations.

**Implementation entry point:** [Compiler.cpp](https://raw.githubusercontent.com/google/angle/main/src/compiler/translator/Compiler.cpp), especially `limitExpressionComplexity`, the common transformation pipeline, and the individual `tree_ops` components referenced there. The whole graphics engine is not being rated here.

### 7. [AcademySoftwareFoundation/OpenShadingLanguage](https://github.com/AcademySoftwareFoundation/OpenShadingLanguage)

**Language/role:** C++; OSL compiler, intermediate code, and runtime shader-network optimization for production renderers.

OSL broadens the category beyond rasterization languages. Individual shaders produce intermediate code, while connected shader networks can be specialized and JIT-compiled with knowledge of runtime parameters. Radiance closures separate material descriptions from the renderer's integration strategy. [Architecture and language overview](https://github.com/AcademySoftwareFoundation/OpenShadingLanguage#how-osl-is-different).

- **C2:** Shader groups, lazy network evaluation, closures, and renderer interfaces support different material systems and rendering algorithms.
- **C3:** Runtime specialization and LLVM JIT compilation exploit information unavailable during source compilation; lazy evaluation avoids unnecessary shader layers.
- **C1/C4:** The multi-year changelog records numerical and compatibility maintenance, including 2023 constant-conversion and derivative fixes, later strict-FMA behavior for numerical consistency, and evolving LLVM support and CI coverage.

**Evolution entry point:** [CHANGES.md](https://github.com/AcademySoftwareFoundation/OpenShadingLanguage/blob/main/CHANGES.md). Released fixes are distinguishable from development-version entries; no numerical speedup claim is adopted here.

### 8. [HeapsIO/heaps](https://github.com/HeapsIO/heaps)

**Language/role:** Haxe; **HXSL** compiler and runtime shader linker inside the Heaps engine.

HXSL provides a useful engine-community counterpart to Slang: separately authored shader effects are linked at runtime according to requested outputs, then optimized and emitted for the target language. [HXSL language and pipeline documentation](https://github.com/HeapsIO/heaps/wiki/HXSL).

- **C1:** Linking checks that reads have preceding writes. The implementation reconciles shared variables, checks kinds and types, merges struct fields, and handles collisions without arbitrarily renaming vertex inputs.
- **C2:** Shader components, shared pipeline variables, per-instance parameters, and configurable outputs let the same effects participate in different material pipelines.
- **C3:** Compile-time shader constants and requested outputs enable removal of unreachable branches, unused textures, and computations that do not affect results.

**Implementation entry point:** [hxsl/Linker.hx](https://raw.githubusercontent.com/HeapsIO/heaps/master/hxsl/Linker.hx). Only HXSL is in scope; the old standalone `ncannasse/hxsl` project is not counted separately.

## SPIR-V processing and reflection libraries

### 9. [KhronosGroup/SPIRV-Tools](https://github.com/KhronosGroup/SPIRV-Tools)

**Language/role:** C++ with supporting Python; SPIR-V assembly, parsing, disassembly, validation, optimization, and related transformation tools.

Study the boundary between binary validity and semantics-preserving transformations, including how target environments constrain otherwise common IR processing. The repository exposes libraries as well as command-line tools. [Project overview](https://github.com/KhronosGroup/SPIRV-Tools#overview).

- **C1:** The optimizer validates input by default, can validate after transforms, and applies client-API rules in addition to the module's SPIR-V version. Its API explicitly warns that failed processing can leave invalid output.
- **C2:** Move-only pass tokens, ordered registration, diagnostics consumers, and target contexts provide reusable pass-pipeline abstractions.
- **C3:** Distinct performance, size, and HLSL-legalization recipes make optimization objectives and preconditions explicit; interface preservation constrains elimination.

**API/design entry point:** [optimizer.hpp](https://raw.githubusercontent.com/KhronosGroup/SPIRV-Tools/main/include/spirv-tools/optimizer.hpp). Fuzzing/reduction components belonging to this repository are not counted again as separate repositories.

### 10. [KhronosGroup/SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross)

**Language/role:** C++; SPIR-V-to-GLSL/HLSL/MSL translation and reflection.

Study the reconstruction of readable source languages from a binary interchange representation. The architecture exposes a parsed IR usable by both reflection and code generation, rather than tying all processing directly to the binary parser. [Supported translation and reflection roles](https://github.com/KhronosGroup/SPIRV-Cross#features).

- **C1:** The parsed IR tracks loop headers, merge blocks, continue relationships, decorations, and special constant/type ordering. Explicit iteration locks prevent unsafe mutation of typed-ID collections during traversal.
- **C2:** The parser-independent `ParsedIR` combines entry points, type/resource data, and decoration helpers for reuse across back ends and reflection clients.
- **C3:** Object pools and per-type ID collections address allocation and traversal costs without hiding the representation's ownership requirements.

**Implementation entry point:** [spirv_cross_parsed_ir.hpp](https://raw.githubusercontent.com/KhronosGroup/SPIRV-Cross/main/spirv_cross_parsed_ir.hpp), including copy semantics, indexing structures, and `LoopLock`.

### 11. [KhronosGroup/SPIRV-Reflect](https://github.com/KhronosGroup/SPIRV-Reflect)

**Language/role:** C with a C++ interface; shader reflection and descriptor-binding remapping.

This is a focused codebase for studying the relationship between shader bytecode and host-side pipeline layouts. It extracts descriptor bindings, push constants, buffer layouts, and shader inputs/outputs. It **assumes valid SPIR-V and is not a validator**. [API scope and limitations](https://github.com/KhronosGroup/SPIRV-Reflect#features).

- **C1:** Reflection must recover matrix/array strides, member decorations, access chains, and recursive physical-pointer structures. The implementation explicitly tracks previously visited physical-pointer structs to avoid infinite recursion.
- **C2:** The module-based reflection interface serves descriptor layout construction, host buffer updates, interface checking, and binding remapping.
- **C3:** An ID-to-node index replaces repeated node scans, while function and access-chain records support resource-use analysis.

**Implementation entry point:** [spirv_reflect.c](https://raw.githubusercontent.com/KhronosGroup/SPIRV-Reflect/main/spirv_reflect.c). Its defensive checks should not be mistaken for complete validation of hostile modules.

### 12. [gfx-rs/rspirv](https://github.com/gfx-rs/rspirv)

**Language/role:** Rust; native SPIR-V data representation, builder, parser, assembler, and disassembler.

Unlike a language binding around SPIRV-Tools, rspirv supplies its own processing implementation. It separates binary decoding, grammar-aware parsing, a consumer interface, and an in-memory representation. [Parser API](https://docs.rs/rspirv/latest/rspirv/binary/struct.Parser.html).

- **C1:** Parser states distinguish incomplete/incorrect headers, zero instruction word counts, unknown opcodes, missing/excess operands, unsupported types, and consumer failures. Errors retain instruction and byte-offset context.
- **C2:** Parsing can stream to a custom consumer or build the common representation through a loader; the same representation also supports programmatic construction and reassembly.

**Implementation entry point:** [Published parser source](https://docs.rs/rspirv/latest/src/rspirv/binary/parser.rs.html), including error modeling and grammar-driven operand handling. Some repository README version/status statements lag the published API; parsing support should not be equated with full SPIR-V semantic validation.

## Alternative source languages and research IRs

### 13. [Rust-GPU/rust-gpu](https://github.com/Rust-GPU/rust-gpu)

**Language/role:** Rust; a `rustc` code-generation backend producing SPIR-V, plus shader-library and build infrastructure.

Study the mismatch between general-purpose Rust compilation and shader restrictions. The project describes itself as early-stage and not production-ready; that limitation is material. Its compiler backend is the relevant subsystem, rather than its example applications. [Scope and status](https://github.com/Rust-GPU/rust-gpu#current-status-).

- **C1:** The linker pipeline contains storage-class inference, control-flow structurization, entry-interface handling, duplicate elimination, and handling of unsupported constructs. Linking multiple modules also requires consistent ID rewriting.
- **C2:** Distinct code-generation, linking, legalization, and SPIR-T pass components support multi-crate shaders and single- or multiple-module output.

**Implementation entry point:** [Compiler linker and pass organization](https://raw.githubusercontent.com/Rust-GPU/rust-gpu/main/crates/rustc_codegen_spirv/src/linker/mod.rs). This is the community repository; its earlier Embark home is not a second entry.

### 14. [Rust-GPU/spirt](https://github.com/Rust-GPU/spirt)

**Language/role:** Rust; SPIR-T, a research shader IR and transformation framework derived from SPIR-V.

SPIR-T is valuable for studying why an interchange format is not automatically an ideal optimizer representation. It separates interned attributes/types/constants from module-owned entities and provides SPIR-V lowering/lifting, traversal, linking, and control-flow restructuring. [API architecture](https://docs.rs/spirt/latest/spirt/).

- **C1:** Structured regions carry explicit inputs and outputs, including loop-carried values. Conversion between arbitrary control flow, structured regions, and SPIR-V requires careful preservation of data flow. The documentation also exposes unresolved representation limitations rather than claiming universal coverage.
- **C2:** Context interning, entity handles, visiting/transformation utilities, and independent passes provide a reusable substrate for shader legalization.
- **C3:** Interning deduplicates recurring data and supports indexed access throughout the IR.

**Detailed entry point:** [ControlRegionDef semantics](https://docs.rs/spirt/latest/spirt/struct.ControlRegionDef.html). The published documentation identifies this community continuation; the archived Embark repository is not counted separately. APIs remain research-oriented, and the OpenCL `Kernel` dialect is outside the stated short-term scope.

### 15. [shady-gang/shady](https://github.com/shady-gang/shady)

**Language/role:** C11 with Python generation; research shader IR, lowering framework, and Vcc LLVM-to-Vulkan compilation path.

Study a mostly immutable, structural IR with selected nominal mutable nodes, local uniformity analysis, and explicit reconvergence. JSON-described grammar and generated visitors/rewriters reduce repetitive implementation work. The README distinguishes working, planned, and untested capabilities; these should not be flattened into a claim of complete C/C++ shader support. [Architecture and scope](https://github.com/shady-gang/shady#shady).

- **C1:** Pointer simplification preserves pointee types and scopes. The folding code defines a canonical ordering of pointer casts specifically to avoid infinite rewrite loops.
- **C2:** Construction-time folding, general rewriters, and separately ordered pipelines support different lowering and experimentation needs.
- **C3:** Local folding performs simple optimizations during IR construction, reserving broader rewrites for explicit passes.

**Implementation entry point:** [src/shady/fold.c](https://github.com/shady-gang/shady/blob/main/src/shady/fold.c), especially memory-operation folding and canonical pointer chains.

### 16. [google/clspv](https://github.com/google/clspv)

**Language/role:** C++; OpenCL C to **Vulkan compute shaders**, implemented through LLVM module passes.

This belongs here because it targets Vulkan's shader execution environment, rather than merely producing OpenCL-flavored SPIR-V. It is useful for studying how a richer pointer and kernel-argument model is adapted to shader capabilities and resource bindings. [OpenCL C on Vulkan mapping](https://github.com/google/clspv/blob/main/docs/OpenCLCOnVulkan.md).

- **C1:** The mapping specifies variable-pointer capabilities, storage widths, Vulkan device requirements, descriptor types, and incompatible argument-layout options. Source-language acceptance and legal target output must be coordinated.
- **C2:** LLVM transformation passes and a documented host-visible mapping support reuse by runtime implementations; reflection information is embedded through non-semantic SPIR-V instructions.

**Entry point:** The mapping document above, followed by the repository's compiler/pass structure. Its opaque-pointer transition and replacement of the old descriptor-map API are concrete compatibility lessons. The conformance statement in the README applies to specified clvk/clspv tags, not every checkout or configuration.

## Driver-facing lowering and established translation pipelines

### 17. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language/role:** C++ and TableGen; specifically the **DirectX backend, DXILUpgrade, and shared DXIL utilities**.

Study a modern compiler's handling of an older bitcode contract. Upstream LLVM treats DXIL largely as an interchange representation: it lifts format-specific constructs into generic LLVM IR and introduces DXIL-specific forms late during emission. [DXIL architecture](https://llvm.org/docs/DirectX/DXILArchitecture.html).

- **C1:** The backend must reconcile contemporary LLVM types, attributes, operations, and metadata with LLVM-3.7-era DXIL encoding. Reading requires more than the generic bitcode upgrader.
- **C2:** Shared ABI definitions, translation utilities, analyses, IR-to-IR passes, and container readers/writers avoid duplicating conversion logic between producers and consumers.

**Design/testing entry point:** The architecture document identifies `DXILOpLowering`, `DXILPrepare`, metadata translation, the writer, and testing with `opt`/FileCheck. It explicitly records gaps in format round-trip testing. This entry does not rate all LLVM subsystems or imply feature parity with DXC.

### 18. [GPUOpen-Drivers/llpc](https://github.com/GPUOpen-Drivers/llpc)

**Language/role:** C++; LLVM-Based Pipeline Compiler for AMD GPUs. **Archived September 15, 2025; historical implementation.**

LLPC provides an unusually clear view of the division between Vulkan/SPIR-V handling, a reusable graphics middle end, and machine-code generation. Its front end combines shader modules into a pipeline IR; LGC lowers to AMDGPU intrinsics and PAL ABI metadata. [Compilation architecture](https://github.com/GPUOpen-Drivers/llpc/blob/dev/llpc/docs/LlpcOverview.md).

- **C1:** Shader-stage merging, register argument setup, and metadata generation must agree with GPU-generation-specific pipeline ABI rules.
- **C2:** The LGC builder/recorder interface separates API-specific translation from GPU-specific processing and the LLVM AMDGPU backend.
- **C3:** Partial-pipeline caching can reuse vertex or fragment portions independently. The cache key incorporates inter-stage input/output mappings, showing how performance depends on correct semantic cache boundaries.

**Entry point:** The overview above covers both the three-stage compiler and cache callback protocol. Treat the repository as a frozen architectural study, not a currently maintained driver component.

### 19. [HansKristian-Work/dxil-spirv](https://github.com/HansKristian-Work/dxil-spirv)

**Language/role:** C++; DXIL-to-SPIR-V translation for D3D12 translation layers, with a compact LLVM-compatible infrastructure subset.

Study a runtime-facing converter that must preserve DirectX shader behavior while expressing it through Vulkan. The project supplies a C integration boundary and a reference-shader regression workflow; its README also distinguishes public tests from private real-world reproducer collections. [Architecture, integration, and testing](https://github.com/HansKristian-Work/dxil-spirv#dxil-spirv).

- **C1:** Conversion coordinates root-signature resources, shader-stage metadata, required capabilities, and wave-size constraints. The implementation contains explicit compatibility conditions, such as multiview output-layer mappings.
- **C2:** A bitcode parser, converter, SPIR-V module builder, and public C API separate parsing and translation from application integration; the small LLVM API substitute also permits an alternate native-LLVM build.

**Implementation entry point:** [dxil_converter.cpp](https://raw.githubusercontent.com/HansKristian-Work/dxil-spirv/master/dxil_converter.cpp). No claim is made that the unavailable private reproducer suite was inspected.

### 20. [Unity-Technologies/HLSLcc](https://github.com/Unity-Technologies/HLSLcc)

**Language/role:** C++; DirectX bytecode cross-compiler to GLSL-family languages and Metal.

HLSLcc is a substantive evolution of HLSLCrossCompiler, with reorganized C++ code, multiple back ends, register type inference, loop reconstruction, and precision analysis. Those changes justify treating this implementation as its own project. Its Unity usage statements are historical project context, not evidence of every current Unity compilation path. [Implementation differences](https://github.com/Unity-Technologies/HLSLcc#hlslcc).

- **C1:** Typeless four-component registers require inferred types; partial-precision values and samplers require additional analysis. The entry path also checks duplicate constant-buffer names and rejects unsupported stage/backend combinations.
- **C2:** A decoded shader, shared translation context, reflection callbacks, and separate GLSL/Metal translators support multiple output languages and embedding scenarios.

**Implementation entry point:** [HLSLcc.cpp](https://raw.githubusercontent.com/Unity-Technologies/HLSLcc/master/src/HLSLcc.cpp), particularly `TranslateHLSLFromMem`. Maintenance cadence was not established, so this is an implementation-study selection rather than an assertion of current support.

### 21. [aras-p/glsl-optimizer](https://github.com/aras-p/glsl-optimizer)

**Language/role:** C++; Mesa-derived offline GLSL optimization with GLSL and Metal emission. **Historical:** the maintainer says significant development was unlikely after mid-2016.

This extraction is useful for studying optimization without a full graphics-driver stack. It preserves substantial Mesa compiler machinery while adding source emission and GLES precision handling; the project clearly attributes that ancestry. [Scope and maintenance notice](https://github.com/aras-p/glsl-optimizer#glsl-optimizer).

- **C1:** Precision propagation is explicit in the implementation: dereferences inherit variable precision, so rewriting the IR must preserve more than mathematical expression shape.
- **C2:** A target-aware optimization context, shader objects, reflection information, and configurable unroll limits expose reusable offline compilation facilities.
- **C3:** Inlining, propagation, dead-code elimination, and loop optimization address shader instruction count and source size, with a visible pass-oriented implementation.

**Implementation entry point:** [glsl_optimizer.cpp](https://raw.githubusercontent.com/aras-p/glsl-optimizer/master/src/glsl/glsl_optimizer.cpp). This is a distinct historical adaptation, not a substitute for current Mesa NIR or its hardware back ends.

## Compiler testing and reproducible shader failures

### 22. [google/graphicsfuzz](https://github.com/google/graphicsfuzz)

**Language/role:** Primarily Java and Python; metamorphic GLSL shader generation, reduction, and testing orchestration. **Archived December 8, 2025.**

GraphicsFuzz is useful for studying compiler correctness when a direct expected-output oracle is difficult to construct. The repository's GLSL tools generate related shaders and reduce failures; it also orchestrates SPIR-V tools whose implementations live in SPIRV-Tools. [Tool ownership and overview](https://github.com/google/graphicsfuzz#tool-documentation).

- **C1:** Wrong-image reduction requires preserving semantics, while crash reduction may permit semantic changes. Removing loop-control statements can introduce nontermination, so interestingness checks, timeouts, and reduction mode are part of correctness.
- **C2:** Shader jobs combine shader stages with metadata, and custom interestingness predicates allow the reducer to serve different compilers and failure classes.

**Algorithm/operation entry point:** [Reduction manual](https://raw.githubusercontent.com/google/graphicsfuzz/master/docs/glsl-fuzz-reduce.md), explaining preservation modes, image comparisons, retries, and when rendering must remain in the test loop. The archived status does not diminish its value as a testing architecture study.

### 23. [google/amber](https://github.com/google/amber)

**Language/role:** C++; shader execution and regression-test framework with a declarative test language.

Amber sits at the testing edge of this category: it makes shader-compiler failures reproducible by bundling shaders, pipeline state, inputs, and expected results. It accepts SPIR-V assembly/binary as well as higher-level shader sources. [Project purpose](https://github.com/google/amber#amber).

- **C1:** Tests must state device features, shader target environments, pipeline-stage restrictions, and numeric comparison tolerances. The script language distinguishes exact comparisons from tolerance, RMSE, and histogram-based comparisons.
- **C2:** Named shaders, buffers, pipelines, virtual files, and execution/expectation commands express many graphics and compute tests without requiring each reproducer to implement graphics-API setup.

**Design entry point:** [AmberScript specification](https://github.com/google/amber/blob/main/docs/amber_script.md), especially shader formats, target environments, pipeline rules, and `EXPECT`. The README labels Dawn support as work in progress; multi-API intent should not be read as equal backend completeness.

## Coverage, search method, and limits

Discovery used more than six distinct live-search formulations, including shader IR architecture; WGSL/Naga/Tint; LLVM/DXIL and AMD pipeline compilation; SPIR-V parsing/reflection/optimization; Rust shader back ends and SPIR-T; legacy HLSL/GLSL cross-compilation; metamorphic compiler testing; research C shader IRs; production OSL; and Haxe/HXSL composition. Later broad and small-project queries increasingly repeated DXC, Shady, and compiler-integration wrappers; the Haxe search added the distinct HXSL subsystem. Repository roots were opened to verify canonical GitHub identities, and every retained entry has an additional opened primary document or source implementation. Some raw-file requests failed; retained citations use successfully opened alternatives, including project-generated Rust API/source documentation.

The resulting selection spans C++, C, Rust, Haxe, and Java/Python testing infrastructure; standards organizations, browser projects, GPU/OS vendors, rendering studios, game-engine communities, and research implementations. C4 is only assigned where multi-year change and compatibility/testing evidence was actually inspected. A repository being public, recently indexed, or unarchived is not treated as proof of active maintenance.

Important boundaries and exclusions:

- Current Mesa NIR/ACO/NAK and Wine shader infrastructure are important ecosystem areas, but this report did not establish a qualifying official GitHub mirror for their primary projects. They are not represented by arbitrary third-party mirrors.
- Naga, Tint, HXSL, and LLVM are counted at their containing-repository level. Earlier standalone or former-owner copies are not extra entries. SPIR-T uses the community continuation identified by its published documentation; the archived Embark copy is excluded from the count.
- General GPU compute frameworks, shader asset collections, editors, awesome-lists, generated bindings, and thin command-line integration wrappers were not added merely to enlarge the list. Clspv is retained specifically because its output is Vulkan compute-shader SPIR-V.
- GraphicsFuzz and Amber are deliberately limited testing-tool inclusions. Their value here is shader transformation correctness and reproducible compiler/IR failures, not general test infrastructure.
- This was read-only source/document research. No candidate repository was cloned, built, benchmarked, or executed. Source branches and `latest` API documentation can change after the research date, and documented feature support is not independently validated on hardware.
