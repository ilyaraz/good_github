# Graphics API implementations and translation layers

Research date: **2026-10-09**.

This selection covers implementations of established graphics APIs, compatibility layers that translate their semantics, and the substantial runtime machinery that makes those translations possible. It includes browser-facing implementations, native drivers, software rendering, virtual GPU remoting, and older APIs. The 20 repositories below are study candidates, not a ranking or a claim of uniform code quality, complete conformance, or current production suitability. Large repositories are included only for the named graphics subsystem.

Criteria used:

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and components supporting multiple applications or backends.
- **C3 — Performance with structure:** explicit treatment of real execution costs through inspectable architectural mechanisms.
- **C4 — Evolution:** evidence spanning years together with compatibility work, testing, or complexity management. Repository age alone does not qualify.

## Browser graphics and portable API implementations

### 1. [google/angle](https://github.com/google/angle)

**Language/role:** C++; OpenGL ES and EGL implementation over platform graphics APIs. **Official source mirror** of Chromium's ANGLE repository.

Study how a stateful API is implemented over Vulkan's explicit execution model. The Vulkan design separates display-wide device/queue ownership in `Renderer` from per-context state and commands in `ContextVk`.

- **C1:** Render passes have distinct unstarted, active, and inactive states. Moving commands outside a pass can require ending it and inserting barriers; this is a concrete ordering invariant, not just function-name translation.
- **C3:** Secondary command recording, deferred flushing, and recycling separate OpenGL call processing from Vulkan submission. These mechanisms expose where compatibility and batching interact. Both points are described in the [Vulkan backend design](https://github.com/google/angle/blob/main/src/libANGLE/renderer/vulkan/README.md).
- **C4:** The repository records conformance milestones from 2011 through 2023, while the [testing infrastructure](https://github.com/google/angle/blob/main/infra/README.md) describes pre-commit and post-commit coverage across GPU families and software implementations. This supports sustained compatibility engineering rather than age alone.

### 2. [google/dawn](https://github.com/google/dawn)

**Language/role:** C++; native WebGPU implementation, wire protocol, and Tint shader compiler. **Official GitHub mirror** of Dawn's Googlesource repository; counted once, including Tint.

Study the boundary between API validation, backend translation, and remote execution. The [repository overview](https://github.com/google/dawn/blob/main/docs/dawn/overview.md) explains `dawn_native`, `dawn_wire`, and the generated procedure table.

- **C1:** The native frontend owns state tracking and validation; the wire server separately validates serialized commands before executing them. Validation tests, fuzzers, GPU end-to-end tests, and internal white-box tests exercise different boundaries.
- **C2:** A common frontend serves D3D12, Metal, Vulkan, and other backends. Native and wire implementations share the API through procedure tables, allowing the same application/test interface to select either path. API descriptions also generate headers and serialization machinery, reducing duplicated interface maintenance.

Entry point: the overview above provides verified links into the native, wire, compiler, and test subsystems.

### 3. [gfx-rs/wgpu](https://github.com/gfx-rs/wgpu)

**Language/role:** Rust; WebGPU implementation and portable graphics API. Relevant components are `wgpu-core`, `wgpu-hal`, and the shader infrastructure in the same repository.

Study how an unsafe backend interface can support a safe API exposed to untrusted browser content. The [HAL module's design documentation](https://raw.githubusercontent.com/gfx-rs/wgpu/trunk/wgpu-hal/src/lib.rs) explicitly assigns validation responsibilities.

- **C1:** `wgpu-core` must track resource state and lifetime comprehensively; HAL callers must honor mapping, layout, and explicit barrier contracts. The documentation explains why partial backend validation cannot replace exhaustive frontend validation.
- **C2:** Backend traits describe instances, adapters, devices, queues, command encoders, and surfaces across Vulkan, Metal, D3D12, and GL. This is reusable implementation machinery beneath both native applications and browser integrations.
- **C3:** The HAL minimizes redundant validation and uses static dispatch; persistent mapping and caller-provided iterators expose concrete overhead choices. The same document candidly notes that some safety requirements remain incompletely documented.

### 4. [emscripten-core/emscripten](https://github.com/emscripten-core/emscripten)

**Language/role:** JavaScript runtime with C/C++ interfaces and Python toolchain support; specifically the OpenGL/OpenGL ES-to-WebGL compatibility subsystem.

Study the consequences of translating native memory-oriented graphics calls into a browser API. The [OpenGL support guide](https://emscripten.org/docs/porting/multimedia_and_graphics/OpenGL-support.html) distinguishes direct WebGL-compatible calls, additional ES emulation, and legacy desktop GL emulation.

- **C1:** Client-side vertex/index arrays require automatic GPU-buffer setup because WebGL requires bound buffers. The guide documents an index-buffer limitation, memory mapping emulation, and extension activation differences rather than pretending the APIs are equivalent.
- **C2:** Selectable compatibility modes support both new ES-style applications and existing immediate-mode code through the same toolchain.
- **C3:** Compile-time options remove unused WebGL versions, restrict fixed-function behavior, and avoid unnecessary texture-unit processing. The documented tradeoff between compatibility coverage and overhead is a useful design case.

Entry point: the guide also links the browser tests that exercise the emulation modes.

## Direct3D implementations and translation machinery

### 5. [doitsujin/dxvk](https://github.com/doitsujin/dxvk)

**Language/role:** C++; Direct3D 8/9/10/11 implementation over Vulkan.

Study automatic synchronization for an API whose applications often leave ordering implicit. The [barrier tracker and batch interfaces](https://raw.githubusercontent.com/doitsujin/dxvk/master/src/dxvk/dxvk_barrier.h) make a particularly focused entry into the larger renderer.

- **C1:** The tracker distinguishes read and written resource ranges, while image barriers account for layout transitions and queue ownership. Host-read visibility is handled at command-list boundaries.
- **C3:** Range tracking uses a two-part hash table backed by trees, and a separate barrier batch accumulates synchronization commands. Image barriers can collapse into ordinary memory barriers when neither layout nor ownership changes. These are concrete ways to reduce synchronization overhead without discarding hazard information.

The [release history](https://github.com/doitsujin/dxvk/releases) supplies application and driver compatibility context; it should be read alongside the implementation rather than interpreted as universal performance guarantees.

### 6. [HansKristian-Work/vkd3d-proton](https://github.com/HansKristian-Work/vkd3d-proton)

**Language/role:** Primarily C, with C++ components; Direct3D 12 over Vulkan. A **substantively evolved VKD3D fork** for Proton, with its own game-compatibility priorities and release history.

Study translation between two explicit APIs whose descriptor, indirect-execution, shader, and queue semantics still differ. The repository documents aggressive use of newer Vulkan functionality and explicitly does not promise compatibility with the original standalone VKD3D API.

- **C1:** The implementation and debugging material address descriptor misuse, shader conversion failures, and GPU hangs. [Release notes](https://github.com/HansKristian-Work/vkd3d-proton/releases) record shader-system-value corrections and restoration of compatibility behavior lost during compiler changes.
- **C3:** The same notes explain deferred clears/discards, render-pass suspend/resume, moving query operations to avoid pass breaks, batched complex `ExecuteIndirect`, and using transfer queues for eligible copy work. These reveal concrete costs and driver-dependent tradeoffs.

Entry points: the repository's descriptor-QA debugging discussion and the implementation-focused release notes above.

### 7. [wine-mirror/wine](https://github.com/wine-mirror/wine)

**Language/role:** C; specifically WineD3D and its Direct3D-facing DLLs. **Official GitHub source mirror** of Wine's GitLab repository; the monorepo counts once.

Study how Windows graphics object semantics feed a shared rendering core. The [WineD3D tree](https://github.com/wine-mirror/wine/tree/master/dlls/wined3d) separates common resources and state from OpenGL/Vulkan adapters, contexts, textures, and shader paths.

- **C1:** The [command stream implementation](https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/wined3d/cs.c) transfers resource, upload, nested-command-list, and query references into recorded command lists. Locks, atomic reference counts, and deferred destruction make ownership across execution boundaries explicit.
- **C2:** Common command operations, resources, views, state blocks, and shader handling form a reusable layer beneath API-facing code. The [D3D9 device implementation](https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/d3d9/device.c) shows this delegation directly.

The selection concerns these graphics components, not an assessment of every Wine subsystem.

### 8. [microsoft/D3D12TranslationLayer](https://github.com/microsoft/D3D12TranslationLayer)

**Language/role:** C++; shared machinery for translating D3D11-style graphics semantics into D3D12. Used by both D3D11On12 and D3D9On12.

Study the machinery needed to preserve the illusion of one CPU/GPU timeline: resource renaming, descriptor binding, deferred destruction, pooling, and command batching. The repository explains why these responsibilities move from drivers into an explicit-API consumer.

- **C1:** [Resource-state tracking](https://raw.githubusercontent.com/microsoft/D3D12TranslationLayer/master/include/ResourceState.hpp) distinguishes shared reads across queues from exclusive ownership, preserves the last write for read mapping, and updates recorded state only after barriers and waits establish the correct fence values.
- **C2:** Resource identity is separated from backing memory so discard/rename behavior can be reused by multiple API mapping layers.
- **C3:** Batched contexts move work to another thread; pipeline compilation uses workers, while pooling and suballocation address small-resource costs. The state manager also exposes a simulation interface so tests can inspect intended submissions.

Entry point: `ResourceState.hpp` above, paired with the repository's architectural README.

### 9. [microsoft/D3D9On12](https://github.com/microsoft/D3D9On12)

**Language/role:** C++; D3D9 **user-mode driver interface** mapped to D3D12. It is a driver mapping layer, not a replacement `d3d9.dll`.

Its shared resource machinery belongs to D3D12TranslationLayer, but its legacy shader adaptation supplies a distinct study target. The [shader implementation](https://raw.githubusercontent.com/microsoft/D3D9On12/main/src/9on12Shader.cpp) handles derived shader forms and input/output signatures.

- **C1:** Conversion depends on raster state, input declarations, and legacy numerical behavior. An explicit compatibility option controls “anything multiplied by zero gives zero”; generated geometry shaders treat that option differently because their inputs are controlled by the layer. Point-sprite conversion can require additional output signatures.
- **C3:** Original shader deduplication and caches of derived pixel, vertex, and geometry shaders avoid repeating conversion for equivalent state combinations.

Entry points: `9on12Shader.cpp` above and the repository README's explanation of its DDI boundary and relationship to the shared translation library.

### 10. [WinterSnowfall/d7vk](https://github.com/WinterSnowfall/d7vk)

**Language/role:** C++; early immediate-mode Direct3D APIs over Vulkan, using a modified DXVK D3D9 backend and existing DirectDraw services. **Substantive DXVK fork; maintenance mode announced in v2.3.**

Study compatibility with applications that depend on legacy COM identity, inconsistent validation, and mixed DirectDraw/3D presentation. Its early-API implementation and presentation machinery distinguish it from an unchanged DXVK fork.

- **C1:** The [v2.3 implementation notes](https://github.com/WinterSnowfall/d7vk/releases/tag/v2.3) cover interrupted surface enumeration, unusual execute-buffer inputs, stale blend state, texture-handle unification, and viewport object identity relied upon by application hooks.
- **C2:** Common material, texture, and viewport implementations reduce duplicated behavior across several generations of Direct3D interfaces.
- **C3:** Shadow surfaces prevent competing presentation paths; their memory placement is tuned for games that blit cursors into the final image, with an explicit configuration escape hatch for a regression.

The repository excludes retained-mode D3D and warns of remaining mixed-API limitations.

## Vulkan targets, drivers, software execution, and remoting

### 11. [KhronosGroup/MoltenVK](https://github.com/KhronosGroup/MoltenVK)

**Language/role:** C++/Objective-C++; Vulkan Portability implementation over Apple's Metal.

Study how an API implementation exposes platform differences without assuming complete semantic equivalence. The [runtime guide](https://github.com/KhronosGroup/MoltenVK/blob/main/Docs/MoltenVK_Runtime_UserGuide.md) documents extension restrictions, shader conversion, pipeline caching, and presentation behavior.

- **C1:** Vulkan-to-Metal shader conversion and capability reporting must respect Metal limitations. The guide identifies unsupported query behavior and format-upload restrictions, making the limits of the implementation explicit.
- **C2:** Vulkan remains the application interface while Metal-specific configuration and shader conversion are contained behind the implementation.
- **C3:** Serialized Vulkan pipeline caches preserve converted MSL and avoid repeated SPIR-V conversion. The guide also explains how Metal retaining presentation images can stall rendering and why swapchain image availability matters.

This is a portability implementation of a supported Vulkan subset, not a claim that arbitrary Vulkan applications run unchanged.

### 12. [google/swiftshader](https://github.com/google/swiftshader)

**Language/role:** C++; CPU implementation of Vulkan. **Official GitHub mirror** of SwiftShader's Googlesource repository.

Study software graphics as a specialization/compiler problem. [Reactor](https://github.com/google/swiftshader/blob/master/docs/Reactor.md) is an embedded C++ language for constructing generated routines rather than directly executing the corresponding arithmetic.

- **C2:** Reactor gives renderer code reusable typed arithmetic, control-flow, and pointer operations while hiding verbose compiler-IR construction. Its C-like notation makes generated computations inspectable.
- **C3:** Dynamic specialization removes operations and branches that are unnecessary for a particular graphics state. The [architecture overview](https://github.com/google/swiftshader/blob/master/docs/Index.md) also explains caching generated routines and parallel processing across CPU cores and SIMD lanes.

The architecture overview is explicitly marked **out of date** and describes older API layers. Use it for the specialization design, not the current supported-API list; the current repository describes Vulkan and ANGLE-based OpenGL ES layering.

### 13. [GPUOpen-Drivers/xgl](https://github.com/GPUOpen-Drivers/xgl)

**Language/role:** C++; AMD's Vulkan API layer, translating Vulkan to PAL and compiling pipeline shaders through LLPC. **Archived by its owner on 2025-09-15.**

Study a hardware driver's API-facing implementation rather than a platform-to-platform compatibility DLL. The [command buffer source](https://raw.githubusercontent.com/GPUOpen-Drivers/xgl/dev/icd/api/vk_cmdbuffer.cpp) exposes the Vulkan/PAL boundary.

- **C1:** Clear operations must map Vulkan image aspects, array layers, 3D slices, and multiview masks into PAL's different subresource rules. The code distinguishes those cases and explicitly documents constraints on slice ranges.
- **C2:** Vulkan objects and commands sit above PAL, while pipeline-wide shader compilation is delegated to LLPC. This separates API semantics from shared hardware services and compiler work.
- **C3:** The inspected clear helpers use bounded inline storage where allocation can be avoided; command-buffer settings also expose prefetch and state-management choices. These are inspectable mechanisms, not benchmark claims.

Treat this as a historical driver architecture reference, not a maintained deployment recommendation.

### 14. [google/gfxstream](https://github.com/google/gfxstream)

**Language/role:** C++ and Python generators; graphics API streaming between VM guests and hosts, processes, or machines.

Study the additional object and synchronization model needed when graphics calls cross an address-space boundary. The GitHub repository contains substantial host implementation code and documents GLES/Vulkan code generation and end-to-end testing.

- **C1:** An inspected [AOSP implementation revision of `VkDecoderGlobalState`](https://android.googlesource.com/platform/hardware/google/gfxstream/+/b09d20f9d591c7f8b3d4a0ea85e21c629ad7a89e/host/vulkan/VkDecoderGlobalState.cpp) maintains boxed/unboxed handle mappings, delayed removal, per-queue locking, sequence ordering, and fence waitability. Those mechanisms illustrate why remotely replaying calls requires more than serialization.
- **C2:** Shared generators and streaming libraries serve VM, IPC, and network use cases. The [GitHub Vulkan host tree](https://github.com/google/gfxstream/tree/main/host/vulkan) exposes reusable buffer, composition, external-memory, and device-operation components.

The detailed decoder evidence is pinned to an AOSP revision because current GitHub file-level retrieval was incomplete; its exact internal layout should not be assumed to match today's tree.

## Smaller and legacy-focused implementations

### 15. [ptitSeb/gl4es](https://github.com/ptitSeb/gl4es)

**Language/role:** C; desktop OpenGL compatibility over OpenGL ES. A **substantively evolved glshim descendant**, included without separately counting glshim.

Study fixed-function emulation on constrained GLES hardware. The [fixed-pipeline implementation](https://raw.githubusercontent.com/ptitSeb/gl4es/master/src/gl/fpe.c) combines shader generation, state-dependent variants, and uniform synchronization.

- **C1:** Derived programs must preserve application uniform state and attribute bindings while adding emulated fixed-function behavior. The source checks compilation/link failures and falls back when custom variants fail.
- **C3:** State-keyed program caches avoid rebuilding equivalent shaders, while tracked hardware state avoids redundant program changes. The [changelog](https://github.com/ptitSeb/gl4es/blob/master/CHANGELOG.md) documents draw merging, precompiled shader archives, fewer format conversions, and removal of an incorrect mode that complicated the implementation.

The README documents compatibility gaps; this is a practical translator, not a blanket desktop OpenGL conformance claim.

### 16. [rswinkle/PortableGL](https://github.com/rswinkle/PortableGL)

**Language/role:** C99; an embeddable software implementation of an OpenGL 3.x-like programmable pipeline.

Study the complete path from API state to clipping, primitive assembly, fragment processing, and framebuffer writes in a codebase small enough to inspect directly. Its shader interface uses C/C++ functions rather than a GLSL compiler, an important intentional departure from OpenGL.

- **C1:** The [implementation header](https://raw.githubusercontent.com/rswinkle/PortableGL/master/portablegl.h) handles clipping roundoff, window-coordinate winding, provoking-vertex selection, depth tests, and depth/stencil processing before multi-target color writes. These expose numerical and ordering semantics normally hidden in hardware drivers.
- **C2:** Contexts, resource objects, shader callbacks, uniforms, and output-buffer integration form a reusable software rendering library rather than a single rasterization demo.

The repository also describes regression images and performance tests. Study it as an explicitly limited implementation; its “3.x-ish” description is not a conformance certification.

### 17. [FunkyFr3sh/cnc-ddraw](https://github.com/FunkyFr3sh/cnc-ddraw)

**Language/role:** C; DirectDraw reimplementation with GDI, OpenGL, and D3D9 rendering paths. A **substantively developed fork** of the earlier cnc-ddraw project.

Study compatibility at the intersection of legacy surfaces, palettes, clipping, window behavior, and modern presentation. It supports DirectDraw-rendered 2D applications; it explicitly does not implement Direct3D games.

- **C1:** The [surface implementation](https://raw.githubusercontent.com/FunkyFr3sh/cnc-ddraw/master/src/ddsurface.c) combines attached-surface ownership, pixel-format validation, clipping regions, stretch ratios, and application-specific blit behavior. This shows how surface semantics and historical application assumptions interact.
- **C2:** A common DirectDraw surface model feeds multiple rendering backends and many applications. Renderer selection, scaling, and window/fullscreen handling are shared infrastructure rather than patches for one game.

Entry points: `ddsurface.c` above and the repository's backend/support documentation. The inherited fork relationship does not make the modern implementation a duplicate of its ancestor.

### 18. [elishacloud/dxwrapper](https://github.com/elishacloud/dxwrapper)

**Language/role:** C++; specifically the **Dd7to9** DirectDraw/Direct3D 1–7-to-D3D9 subsystem. Other bundled compatibility tools are outside this entry's assessment.

Study translating old COM interfaces and execute-buffer semantics into a newer rendering API. The [DirectDraw subsystem tree](https://github.com/elishacloud/dxwrapper/tree/master/ddraw) contains shared device/material/texture implementations and version-specific interfaces.

- **C1:** The [execute-buffer implementation](https://raw.githubusercontent.com/elishacloud/dxwrapper/master/ddraw/IDirect3DExecuteBuffer.cpp) tracks lock state, rejects deleted objects, validates instruction data before use, and distinguishes caller-owned memory from internally allocated storage.
- **C2:** Common `X` implementations and version adapters centralize behavior across several legacy interface generations. That makes the original Dd7to9 implementation substantive even though the larger repository also aggregates other projects.

Do not count its bundled D3D9On12, DDrawCompat, or d3d8to9 copies as additional implementations owned by this project.

### 19. [libcg/grvk](https://github.com/libcg/grvk)

**Language/role:** C; experimental AMD Mantle implementation over Vulkan, including runtime AMDIL-to-SPIR-V translation.

Study preservation of a discontinued API with a small ecosystem and limited shader tooling. The [release/compiler-development notes](https://github.com/libcg/grvk/releases) explain the translation pipeline and how the author constructed known-output shader cases by converting human-readable shaders to AMDIL and comparing disassembly/output.

- **C1:** Runtime shader translation must reconstruct AMDIL instruction semantics in SPIR-V. The notes document compiler bring-up through nontrivial shaders, dynamic-state validation fixes, and driver-specific blend-state failures.
- **C2:** Mantle-compatible DLL entry points and the shader translator together serve existing applications without modifying their API calls. This is a general API implementation, although its demonstrated application coverage is much smaller than DXVK's.

The inspected release series remains explicitly experimental and documents substantial missing functionality. Current maintenance was not established; old release driver requirements and performance observations are not treated as current guidance. This entry relies on substantive release documentation because file-level source retrieval failed.

### 20. [ileben/ShivaVG](https://github.com/ileben/ShivaVG)

**Language/role:** ANSI C; historical OpenVG implementation over OpenGL.

Study a vector-graphics state machine rather than another triangle-oriented API. Contexts, paths, paints, matrices, and images provide a different abstraction family. The repository publishes a function-by-function implementation-status list.

- **C1:** The [path implementation](https://raw.githubusercontent.com/ileben/ShivaVG/master/src/shPath.c) validates context-owned handles, path format/datatype and nonzero scale, reports allocation failures, masks capabilities, and invalidates cached path data when mutation changes its meaning.
- **C2:** Reusable path objects support coordinate transformation and interpolation, while separate paint and image APIs support solid colors, gradients, and patterns across applications. The repository's status documentation distinguishes implemented, partial, and missing operations.

This is a historical study candidate with significant limits: no EGL context implementation, incomplete OpenVG coverage, and a README that explicitly says the examples are not a proper validation suite. No C4 or active-maintenance claim is made.

## Search coverage, exclusions, and limits

Discovery used well over six distinct live-search formulations: general graphics API translation; WebGPU implementation architecture; software Vulkan/OpenGL renderers; Microsoft's D3D mapping layers; virtual GPU/API streaming; desktop GL-to-GLES compatibility; DirectDraw/Glide preservation; OpenVG implementations; and less familiar OpenGL/Vulkan/Mantle translators. Follow-up searches targeted command streams, shader conversion, driver source, architecture documents, and release notes. Later broad queries mostly returned already-covered implementations, forks, application rendering abstractions, or tutorials, with GRVK and D7VK adding distinct coverage.

The selection spans Rust, C, C++, Objective-C++, and JavaScript/Python runtime/tooling components; browser and operating-system projects, hardware-driver code, community compatibility projects, and smaller software/vector implementations. Language diversity reflects the available implementation ecosystem rather than a quota.

- **GitHub boundary:** Mesa is a major omission, including Zink, llvmpipe/lavapipe, Dozen, and hardware drivers. Its [official source documentation](https://docs.mesa3d.org/repository.html) directs readers to freedesktop GitLab; this search did not establish an official substantive GitHub mirror meeting the requested provenance rule. Virglrenderer likewise was not retained without verified qualifying GitHub provenance. These exclusions do not judge engineering quality.
- **Avoiding duplicates and adjacent categories:** Dawn/Tint, wgpu's internal crates, Wine's graphics DLLs, and dxwrapper's Dd7to9 are each counted once. D3D11On12 was inspected but left out because its own [README](https://github.com/microsoft/D3D11On12) describes it largely as an adapter around the separately selected D3D12TranslationLayer. D3D9On12 remains for its distinct shader-semantics work. DDrawCompat explicitly says it performs [no API conversion](https://github.com/narzoul/DDrawCompat), so it is excluded. General rendering libraries, generated bindings/loaders, standalone conformance suites, and binary-only compatibility products are outside this report's scope.
- **Evidence limitations:** Repository roots were opened for every retained entry, and every entry has additional opened primary material containing implementation or architectural detail. Some GitHub files failed retrieval; Gfxstream uses a clearly identified AOSP source revision, and GRVK uses compiler-development release documentation. MonkVG was investigated but omitted when a substantive additional source could not be retrieved. No candidate code was executed, built, or benchmarked. Moving branch links can change after this research date.

The C1–C4 assignments are engineering judgments grounded in the cited mechanisms. They indicate worthwhile study material, not proof that every invariant is correctly enforced or every optimization is beneficial on every platform.
