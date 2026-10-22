# Image codecs and image format libraries

Research date: **2026-10-09**.

This report selects 25 GitHub repositories for studying raster image compression, decoding, containers, and reusable image-file I/O. It covers web images, scientific and HDR images, camera RAW, GPU textures, and applications' common image abstractions. Codec implementations and libraries that organize external codecs are distinguished explicitly. Broader graphics repositories are included only for an identified image subsystem and counted once.

The criteria below are evidence-based selection judgments, not a certification of security, complete format conformance, or uniformly exemplary code. Performance mechanisms are discussed without treating project benchmark claims as independently reproduced results. Repository pages and additional primary implementation or documentation sources were opened for every selection.

- **C1 — Difficult correctness:** invariants, numerical semantics, concurrency, malformed input, or failure recovery require careful engineering.
- **C2 — Reusable abstractions:** substantial interfaces and data models serve multiple applications or workflows.
- **C3 — Performance with structure:** meaningful time, memory, or bandwidth constraints are addressed through an understandable decomposition.
- **C4 — Sustained evolution:** multi-year changes show compatibility work, testing, or deliberate complexity management; repository age alone does not qualify.

## JPEG and PNG foundations

### 1. [libjpeg-turbo/libjpeg-turbo](https://github.com/libjpeg-turbo/libjpeg-turbo)

**Language/role:** C and architecture-specific assembly/intrinsics; JPEG encoding and decoding.

Study how an established codec gains hardware acceleration while preserving a widely used interface. The repository distinguishes the traditional libjpeg API from the simpler TurboJPEG API, including planar YUV and lossless transformation operations.

- **C2:** Two APIs expose the same codec at different abstraction levels; the repository documents mathematical and API/ABI compatibility with libjpeg v6b and configurable compatibility with later interfaces.
- **C3:** SIMD modules plug into existing algorithm boundaries for color conversion, sampling, DCT, and related stages. The [SIMD architecture guide](https://github.com/libjpeg-turbo/libjpeg-turbo/blob/main/simd/README.md) explains algorithm coverage and profiling rather than presenting acceleration as an opaque replacement.
- **C4:** The [change history](https://raw.githubusercontent.com/libjpeg-turbo/libjpeg-turbo/main/ChangeLog.md) records regression-test-driven SIMD restrictions around 2020 and later fixes to symbol isolation, scaling, cropping, and reused decoder state. This is useful evidence of compatibility and numerical maintenance over multiple generations.

**Entry points:** SIMD architecture guide and change history above.

### 2. [mozilla/mozjpeg](https://github.com/mozilla/mozjpeg)

**Language/role:** C with inherited SIMD code; JPEG encoder optimized for compression efficiency.

This is a substantive libjpeg-turbo derivative, included for its separate encoder decisions rather than counted as an unrelated implementation. Study how extra encoding work improves a conventional, broadly decodable format.

- **C1:** Trellis quantization balances coefficient distortion against encoded rate; scan optimization, DC treatment, and quantization-table choices interact. The [Mozilla implementation notes](https://raw.githubusercontent.com/mozilla/mozjpeg/master/README-mozilla.txt) explain the objective and parameter dependencies.
- **C2:** New options live behind accessors and opaque compressor state so that extension settings do not require changing public libjpeg structures and breaking their ABI.
- **C3:** The same notes explicitly describe asymmetric performance: substantially more encoder work is acceptable in a web publishing workflow, while real-time compression is not the intended default use. Compression profiles expose that tradeoff.

**Entry point:** Mozilla implementation notes, especially the extensibility framework and trellis parameters.

### 3. [pnggroup/libpng](https://github.com/pnggroup/libpng)

**Language/role:** C; official PNG support library.

An especially useful study in maintaining a configurable binary-format library whose transformation and error-handling contracts have accumulated many real-world edge cases.

- **C1:** The [manual](https://github.com/pnggroup/libpng/blob/libpng16/libpng-manual.txt) explains nonlocal error handling, destruction after errors, custom allocation, and separate critical/ancillary CRC policy. Correct callers must manage those contracts as carefully as pixel buffers.
- **C2:** Per-image contexts, replaceable I/O and allocator functions, and configurable pixel transformations support more than simple file-to-RGBA decoding.
- **C4:** The [change history](https://raw.githubusercontent.com/pnggroup/libpng/libpng16/CHANGES) includes 2015 compatibility-preserving deprecations and validation changes, followed by 2025–2026 allocation-failure fuzzing, negative-stride tests, and fixes to palette ownership and transformed row sizes. It shows both the benefit and cost of a long-lived API.

**Entry points:** Manual and change history above.

### 4. [randy408/libspng](https://github.com/randy408/libspng)

**Language/role:** C; independent PNG reader/writer with an API distinct from libpng.

Study a smaller context-based API that makes output formats and progressive decoding explicit. It provides a useful comparison with libpng's integration contracts, without being another libpng fork.

- **C1:** The [decoding guide](https://libspng.org/docs/decode/) distinguishes scanlines from reconstructed rows, explains repeated/nonsequential row access during interlacing, and specifies critical failure on truncated input. A partial image is not promised merely because some bytes decoded.
- **C2:** One decoder context supports several output layouts, transparency and gamma options, whole-image decoding, and progressive row/scanline operations. The documented end-of-image status and context lifecycle let callers build streaming workflows without embedding PNG-specific row scheduling themselves.

**Entry point:** Decoding guide, particularly supported format combinations and progressive image decoding.

### 5. [lvandeve/lodepng](https://github.com/lvandeve/lodepng)

**Language/role:** C/C++; compact PNG encoder/decoder with its own compression implementation.

Study the progression from convenient decode functions to an explicit state object, with C ownership rules and a C++ RAII alternative. Its compact distribution makes cross-layer reading practical.

- **C1:** The [public header and embedded documentation](https://github.com/lvandeve/lodepng/blob/master/lodepng.h) specify state invalidation after failure and precise raw-pixel conventions: sub-byte samples have no scanline padding, while 16-bit channels use big-endian order. Decoder settings separately control checksum and critical-chunk handling.
- **C2:** `LodePNGState` groups encoder/decoder settings, raw color mode, and PNG metadata; separate header and metadata inspection operations allow applications to inspect images without immediately decoding their pixels. C++ state management adds automatic lifetime handling over the same underlying model.

**Entry point:** `lodepng.h`, starting with `LodePNGState`, the inspection API, and its extended documentation.

## Modern web formats and image containers

### 6. [webmproject/libwebp](https://github.com/webmproject/libwebp)

**Language/role:** C and SIMD implementations; WebP codec and supporting APIs. **Official GitHub mirror:** the repository directs development contributions to Chromium's upstream infrastructure.

Study how a codec exposes both convenient decoding and an incremental interface suitable for partially available data.

- **C1:** The [decoder interface](https://raw.githubusercontent.com/webmproject/libwebp/main/src/webp/decode.h) distinguishes suspended decoding from malformed bitstreams and defines which output-buffer fields may change between calls. Buffer lifetime, strides, and capacity remain explicit contracts.
- **C2:** RGB, premultiplied-alpha, and planar YUV outputs share a configurable decoding model, with either library-owned or caller-owned storage.
- **C3:** Direct decoding into supplied buffers avoids an obligatory copy. The interface even distinguishes external memory that is expensive to access, giving the implementation a way to avoid repeated reads and writes.

**Entry point:** `src/webp/decode.h`, especially `WebPDecBuffer` and incremental decoding.

### 7. [AOMediaCodec/libavif](https://github.com/AOMediaCodec/libavif)

**Language/role:** C; AVIF image/container library using underlying AV1 codec implementations.

Study the boundary between an image container, image semantics, and a video-derived compression backend. This is not an independent AV1 bitstream implementation.

- **C1:** The [public API](https://raw.githubusercontent.com/AOMediaCodec/libavif/main/include/avif/avif.h) defines dimension, pixel-count, and frame-count limits, strictness flags, and container-versus-payload metadata handling. It explicitly notes that not every underlying AV1 codec supports the same configurable size limit.
- **C2:** `avifImage`, decoder state, codec selection, and custom I/O separate pixel planes and metadata from the compression backend. Streaming callers can handle waiting-for-I/O and choose whether to fetch metadata located late in a file.

**Entry point:** `include/avif/avif.h`, particularly `avifIO`, `avifImage`, and `avifDecoder` contracts.

### 8. [strukturag/libheif](https://github.com/strukturag/libheif)

**Language/role:** C++ with C API; HEIF/AVIF container and image library with codec plugins.

Study image composition and selective access inside a container. The repository documents external codec integration and optional dynamically loaded codec plugins; much of its distinct engineering is above the elementary codec layer.

- **C1:** The [tiled-image guide](https://github.com/strukturag/libheif/wiki/Reading-and-Writing-Tiled-Images) explains tile indices versus pixel coordinates, differing edge-cropping rules, and how rotation and cropping change tile placement. These details matter when reconstructing an image from individually decoded tiles.
- **C2:** A common tile-reading interface handles different tiling schemes and non-tiled images, while image handles and codec plugins separate representation from compression.
- **C3:** Custom readers support byte-range requests and optional prefetch hints. The guide connects those abstractions to fetching only a requested tile and avoiding inefficient sequences of tiny network reads.

**Entry point:** Tiled-image guide, including its network-streaming section. Its proprietary `tili` extension is identified as such and should not be confused with universally supported HEIF features.

### 9. [libjxl/libjxl](https://github.com/libjxl/libjxl)

**Language/role:** C++ with C API; JPEG XL reference implementation.

Study a modern codec whose lossless and lossy representations share infrastructure while preserving precise rendering semantics.

- **C1:** The [format overview](https://raw.githubusercontent.com/libjxl/libjxl/main/doc/format_overview.md) distinguishes reversible integer-based Modular coding from VarDCT, and explains why orientation, color interpretation, and frame blending belong to rendering-critical codestream data. Bit-identical reconstruction of an original JPEG additionally requires reconstruction metadata.
- **C3:** Independently addressable groups and a table of contents enable parallel work, regional access, and progressive previews. Low-frequency data precedes progressively refined detail, making the format organization directly relevant to latency and memory scheduling.
- **C2:** The same architecture accommodates still images, animation, extra channels, and existing JPEG reconstruction. The repository warns that library APIs may change even though encoded files follow the standardized format.

**Entry point:** Format overview, especially pixel-data modes, groups, and JPEG bitstream reconstruction.

### 10. [tirr-c/jxl-oxide](https://github.com/tirr-c/jxl-oxide)

**Language/role:** Rust; independent JPEG XL decoder organized as cooperating crates.

Study a Rust implementation of the same demanding format and compare its public state model with libjxl. The project is an implementation, not merely bindings to the reference library.

- **C1:** The [crate documentation](https://docs.rs/jxl-oxide/latest/jxl_oxide/) exposes an uninitialized image state that accepts more bytes and returns either `NeedMoreData` or an initialized image. It also clearly separates basic color conversion from arbitrary ICC conversion, which requires an external color-management implementation.
- **C2:** A facade over smaller crates accepts files, `Read` sources, or asynchronously supplied byte buffers; frame rendering and pluggable color management are separate steps. This supports embedding in applications with different I/O and display pipelines.

**Entry point:** Crate documentation, including the initialization example and color-management integration. Built-in support alone should not be interpreted as arbitrary CMYK/ICC conversion support.

## Scientific, HDR, camera RAW, and texture formats

### 11. [uclouvain/openjpeg](https://github.com/uclouvain/openjpeg)

**Language/role:** C; JPEG 2000 implementation, principally `src/lib/openjp2`. **Status:** the official repository explicitly says it should be considered unmaintained, even if occasional commits appear.

Retained as a substantial reference for codec state and region-oriented decoding, not as an endorsement of its maintenance situation.

- **C1:** The [API header](https://raw.githubusercontent.com/uclouvain/openjpeg/master/src/lib/openjp2/openjpeg.h) describes strict versus partial-bitstream decoding and sequencing constraints around setup, header parsing, worker creation, and component selection.
- **C2:** Opaque codec handles, stream callbacks, event handlers, component selection, and region/tile operations support applications beyond a whole-file command-line decoder.
- **C3:** Region decoding and worker-thread configuration expose performance choices explicitly. The API documents the special single-tile case where repeated region decoding can reuse the codec, unlike the general lifecycle.

**Entry point:** `openjpeg.h`, particularly decoder setup, `opj_set_decode_area`, and tile decoding. The monorepo is counted once; deprecated or removed components are not separate recommendations.

### 12. [team-charls/charls](https://github.com/team-charls/charls)

**Language/role:** C++ with C/C++ APIs; lossless and near-lossless JPEG-LS.

Study predictive coding whose correctness depends on neighborhood context, run state, interleaving, and restart behavior. It offers a focused alternative to transform-based JPEG implementations.

- **C1:** The [scan decoder](https://raw.githubusercontent.com/team-charls/charls/main/src/scan_decoder_impl.hpp) derives contexts from neighboring gradients, switches between regular and run modes, and explicitly resets line buffers, run indices, and coding parameters after restart markers.
- **C3:** Traits specialize sample and pixel handling; two rolling scanline buffers avoid retaining a full intermediate image. Compile-time branches distinguish scalar samples and multi-component pixels without hiding the main decoding loop.
- **C2:** The repository documents C and C++ integration and different interleave modes. Its stated limitations include unsupported JPEG-LS Part 2 features and no corrupted-stream recovery despite support for decoding restart markers.

**Entry point:** `src/scan_decoder_impl.hpp`, read alongside the repository's limitations section.

### 13. [AcademySoftwareFoundation/openexr](https://github.com/AcademySoftwareFoundation/openexr)

**Language/role:** C/C++; EXR specification and reference libraries for HDR image storage.

Study the separation between shared file metadata and per-worker compression/decompression machinery, particularly in the OpenEXRCore subsystem.

- **C1:** The [C API guide](https://openexr.com/en/latest/OpenEXRCoreAPI.html) makes a crucial concurrency distinction: threads can share an opened read context, but must not concurrently share one decode-pipeline instance. Custom I/O must honor the required concurrency contract, and parallel writing must respect chunk order.
- **C2:** Context, part, chunk, channel, and pipeline abstractions support multipart images, varied channel layouts, and custom allocators or processing stages.
- **C3:** Pipelines can retain intermediate buffers and compression contexts between chunks, reducing repeated allocation. Function pointers allow specialized unpacking/conversion stages while keeping the orchestration visible.

**Entry point:** OpenEXRCore API guide, especially context creation and the decoding/encoding pipelines.

### 14. [syoyo/tinyexr](https://github.com/syoyo/tinyexr)

**Language/role:** C++ with a C-facing interface; compact EXR loading and saving implementation.

Study a more locally readable EXR implementation and its explicit boundary between parsing headers, choosing sample representation, and allocating image data.

- **C1:** The [implementation header](https://raw.githubusercontent.com/syoyo/tinyexr/master/tinyexr.h) checks input availability and header validity and distinguishes cleanup after header and image-data failures. Its B44 decoder checks multiplication and accumulation overflow while calculating output size across differently sampled channels.
- **C2:** Convenience RGBA loading coexists with lower-level header/image and multipart APIs. Callers can request conversion of half-precision channels to floating-point output before loading, rather than accepting one universal pixel layout.

**Entry point:** `tinyexr.h`, beginning with `EXRHeader`, `ParseEXRHeaderFromMemory`, and `LoadEXRImageFromMemory`. The compact interface does not imply a trivial implementation or identical feature coverage to OpenEXR.

### 15. [LibRaw/LibRaw](https://github.com/LibRaw/LibRaw)

**Language/role:** C++ with C API; extraction of camera RAW pixels, processing metadata, and previews.

Study normalization across vendor-specific formats while preserving information needed for later photographic processing. The repository explicitly keeps production-quality rendering outside its principal scope; inherited conversion routines are not the main reason for selection.

- **C2:** The [C++ API](https://www.libraw.org/docs/API-CXX.html) separates opening and metadata extraction, RAW unpacking, thumbnail access, and optional processing. Abstract datastreams permit file, memory, and application-defined input sources with documented ownership.
- **C1:** Bayer layout, sample packing, byte order, black levels, and white-balance state are explicit semantic concerns rather than generic RGB decoding options.
- **C4:** The [changelog](https://raw.githubusercontent.com/LibRaw/LibRaw/master/Changelog.txt) connects 2015 fuzz-discovered fixes to 2025 decoder replacements and backward camera-format support. The repository also states that minor releases preserve API/ABI, while major releases have a broader change policy.

**Entry points:** C++ API and changelog above.

### 16. [cgohlke/tifffile](https://github.com/cgohlke/tifffile)

**Language/role:** Python; TIFF/BigTIFF structures and scientific multidimensional image I/O, using `imagecodecs` for many compressed payloads.

Study how pages, series, metadata dialects, and NumPy arrays fit together. This is substantial format and storage logic, rather than just a wrapper around a TIFF decoder.

- **C1:** The [implementation](https://raw.githubusercontent.com/cgohlke/tifffile/master/tifffile/tifffile.py) coordinates shared file access with locks, propagates worker exceptions, and handles offsets, strips, tiles, and differing array shapes. The repository's revision notes give concrete examples of large-file offset and proprietary metadata corrections.
- **C2:** Page/series models, memory-mapped output, and multidimensional file sequences support scientific workflows that a single RGBA image abstraction cannot represent.
- **C3:** Segment decoding batches work to control executor memory overhead, while page stacking chooses between page-level and segment-level parallelism. Those policies make its performance architecture particularly worth reading.

**Entry point:** `tifffile/tifffile.py`, especially segment decoding and `stack_pages`. Revision notes explicitly identify breaking API changes; do not infer a frozen interface.

### 17. [BinomialLLC/basis_universal](https://github.com/BinomialLLC/basis_universal)

**Language/role:** C++; portable compressed GPU textures, encoder library, and transcoder.

Study a codec optimized for distribution across incompatible GPU texture formats. The relevant subsystem is the reusable encoder/transcoder, not merely the command-line packaging tool.

- **C3:** The [transcoder guide](https://github.com/BinomialLLC/basis_universal/wiki/How-to-Use-and-Configure-the-Transcoder) explains direct conversion from ETC1S/UASTC using lookup tables or per-block hints, avoiding the usual full texel decompression/recompression path for those conversions.
- **C2:** Container-aware interfaces expose images and mip levels, while lower-level transcoders can work inside custom containers. Compile-time format selection allows applications to omit unused conversion tables and reduce distribution size.
- **C1:** Initialization, endianness, alignment assumptions, and compiler aliasing requirements are documented integration constraints. These are useful examples of portability obligations in otherwise compact, performance-oriented code.

**Entry point:** Transcoder guide. It documents particular transcoder modes; its direct-conversion explanation should not be generalized to every newer codec or DDS conversion path in the repository.

## Reusable multi-format libraries and decoder frameworks

### 18. [google/wuffs](https://github.com/google/wuffs)

**Language/role:** Wuffs language and standard library, Go tooling, generated C; selected here for the image-decoder subsystem.

Study an unusual approach to handling untrusted image data: a constrained source language paired with a reusable C-facing decoder model. The language/toolchain and its image codecs count as one repository.

- **C1:** The [image-decoder contract](https://raw.githubusercontent.com/google/wuffs/main/doc/std/image-decoders.md) limits dimensions to simplify overflow reasoning, defines resumable operations, rejects switching operations while one is suspended, and makes subsequent calls fail after a terminal error until reinitialization.
- **C2:** Common image-configuration, frame-configuration, pixel-buffer, metadata, and restart interfaces span multiple formats and animated images.
- **C3:** Header/frame inspection can skip compressed pixel payloads when only counting frames, and explicit work buffers make temporary storage visible. The same contract describes incremental input rather than requiring an entire file in memory.

**Entry point:** Image-decoder contract, followed by its linked standard-library implementations.

### 19. [nothings/stb](https://github.com/nothings/stb)

**Language/role:** C/C++; monorepo selected for `stb_image.h` and the related image-writing subsystem.

Study how multiple format decoders can share a small integration surface without separate library installation. This selection concerns image loading/writing, not the repository's font, container, or other unrelated libraries.

- **C2:** The [image header](https://raw.githubusercontent.com/nothings/stb/master/stb_image.h) provides file, memory, and callback input; its shared interface exposes byte and floating-point image outputs and configurable allocation.
- **C3:** The JPEG path separates SIMD kernels from scalar fallbacks, performs x86 capability selection, and explains buffering for callback I/O. Algorithm comments make the tradeoffs between intermediate storage, upsampling quality, and decoding speed visible.
- **C1:** Color conversion code deliberately uses matching reduced-precision arithmetic in scalar and SIMD paths, illustrating numerical equivalence as a correctness requirement rather than treating all approximations as interchangeable.

**Entry point:** `stb_image.h`, especially its I/O/SIMD documentation and JPEG color-conversion implementation. Compact packaging is not a claim of exhaustive format support.

### 20. [image-rs/image](https://github.com/image-rs/image)

**Language/role:** Rust; common image types, image codecs, and format-independent I/O.

Study the interface between statically typed pixels and dynamically discovered files. Some codecs are implemented in the repository and others are delegated to dedicated crates; those dependencies are not counted again here as part of this entry.

- **C2:** `ImageBuffer<P>`, `DynamicImage`, image-view traits, and `ImageDecoder` provide different levels of type and format knowledge. Applications can retain a specific pixel representation or dispatch on the decoded image at runtime.
- **C1:** The [resource-limit contract](https://docs.rs/image/latest/image/struct.Limits.html) distinguishes strict width/height limits from best-effort allocation limits, requires failure for unsupported strict limits, and supplies reserve/free accounting helpers. This is a concrete study of how a common API expresses unequal guarantees across decoder backends.

**Entry point:** `Limits` documentation, together with the repository's image-type and decoder-trait overview. The allocation limit is not a universal hard cap.

### 21. [etemesi254/zune-image](https://github.com/etemesi254/zune-image)

**Language/role:** Rust; workspace of codecs and an image facade, including `zune-jpeg` and `zune-png`.

Study small codec crates with explicit performance kernels and a common integration layer. The workspace is counted once; JPEG, PNG, and the other contained codecs are not separate repository entries.

- **C3:** The [JPEG IDCT dispatch module](https://raw.githubusercontent.com/etemesi254/zune-image/dev/crates/zune-jpeg/src/idct.rs) selects scalar, AVX2, or NEON implementations and exposes reduced-size IDCT paths. Its comments explain an all-zero-AC shortcut and why the vector path is structured separately.
- **C1:** SIMD calls are gated on feature support, reduced-size transforms have a stated coefficient invariant, and the same module compares scalar and vector results in tests.
- **C2:** The repository documents common decoder options, header-only inspection, bit-depth preservation, and decoder/encoder traits while allowing individual codecs to be used independently.

**Entry point:** JPEG IDCT dispatch and tests. The repository's performance goals are not treated as verified cross-library benchmark results.

### 22. [SixLabors/ImageSharp](https://github.com/SixLabors/ImageSharp)

**Language/role:** C#; managed image library with multiple format decoders and encoders. The repository identifies its Six Labors Split License.

Study how managed-language image codecs integrate with generic pixel storage and efficient memory access. The selected subject is the format/pixel infrastructure, not every drawing or processing operation.

- **C2:** The [format guide](https://docs.sixlabors.com/articles/imagesharp/imageformats.html) describes the supported image families, while `Image<TPixel>` and frame abstractions give decoded formats a common typed representation.
- **C3:** The [pixel-buffer guide](https://docs.sixlabors.com/articles/imagesharp/pixelbuffers.html) explains contiguous row access even when a large image uses several backing buffers. It contrasts direct typed spans with reusable `Vector4` processing and makes the extra conversion work explicit.
- **C1:** Row-span lifetime restrictions prevent retaining callback-owned access or carrying it across asynchronous boundaries; callers must distinguish decoded pixel layout from the original file's packing.

**Entry points:** Format and pixel-buffer guides above.

### 23. [haraldk/TwelveMonkeys](https://github.com/haraldk/TwelveMonkeys)

**Language/role:** Java; plugins and extensions for Java ImageIO.

Study compatibility engineering at the boundary between a platform API and real image files. The JPEG reader deliberately builds on the JRE reader while correcting and extending behavior; the project also contains other format implementations.

- **C1:** The [JPEG reader implementation](https://raw.githubusercontent.com/haraldk/TwelveMonkeys/master/imageio/imageio-jpeg/src/main/java/com/twelvemonkeys/imageio/plugins/jpeg/JPEGImageReader.java) handles CMYK/YCCK, inconsistent component counts, corrupt or misindexed ICC chunks, and subsampling coordinate adjustments. Warning and fallback paths distinguish recoverable metadata faults from decoding failures.
- **C2:** Plugins participate in standard ImageIO discovery and preserve `ImageReader`/`ImageReadParam` workflows for regions, subsampling, thumbnails, and metadata. Applications gain format handling without adopting a wholly separate image model.

**Entry point:** JPEG reader implementation, especially color conversion and embedded ICC profile assembly. Its delegation is substantive compatibility logic, not a generated wrapper.

### 24. [python-pillow/Pillow](https://github.com/python-pillow/Pillow)

**Language/role:** Python and C; image-format plugins and native image/codec infrastructure.

Pillow is the independently evolved PIL fork, counted once. Study the split between Python format recognition and a reusable tile/codec engine.

- **C2:** The [plugin guide](https://pillow.readthedocs.io/en/stable/handbook/writing-your-own-image-plugin.html) separates header recognition and tile descriptions from actual pixel loading. A tile identifies the decoder, output region, file offset, and parameters; both Python and C codecs fit the model.
- **C1:** Codecs must account for consumed bytes and retained tails, report errors through the codec state, and release resources even when a transform fails. Packed bit order, sign extension, stride, and orientation are explicit rather than guessed.
- **C4:** The [2016–2024 change history](https://raw.githubusercontent.com/python-pillow/Pillow/main/CHANGES.rst) records format regression tests, overflow fixes, compatibility changes, and later memory-arena locking/free-threaded Python work. This demonstrates sustained evolution beyond the original fork.

**Entry points:** Plugin guide and change history above; that changelog points to GitHub Releases for newer entries.

### 25. [AcademySoftwareFoundation/OpenImageIO](https://github.com/AcademySoftwareFoundation/OpenImageIO)

**Language/role:** C++ with Python bindings; format-independent image I/O and image/texture caching for VFX.

Study a larger architecture that builds reusable image access over format implementations and external codecs. The relevant subsystems are `ImageInput`/`ImageOutput`, format plugins, and `ImageCache`.

- **C2:** The [architecture document](https://github.com/AcademySoftwareFoundation/OpenImageIO/blob/main/docs/dev/Architecture.md) distinguishes caller-owned scanline/tile buffers, whole-image `ImageBuf` ownership, and the normalization of mixed channel types. It also clarifies that common plugins are compiled in despite the extensible plugin model.
- **C3:** `ImageCache` separately bounds open files and pixel-tile storage, evicting older entries as needed. `TextureSystem` adds filtered mipmapped lookups above that cache instead of making every format reader solve those problems.
- **C1:** The documented fuzzing design exercises compiled format readers through shared read routines, reducing divergence between normal decoding and the fuzz harness.

**Entry point:** Architecture document, especially file abstractions, caching, and fuzzing. The canonical repository is now under the Academy Software Foundation; older `OpenImageIO/oiio` references are not separate projects.

## Coverage and search notes

Discovery used more than six distinct live-search formulations, followed by direct repository and implementation/documentation reads. Search angles included:

- JPEG/PNG reference libraries, SIMD implementations, and smaller independent alternatives.
- Pure Rust codecs and independent JPEG XL decoding.
- HEIF/AVIF containers, HDR/EXR storage, and VFX image I/O.
- Java, C#, Python, Go, and JavaScript image-library ecosystems.
- JPEG-LS/JPEG 2000 predictive and wavelet-codec families.
- Camera RAW metadata and scientific TIFF/BigTIFF storage.
- GPU texture compression/transcoding and hardened untrusted-input decoders.
- Follow-up searches for alternative PNG libraries and format-plugin architectures.

Later searches increasingly returned already selected libraries, bindings to those libraries, broad image-processing packages, and adjacent alternatives rather than new architectural families. SAIL, KTX-Software, image-rs/image-png, and other plausible projects surfaced; their omission is a selection decision, not a judgment that they fail the criteria. Go and JavaScript were searched, but no standalone candidate from those searches displaced the better-supported selections here. Language coverage is consequently uneven.

The scope excludes pure video-codec projects, image editors/viewers, format-conversion websites, benchmark-only repositories, tutorial implementations, and thin/generated bindings. It does not attempt a complete catalog of TIFF, GIF, microscopy, or geospatial libraries. Non-GitHub upstreams were not substituted with arbitrary third-party mirrors. The official libwebp mirror is retained and labeled; OpenJPEG's explicit maintenance limitation is retained and labeled. MozJPEG's distinct encoder work and Pillow's substantial independent evolution justify their inclusion as derivatives.

Every heading points to a repository page opened during this research, and every entry has an additional opened primary source containing implementation or architectural detail. Source links generally track development branches or current documentation rather than immutable releases; details can change after the research date. No candidate code was run, no dependencies were installed, and no benchmark, fuzz campaign, or exhaustive conformance audit was performed. Criteria indicate concrete opportunities for engineering study, not a blanket recommendation to deploy any version without evaluating it.
