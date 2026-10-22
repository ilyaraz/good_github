# SIMD abstraction and vectorization libraries

Research date: **2026-10-09**.

This report selects 24 GitHub repositories implementing reusable SIMD interfaces, instruction-set portability layers, vectorized mathematical primitives, or library-driven loop vectorization. It covers C/C++, Rust, Julia, C#, and Java, including fixed-width and scalable-vector designs. The OpenJDK entry concerns only its Vector API subsystem. This is a guide to engineering ideas worth studying, not a benchmark ranking or a claim that every component is equally robust.

Criteria legend:

- **C1 — Difficult correctness:** numerical semantics, masks, memory bounds, alignment, instruction availability, or other nontrivial invariants.
- **C2 — Reusable abstractions:** substantial interfaces or mechanisms serving multiple algorithms and applications.
- **C3 — Performance with structure:** concrete performance constraints addressed through understandable implementation boundaries.
- **C4 — Sustained evolution:** multiyear evidence of compatibility work, testing, or complexity management, beyond repository age alone.

Repository headings link to canonical GitHub pages opened during research. Additional links identify primary material that was also opened and read. Criteria describe evidence in those materials; judgments about what engineers can learn are grounded interpretations.

## General-purpose C++ vector abstractions

### 1. [google/highway](https://github.com/google/highway)

**Language/role:** C++; portable SIMD with target multiversioning and runtime dispatch.

Highway is particularly useful for studying an interface that accommodates both conventional registers and Arm SVE/RISC-V variable-length vectors. Its implementation separates target-independent operations from architecture headers, and uses descriptor types to select lane types and vector sizes without storing runtime descriptor objects.

- **C2:** The descriptor/vector distinction supplies a common vocabulary for loads, arithmetic, conversions, and other algorithms across targets. Sizeless native types on scalable-vector machines influence the abstraction itself.
- **C3:** Re-includable headers and target-specific namespaces allow multiple implementations of one function in a binary. Common operations are composed above architecture primitives, making the tradeoff between shared implementation and specialization visible.

**Entry point:** The [implementation design](https://raw.githubusercontent.com/google/highway/master/g3doc/impl_details.md) explains descriptors, overload selection, per-target inclusion, backend organization, and tests instantiated across lane types and targets.

### 2. [xtensor-stack/xsimd](https://github.com/xtensor-stack/xsimd)

**Language/role:** C++; typed batches, mathematical functions, architecture selection, and dispatch.

xsimd is a useful study in integrating explicit vector operations into ordinary numeric C++ code. Its architecture machinery makes the difference between compiler-enabled instruction sets and features available on the executing processor explicit.

- **C2:** Numeric and Boolean batches, complex-number support, memory operations, and math functions form a reusable interface rather than a collection of isolated kernels.
- **C3:** Ordered architecture lists filter compile-supported backends; the dispatcher traverses candidates using runtime availability. Alignment information and fallback selection are part of the same machinery. See [architecture and dispatch implementation](https://raw.githubusercontent.com/xtensor-stack/xsimd/master/include/xsimd/config/xsimd_arch.hpp).
- **C1:** The [changelog](https://raw.githubusercontent.com/xtensor-stack/xsimd/master/Changelog.rst) documents concrete semantic hazards: SVE dispatch ODR violations, vector-length detection, under-aligned stores, mask bugs, and fast-math reassociation barriers. These are valuable regression-study starting points, not evidence that every backend is interchangeable in every detail.

### 3. [jfalcou/eve](https://github.com/jfalcou/eve)

**Language/role:** C++20; expressive vector types and numerical algorithms.

EVE is especially interesting for its callable/options architecture: numerical behavior is selected through decorators while lane compatibility and scalar/vector mixing are constrained by the type system. Its README presents a research-oriented project that permits API evolution; do not assume a frozen interface.

- **C1:** Addition alone exposes saturation, directed rounding, widening, and compensated variants. The interface discusses the non-associativity of saturation and constrains participating lane counts.
- **C2:** The same callable machinery handles ordinary operands, tuples, masks, and semantic options, allowing a large numerical API to share conventions.
- **C3:** Generic callable definitions connect to architecture-specific implementations rather than duplicating the entire public API for each instruction set.

**Entry point:** The [addition interface and backend wiring](https://raw.githubusercontent.com/jfalcou/eve/main/include/eve/module/core/regular/add.hpp) is a compact example of all three concerns.

### 4. [vectorclass/version2](https://github.com/vectorclass/version2)

**Language/role:** C++; Agner Fog's x86 vector class library.

This deliberately x86-focused library is worth studying for the relationship between logical vector width and physical register width. It retains a wide-vector programming interface when an implementation must use narrower instructions.

- **C2:** Vector classes, masks, arithmetic, permutations, and memory operations let algorithms express vector intent without spelling every intrinsic.
- **C3:** The emulated `Vec8f` implementation stores two `Vec4f` halves and implements operations by composing them. This makes the cost and structure of width emulation unusually easy to inspect.
- **C1:** Partial loads/stores split work between halves and handle inactive elements explicitly; floating-point operations also expose details such as signed-zero-preserving sign manipulation.

**Entry point:** Read [the 256-bit floating-point emulation header](https://github.com/vectorclass/version2/blob/master/vectorf256e.h), particularly `Vec8f`, its memory methods, and arithmetic operators. This is an x86 design reference, not a cross-architecture portability layer.

### 5. [VcDevel/Vc](https://github.com/VcDevel/Vc)

**Language/role:** C++; typed SIMD vectors and portable data-parallel programming. **Maintenance mode:** the repository explicitly states that active development has stopped while bug-fix contributions remain welcome.

Vc remains useful as a historical design study in the promises a vector abstraction can realistically make across compilers and instruction sets.

- **C2:** Vector types, masks, scalar fallback, and higher-level SIMD facilities provide a coherent programming model for reusable algorithms.
- **C1:** Its portability documentation distinguishes guaranteed lane relationships from hardware-dependent properties. It explains that narrow integer types may use wider intermediate representations, so overflow behavior can differ before values reach memory. It also discusses runtime instruction support and ABI/alignment problems when passing vector objects by value.
- **C3:** Those portability choices expose the cost of translating a convenient C++ interface onto compiler calling conventions and physical register types.

**Entry point:** The [Vc 1.4 portability guide](https://vcdevel.github.io/Vc-1.4/portability.html) is more informative than treating the old API as a drop-in contemporary recommendation.

### 6. [p12tic/libsimdpp](https://github.com/p12tic/libsimdpp)

**Language/role:** C++; portable intrinsic-style operations and multi-architecture dispatch.

libsimdpp is a strong study of deployment mechanics: how separately compiled ISA variants coexist, how callers reach the correct one, and how templates interact with dispatch. Its published compiler-support material is dated; this report makes no current-maintenance claim.

- **C2:** The abstraction includes arithmetic, conversions, shuffles, interleaving, and emulation of operations missing from a target ISA.
- **C1:** ISA-specific namespaces prevent ODR collisions. Dispatch emission and explicit template instantiation have rules that matter for linking, and the documentation describes race-free first-call dispatcher initialization.
- **C3:** Each implementation can be compiled with its own target flags while callers use a common entry point; dispatch is isolated from the algorithm body.

**Entry points:** The [library documentation](https://p12tic.github.io/libsimdpp/v2.2-dev/libsimdpp/w/) and detailed [dispatch architecture guide](https://p12tic.github.io/libsimdpp/v2.2-dev/libsimdpp/w/arch/dispatch.html).

### 7. [aff3ct/MIPP](https://github.com/aff3ct/MIPP)

**Language/role:** C++; portable SIMD wrappers developed in the AFF3CT community.

MIPP offers both a lower-level register API and an object-oriented interface. It is useful for tracing how a relatively approachable wrapper preserves access to specialized operations while supporting sequential execution.

- **C2:** `Reg<T>`, masks, half-width registers, and paired registers provide reusable types for numerical and data-movement algorithms. The API includes operations such as transposition and compression, beyond basic arithmetic.
- **C3:** The object layer delegates to lower-level operations; under the no-intrinsics configuration, a register object holds a scalar instead. This provides a clear seam for comparing vector and sequential implementations. Some compression support uses separately generated lookup tables, and successful inlining matters to performance.

**Entry point:** [The object wrapper implementation](https://github.com/aff3ct/MIPP/blob/master/include/mipp_object.hxx) shows `Reg`, conditional scalar storage, conversions, and transpose forwarding. The repository labels its SVE support as length-specific and work in progress; avoid assuming general vector-length-agnostic support.

### 8. [agenium-scale/nsimd](https://github.com/agenium-scale/nsimd)

**Language/role:** C/C++ interfaces with Python generation; portable SIMD and SPMD-style programming.

NSIMD spans low-level operations and a higher-level kernel language. The latter is an instructive example of encoding per-lane control flow in an existing language while targeting CPU SIMD and GPU execution.

- **C1:** On CPUs, the SPMD layer represents divergent control flow with masks. Its assignment and store macros preserve inactive lanes; ordinary C++ assignments inside a masked region can violate that model. Unmasked operations require stronger assumptions.
- **C2:** Multiple C/C++ interface levels and the kernel DSL support both individual vector operations and larger algorithms.
- **C3:** The implementation distinguishes small inline operations from larger compiled functions. Kernel launch parameters map to CPU unrolling or GPU block dimensions, exposing target-specific tuning through a shared structure.

**Entry point:** The [SPMD module guide](https://agenium-scale.github.io/nsimd/module_spmd_overview.html) explains masking, control flow, memory operations, and launch behavior with concrete examples.

### 9. [root-project/veccore](https://github.com/root-project/veccore)

**Language/role:** C++; a common interface over SIMD backends for scientific software.

VecCore is worth studying when algorithms need to support both true scalars and several vector libraries. Its abstraction focuses on shared traits and operations instead of imposing an additional owning vector representation.

- **C2:** Backends expose vector types through aliases, while `Scalar<T>`, `Mask<T>`, and `Index<T>` let generic algorithms discover associated types. The same interface covers gather/scatter, reductions, and scalar fallback.
- **C1:** Comparisons return backend-dependent mask types, so generic code must not assume Boolean results. `Get`/`Set` also avoid assuming that every backend type supports vector-style indexing, an important invariant when scalars participate.
- **C3:** Direct backend aliases and lightweight operation forwarding keep the abstraction boundary visible and reduce unnecessary representation conversions.

**Entry point:** The [API specification](https://github.com/root-project/veccore/blob/master/doc/api.md) describes the backend contract, masks, lane access, and memory operations.

### 10. [mattkretz/vir-simd](https://github.com/mattkretz/vir-simd)

**Language/role:** C++; fallback and extensions for `std::experimental::simd` from Parallelism TS 2.

This smaller project is useful for examining the space between a standard-library SIMD type and usable SIMD algorithms. It selects an available standard-library implementation or supplies scalar/fixed-size fallback behavior. Some extensions, including `simdize`, are explicitly experimental.

- **C2:** Permutations, mask/bitset conversions, resizing, aggregate transformations, and a SIMD execution policy extend the base vector vocabulary to ordinary algorithms.
- **C3:** Execution-policy modifiers select chunk size, unrolling, alignment prologues, and assumptions that eliminate epilogues. Their documented preconditions make code-size and memory-access tradeoffs concrete; the fallback is not a promise of hardware acceleration.

**Entry points:** The repository's detailed execution-policy documentation and its [standard-library identification probe](https://github.com/mattkretz/vir-simd/blob/master/stdlibtest.cpp). The latter distinguishes libstdc++ and libc++ versions, illustrating the compatibility boundary. Evidence here is stronger for public design than for internal algorithm implementation, because several deeper source pages could not be retrieved.

### 11. [db-tu-dresden/TSL](https://github.com/db-tu-dresden/TSL)

**Language/role:** Python generator and C++ Template SIMD Library.

TSL is included for its substantive generator implementation and architecture, rather than merely for generated wrappers. Primitive definitions, target descriptions, and templates are separate inputs to a pipeline that produces a tailored SIMD library.

- **C2:** Hardware-independent primitives and extension descriptions support reusable kernels while allowing the API and implementation templates to evolve together.
- **C3:** Generation can select architectures, operations, and data types, reducing irrelevant library material. The generator chooses among applicable implementations using hardware-capability information.
- **C1:** Input validation and generated tests address a second correctness surface: the generator must emit consistent declarations, definitions, and target combinations. The authors explain dependency-aware test generation.

**Entry point:** The authors' [framework paper, especially sections 3–4](https://arxiv.org/html/2407.18728v1), details the pipeline, selection heuristics, templates, and testing. Performance observations in the paper concern its evaluated cases, not a universal superiority claim.

## Instruction-set translation and semantic compatibility

### 12. [simd-everywhere/simde](https://github.com/simd-everywhere/simde)

**Language/role:** C/C++; implementations of intrinsic APIs on other instruction sets.

SIMDe is a rich study of preserving an existing ISA-shaped API across native instructions, another architecture's intrinsics, compiler vector extensions, and scalar fallback. Unlike a lowest-common-denominator API, it must account for quirks of the source instruction set.

- **C1:** Scalar-lane SSE operations must retain the upper lanes and avoid generating floating-point exceptions from irrelevant values. The implementation broadcasts the active lane in one fallback path specifically to avoid such spurious exceptions.
- **C2:** Optional native aliases and intrinsic-compatible interfaces let existing kernels migrate incrementally.
- **C3:** One operation may forward directly on x86, use NEON/Wasm/POWER/LoongArch instructions elsewhere, or fall back to a vectorizable loop.

**Entry point:** [The SSE implementation](https://github.com/simd-everywhere/simde/blob/master/simde/x86/sse.h), particularly `simde_mm_add_ps`, `simde_mm_add_ss`, and the low-lane broadcast helper, makes these implementation choices explicit.

### 13. [DLTcollab/sse2neon](https://github.com/DLTcollab/sse2neon)

**Language/role:** C/C++; SSE intrinsics translated to Arm NEON.

This narrower compatibility layer is useful for studying where apparently equivalent machine instructions disagree. The README explains how reciprocal-square-root refinement can turn a zero input into a NaN, and provides precision configuration switches for several operation families.

- **C1:** Floating-point exceptional values, rounding, NaN behavior, and allocator pairing have explicit caveats. Precision switches improve particular behaviors but do not establish complete SSE equivalence in every environment.
- **C3:** Direct NEON mappings and optional more precise implementations expose the cost of emulating source-ISA semantics while preserving a recognizable intrinsic interface.
- **C2:** The header supports reuse of a broad family of existing SSE kernels rather than implementing one application algorithm.

**Entry point:** The [testing guide](https://github.com/DLTcollab/sse2neon/blob/master/tests/README.md) describes reference-versus-NEON checks, test registration, and pass/fail/unimplemented results. Its little-endian scope and the README's platform/ABI restrictions matter when selecting it.

### 14. [howjmay/neon2rvv](https://github.com/howjmay/neon2rvv)

**Language/role:** C/C++; Arm NEON intrinsics implemented using RISC-V Vector instructions.

neon2rvv provides a less common architecture pairing and a useful contrast to SSE-to-NEON translation. Fixed NEON vector shapes must be represented using RVV types, while preserving arithmetic details.

- **C1:** The implementation contains explicit saturation helpers, rounding-mode choices, and configurable strict handling for extended multiply semantics. These show why a port requires more than replacing intrinsic names.
- **C2:** NEON vector/tuple types and a broad intrinsic surface provide an abstraction for porting many existing Arm kernels.
- **C3:** RVV vector types and operations are the implementation substrate, with compile-time vector-length checks controlling supported configurations.

**Entry point:** [The implementation header](https://raw.githubusercontent.com/howjmay/neon2rvv/main/neon2rvv.h). The README calls support preliminary and emphasizes RV64 with VLEN 128, while the inspected header accepts minimum vector lengths of 128, 256, or 512. Treat that mismatch as a verification requirement, not proof of unrestricted scalable-vector support.

## Rust interfaces, dispatch, and safety boundaries

### 15. [rust-lang/portable-simd](https://github.com/rust-lang/portable-simd)

**Language/role:** Rust; development of the portable SIMD API exposed through `core::simd`/`std::simd`. **Status:** the inspected API documentation still marks it nightly-only and experimental.

The project is useful for studying language-level semantic promises rather than simply wrapping each platform's fastest instruction.

- **C1:** Portable operations can intentionally differ from a similarly named intrinsic: floating-point minimum semantics are an example. Documentation also identifies exceptions involving subnormal flushing on some older targets, and does not promise a fixed mask representation.
- **C2:** `Simd<T, N>`, masks, comparisons, conversions, and numeric traits offer a common programming model across element types and lane counts.
- **C3:** Operations can lower to hardware vectors or scalar code, so semantic portability does not imply a particular instruction sequence.

**Entry point:** The official [portable SIMD module documentation](https://doc.rust-lang.org/stable/core/simd/) explains these guarantees and limitations. The `/stable/` documentation URL does not mean the feature itself is stabilized.

### 16. [sarah-quinones/pulp](https://github.com/sarah-quinones/pulp)

**Language/role:** Rust; safe SIMD abstractions with runtime CPU dispatch.

pulp is a useful study of capability tokens: possessing a backend value can represent that the processor supports the instructions needed by operations on that backend. Its generic kernel interface also keeps dispatch outside the mathematical loop.

- **C1:** The x86 `V3` token has a checked constructor returning `None` when required features are absent. Its unchecked constructor explicitly transfers that obligation to the caller. This makes instruction availability a visible API invariant.
- **C2:** `WithSimd`, the `Simd` trait, complex-number operations, and slice-to-vector chunk helpers support reusable numerical kernels with scalar remainders.
- **C3:** `Arch::dispatch` selects a specialized implementation while the algorithm is expressed through a common trait.

**Entry point:** The [V3 API and constructor safety contract](https://docs.rs/pulp/latest/pulp/x86/struct.V3.html) show the token's feature set and its checked/unchecked construction boundary.

### 17. [Lokathor/wide](https://github.com/Lokathor/wide)

**Language/role:** Rust; convenient fixed-width numeric vector types.

wide is valuable for studying an intentionally simpler deployment model. The README states that instruction selection happens at compile time; enabling runtime CPU detection alone does not change the implementation selected by the crate.

- **C2:** Types such as `f32x4` expose arithmetic, comparisons, bit operations, and mathematical helpers through normal Rust operators and methods.
- **C3:** The implementation selects an SSE, Wasm SIMD, AArch64 NEON, or fallback representation with configuration macros, then implements the same operation against that representation. This keeps platform specialization local to each vector type.
- **C1:** Comparison results and bitwise floating-point operations require deliberate bit representations: the fallback constructs all-bits-set comparison lanes rather than ordinary floating-point `1.0` values.

**Entry point:** [The `f32x4` implementation](https://raw.githubusercontent.com/Lokathor/wide/main/src/f32x4_.rs) exposes representation choices and per-backend operators directly.

### 18. [arduano/simdeez](https://github.com/arduano/simdeez)

**Language/role:** Rust; generic SIMD kernels with compile-time and runtime dispatch.

This is the repository identified by its README as the maintained continuation of the original jackmott project; the old repository is not counted separately. Study how one generic kernel can target multiple SIMD backends without copying its algorithm.

- **C2:** Backend traits and generation/dispatch macros support scalar, x86, Arm, and Wasm implementations behind a common kernel structure.
- **C1:** Math maintenance explicitly includes scalar-lane repair for exceptional cases and precision-sensitive behavior. Some double-precision functions deliberately retain scalar-reference or mixed implementations.
- **C3:** Portable vector math is the default; backend overrides are introduced when justified by profiling. Dispatch glue, public API, and math implementations have separate responsibilities.

**Entry point:** The [SIMD math architecture guide](https://raw.githubusercontent.com/arduano/simdeez/master/SIMD_MATH.md) explains portable kernels, specialized overrides, exceptional-value handling, and why a SIMD-shaped API need not imply every path is fully vectorized.

### 19. [linebender/fearless_simd](https://github.com/linebender/fearless_simd)

**Language/role:** Rust; safe architecture-specific intrinsics, portable vectors, and kernel dispatch.

Fearless SIMD provides several abstraction levels, from backend tokens to fixed/native-width vectors and kernel macros. That layering is useful for understanding how ergonomic safety and explicit performance control can coexist.

- **C1:** Architecture tokens and checked dispatch establish that required instructions are available. Slice chunking separates complete vector chunks from a remainder instead of silently assuming divisible input lengths.
- **C2:** Direct intrinsic access, portable vectors, and optional procedural macros support different kernel styles within one design.
- **C3:** Dispatch selects among CPU levels; generated repetitive code supports multiple vector forms while common kernel logic stays readable. Wasm deployment has a distinct constraint: the documentation discusses separate bundles rather than ordinary runtime feature dispatch.

**Entry point:** The [core crate guide](https://github.com/linebender/fearless_simd/blob/main/fearless_simd/README.md) explains tokens, kernels, dispatch levels, and slice handling. This report does not infer long-term maturity from the project's earlier experimental history.

## Julia and managed-runtime vectorization

### 20. [eschnett/SIMD.jl](https://github.com/eschnett/SIMD.jl)

**Language/role:** Julia; explicit LLVM-backed SIMD values and array operations.

SIMD.jl shows how a dynamic-language ecosystem can expose explicit vector operations while retaining ordinary scalar arrays. It also makes the interaction between bounds checking, garbage collection, and pointer-based vector memory access concrete.

- **C2:** Immutable `Vec` values, reductions, overflow/saturating operations, gather/scatter, and `VecRange` indexing support many algorithms without requiring an application-specific array container.
- **C1:** Array overloads perform bounds checks and preserve the array against garbage collection while deriving and using pointers. Pointer overloads and `@inbounds` carry different caller obligations; masking should not be mistaken for automatically relaxing every array bounds check.
- **C3:** Aligned, non-temporal, and masked operations forward to LLVM intrinsics, with separate methods for contiguous arrays and pointer access.

**Entry point:** [Array-operation implementation](https://raw.githubusercontent.com/eschnett/SIMD.jl/master/src/arrayops.jl). GPU support is explicitly experimental in the README, with OpenCL the stated CI-tested backend.

### 21. [JuliaSIMD/LoopVectorization.jl](https://github.com/JuliaSIMD/LoopVectorization.jl)

**Language/role:** Julia; macro-driven loop optimization and vectorization.

LoopVectorization operates above explicit registers: it models loops, chooses an execution strategy, and emits optimized code. It is a substantial example of compiler-like engineering packaged as a reusable library.

- **C1:** `@turbo` imposes meaningful obligations concerning bounds, empty iteration spaces, and iteration independence. Reordering is unsafe when an algorithm relies on a particular execution order.
- **C2:** The interface applies to loop nests and numerical array operations rather than a fixed list of mathematical kernels.
- **C3:** Its strategy search considers loop order, vectorization, and unrolling, using estimates involving latency, reciprocal throughput, register pressure, and memory layout. Unrolling can create independent reduction chains.

**Entry point:** The [strategy-selection design](https://juliasimd.github.io/LoopVectorization.jl/latest/devdocs/evaluating_loops/) explains that model. The repository's maintenance notice describes SciML-supported compatibility work; do not interpret this as unrestricted support for all future Julia versions or array types.

### 22. [zyl910/VectorTraits](https://github.com/zyl910/VectorTraits)

**Language/role:** C#; portable enhancements to .NET vector types.

VectorTraits addresses the mismatch between available SIMD instructions and the operations exposed by different .NET releases. It supplies shifts, shuffles, saturating narrowing, interleaving, and other operations across variable and fixed-width vector types.

- **C2:** Shared traits and utility classes cover `Vector<T>` and fixed-width vectors, with architecture-specific implementations for x86, Arm, and Wasm. This helps algorithms span runtime versions and register widths.
- **C3:** `_Args`/`_Core` operation pairs move reusable preparation outside a loop, while acceleration-reporting properties expose which element types have optimized implementations. The README illustrates resulting instruction sequences.
- **C1:** The [changelog](https://github.com/zyl910/VectorTraits/blob/main/ChangeLog.md) documents compatibility boundaries, including Native AOT reflection changes and extended integer-vector behavior that does not work uniformly across .NET versions. It also records Wasm unit-test/benchmark infrastructure.

**Entry points:** The repository's architecture and `_Args`/`_Core` examples, plus the linked changelog. Runtime and type support must be checked per operation.

### 23. [openjdk/jdk](https://github.com/openjdk/jdk)

**Language/role:** Java API with JVM integration; specifically the `jdk.incubator.vector` subsystem. The monorepo is counted once, not as a general endorsement of all JDK code.

The Vector API is useful for studying how explicit vector programming interacts with a managed runtime and optimizing JIT. The inspected package remains marked incubating.

- **C2:** Element-specific vectors share species, shapes, masks, shuffles, and operator tokens. Preferred species let an algorithm adapt its lane count to the executing platform.
- **C1:** Masked array accesses handle tails explicitly. The documentation warns that hand-written power-of-two loop-bound arithmetic can be wrong for other vector shapes, showing why shape-aware helpers matter.
- **C3:** The runtime can lower operations to vector instructions or use scalar implementations. Unsupported shapes, identity-sensitive operations, and storing vector objects in fields can affect optimization.

**Entry point:** The [Vector API package specification](https://raw.githubusercontent.com/openjdk/jdk/master/src/jdk.incubator.vector/share/classes/jdk/incubator/vector/package-info.java) combines the abstraction model, tail-loop examples, and implementation-sensitive performance guidance.

## Reusable vector mathematical primitives

### 24. [shibatch/sleef](https://github.com/shibatch/sleef)

**Language/role:** Primarily C for vector math, with C++ components; portable mathematical functions used by vectorized applications.

SLEEF complements the register abstractions above: implementing a vector `sin` or `log` requires substantial numerical algorithms after loads and arithmetic are already portable.

- **C1:** Trigonometric implementations combine range reduction, double-double arithmetic, exceptional-value handling, and signed-zero preservation. The source explicitly controls floating-point contraction.
- **C3:** Shared mathematical algorithms operate through ISA helper layers. Vector predicates select range-reduction paths, exposing how expensive cases coexist with common inputs. See [double-precision vector math implementation](https://raw.githubusercontent.com/shibatch/sleef/master/src/libm/sleefsimddp.c).
- **C4:** The [changelog](https://github.com/shibatch/sleef/blob/master/CHANGELOG.adoc) records 2018 cross-platform and ABI testing, later accuracy/compiler fixes, and 2025 testing changes using TLFloat to broaden post-build validation. This establishes sustained complexity management, not merely age.

Backend support is uneven: the inspected repository labels RVV variants unmaintained and some other targets experimental. Historical backend additions do not establish current maintenance for those targets.

## Coverage, exclusions, and limitations

Discovery used more than six distinct live-search formulations, including portable C++ SIMD wrappers; Rust dispatch and safe vector traits; SSE/NEON translation; RISC-V vector compatibility; Julia explicit vectors and loop transformation; .NET and Java vector APIs; template/generator-based SIMD; standard-library SIMD extensions; vector mathematical libraries; and smaller Go, Haskell, and Swift ecosystems. Architecture searches covered x86, Arm NEON/SVE, RISC-V RVV, Wasm, POWER, and less common backends. Later queries increasingly returned already inspected libraries, language/compiler facilities, application-specific kernels, and packaging variants.

The selection deliberately includes smaller projects such as TSL, vir-simd, neon2rvv, and VectorTraits alongside widely used libraries. It separates three different ideas often conflated in search results: portable vector semantics, emulation of another ISA's semantics, and library-driven generation of vectorized loops. Fixed-width wrappers, length-aware APIs, and scalable-vector implementations are not assumed equivalent.

Standalone compilers such as ISPC, application-focused SIMD users such as parsers, and narrowly focused similarity/hash kernels are outside this report's main scope. Awesome lists, tutorial implementations, generated distribution-only packages, and duplicate forks were not retained. The original simdeez lineage is represented only by the continuation listed above. OpenJDK is included solely because its reusable Vector API directly fits the category. No unofficial mirror is presented as an independent implementation.

Each retained repository had its canonical GitHub page opened and at least one additional primary source read. Evidence is sampled architecture/API documentation, implementation, testing material, or change history; candidate code was not cloned, built, or executed. Some web fetches returned incomplete GitHub pages or cache errors, so alternate primary documents were used. The vir-simd entry explicitly identifies its thinner internal-source coverage. Documentation versions and moving source branches can differ, particularly for experimental APIs and emerging architectures; the neon2rvv discrepancy is called out rather than resolved by assumption.

Maintenance claims are deliberately limited to explicit project notices and the history actually inspected. C4 is only assigned where multiyear change-management evidence was read. This is a diverse selection, not an exhaustive inventory, a correctness audit, or a measurement of comparative performance.
