# Digital signal processing and audio effects libraries

Research date: **2026-10-09**

This selection covers reusable DSP kernels, audio synthesis and effects components, processing graphs, sample-rate conversion, spatial audio, and differentiable audio processing. It includes embedded, desktop, browser, and scientific-computing implementations. General frameworks appear only where a substantial DSP subsystem is identified; applications, device-I/O-only libraries, and thin bindings are outside the main scope. The 26 repositories below are study candidates, not a claim that every component is uniformly exemplary.

Criteria legend:

- **C1 — Correctness:** demanding numerical semantics, state invariants, concurrency, or failure handling.
- **C2 — Abstraction:** substantial reusable interfaces and components that support multiple applications.
- **C3 — Performance:** real processing constraints addressed through an understandable implementation structure.
- **C4 — Evolution:** documented development over years, accompanied by compatibility work, testing, or complexity management.

Criterion assignments are engineering judgments grounded in the linked primary material. Repository URLs were checked through GitHub pages or its API; implementation links were opened and read. Archive status was checked, but an unarchived repository is not automatically being described as actively maintained.

## General DSP libraries and compositional audio systems

### 1. [juce-framework/JUCE](https://github.com/juce-framework/JUCE)

**Language/role:** C++; the relevant subsystem is `modules/juce_dsp`, counted once within the larger application framework.

Study how a production-oriented DSP API represents preparation, processing, latency, and background work. Its convolution component offers a particularly concrete example of constraints that callers must respect.

- **C1:** The convolution API distinguishes wait-free impulse-response loading from permission to call methods concurrently: loading and processing must still be serialized. It also specifies background-queue lifetime and when preparation makes a new impulse response ready.
- **C3:** Uniform, fixed-latency, and nonuniform partitioned convolution expose different latency/CPU tradeoffs through distinct configuration types, with engine updates dispatched through a shareable background queue.

Entry point and evidence: [convolution API and threading contract](https://github.com/juce-framework/JUCE/blob/master/modules/juce_dsp/frequency/juce_Convolution.h). These contracts apply to this component, not automatically to every JUCE operation.

### 2. [kfrlib/kfr](https://github.com/kfrlib/kfr)

**Language/role:** C++; SIMD-oriented numerical and DSP framework with filtering, transforms, and resampling.

KFR is useful for studying how a common expression system accommodates stateful filters without hiding their data dependencies.

- **C2:** FIR expressions separate coefficient parameters, sample types, and filter state. State can be owned or referenced; real coefficients can operate on complex samples.
- **C3:** The short-FIR path computes vector outputs using compile-time tap traversal and concatenated history vectors. The arbitrary-length path instead uses a ring buffer and split dot products. Both explicitly disable random-access expression evaluation because results depend on prior samples.

Entry point and evidence: [FIR state and expression implementations](https://github.com/kfrlib/kfr/blob/main/include/kfr/dsp/fir.hpp). This is more informative than treating the repository's benchmark headlines as universal speed guarantees.

### 3. [Signalsmith-Audio/dsp](https://github.com/Signalsmith-Audio/dsp)

**Language/role:** C++11; header-only audio DSP components. **Official GitHub mirror**, identified as such by the repository and linked from the [author's project page](https://signalsmith-audio.com/code/dsp/).

Study reusable spectral machinery with unusually explicit conventions for windowing, normalization, latency, and valid buffer regions.

- **C1:** `WindowedFFT` uses a half-bin-shifted real transform, with corresponding rotation signs and inverse scaling. The STFT documents partially accumulated future output and the boundary of valid output history.
- **C2:** Windowed transforms, multichannel buffers, and STFT analysis/synthesis are composable building blocks; callers can supply window functions and spectral-processing callbacks instead of adopting a complete effects engine.

Entry point and evidence: [spectral transforms and STFT implementation](https://github.com/Signalsmith-Audio/dsp/blob/main/spectral.h). The repository also explains that audio-characteristic tests live in a separate documentation repository; those tests were not independently audited here.

### 4. [grame-cncm/faustlibraries](https://github.com/grame-cncm/faustlibraries)

**Language/role:** Faust; the DSP standard-library collection, distinct from the Faust compiler repository.

This is a useful alternative to object-oriented DSP: filters and effects are expressed as functional signal networks with reusable combinators and embedded mathematical documentation.

- **C1:** The normalized-ladder biquad `tf2np` explicitly limits reflection coefficients to a stability region and describes its behavior under modulation. Its implementation connects coefficient transformations to the underlying ladder structure.
- **C2:** The repository contains separate libraries for filters, delays, reverbs, compressors, physical models, routing, and other signal operations. The filter library alone builds higher-level filters from reusable direct-form, lattice, and allpass structures.

Entry point and evidence: [filter library, especially `tf2np` and ladder/lattice sections](https://github.com/grame-cncm/faustlibraries/blob/master/filters.lib). Stability safeguards in a particular implementation do not imply every possible user-composed network is stable.

### 5. [thestk/stk](https://github.com/thestk/stk)

**Language/role:** C++; Synthesis ToolKit audio-processing and algorithmic-synthesis classes.

Study the relationship between small DSP primitives and higher-level instrument models, along with the long-term cost of maintaining portable sample and frame interfaces.

- **C2:** STK provides independently reusable filters, delay lines, synthesis classes, and multichannel frame processing. `DelayL` is a compact example: a fractional delay with explicit interpolation characteristics and buffer-growth behavior.
- **C4:** Dated release notes document evolution from at least 2010 through 2023, including multichannel `tick()` changes, 24-bit sample representation fixes, delay and pitch-shift corrections, and adaptation to newer RtAudio APIs. This is evidence of compatibility and numerical maintenance, rather than merely an old creation date.

Entry points: [fractional-delay implementation](https://github.com/thestk/stk/blob/master/src/DelayL.cpp) and [dated release notes](https://github.com/thestk/stk/blob/master/doc/ReleaseNotes.txt). The dates describe the inspected history, not a claim about current release cadence.

### 6. [SamiPerttu/fundsp](https://github.com/SamiPerttu/fundsp)

**Language/role:** Rust; audio synthesis, effects, and compositional processing networks.

FunDSP offers both type-level graph composition and dynamic networks. It is especially interesting when studying how graph editing interacts with persistent DSP state.

- **C1:** `Net` tracks stable node identities, connection topology, channel counts, and revisions. It detects connection cycles and provides consistency checks; migration reuses existing units when their revisions permit it, preserving state across network changes.
- **C2:** The typed graph notation composes reusable audio nodes, while `Net` supports dynamically connected `AudioUnit` objects through the same broader processing ecosystem. The README also describes analytical signal-flow/frequency-response evaluation for linear networks.

Entry point and evidence: [dynamic network implementation](https://github.com/SamiPerttu/fundsp/blob/master/src/net.rs), particularly cycle detection, `check`, `migrate`, and backend creation. This exposes substantial graph machinery beyond the concise user-facing notation.

### 7. [RustAudio/dasp](https://github.com/RustAudio/dasp)

**Language/role:** Rust; foundational PCM sample, frame, signal, interpolation, and buffer abstractions.

Study the semantic layer underneath effects engines: how signed, unsigned, floating-point, and unusual-width samples map to one another without treating audio conversion as a plain numeric cast.

- **C1:** The conversion module specifies input-range preconditions, unsigned offsets, and the treatment of custom-width integer samples. It deliberately does not validate all incoming ranges, making caller obligations an essential part of correctness.
- **C2:** Separate crates expose sample/frame traits, iterator-like signals, ring buffers, envelopes, interpolation, and graphs, allowing consumers to select the level of abstraction they need.

Entry point and evidence: [sample conversion functions and contracts](https://github.com/RustAudio/dasp/blob/master/dasp_sample/src/conv.rs). The unchecked-range design is a study topic, not evidence of adversarial-input hardening.

## Embedded DSP and explicit memory/state management

### 8. [ARM-software/CMSIS-DSP](https://github.com/ARM-software/CMSIS-DSP)

**Language/role:** Primarily C, with C++ extensions; Cortex-M/Cortex-A compute library. The relevant subsystems are filtering and signal transforms.

CMSIS-DSP is particularly valuable for studying numerical contracts that change with arithmetic representation and processor features.

- **C1:** The Q31 direct-form-I biquad documents its accumulator format, guard-bit limitation, wraparound behavior, required input scaling, and post-shift truncation. These are observable algorithm semantics, not incidental optimization details.
- **C3:** The same implementation contains architecture-specific vector processing and a scalar path; the API documentation distinguishes a faster, less precise variant. Filter state and coefficients remain explicit despite those specialized kernels.

Entry point and evidence: [Q31 biquad cascade](https://github.com/ARM-software/CMSIS-DSP/blob/main/Source/FilteringFunctions/arm_biquad_cascade_df1_q31.c). This report does not assess the repository's unrelated machine-learning kernels.

### 9. [daisyaudio/DaisySP](https://github.com/daisyaudio/DaisySP)

**Language/role:** C++; modular audio DSP used with Daisy hardware and other audio environments. This is the verified current canonical owner; older documentation uses `electro-smith`.

Study compact, sample-oriented components whose storage costs can be understood before deploying to a microcontroller.

- **C2:** Oscillators, filters, envelopes, physical-modeling components, and effects can be assembled independently. `DelayLine<T, max_size>` itself supplies ordinary, fractional, Hermite-interpolated, and allpass operations.
- **C3:** That delay line stores its buffer directly in a compile-time-sized array and uses inline sample operations. This gives a concrete example of avoiding heap allocation in the processing path while exposing capacity as a design choice.

Entry point and evidence: [fixed-capacity delay line](https://github.com/daisyaudio/DaisySP/blob/master/Source/Utility/delayline.h). Initialization and parameter preconditions still matter; fixed storage does not establish correctness for arbitrary inputs.

### 10. [spiricom/LEAF](https://github.com/spiricom/LEAF)

**Language/role:** C; Lightweight Embedded Audio Framework for synthesis and effects, especially bare-metal ARM systems.

LEAF is useful for studying how a reusable DSP object model can coexist with application-controlled memory placement.

- **C1:** Its pool allocator tracks free-list nodes, alignment, block splitting, usage accounting, and allocation failure. It distinguishes fragmentation from exhaustion through error callbacks, making bounded-memory failure modes visible.
- **C2:** DSP objects follow consistent initialization, processing, and freeing conventions and can be initialized into selected pools. Oscillators, filters, envelopes, delays, and reverbs therefore share infrastructure without requiring a particular desktop host.

Entry point and evidence: [memory-pool implementation](https://github.com/spiricom/LEAF/blob/master/leaf/Src/leaf-mempool.c). The source also offers an optional conventional-allocation configuration; pool-backed operation should not be confused with a blanket allocation-free guarantee.

### 11. [Orastron/brickworks](https://github.com/Orastron/brickworks)

**Language/role:** C headers with C++ interfaces; music DSP building blocks for embedded, browser, plugin, and mobile engines.

Study an API that exposes coefficient state, per-channel signal state, and control-rate versus audio-rate updates rather than hiding them inside one opaque processor.

- **C1:** The state-variable filter checks initialization/reset lifecycle, finite values, and output-pointer aliasing in its debugging paths. Its embedded changelog records prewarping stability corrections and adjustments to validity checks for extreme values.
- **C2:** Separate coefficient and state structures allow shared parameterization across multiple channel states. Single-sample and multichannel functions use the same underlying component model.

Entry point and evidence: [state-variable filter API and implementation](https://github.com/Orastron/brickworks/blob/main/include/bw_svf.h). Debug assertions document invariants; they are not a promise of runtime validation in every build configuration.

## Resampling, time stretching, and pitch shifting

### 12. [libsndfile/libsamplerate](https://github.com/libsndfile/libsamplerate)

**Language/role:** C; audio sample-rate conversion, also known as Secret Rabbit Code.

Study persistent interpolation state and tests that assess numerical output instead of merely checking whether a conversion call succeeds.

- **C1:** The sinc converter maintains fractional position, filter-table indexing, and buffered input history, including explicit protection against buffer-index underflow. Variable-speed tests verify input consumption and compare reconstructed output against an SNR threshold.
- **C2:** Converter-specific processing lives behind common state operations for processing, reset, copy, and destruction, with specialized mono, stereo, and multichannel sinc implementations.

Entry points: [sinc conversion implementation](https://github.com/libsndfile/libsamplerate/blob/master/src/src_sinc.c) and [variable-speed regression tests](https://github.com/libsndfile/libsamplerate/blob/master/tests/varispeed_test.c). The tests were inspected, not executed.

### 13. [avaneev/r8brain-free-src](https://github.com/avaneev/r8brain-free-src)

**Language/role:** C++; header-oriented, high-precision audio resampling.

This codebase makes the decomposition of a resampler into rate-conversion stages, filters, interpolation, and intermediate buffers particularly visible.

- **C1:** The main API specifies maximum input block length, output sizing consequences, filter transition-band/attenuation parameters, and latency. Buffer capacity depends on constructor parameters, so violating a block-size contract can invalidate processing assumptions.
- **C3:** The implementation selects power-of-two conversion stages where applicable and fractional interpolation otherwise. The project also reuses expensive FFT/filter resources and exposes precision/backend choices rather than treating all ratios identically.

Entry point and evidence: [resampler construction and processing](https://github.com/avaneev/r8brain-free-src/blob/master/CDSPResampler.h). Each concurrent channel/stream requires its own resampler according to the repository documentation; no published throughput number is adopted here.

### 14. [HEnquist/rubato](https://github.com/HEnquist/rubato)

**Language/role:** Rust; synchronous and asynchronous multichannel sample-rate conversion.

Study the interface between variable-rate DSP and fixed-size audio callbacks, including drift compensation and final partial chunks.

- **C1:** The `Resampler` contract distinguishes required next input/output frame counts, startup delay, partial input, channel masks, and flushing. Partial input can be padded, but the output still needs capacity for a complete output chunk.
- **C3:** The API separates allocating convenience processing from processing into caller-provided buffers. The repository documents fixed-ratio FFT processing and adjustable-ratio sinc or polynomial processing, with explicit quality/CPU tradeoffs and real-time setup requirements.

Entry point and evidence: [`Resampler`, `Indexing`, and processing contracts](https://github.com/HEnquist/rubato/blob/master/src/lib.rs). “Asynchronous” here concerns independent sample clocks and adjustable ratios, not Rust async task execution.

### 15. [breakfastquay/rubberband](https://github.com/breakfastquay/rubberband)

**Language/role:** C++; independent audio time stretching and pitch shifting. **Official GitHub mirror** of the upstream repository identified in its README.

Study an API that must reconcile perceptual processing, variable output production, streaming constraints, and a long-lived caller contract.

- **C1:** Offline processing has a study pass and automatic duration/delay compensation; streaming processing has different padding and ratio-update rules. The header explicitly limits same-instance concurrency and describes buffer-size and extreme-ratio conditions that can trigger allocation.
- **C3:** R2 and R3 processing engines share the public API while offering different processing-cost/quality choices. Real-time behavior is qualified by mode and parameters, rather than promised universally.

Entry points: [processing and thread-safety contract](https://github.com/breakfastquay/rubberband/blob/default/rubberband/RubberBandStretcher.h) and [changelog](https://github.com/breakfastquay/rubberband/blob/default/CHANGELOG), which records final-block fixes, expanded tests, and binary-compatibility commitments back to version 1.7.

## Circuit models, neural effects, and spatial processing

### 16. [Chowdhury-DSP/chowdsp_wdf](https://github.com/Chowdhury-DSP/chowdsp_wdf)

**Language/role:** C++; header-only wave digital filter components for real-time circuit modeling.

Study the mapping from electrical-network structure to typed wave ports and scattering operations, especially beyond simple series/parallel circuits.

- **C1:** The R-type adaptor distinguishes incident and reflected waves, adapted-port impedance, and scattering-matrix port ordering. Its reflected-wave computation explicitly relies on the adapted port's diagonal matrix element being zero.
- **C2:** Port types and impedance calculation are template parameters. Components can therefore be assembled into different circuit topologies while reusing adaptor logic; the project also supports SIMD-valued processing for parallel circuits and matrix operations.

Entry point and evidence: [R-type adaptor implementation](https://github.com/Chowdhury-DSP/chowdsp_wdf/blob/main/include/chowdsp_wdf/rtype/rtype_adaptor.h). This is a dedicated circuit-modeling library, not a duplicate listing of a plugin that happens to use it.

### 17. [jatinchowdhury18/RTNeural](https://github.com/jatinchowdhury18/RTNeural)

**Language/role:** C++; neural-network inference intended for real-time systems, explicitly including audio effects.

RTNeural is a useful bridge between trained neural audio models and per-sample processing constraints. Its role here is inference deployment, not generic model training.

- **C2:** It supports reusable dense, recurrent, convolutional, normalization, and activation layers, with both runtime-loaded models and compile-time model definitions. Weight-loading helpers connect these structures to training-framework exports.
- **C3:** `ModelT` represents layers as a compile-time tuple and unrolls forward propagation through them. Backend choices include Eigen, xsimd, and standard-library implementations, allowing the same model abstraction to target different execution strategies.

Entry point and evidence: [compile-time model and layer-loading implementation](https://github.com/jatinchowdhury18/RTNeural/blob/main/RTNeural/ModelT.h). Static model structure is a concrete optimization mechanism; its speed benefit depends on the model and target.

### 18. [leomccormack/Spatial_Audio_Framework](https://github.com/leomccormack/Spatial_Audio_Framework)

**Language/role:** C/C++; spatial DSP, including spherical harmonics, Ambisonics, HRTFs, panning, and room processing.

Study spatial-audio algorithms where coordinate conventions and numerical normalization are part of the API, and where precision choices affect interactive processing.

- **C1:** Spherical-harmonic functions specify angle conventions, radians, matrix shapes, and normalization. Real/complex basis conversion is expressed through transformation matrices; confusing inclination with elevation would change the rendered field.
- **C3:** The API distinguishes a double-precision harmonic calculation from a single-precision recursive alternative suitable for real-time use, documenting error propagation and limited cases with static buffers. The framework also abstracts optimized BLAS/LAPACK backends.

Entry point and evidence: [spherical-harmonic APIs and numerical tradeoffs](https://github.com/leomccormack/Spatial_Audio_Framework/blob/master/framework/modules/saf_sh/saf_sh.h). Precision/performance claims here are documented design choices, not independently measured comparisons.

## Higher-level language libraries and scientific DSP

### 19. [spotify/pedalboard](https://github.com/spotify/pedalboard)

**Language/role:** Python and C++; audio effects chains, rendering, and external plugin integration.

Although it incorporates JUCE and other engines, Pedalboard has substantial independent processing orchestration. Study how Python arrays and user-selected effect chains meet native processors with variable latency and output behavior.

- **C1:** Its processing loop validates output sample counts, accounts for latency, compacts gaps when plugins return partial blocks, and extends final processing to collect delayed output.
- **C3:** It runs effects over bounded chunks to limit working-memory demands and trims buffers with an allocation-avoidance option. The source also shows why this rendering path must not be generalized into a universal allocation-free callback guarantee.

Entry point and evidence: [native processing and latency reconciliation](https://github.com/spotify/pedalboard/blob/master/pedalboard/process.h). This retained entry is supported by that implementation, not merely by its Python bindings or bundled dependencies.

### 20. [belangeo/pyo](https://github.com/belangeo/pyo)

**Language/role:** Python API with C DSP implementation; synthesis, effects, and interactive signal-processing chains.

Pyo is worth studying for its boundary between a flexible scripting interface and specialized native processing routines.

- **C2:** Audio objects compose into chains, while parameters can be scalars or audio streams. The delay implementation represents both forms explicitly, allowing a single conceptual effect to support static and sample-varying control.
- **C3:** Separate routines handle the scalar/scalar, audio/scalar, and other parameter combinations. Scalar values and derived quantities can be handled outside the inner loop, while audio-rate variants update per sample; ring-buffer interpolation remains native C.

Entry point and evidence: [delay effect and parameter-mode processing](https://github.com/belangeo/pyo/blob/master/src/objects/delaymodule.c). The implementation also bounds delay and feedback values, but no blanket hard-real-time claim is made for the Python environment.

### 21. [JorenSix/TarsosDSP](https://github.com/JorenSix/TarsosDSP)

**Language/role:** Java; audio analysis, filters, time stretching, pitch processing, and effects.

Study how a relatively approachable processing chain handles overlapping windows and stream boundaries without reducing the library to isolated algorithm demos.

- **C1:** `AudioDispatcher` distinguishes byte and sample positions, overlap, and first/last-buffer padding. Processors must cope with a shorter final buffer when padding is disabled. A copy-on-write processor list permits list changes during traversal.
- **C2:** The dispatcher feeds a common `AudioProcessor` chain, allowing FFT analysis, pitch detection, effects, and playback to share stream handling and event metadata.

Entry point and evidence: [audio dispatcher implementation](https://github.com/JorenSix/TarsosDSP/blob/master/core/src/main/java/be/tarsos/dsp/AudioDispatcher.java). The copy-on-write list does not by itself make all dispatcher state thread-safe.

### 22. [Tonejs/Tone.js](https://github.com/Tonejs/Tone.js)

**Language/role:** TypeScript/JavaScript; Web Audio signal control, synthesizers, and effects.

Tone.js contributes reusable audio-graph and automation architecture on top of browser DSP nodes. It is particularly useful for studying the correctness of time-varying control rather than CPU filter kernels.

- **C1:** `Param` reconstructs parameter values from an event timeline, distinguishing target approaches, linear ramps, and exponential ramps. The feedback-effect base class also documents the required delay node in a feedback cycle.
- **C2:** Common effect send/return routing, feedback gain, parameter units, context ownership, and disposal support families of effects rather than one application-specific graph.

Entry points: [parameter automation semantics](https://github.com/Tonejs/Tone.js/blob/dev/Tone/core/context/Param.ts) and [feedback-effect abstraction](https://github.com/Tonejs/Tone.js/blob/dev/Tone/effect/FeedbackEffect.ts). The inspected default branch is `dev`; it should not be assumed identical to a published stable package.

### 23. [ar1st0crat/NWaves](https://github.com/ar1st0crat/NWaves)

**Language/role:** C#; .NET filtering, transforms, audio effects, feature extraction, and signal analysis.

NWaves adds a substantive managed-language implementation rather than a wrapper around the C++ libraries above. Study how offline and incremental processing share DSP kernels.

- **C1:** Its overlap-add convolver derives the hop from FFT and kernel sizes, saves the overlap tail, normalizes spectral multiplication, and explicitly drains delayed output for full-signal filtering.
- **C2:** `OlaBlockConvolver` implements both `IFilter` and `IOnlineFilter`, supports construction from an FIR filter, and offers reset and compatible kernel replacement. This bridges reusable filter abstractions with block-based convolution.
- **C3:** FFT working arrays and the kernel spectrum are prepared and reused, keeping the ordinary per-sample path from allocating those resources repeatedly.

Entry point and evidence: [overlap-add block convolver](https://github.com/ar1st0crat/NWaves/blob/master/NWaves/Operations/Convolution/OlaBlockConvolver.cs).

### 24. [JuliaDSP/DSP.jl](https://github.com/JuliaDSP/DSP.jl)

**Language/role:** Julia; scientific DSP, filter design, spectral estimation, and signal processing.

Study how multiple dispatch expresses distinct filter representations, numeric types, array shapes, and persistent streaming state.

- **C1:** Filtering checks output dimensions, promotes coefficient/sample types, maintains per-section state, and distinguishes ordinary filtering from a stateful direct-form-II-transposed filter. The documented aliasing restrictions matter when callers supply output arrays.
- **C2:** Polynomial ratios, biquads, second-order sections, and zero/pole/gain forms participate in a common filtering API, with conversions where needed. Stateful filters also expose the extra dimensions required for column-wise processing.
- **C3:** FIR dispatch can select direct or FFT-based processing according to data and filter lengths, while direct biquad paths use tight multiply-add recurrences.

Entry point and evidence: [filter dispatch, state, and implementations](https://github.com/JuliaDSP/DSP.jl/blob/master/src/Filters/filt.jl). This is a scientific processing library, not a guarantee of allocation-free live-audio execution.

### 25. [magenta/ddsp](https://github.com/magenta/ddsp)

**Language/role:** Python/TensorFlow; differentiable synthesizers, effects, and DSP functions.

DDSP is included for reusable audio-processing mechanisms, not merely for pretrained models. Study how DSP control constraints and numerical behavior are represented inside trainable tensor computations.

- **C1:** `angular_cumsum` chunks and wraps accumulated phase to reduce long-sequence numerical error; oscillator helpers suppress components above Nyquist. These are concrete numerical issues that remain relevant when the surrounding system is differentiable.
- **C2:** `Processor` separates conversion of inputs into controls from signal generation. `ProcessorGroup` composes named processors through a documented, topologically ordered DAG, making synths, effects, and routing reusable in different models.

Entry points: [DSP numerical primitives](https://github.com/magenta/ddsp/blob/main/ddsp/core.py) and [processor/DAG abstraction](https://github.com/magenta/ddsp/blob/main/ddsp/processors.py). No current framework-version compatibility or real-time deployment claim is inferred from these sources.

## DSP beyond musical audio

### 26. [jgaeddert/liquid-dsp](https://github.com/jgaeddert/liquid-dsp)

**Language/role:** C; reusable DSP for software-defined radio and embedded signal processing.

This is the deliberate non-audio-centered inclusion: its filtering and multirate machinery falls directly within digital signal processing and offers a contrasting complex-signal community.

- **C1:** The arbitrary resampler records explicit timing-phase and filterbank-index invariants, distinguishes boundary and interpolation states, validates construction parameters, and normalizes the designed filter's DC gain.
- **C2:** A macro-parameterized implementation separates input, output, and coefficient types while reusing a polyphase-filterbank abstraction. The broader library exposes filters, oscillators, synchronizers, and other DSP objects independently of a radio application.

Entry point and evidence: [arbitrary-rate resampler implementation](https://github.com/jgaeddert/liquid-dsp/blob/master/src/filter/src/resamp.proto.c). Radio-specific framing and modem functionality were not treated as audio effects.

## Search coverage, exclusions, and limitations

Discovery used **20 distinct live search formulations** across C++ real-time filtering, Rust audio traits and graphs, C embedded effects, wave digital filters, Python/Java/browser libraries, resampling and time stretching, spatial audio, CMSIS/Faust/radio DSP, neural inference, LEAF memory pools, Soundpipe provenance, Julia filtering, and .NET DSP. Later searches revisited portable embedded memory management and arbitrary-rate resampling; these largely returned already-inspected libraries, forks, bindings, and application integrations. The late .NET search added NWaves, justifying extending the selection to 26 rather than omitting a distinct implementation community.

Canonical identity and category fit were checked against repository pages/API metadata and project documentation. Every retained repository also has at least one separately read implementation or substantive API source; selected numerical tests and release notes supplied additional evidence. Failed guessed source paths were resolved through GitHub directory listings and are not cited. API rate limiting was handled by reading public repository pages and raw source files instead. Source links generally track the inspected default branches and may change after the research date.

Important exclusions and boundaries:

- **Soundpipe:** its GitHub repository is archived, and the [author's current project page](https://paulbatchelor.github.io/proj/soundpipe.html) points to SourceHut. It was excluded under the moved-project rule; third-party forks were not substituted for an official current mirror.
- **Forks and wrappers:** search results included alternative Rubber Band, r8brain, DaisySP, and Rust DSP forks/ports, along with thin resampling bindings. These were not counted as independent implementations without evidence of a distinct substantial contribution.
- **Applications and adjacent infrastructure:** DAWs, standalone effects applications, device-I/O transports, plugin-format specifications, tutorial collections, and broad scientific stacks without a closely inspected DSP subsystem were not used to pad the list.
- **Evidence limits:** no candidate was installed, cloned, built, benchmarked, or auditioned. Tests were read, not run. Numerical performance comparisons, uniform code-quality claims, and blanket active-maintenance claims are intentionally absent. C4 is assigned only where dated evolution and concrete maintenance work were inspected; other projects qualify through their implementation evidence.

The strongest use of this report is to choose a code-reading path: start at the linked component, trace its invariants and callers, then inspect the surrounding tests before adopting its techniques.
