# Audio synthesis and sampling engines

Research date: **2026-10-09**.

This selection covers engines that generate musical audio: programmable synthesis runtimes, SoundFont/SFZ samplers, polyphonic instrument cores, embedded synthesis libraries, browser and managed-language engines, and differentiable DSP. The focus is the sound-generating implementation and its control, scheduling, memory, and numerical design. General audio drivers, DAWs, codec libraries, preset collections, thin language bindings, and text-to-speech systems are outside this report. The 25 repositories below are study candidates, not a claim that every component is uniformly exemplary or suitable for immediate production adoption.

**Criteria legend:** **C1** — difficult correctness involving numerical semantics, invariants, concurrency, inputs, or failure modes. **C2** — substantial reusable abstractions supporting multiple uses. **C3** — real performance constraints addressed through understandable architectural choices. **C4** — sustained evolution evidenced by compatibility work, testing, or complexity management; age alone does not qualify. Criteria assignments are engineering judgments grounded in the linked primary material.

## Programmable synthesis runtimes and compilers

### 1. [supercollider/supercollider](https://github.com/supercollider/supercollider)

**Language / role:** C++ and SuperCollider; synthesis servers, language runtime, and supporting tools. Counted once, with emphasis on `scsynth` and the parallel `supernova` server.

Study how a language-independent audio server combines reusable synthesis graphs with strict execution and memory boundaries.

- **C2:** Synth definitions instantiate networks of unit generators; audio/control buses and shared buffers decouple instruments from their consumers. The [server architecture reference](https://doc.sccode.org/Reference/Server-Architecture.html) explains node ordering, graph control, buffer ownership, and the OSC command model.
- **C1, C3:** Supernova's [server implementation header](https://github.com/supercollider/supercollider/blob/develop/server/supernova/server/server.hpp) separates scheduling, node graphs, audio backends, and asynchronous callbacks. Its audio-to-system callbacks use a dedicated memory pool, while deletion callbacks move reclamation out of real-time threads. This makes allocation ownership and multicore scheduling concrete study topics rather than an undifferentiated claim of speed.

### 2. [csound/csound](https://github.com/csound/csound)

**Language / role:** Primarily C/C++; orchestra compiler, opcode ecosystem, and embeddable sound-computing engine. The inspected default branch identifies itself as Csound 7 beta and describes the 6.x line as end-of-life.

Study an engine whose host lifecycle and historical sonic behavior are both part of its interface.

- **C2:** The [public C API](https://github.com/csound/csound/blob/develop/include/csound.h) exposes compilation, instrument/event loading, host audio buffers, and execution one `ksmps` block at a time. Applications can integrate the same engine into real-time hosts or externally driven rendering loops.
- **C1:** That API specifies start/reset ordering, buffer timing, and synchronous versus asynchronous compilation. The [opcode compatibility policy](https://github.com/csound/csound/blob/develop/docs/opcode-deprecation.md) adds a less obvious correctness problem: some legacy output must remain unchanged, even when a supported replacement behaves differently. Source-local alias/legacy/frozen descriptors and generated-inventory checks make these distinctions reviewable. This is evidence of explicit compatibility management, without treating every old opcode as desirable new code.

### 3. [ccrma/chuck](https://github.com/ccrma/chuck)

**Language / role:** C++; strongly timed music language, virtual machine, and synthesis core.

Study the interaction between logical time, concurrent language tasks, and sample generation.

- **C1:** In [the VM implementation](https://github.com/ccrma/chuck/blob/main/src/core/chuck_vm.cpp), `compute()` runs shreds scheduled for the current logical instant, handles queued global messages, and continues through pending events before time advances. Shred removal and object teardown introduce lifetime constraints alongside scheduling correctness.
- **C2:** The [core/host integration documentation](https://github.com/ccrma/chuck/blob/main/README.md#integrating-chuck-as-component-in-other-c-hosts) describes embedding the compiler, VM, and synthesis engine independently of platform audio I/O. The host boundary supports applications, plugins, game engines, and WebAssembly rather than tying the language to its command-line front end.

### 4. [pure-data/pure-data](https://github.com/pure-data/pure-data)

**Language / role:** Primarily C, with Tcl/Tk UI code; visual dataflow synthesis environment. The relevant subsystem is Pd's DSP graph compiler and scheduler, not its patch editor.

Study how an editable patch becomes an efficient executable DSP sequence.

- **C1:** [The DSP graph implementation](https://github.com/pure-data/pure-data/blob/master/src/d_ugen.c) tracks inlet/outlet connectivity, block sizes, overlap, up/downsampling, and borrowed signal buffers. It validates power-of-two reblocking parameters and distinguishes buffer ownership from graph connectivity.
- **C3:** The same file documents copying the DSP graph, sorting it into a linear sequence of operations, and then discarding the graph copy. Size-indexed free lists allow signal buffers to be reused. These are understandable mechanisms for reducing work during repeated audio cycles.

The [repository introduction](https://github.com/pure-data/pure-data/blob/master/README.txt) establishes the real-time computer-music scope and the extension ecosystem; embedding wrappers are not counted separately here.

### 5. [grame-cncm/faust](https://github.com/grame-cncm/faust)

**Language / role:** Primarily C++; functional DSP compiler and synthesis runtime architecture library. Included for generated sound engines and their runtime support, not merely for compiler construction.

- **C2:** The [architecture manual](https://faustdoc.grame.fr/manual/architectures/) separates a DSP computation from audio drivers, controller interfaces, plugin lifecycle, and sample-format adaptation. One synthesis specification can therefore target many host environments through reusable architecture components.
- **C1:** [The polyphonic DSP wrapper](https://github.com/grame-cncm/faust/blob/master-dev/architecture/faust/dsp/poly-dsp.h) implements explicit free, active, release, and legato voice states. Voice reuse, release termination, MIDI-to-parameter mapping, and splitting a processing block around a legato transition expose difficult musical-state and buffer-boundary semantics.

The useful reading path is from the architecture contract to its polyphonic implementation: it connects compilation output to the behavior expected of a playable instrument.

## SoundFont, SFZ, and creative sampling engines

### 6. [FluidSynth/fluidsynth](https://github.com/FluidSynth/fluidsynth)

**Language / role:** C; MIDI-driven SoundFont synthesis library and command-line renderer.

Study format-driven synthesis where MIDI state, sample presets, modulators, and voice ownership interact.

- **C1:** [The synthesizer core](https://github.com/FluidSynth/fluidsynth/blob/master/src/synth/fluid_synth.c) handles note retrigger/release semantics, sustain, channel validation, tuning messages, and voice-overflow policy. Its API entry/exit machinery and configurable thread-safe API show that concurrency is an explicit integration concern.
- **C2:** The [project's design explanation](https://github.com/FluidSynth/fluidsynth/blob/master/README.md#design-decisions) describes a self-contained synthesis component intended for integration into plugins, language bindings, and application frameworks. The implementation exposes MIDI events and synthesis state independently of a particular GUI or device driver.

This is a particularly useful reference for the gap between “play this sample” and implementing a standards-oriented musical instrument.

### 7. [sfztools/sfizz](https://github.com/sfztools/sfizz)

**Language / role:** C++; SFZ parser and sample-synthesis library. **Archived on 2026-06-21**, as shown on the repository page; retained as a substantive historical implementation. Its separate `sfizz-ui` consumer is not another entry.

- **C2:** The [engine description](https://sfztools.github.io/sfizz/engine_description/) separates passive region descriptions, MIDI state, reusable resource pools, and active voices. A callback-based parser can also support non-synthesizer SFZ consumers.
- **C1, C3:** [The file pool implementation](https://github.com/sfztools/sfizz/blob/develop/src/sfizz/FilePool.cpp) manages preloaded sample data, background loading, atomic progress reporting, dispatch, and garbage collection. Reading it alongside the region/voice model reveals the lifetime problem: audio rendering and sample loading must agree about which data is available and still referenced.

The architecture document includes forward-looking descriptions, so current implementation details should be taken from the source rather than assuming every documented plan was completed.

### 8. [swesterfeld/liquidsfz](https://github.com/swesterfeld/liquidsfz)

**Language / role:** C++; embeddable SFZ/Hydrogen sampler with JACK and LV2 front ends.

Study a smaller streaming sampler with unusually explicit operational contracts.

- **C2, C3:** [The public API](https://github.com/swesterfeld/liquidsfz/blob/master/lib/liquidsfz.hh) distinguishes nonblocking live playback from offline rendering that waits for sample loading. It exposes preload duration, voice limits, interpolation quality, and which calls are safe on the audio thread. These controls make latency, memory, and quality tradeoffs visible to the host.
- **C1:** [The change history](https://github.com/swesterfeld/liquidsfz/blob/master/NEWS) documents concrete failure modes: sample-cache races during loading, unsorted MIDI events, malformed SFZ input, invalid loop ranges, and WAV loop-point off-by-one errors. It also records regression testing and sanitizer support. These are specific correctness lessons, not proof that every malformed file is handled safely.

### 9. [schellingb/TinySoundFont](https://github.com/schellingb/TinySoundFont)

**Language / role:** C-compatible single-header SoundFont2 synthesizer; a substantive implementation derived from SFZero.

Study how much synthesis infrastructure can fit behind a compact embedding interface.

- **C2:** [The API and implementation in `tsf.h`](https://github.com/schellingb/TinySoundFont/blob/main/tsf.h) support file, memory, and custom-stream loading, shared sound-bank data across synthesizer instances, channel controls, and float or integer rendering. Allocator and standard-library hooks enable reuse in constrained hosts.
- **C3:** The same source offers voice preallocation to avoid note-on reallocations, bounded conversion buffers, and a configurable control/effect update block size. The comments explain the CPU-versus-modulation-resolution tradeoff.

The [overview](https://github.com/schellingb/TinySoundFont/blob/main/README.md) provides a minimal embedding example. Important limits are explicit in the header: SoundFont modulators and some effect-send behavior are unimplemented, and preallocation is not a general thread-safety guarantee.

### 10. [sinshu/meltysynth](https://github.com/sinshu/meltysynth)

**Language / role:** C#; managed SoundFont/MIDI synthesis engine for .NET. Inspired by earlier synthesizers, but implemented as a distinct managed engine rather than a native-library binding.

- **C1:** [The synthesizer implementation](https://github.com/sinshu/meltysynth/blob/main/MeltySynth/src/Synthesizer.cs) adapts arbitrary equal-length stereo output spans to internal fixed-size rendering blocks while preserving partially consumed blocks. It also interpolates mixing gains and coordinates voice, chorus, and reverb buffers.
- **C2, C3:** Synthesizer state, channels, a bounded voice collection, and reusable audio buffers are initialized separately from repeated rendering. The [usage documentation](https://github.com/sinshu/meltysynth/blob/main/README.md) shows both direct note synthesis and MIDI sequencing into host-provided output buffers, independent of a particular audio driver.

The documentation expressly requires callers to serialize simultaneous note/control and rendering operations; managed memory does not imply a thread-safe instrument.

### 11. [surge-synthesizer/shortcircuit-xt](https://github.com/surge-synthesizer/shortcircuit-xt)

**Language / role:** C++; creative sampler rebuilt from the Shortcircuit lineage. The repository advertises a **beta**; old Shortcircuit code and this substantial rebuild are not counted as separate projects.

- **C1, C3:** [The messaging design embedded in `messaging.h`](https://github.com/surge-synthesizer/shortcircuit-xt/blob/main/src/scxt-core/messaging/messaging.h) distinguishes audio, serialization, and client threads. Fixed-size messages cross the audio boundary through lock-free queues; allocations and later freeing belong on the serialization side. It explains why JSON parsing and UI work cannot enter the audio callback.
- **C2:** [The voice-routing design](https://github.com/surge-synthesizer/shortcircuit-xt/blob/main/doc/VoiceRouting.md) separates zones, groups, parts, internal mixer buses, auxiliary sends, and host outputs, including routing overrides. These abstractions support layered instruments and multiple output arrangements without equating an instrument part with a physical output.

This is a useful evolving design reference; beta status should not be confused with a settled compatibility contract.

## Complete polyphonic instrument cores

### 12. [surge-synthesizer/surge](https://github.com/surge-synthesizer/surge)

**Language / role:** C++; Surge XT synthesizer. Focus on `src/common`, which contains DSP and voice handling, rather than the JUCE interface wrappers.

- **C1:** [The architecture guide](https://github.com/surge-synthesizer/surge/blob/main/doc/Surge%20Architecture.md) explains parameter update semantics, host/UI state synchronization, multiple polyphony modes, MPE channel state, and voice stealing. Patch loading and live parameter changes pass through shared storage abstractions.
- **C3:** The same guide documents startup voice allocation with in-place construction and SIMD code with explicit alignment requirements. It also identifies the headless test/debug host, making these performance choices accessible outside the GUI.

Study how a broad instrument keeps patch state, voice state, and processing code connected. The guide describes itself as incomplete; use its named classes as navigation aids rather than assuming it specifies every invariant.

### 13. [zynaddsubfx/zynaddsubfx](https://github.com/zynaddsubfx/zynaddsubfx)

**Language / role:** C++; additive, subtractive, and PAD synthesis instrument. All three engines belong to this single entry.

- **C1:** [The additive voice implementation](https://github.com/zynaddsubfx/zynaddsubfx/blob/master/src/Synth/ADnote.cpp) handles unison state, modulation, legato-related state, and interpolated wavetable lookup. Its phase accumulator divides integer and fractional components and explicitly manages carry and table wraparound.
- **C3:** The same file explains converting fractional phase to fixed-point inside oscillator loops, while retaining floating-point state outside them. Temporary buffers and unison arrays are allocated through an explicit memory transaction during voice setup. These are concrete numerical and allocation optimizations that can be studied without repeating the source's benchmark percentage.

The [project overview](https://github.com/zynaddsubfx/zynaddsubfx/blob/master/README.adoc) explains the larger engine and instrument-kit structure, including layering and flexible per-part effects.

### 14. [asb2m10/dexed](https://github.com/asb2m10/dexed)

**Language / role:** C++; DX7-oriented FM synthesizer and patch editor, with a synthesis core derived from Google's MSFA work.

Study compatibility-oriented digital synthesis with a compact, data-driven operator graph.

- **C1:** [The FM core](https://github.com/asb2m10/dexed/blob/master/Source/msfa/fm_core.cc) encodes the DX7 algorithm routings as tables and tracks which intermediate buses contain valid data. Fixed-point phase and gain calculations, feedback history, and add-versus-replace behavior must remain consistent across operator orderings.
- **C3:** Rendering selects specialized pure, modulated, and feedback kernels, reuses intermediate buffers, and skips operators below a level threshold. The organization exposes why optimizations must preserve synthesis state even when an operator contributes little audible output.

The [README and changelog](https://github.com/asb2m10/dexed/blob/master/README.md) establish the instrument's DX7 compatibility goals and separate engine choices from plugin/editor behavior. Related ports are not counted independently.

### 15. [mtytel/vital](https://github.com/mtytel/vital)

**Language / role:** C++; spectral-warping wavetable synthesizer. The [repository policy](https://github.com/mtytel/vital/blob/main/README.md) states that source releases lag binary releases and that pull requests are not accepted; this is not presented as an open community development workflow.

- **C2:** [The processor router](https://github.com/mtytel/vital/blob/main/src/synthesis/framework/processor_router.cpp) composes processors behind a common interface, clones local processing state, and propagates sample rate and oversampling settings through a graph. This is useful for understanding reusable infrastructure inside a complete instrument.
- **C1:** The router treats feedback explicitly: it refreshes feedback outputs before executing normal processors, then stores new feedback values afterward. Dependency tracking and graph reordering must preserve that causality while processor configurations change.

The most instructive subsystem here is the synthesis framework's treatment of graph structure and per-instance state, not the surrounding product UI.

## Embedded and reusable native synthesis libraries

### 16. [thestk/stk](https://github.com/thestk/stk)

**Language / role:** C++; Synthesis ToolKit, including physical models, oscillators, filters, and instrument interfaces.

- **C1:** [The plucked-string implementation](https://github.com/thestk/stk/blob/master/src/Plucked.cpp) is a compact numerical study: it compensates delay length for filter phase delay, constrains loop gain below unity, and validates excitation amplitude. These details connect pitch accuracy and stability to a recognizable physical model.
- **C4:** [Dated release notes](https://github.com/thestk/stk/blob/master/doc/ReleaseNotes.txt) document evolution across many years, including multichannel API restructuring, delay and envelope corrections, file-format compatibility, and updates for new audio-backend APIs. This is evidence of sustained complexity management, not simply an old copyright date.

Read the instrument implementation first, then use the release history to see which abstractions and numerical details required repair over time.

### 17. [daisyaudio/DaisySP](https://github.com/daisyaudio/DaisySP)

**Language / role:** C++; modular synthesis and DSP components for embedded hardware and other audio hosts. The former `electro-smith/DaisySP` URL redirects to this canonical repository.

- **C2:** The [library overview](https://github.com/daisyaudio/DaisySP/blob/master/README.md) organizes control generators, oscillators, drum models, physical models, and processing components for reuse in embedded devices, plugins, and applications.
- **C1, C3:** [The oscillator implementation](https://github.com/daisyaudio/DaisySP/blob/master/Source/Synthesis/oscillator.cpp) keeps a small per-instance sample state and offers both direct waveform formulas and polyBLEP-corrected discontinuities. The triangle path uses a leaky integrator; phase wrapping and pulse-width transitions are visible in short routines. The inspected per-sample path performs no heap allocation.

This is a good counterpart to desktop voice engines: individual components make their numerical and per-sample cost decisions easy to inspect. Some algorithms have upstream ancestry; the library is not evidence that every included algorithm was independently invented.

### 18. [PaulBatchelor/Soundpipe](https://github.com/PaulBatchelor/Soundpipe)

**Language / role:** C; lightweight sample-by-sample music DSP library. **Archived on 2024-01-14**, according to the repository page; included as a historical library design.

- **C2:** The [module model](https://github.com/PaulBatchelor/Soundpipe/blob/master/README.md#the-soundpipe-model) separates create, initialize, compute, and destroy phases. A callback drives output frames, while synthesis modules share a small context and consistent lifecycle. Modules include original work and ports from other DSP systems.
- **C1:** [The morphing wavetable oscillator](https://github.com/PaulBatchelor/Soundpipe/blob/master/modules/oscmorph.c) checks table-size agreement, interpolates between tables and adjacent samples, and masks phase wraparound. It is a tractable example of the invariants behind a reusable oscillator.

The README also explains rendered-output hash regression tests. Their presence supports studying deterministic DSP regression practices; it does not establish exhaustive numerical validation or current maintenance.

### 19. [pichenettes/eurorack](https://github.com/pichenettes/eurorack)

**Language / role:** Primarily C/C++; Mutable Instruments hardware/firmware monorepo. Counted once, with the historical Plaits sound-generation subsystem as the entry point; Clouds, Rings, and other modules are not separate repositories.

- **C2, C3:** [Plaits' voice implementation](https://github.com/pichenettes/eurorack/blob/master/plaits/dsp/voice.cc) registers different synthesis engines behind a shared rendering contract. Initialization deliberately reuses the same RAM arena across engines, and shared postprocessing handles gain and low-pass-gate behavior. This makes embedded memory constraints visible in the architecture.
- **C1:** The same implementation delays triggers to accommodate gate/CV timing differences, applies trigger hysteresis, constrains modulation ranges, and resets engine/postprocessor state when selecting another algorithm. These are physical-interface failure modes that desktop-only synthesis examples often omit.

The [module inventory](https://github.com/pichenettes/eurorack/blob/master/README.md) establishes scope. This entry recommends the firmware as an engineering reference and makes no claim of ongoing product support.

## Rust, JVM, browser, Python, and Common Lisp engines

### 20. [SamiPerttu/fundsp](https://github.com/SamiPerttu/fundsp)

**Language / role:** Rust; compositional audio synthesis and processing library, with static graph expressions and dynamic networks.

- **C1, C2:** [The dynamic network implementation](https://github.com/SamiPerttu/fundsp/blob/master/src/net.rs) exposes stable node identities, checked port connections, graph mutation, topology determination, and recoverable cycle errors. Its ordering deliberately includes nodes disconnected from outputs because those nodes may have side effects.
- **C3:** [The real-time network backend](https://github.com/SamiPerttu/fundsp/blob/master/src/realnet.rs) receives new graph versions through queues, migrates existing node state, and returns superseded graphs and units to the front end for deallocation. This separates interactive editing from repeated audio processing and makes state continuity during graph replacement a central concern.

Study the dynamic network/backend pair alongside the repository's type-based composition model to compare compile-time structure with runtime editability.

### 21. [philburk/jsyn](https://github.com/philburk/jsyn)

**Language / role:** Java; modular unit-generator synthesizer.

- **C2:** The [project documentation](https://github.com/philburk/jsyn/blob/master/README.md) describes connectable oscillators, filters, and envelopes controlled from ordinary Java programs. The engine separates the public synthesizer interface from audio-device management and unit execution.
- **C1:** [The synthesis engine](https://github.com/philburk/jsyn/blob/master/src/main/java/com/jsyn/engine/SynthesisEngine.java) processes timestamped commands before synthesis blocks, maintains a frame-based clock, and manages running/stopping unit collections. Startup/shutdown synchronization and interrupted audio I/O provide concrete lifecycle problems to inspect.

This offers a useful comparison with native engines: the implementation contains synchronization and allocation, so “real-time synthesis” should not be read as a blanket hard-real-time or allocation-free guarantee.

### 22. [Tonejs/Tone.js](https://github.com/Tonejs/Tone.js)

**Language / role:** TypeScript; browser synthesis, sampling, scheduling, and musical control framework built on Web Audio.

- **C2:** The [architecture and usage overview](https://github.com/Tonejs/Tone.js/blob/dev/README.md) combines musical transport/timing with synths, effects, and signal components. This is a substantial musical runtime above browser audio primitives, rather than a generated binding.
- **C1, C3:** [The polyphonic instrument implementation](https://github.com/Tonejs/Tone.js/blob/dev/Tone/instrument/PolySynth.ts) distinguishes allocated, active, released, and available voices; returns voices through silence callbacks; and reclaims excess idle voices according to recent demand. The inspected implementation drops a note when the polyphony limit is exhausted, despite an older nearby comment mentioning stealing.

The source is valuable for understanding asynchronous envelope completion, overlapping notes, and bounded resource use in a browser host.

### 23. [belangeo/pyo](https://github.com/belangeo/pyo)

**Language / role:** Python and C; scripted synthesis and signal-processing engine with native DSP execution.

- **C2:** The [project overview](https://github.com/belangeo/pyo/blob/master/README.md) describes reusable synthesis generators, signal arithmetic, filters, granulation, and control objects assembled in Python. The native server supports multiple execution contexts, including offline and embedded processing.
- **C1:** [The server implementation](https://github.com/belangeo/pyo/blob/master/src/engine/servermodule.c) coordinates stream activation/duration, channel mixing, MIDI timing, embedded callbacks, and Python's GIL. Its audio-processing code explicitly identifies GIL acquisition/release as a callback bottleneck.

Study this boundary for the tradeoffs of a flexible scripting interface around native synthesis. The source supports a discussion of concurrency and latency costs; it does not justify describing the callback as lock-free.

### 24. [titola/incudine](https://github.com/titola/incudine)

**Language / role:** Common Lisp and C; programmable synthesis environment for SBCL. **Project-listed GitHub mirror:** the [README](https://github.com/titola/incudine/blob/master/README.md) identifies SourceForge as the main repository and this GitHub URL as its mirror. The mirror contains the actual engine, documentation, and tests.

- **C2:** Virtual UGens compose Lisp expressions, nested virtual generators, and compiled generators. DSP construction infers initialization-time versus performance-time actions before compilation, allowing users to define new synthesis primitives rather than only connect a fixed catalog.
- **C1:** [The earliest-deadline-first scheduler](https://github.com/titola/incudine/blob/master/src/edf-sched.lisp) represents events in a preallocated heap with sample-time deadlines and a separate ordering tag for equal-time events. Heap size, event ordering, and mutable callback state make sample scheduling a concrete correctness problem.

The README also explicitly distinguishes facilities for allocation-free DSP from having a real-time garbage collector, which it does not provide. This is a useful compiler-oriented contrast to managed-language unit-generator engines.

## Differentiable sound synthesis

### 25. [magenta/ddsp](https://github.com/magenta/ddsp)

**Language / role:** Python/TensorFlow; differentiable synthesizers and processors used as trainable audio-generation components. This entry concerns the reusable DSP synthesis layer, not a general-purpose audio model collection.

- **C1:** [The synthesizer implementations](https://github.com/magenta/ddsp/blob/main/ddsp/synths.py) define control-tensor shapes, amplitude scaling, envelope resampling, and harmonic normalization after removing components above Nyquist. Correctness therefore includes both sound synthesis and the numerical representation of neural-network controls.
- **C2:** [The processor abstraction](https://github.com/magenta/ddsp/blob/main/ddsp/processors.py) separates conversion into valid controls from signal generation. `ProcessorGroup` composes these layers through a named, topologically ordered graph, allowing harmonic oscillators, filtered noise, and effects to be combined in different models.

This is a useful contrast to callback-driven samplers: batch dimensions, differentiability, and parameter conditioning matter alongside ordinary DSP semantics. No hard-real-time claim is made.

## Coverage, search method, and limitations

Live discovery used more than six distinct formulations, including synthesis-language/server architecture; SFZ disk streaming; SoundFont synthesis in C and .NET; desktop polyphonic/FM/wavetable engines; embedded and physical-modeling libraries; Rust DSP graph engines; Java/JavaScript/Python synthesis; Common Lisp synthesis; granular synthesis; and differentiable DSP. Follow-up searches checked archival status and repository moves. Later broad and niche searches increasingly returned the same established engines, wrappers, ports, or small demonstration projects, providing diminishing additional coverage; the Common Lisp search still added Incudine's distinct compilation model.

Every retained canonical repository URL was opened, and each entry was checked against additional primary code or documentation. Source-file contents were read, not merely inferred from search snippets. The default branches were checked to avoid assuming `main` or `master`; DaisySP's owner redirect was resolved. sfizz and Soundpipe are explicitly marked archived. Vital's delayed source-publication policy and Shortcircuit XT's beta status are also material to interpreting these entries. Links follow inspected branches rather than immutable commits, so later source changes can alter the details.

The selection favors independently substantial implementations. It avoids separately counting Supernova, the three ZynAddSubFX engines, individual Mutable Instruments modules, sfizz's UI, and ports/wrappers around an already listed engine. General audio I/O frameworks, DAWs, effect-only collections, tutorials, and preset repositories were excluded. LinuxSampler's [official source-distribution page](https://linuxsampler.org/downloads.html) directs readers to Subversion; this search did not establish the official status and synchronization of its GitHub copy, so it was not retained. That is a verification limitation, not a judgment about its engine. Small granular-synthesis demonstrations were considered but did not add enough supported architectural depth beyond the retained engines.

This is source/documentation research, not a build, listening test, security audit, benchmark, or exhaustive assessment of supported sample formats. No candidate dependencies were installed and no candidate code was executed. Numerical and concurrency mechanisms are reported as observed; conclusions about what engineers can learn are grounded inference. Historical projects remain useful for study, but lack of an archive banner is not treated as evidence of active maintenance. C4 is awarded only where the inspected history supports sustained evolution, rather than being assumed for every familiar name.
