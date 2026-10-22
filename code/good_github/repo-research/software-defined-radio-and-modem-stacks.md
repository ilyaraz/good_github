# Software-defined radio and modem stacks

Research date: **2026-10-09**.

This selection covers reusable SDR runtimes, hardware streaming interfaces, cellular and other radio physical layers, satellite/navigation receivers, audio-band modems, and substantial receiver applications. The emphasis is the path from sampled signals through synchronization, decoding, and protocol delivery. Hardware-only designs, cellular core networks without a radio subsystem, thin device wrappers, and demonstration flowgraphs are outside this report. The 25 repositories below offer different engineering lessons; inclusion is not a claim that every component is exemplary or currently maintained.

Criteria used throughout:

- **C1 — Difficult correctness:** numerical, synchronization, concurrency, framing, resource-lifetime, or failure-handling invariants.
- **C2 — Reusable abstractions:** substantial interfaces or components that support multiple devices, waveforms, applications, or operating modes.
- **C3 — Performance with structure:** explicit throughput, latency, memory, or processing constraints addressed through an understandable architecture.
- **C4 — Evolution and complexity management:** documented adaptation over years, accompanied by compatibility work, testing, or structural improvements. Age alone does not qualify.

Linked repository headings identify the verified GitHub locations. The implementation and documentation links within each entry are recommended study entry points. Statements about what an engineer can learn are interpretations of those sources, rather than independent benchmark or correctness certifications.

## DSP libraries and execution runtimes

### 1. [gnuradio/gnuradio](https://github.com/gnuradio/gnuradio)

**Language / role:** C++ and Python; general-purpose streaming DSP framework, block libraries, and flowgraph tooling.

GNU Radio is particularly useful for studying the boundary between a DSP algorithm and a scheduler that must keep an entire graph making progress. The relevant subsystem is the runtime, not just the graphical flowgraph editor.

- **C1:** The [block executor](https://github.com/gnuradio/gnuradio/blob/main/gnuradio-runtime/lib/block_executor.cc) reconciles available input, free output space, rate forecasts, output multiples, alignment, and upstream completion. It checks invalid negative input requirements, reduces work requests when input is insufficient, and invokes blocked-buffer callbacks under locks. These are concrete progress and buffer-contract invariants.
- **C2 / C3:** That same executor supports fixed-rate and general blocks through common forecasting and work interfaces, while batching aligned work and propagating stream tags according to relative rates. Study how reusable block contracts carry enough information for scheduling without embedding each modulation scheme in the runtime.

### 2. [jgaeddert/liquid-dsp](https://github.com/jgaeddert/liquid-dsp)

**Language / role:** C; embeddable DSP, synchronization, filtering, coding, and modem library.

This is a strong library-scale counterpart to a full graph runtime. Its object APIs expose communication algorithms without requiring an application to adopt a particular scheduler.

- **C1 / C2:** The [OFDM flexible-frame documentation](https://liquidsdr.org/doc/ofdmflexframe/) describes paired frame-generator and synchronizer objects, pilot/data/null subcarrier allocation, cyclic-prefix and taper constraints, arbitrary input chunk sizes, and separate header/payload validity in callbacks. These make framing and acquisition semantics explicit while allowing many packet formats and modulation configurations.
- **C3 / C4:** The [changelog](https://github.com/jgaeddert/liquid-dsp/blob/master/CHANGELOG.md) records runtime SIMD dispatch, architecture-specific kernels, randomized test execution, spectral tests, state-preserving object copying, and numerical/modem fixes across multiple releases from 2022 through 2026. It is useful evidence of performance work accompanied by testing and API management, rather than merely a long repository lifetime.

### 3. [FutureSDR/FutureSDR](https://github.com/FutureSDR/FutureSDR)

**Language / role:** Rust; asynchronous SDR runtime with stream/message processing and heterogeneous-buffer support.

The project describes itself as experimental, with evolving APIs. Its value here is the explicit treatment of asynchronous block execution and Rust's execution-domain constraints.

- **C1:** The [kernel contract](https://github.com/FutureSDR/FutureSDR/blob/main/src/runtime/kernel.rs) specifies initialization, work, and teardown; consuming and producing handled samples; completion and immediate-reschedule flags; and waiting on futures alongside runtime events. It distinguishes kernels/futures that can cross threads from local execution, exposing concurrency assumptions at the interface.
- **C2:** The same contract separates an algorithm's lifecycle from runtime scheduling. Together with the repository's stream/message blocks and extensible buffers, this gives engineers a compact example of building reusable radio components around async execution rather than a single receiver program.

### 4. [vsergeev/luaradio](https://github.com/vsergeev/luaradio)

**Language / role:** Lua with LuaJIT and native DSP integrations; lightweight composable SDR framework.

LuaRadio offers a smaller, dynamic-language treatment of graph composition. The interesting material is the graph validation and lifecycle model, not simply its concise receiver examples.

- **C1:** The [reference manual's CompositeBlock documentation](https://luaradio.io/docs/reference-manual.html) describes rejection of duplicate or missing port connections, incompatible type signatures, and sample-rate mismatches. These checks move several signal-pipeline errors to graph construction instead of leaving them implicit in sample-processing code.
- **C2:** Composite blocks alias internal ports and can themselves be embedded in larger graphs; ordinary blocks operate on typed sample vectors. The documented start, wait, stop, and run lifecycle provides reusable execution control across different receiver compositions.

## Device interfaces and sample transport

### 5. [pothosware/SoapySDR](https://github.com/pothosware/SoapySDR)

**Language / role:** C++ with a C API and language bindings; vendor-neutral SDR device and streaming interface.

SoapySDR is useful for studying how an abstraction can preserve hardware-specific capabilities while defining predictable behavior for portable applications.

- **C1:** The [Device API](https://pothosware.github.io/SoapySDR/doxygen/latest/classSoapySDR_1_1Device.html) defines stream timeouts, inactive-stream behavior, timestamps, burst/error status, and acquire/release ownership for direct buffers. Its handling of unsupported status polling is an example of making optional capabilities explicit rather than interpreting their absence as a device failure.
- **C2 / C3:** The same interface offers multi-channel streaming and tuning across device implementations, plus direct-buffer access where ordinary copied reads/writes are inadequate. The study opportunity is the relationship between a portable baseline and optional paths for tighter transport constraints.

### 6. [EttusResearch/uhd](https://github.com/EttusResearch/uhd)

**Language / role:** C++ host code, firmware, and Verilog/FPGA components; USRP Hardware Driver and associated radio infrastructure.

Count this monorepo once. The relevant study path runs through host streamers, transport, and their interface to FPGA processing, including RFNoC.

- **C1:** The [streaming manual](https://files.ettus.com/manual/page_stream.html) explains why applications must keep receiving or sending to avoid overflows and underruns, how remote streaming interacts with flow control, and how stream creation differs between the multi-USRP interface and an explicitly connected RFNoC graph.
- **C2 / C3:** Streamers separate application buffers from device/network transport. The manual connects CPU versus wire sample formats, packet/MTU constraints, ring buffers, and FPGA FIFOs to bandwidth and buffering choices. This makes UHD valuable for understanding why real-time sample transport requires coordinated decisions across software and hardware layers.

### 7. [Nuand/bladeRF](https://github.com/Nuand/bladeRF)

**Language / role:** C host library and firmware plus FPGA HDL; bladeRF device software stack.

The host library provides an unusually concrete case study of a synchronous API layered over asynchronous transfers and internal worker threads.

- **C1:** The [synchronous streaming guide](https://www.nuand.com/libbladeRF-doc/v2.5.0/sync_no_meta.html) documents configuration-before-use, module enable/disable order, timeout relationships, and partial-transmit behavior. A short transmission may need padding because the internal transport submits full buffers; this is an observable contract that callers must understand.
- **C2 / C3:** The sync layer accepts user-sized buffers while managing asynchronous internal transfers. The same guide explains how internal buffer size, buffer count, and in-flight transfer count affect latency and susceptibility to overruns/underruns. Study this as a reusable facade with deliberately exposed performance controls. The cited guide is versioned at libbladeRF 2.5.0.

## Cellular radio stacks

### 8. [srsran/srsRAN_4G](https://github.com/srsran/srsRAN_4G)

**Language / role:** C and C++; LTE UE/eNodeB and shared radio/protocol libraries.

This is the substantive 4G repository, distinct from the now-archived srsRAN Project transition repository discussed in the exclusions. It supports study of both radio timing and long-term protocol-stack changes.

- **C1 / C3:** The eNodeB [PHY transmit/receive loop](https://github.com/srsran/srsRAN_4G/blob/master/srsenb/src/phy/txrx.cc) maps carrier/port sample buffers into worker contexts, advances radio timestamps for transmit timing, dispatches PRACH processing, and coordinates worker ordering and shutdown. The worker-pool design is tied directly to subframe processing deadlines.
- **C4:** The [changelog](https://github.com/srsran/srsRAN_4G/blob/master/CHANGELOG) records TTCN-3 test adaptation, nonblocking RRC/NAS and PHY work, data-plane allocation removal, integrity and buffer fixes, timer separation, ASN.1 updates, and compiler compatibility across multiple years. These changes supply stronger evidence of complexity management than a claim of maturity based on age.

### 9. [duranta-project/openairinterface5g](https://github.com/duranta-project/openairinterface5g)

**Language / role:** Primarily C with C++; OpenAirInterface-derived 4G/5G RAN and UE implementations under the current Duranta GitHub location.

The former [OPENAIRINTERFACE namespace](https://github.com/OPENAIRINTERFACE/openairinterface5g) identifies itself as a read-only mirror of this repository. Count the implementation once, at the verified current location. Relevant subsystems include PHY, MAC/RLC/PDCP/RRC, radio interfaces, and their integration.

- **C1:** The [NR UE design document](https://github.com/duranta-project/openairinterface5g/blob/develop/doc/nr-ue-design.md) explains initial synchronization, frame alignment, dummy radio reads used to prevent receive overflow during synchronization, and dependencies between downlink decoding and uplink control generation. It also identifies limitations in the optional continuous resynchronization path rather than promising seamless recovery.
- **C2 / C3:** Explicit MAC–PHY indication and scheduled-response interfaces connect the layers, while separate downlink and uplink actors divide time-sensitive work. Study how protocol interfaces and execution dependencies coexist in a real UE, rather than treating the standards layers as independently scheduled boxes.

### 10. [osmocom/osmo-trx](https://github.com/osmocom/osmo-trx)

**Language / role:** C and C++; GSM/GPRS/EGPRS radio transceiver layer used with OsmoBTS.

**Official GitHub mirror:** the repository identifies Osmocom's Gitea service as its upstream. Its OpenBTS ancestry is explicit, but the retained project has substantive independent Osmocom development and integration.

- **C1:** The [radio buffer implementation](https://github.com/osmocom/osmo-trx/blob/master/Transceiver52M/radioBuffer.cpp) reconciles variable-length writes with fixed processing segments, tracks available/free capacity, and preserves filter history across wraparound. These details connect ordinary ring-buffer correctness to continuity of the radio signal.
- **C2 / C3:** The [multi-carrier interface](https://github.com/osmocom/osmo-trx/blob/master/Transceiver52M/radioInterfaceMulti.cpp) composes resamplers, a channelizer, and a synthesis bank around timestamped device I/O. Logical-to-physical channel mapping, valid frequency spacing, and per-channel filter history make it a focused study of sharing a wideband device among narrower radio channels.

## Reusable waveform implementations

### 11. [bastibl/gr-ieee802-11](https://github.com/bastibl/gr-ieee802-11)

**Language / role:** C++ and Python; GNU Radio IEEE 802.11a/g/p physical-layer transceiver.

This is a research-oriented Wi-Fi PHY, not a claim to implement every modern Wi-Fi generation or a complete production MAC stack. The inspected branch is `maint-3.10`.

- **C1:** The [frame equalizer](https://github.com/bastibl/gr-ieee802-11/blob/maint-3.10/lib/frame_equalizer_impl.cc) couples packet-start tags, pilot-based frequency correction, SIGNAL-field deinterleaving/Viterbi decoding and parity checks, and payload modulation/length selection. An engineer can trace how early synchronization and header errors affect downstream symbol interpretation.
- **C2:** The same block exposes selectable COMB, LS, LMS, and STA equalization algorithms, with synchronized configuration changes, within the repository's hierarchical PHY. This gives a concrete extension point for comparing channel-estimation algorithms while retaining the surrounding frame-processing chain.

### 12. [tapparelj/gr-lora_sdr](https://github.com/tapparelj/gr-lora_sdr)

**Language / role:** C++ and Python; GNU Radio LoRa physical-layer transmitter and receiver.

The implementation includes coding, whitening, headers, modulation, synchronization, and decoding, rather than merely translating bytes into chirps. Its scope is the LoRa PHY; a complete LoRaWAN network stack is a separate concern.

- **C1:** The [frame synchronizer](https://github.com/tapparelj/gr-lora_sdr/blob/master/lib/frame_sync_impl.cc) estimates fractional carrier and symbol-timing offsets. Dechirping, zero-padded FFTs, spectral-peak interpolation, wrapped bin selection, and phase correction expose the numerical work required before reliable payload decoding is possible.
- **C2:** The repository separates transmit/receive stages into GNU Radio blocks and configurable hierarchies, with different spreading factors, coding settings, and soft-decoding options. Its documented simulation applications and hardware interoperability notes give engineers a way to connect component-level processing to complete links; the README also calls out device-specific caveats for the lowest spreading factors.

### 13. [igorauad/gr-dvbs2rx](https://github.com/igorauad/gr-dvbs2rx)

**Language / role:** C++ and Python; DVB-S2 receiver, GNU Radio blocks, and receiver/transmitter command-line tools.

This is a substantively extended descendant of `drmpeg/gr-dvbs2rx`: the README documents added physical-layer synchronization, a full reception chain, BCH work, and accelerated LDPC decoding. The ancestor is not counted separately. The repository's last push reported by GitHub during research was in July 2024; treat this as a useful codebase without assuming ongoing maintenance.

- **C2:** The project connects acquisition and physical-layer synchronization through FEC and baseband-frame handling to transport-stream output. Its separate blocks and CLI integration make it useful for studying where receiver stages can be reused and where frame structure constrains their interfaces.
- **C3:** The [LDPC decoder implementation](https://github.com/igorauad/gr-dvbs2rx/blob/master/lib/ldpc_decoder_bb_impl.cc) dispatches among generic, NEON, SSE4.1, and AVX2 implementations, sizes aligned batches by SIMD width, and sets output multiples/relative rates around complete codewords. This is a concrete link between error-correction throughput and scheduler-visible structure, without requiring an unsupported speedup claim.

## Satellite and navigation processing

### 14. [gnss-sdr/gnss-sdr](https://github.com/gnss-sdr/gnss-sdr)

**Language / role:** C++ with supporting scripts; configurable multi-signal GNSS software receiver.

GNSS-SDR connects acquisition and tracking to navigation data and positioning. Acquisition is an especially well-documented entry point into the numerical and scheduling tradeoffs of a weak-signal receiver.

- **C1:** The [acquisition documentation](https://gnss-sdr.org/docs/sp-blocks/acquisition/) derives the code-phase/Doppler search and detection statistic, explains false-alarm-probability thresholds, and documents noncoherent integration and navigation-bit-transition behavior. Parameter interactions affect statistical interpretation, not just configuration convenience.
- **C2 / C3:** Configurable acquisition implementations use FFT-based correlation and optional resampling to control work. The documentation explicitly explains that nonblocking acquisition can skip arriving samples while a separate thread searches, trading real-time operation against reproducibility relative to blocking file processing. This is a useful, unusually candid explanation of performance semantics.

### 15. [tomojitakasu/PocketSDR](https://github.com/tomojitakasu/PocketSDR)

**Language / role:** C/C++ and Python; compact multi-GNSS acquisition, tracking, navigation decoding, and positioning stack with hardware support.

PocketSDR provides a more concentrated per-channel implementation than a large flowgraph receiver. Its relevant subsystem is the software receiver, not solely the associated RF hardware designs.

- **C1:** The [channel implementation](https://github.com/tomojitakasu/PocketSDR/blob/master/src/sdr_ch.c) contains code/carrier tracking and signal-specific handling of secondary-code boundaries, polarity, and sideband combinations. These are concrete examples of preserving coherent correlation across signal structures and acquisition-to-tracking transitions.
- **C2 / C3:** Acquisition and tracking state are organized as reusable per-signal channels, with precomputed code spectra/Doppler search data and specialized correlation preparation. Study how a common channel lifecycle accommodates different GNSS signal families while keeping expensive numerical work out of repeated setup paths.

### 16. [daniestevez/gr-satellites](https://github.com/daniestevez/gr-satellites)

**Language / role:** Python and C++; GNU Radio satellite telemetry decoders and reusable reception components.

This project is valuable for its decomposition of many independently developed spacecraft protocols. It avoids requiring every satellite to have a wholly separate monolithic receiver.

- **C1 / C2:** The [component architecture](https://github.com/daniestevez/gr-satellites/blob/main/docs/source/components.rst) separates signal sources, demodulators producing soft symbols, deframers, transport reassembly, and data sinks. Its detailed AX.25 and other framing descriptions show why descrambling, NRZI decoding, bit destuffing, error correction, checksums, and packet reassembly belong at specific boundaries rather than in an interchangeable bag of filters.
- **C4:** The repository documents the major component refactor and distinct GNU Radio compatibility generations, including GNU Radio 3.7, 3.9, and 3.10 lines and the frozen older branch. This supports a specific evolution claim: preserving and declaring compatibility boundaries while redesigning reusable receiver structure.

### 17. [SatDump/SatDump](https://github.com/SatDump/SatDump)

**Language / role:** C++; satellite reception, demodulation, decoding, and product-generation application/framework.

SatDump spans more of the path from RF samples to usable satellite products than a modem block library. Focus on its processing pipeline and module infrastructure when comparing it with narrower telemetry decoders.

- **C1:** The [live pipeline implementation](https://github.com/SatDump/SatDump/blob/master/src-core/pipeline/live_pipeline.cpp) connects modules through streams/FIFOs and launches work through a thread pool. Shutdown marks inputs inactive, stops readers/writers and modules, and waits for task futures: a concrete study of how a multistage receiver must release blocked processing safely.
- **C2:** Pipeline steps instantiate modules with merged parameters and adapt to ordinary live, server, and client arrangements. Input and output boundaries can represent sample streams, byte FIFOs, or files, allowing substantial portions of a decoding pipeline to be reused across acquisition and processing modes.

## Audio-band and packet-radio modems

### 18. [drowe67/codec2](https://github.com/drowe67/codec2)

**Language / role:** C and Octave; retained here for its FreeDV/FSK/OFDM modem and FEC subsystems, alongside the speech codec.

Maintenance is uneven: the README explicitly marks several classic FreeDV modes and other legacy components as no longer actively maintained while development focuses on newer work. This entry is about substantive modem implementation and API design, not an assertion that every historical mode is supported.

- **C1:** The [data-mode guide](https://github.com/drowe67/codec2/blob/main/README_data.md) explains burst acquisition, unique words, pilots, CRC/FEC, and OFDM framing over multipath channels. It distinguishes modem-level validation from lost-frame handling, segmentation, and reassembly that the caller must provide.
- **C2:** The same guide describes APIs spanning FSK/LDPC and OFDM data modes, with modulation and framing machinery reusable outside speech applications. Its channel-simulation workflows give a concrete starting point for examining frame-error behavior; the results were not independently reproduced for this report.

### 19. [wb2osz/direwolf](https://github.com/wb2osz/direwolf)

**Language / role:** C; software sound-card TNC, AX.25/APRS modem, and packet-radio integration stack.

Dire Wolf joins audio demodulation, link framing, and application-facing TNC interfaces. It is especially useful for studying practical recovery from imperfect audio rather than an idealized textbook waveform.

- **C1:** The [AFSK demodulator](https://github.com/wb2osz/direwolf/blob/master/src/demod_afsk.c) maintains channel/subchannel/slicer state, uses peak/valley AGC to compensate for tone imbalance, and distinguishes timing-loop behavior during search and lock. The code documents signal-processing alternatives and connects adaptation directly to received-bit decisions.
- **C2:** Demodulated bits pass to an HDLC receiver through a defined boundary, while the complete project exposes virtual-TNC interfaces such as KISS and AGW to applications. This separation makes the same audio/modem machinery useful in multiple station and client arrangements rather than tying it to one APRS user interface.

### 20. [iontodirel/libmodem](https://github.com/iontodirel/libmodem)

**Language / role:** C++20; composable software modem, audio, framing, and transport library.

This is a newer, less established project; it is included for concrete abstractions and tests, with no C4 or long-term maintenance claim.

- **C2:** The [pipeline interfaces](https://github.com/iontodirel/libmodem/blob/main/libmodem/pipeline.h) distinguish audio, PTT, modem, transport, formatting, and bitstream conversion components. Ownership, per-component error events, and atomic fault state make integration behavior part of the library structure rather than application-specific glue.
- **C1:** The [test suite](https://github.com/iontodirel/libmodem/blob/main/tests/tests.cpp) includes AFSK phase-continuity checks and bitstream reconstruction with counters initialized near `size_t` wraparound, alongside waveform/demodulation scenarios. These are meaningful checks of numerical continuity and boundary arithmetic, not merely examples that instantiate the public API.

## Integrated receivers and protocol decoding

### 21. [f4exb/sdrangel](https://github.com/f4exb/sdrangel)

**Language / role:** C++ and Qt; extensible SDR receiver/transmitter application with device and channel plugins.

SDRangel is a useful large-application study because it explains how GUI control, hardware streams, and multiple independent radio channels coexist.

- **C1 / C2:** The [developer notes](https://github.com/f4exb/sdrangel/wiki/Developers-notes) describe device engines, channel processors, FIFO boundaries between processing threads, and message-based interaction with the GUI thread. Separate sample-source/sink and channel plugins make the execution structure reusable across devices and modulations.
- **C3:** Those notes place halfband decimation/interpolation, channelization, frequency translation, and rational resampling at explicit stages. The [special-device documentation](https://github.com/f4exb/sdrangel/wiki/Plugins-for-special-devices) extends the design to remote UDP sample transport, erasure coding, and sample-rate/skew compensation. Study how local DSP rate choices become network queue and clock-drift problems when a device moves off-host.

### 22. [AlexandreRouma/SDRPlusPlus](https://github.com/AlexandreRouma/SDRPlusPlus)

**Language / role:** C++; modular SDR receiver application and internal DSP framework.

The application combines device and demodulator modules with multiple receiver channels. Its small internal stream primitive is a particularly accessible entry point into the concurrency beneath an interactive SDR.

- **C1:** The [typed stream implementation](https://github.com/AlexandreRouma/SDRPlusPlus/blob/master/core/src/dsp/stream.h) uses condition variables for producer/consumer handoff, tracks data-ready and can-swap states, and provides separate reader/writer stop operations that wake blocked participants. Buffer ownership and shutdown are visible in one place.
- **C2 / C3:** The templated stream connects different DSP components using the same read/swap/flush protocol. Exchanging read/write buffer pointers avoids copying each block during handoff, while preserving backpressure. This is a concrete performance-oriented abstraction worth comparing with GNU Radio's more general scheduling contracts.

### 23. [AlbrechtL/welle.io](https://github.com/AlbrechtL/welle.io)

**Language / role:** C++ decoding/backend code and Qt application; DAB/DAB+ software receiver.

The repository warns that its macOS and Android variants are unmaintained; do not infer uniform platform support from its cross-platform origins. Its backend remains a substantive broadcast-receiver study.

- **C1 / C3:** The [OFDM processor](https://github.com/AlbrechtL/welle.io/blob/master/src/backend/ofdm-processor.cpp) handles coarse/fine frequency correction, null-symbol and phase-reference synchronization, repeated acquisition attempts, and processor-thread stop/restart behavior. Its discussion of batch versus per-sample input connects processing overhead to the structure of the receive loop.
- **C2:** The [radio receiver coordinator](https://github.com/AlbrechtL/welle.io/blob/master/src/backend/radio-receiver.cpp) separates input/control interfaces, OFDM processing, FIC/MSC handlers, and service/subchannel selection. Engineers can trace the boundary between ensemble reception and selecting one or more decoded services without starting from the GUI.

### 24. [merbanan/rtl_433](https://github.com/merbanan/rtl_433)

**Language / role:** C; reusable pulse/protocol decoding infrastructure and a large collection of low-power radio device decoders.

Although commonly used as a command-line receiver, rtl_433 contains substantial shared decoding infrastructure. The relevant scope is turning uncertain pulse/bit observations into validated device messages, not merely exposing an RTL-SDR driver.

- **C1:** The [Bresser 6-in-1 decoder](https://github.com/merbanan/rtl_433/blob/master/src/devices/bresser_6in1.c) documents the packet layout and checks row count, bit length, preamble placement, remaining payload, an LFSR digest, and an additive checksum before extracting fields. It is a concrete example of controlling false positives and incomplete/malformed radio packets.
- **C2:** The [contribution guide](https://github.com/merbanan/rtl_433/blob/master/docs/CONTRIBUTING.md) explains device descriptors, shared bit-buffer and structured-output conventions, and labeled signal captures replayed for regression testing. That infrastructure allows many protocol implementations to share acquisition and presentation machinery while retaining device-specific validation.

### 25. [DSheirer/sdrtrunk](https://github.com/DSheirer/sdrtrunk)

**Language / role:** Java; SDR monitoring, decoding, recording, and streaming for trunked and related radio protocols.

sdrtrunk broadens the implementation-language coverage and supplies a substantial managed-runtime DSP example. The channelizer is a better architectural starting point than treating the project solely as a scanner UI.

- **C1:** The [complex polyphase channelizer](https://github.com/DSheirer/sdrtrunk/blob/master/src/main/java/io/github/dsheirer/dsp/filter/channelizer/ComplexPolyphaseChannelizerM2.java) enforces an even channel count, maintains input/history state across sample batches, and coordinates filtered channel results with inverse-FFT processing. Its scratch-buffer reuse is explicitly justified by the dispatcher execution model.
- **C3:** The implementation arranges taps and samples contiguously to support Java SIMD, separates filtering/reordering from inverse FFT work, and batches dispatch to another processing thread. These are inspectable architectural responses to processing a wideband input into many channels; no numerical speedup is assumed here.

## Search coverage, exclusions, and limits

Discovery used more than six distinct live-web query families, followed by opened repository pages or GitHub API metadata and independently read implementation/documentation material for every retained repository. Search angles included:

- SDR graph schedulers and DSP libraries: GNU Radio, Rust runtimes, Lua frameworks, and reusable C modem APIs.
- Hardware streaming: SoapySDR, UHD, bladeRF, transport buffering, and driver abstractions.
- Cellular PHY/RAN: LTE/5G implementations, srsRAN/OpenAirInterface transitions, and Osmocom GSM transceivers.
- Individual waveforms: Wi-Fi, LoRa, DVB-S2, synchronization, and accelerated error correction.
- Space/navigation receivers: GNSS acquisition/tracking, satellite telemetry, and complete satellite-product pipelines.
- Audio and packet modems: FreeDV, FSK/OFDM, AX.25/APRS, and newer composable modem libraries.
- Integrated receiver communities: SDRangel, SDR++, digital broadcasting, sensor protocols, and Java trunked-radio processing.
- Additional language/ecosystem checks: C# SDR libraries and M17/embedded-modem projects, used to test the boundaries of the selection rather than to force a language quota.

Later searches mostly returned overlapping projects, wrappers, demonstrations, or hardware-focused implementations; they also yielded the Java channelizer and newer C++ modem library retained above. This is a deliberately diverse selection, not an exhaustive inventory or popularity ranking.

**Important exclusions and identity checks:** [srsran/srsRAN_Project](https://github.com/srsran/srsRAN_Project) now presents an archived transition notice directing development to OCUDU on GitLab, with an archive branch that does not provide the substantive implementation required here; it is excluded. The older OpenAirInterface GitHub namespace is a mirror and is not counted alongside the current Duranta location. OsmoTRX's official GitHub mirror is explicitly labeled. The DVB-S2 receiver's documented independent additions justify retaining that descendant, while its ancestor is not counted again. Speech codecs without substantial modem machinery, RF hardware alone, core-network-only stacks, and tutorial repositories were not included merely because they mention SDR.

**Verification limits:** Sources and repository status were checked on the research date; branch and documentation links may change. Source code and selected tests were read, but no candidate code was run, no hardware was exercised, and no throughput or error-rate results were independently measured. C4 is used only where the inspected history supports both sustained change and compatibility/testing/complexity work. Maintenance qualifications are called out where material; silence elsewhere should not be read as a support guarantee. The evidence supports the specific study opportunities described, not a full security, standards-conformance, or implementation-quality audit.
