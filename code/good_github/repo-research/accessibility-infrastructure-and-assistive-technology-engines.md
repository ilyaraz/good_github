# Accessibility infrastructure and assistive technology engines

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** implementing accessibility protocols, screen readers, braille and mathematical presentation, speech infrastructure, alternative input, nonvisual graphics, and accessibility evaluation engines. The emphasis is on reusable machinery and difficult implementation decisions, including substantial engines inside applications. Generic accessible component libraries, hardware-only designs, small demonstrations, and thin integrations are outside the selection.

Repository headings link to verified canonical GitHub locations. Links within each entry are recommended implementation or documentation entry points; each repository was checked against additional primary material beyond its landing-page README. The criteria below are engineering judgments grounded in those sources, not certifications of correctness or claims that every component is exemplary. Explicit mirror, fork-lineage, and beta qualifications matter. Inclusion alone does not imply current maintenance or production readiness.

Criteria legend:

- **C1 — Difficult correctness:** meaningful invariants, concurrency, numerical or semantic precision, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components serving multiple integrations, devices, applications, or use cases.
- **C3 — Performance with structure:** actual latency, throughput, memory, or resource constraints addressed through an understandable architecture; no benchmark is implied.
- **C4 — Sustained evolution:** evidence across years together with compatibility work, testing, or explicit complexity management. Repository age alone does not qualify.

## Accessibility protocols and screen-reader engines

### 1. [AccessKit/accesskit](https://github.com/AccessKit/accesskit)

**Language / role:** Rust; a shared accessibility-tree representation and adapters to native accessibility APIs.

AccessKit is useful for studying how a UI toolkit can expose accessibility without adopting one operating system's object model. Its architecture separates the producer-facing schema, a consumer that retains tree state, and platform adapters. The push-update design also accommodates immediate-mode interfaces.

- **C1:** Updates have precise replacement semantics: a supplied node must contain all its properties, while child lists determine insertion and removal. Stable node identities, focus, and separately identified subtrees make incremental updates a genuine consistency problem. These contracts are described in the [architecture document](https://github.com/AccessKit/accesskit/blob/main/ARCHITECTURE.md).
- **C2:** The same document explains how nodes, actions, retained state, and adapters separate toolkit concerns from platform-specific accessibility behavior and threading. That is a reusable interoperability layer, rather than a single application's accessibility implementation.

Scope qualification: the repository documents incomplete support for some complex text scenarios; a common schema does not guarantee identical capability on every platform.

### 2. [GNOME/at-spi2-core](https://github.com/GNOME/at-spi2-core)

**Language / role:** Primarily C, with D-Bus interface definitions; Unix desktop accessibility transport and client infrastructure. **Official read-only GitHub mirror** of GNOME development hosted on GitLab.

Study how multiple toolkits and assistive applications communicate through a shared out-of-process object model. The official [architecture documentation](https://gnome.pages.gitlab.gnome.org/at-spi2-core/devel-docs/architecture.html) describes the accessibility bus, registry, protocol interfaces, toolkit adapters, and client library.

- **C2:** The D-Bus interface contract supports independent toolkit implementations and assistive clients; the ATK adaptor and libatspi occupy different sides of that boundary. This is infrastructure shared across application communities.
- **C3:** The documented adaptor and client caches reduce repeated toolkit queries and interprocess calls. Their placement makes the latency costs of remote accessibility objects visible in the architecture.

The architecture page is a historical layering overview, not proof that every contemporary consumer still uses the exact bindings shown. It also expressly lacks profiling for some proposed optimizations, so no measured speedup is claimed here.

### 3. [nvaccess/nvda](https://github.com/nvaccess/nvda)

**Language / role:** Python and C++; Windows screen reader, application adaptation framework, and speech/braille integration.

NVDA offers an unusually instructive boundary between a high-level assistive application and native code operating inside other processes. Its [technical design overview](https://github.com/nvaccess/nvda/blob/master/projectDocs/design/technicalDesignOverview.md) explains the main event queue, accessibility API adapters, injected helper code, and document buffers.

- **C2:** `NVDAObject` provides a common widget abstraction across Windows accessibility APIs, while `TextInfo` represents text ranges and navigation. App modules, global plugins, gestures, and output drivers extend different parts of the system without each rebuilding that model.
- **C3:** Virtual buffers flatten and cache complex documents. Native helpers gather information in the target process, avoiding a separate cross-process operation for every subsequent navigation query. The architecture exposes the reason for this division and the cost it addresses.

An experienced engineer can follow how API diversity becomes one navigation experience, and where application-specific behavior must remain explicit instead of being hidden by the abstraction.

### 4. [GNOME/orca](https://github.com/GNOME/orca)

**Language / role:** Python; desktop screen reader using AT-SPI, speech, and braille. **Official read-only GitHub mirror** of the GNOME project.

Orca is particularly valuable for event-driven correctness under noisy application behavior. Read the current [event manager implementation](https://raw.githubusercontent.com/GNOME/orca/main/src/orca/event_manager.py), which contains the queueing policy and the rationale for many filters.

- **C1:** The manager distinguishes event priorities, preserves ordering with a sequence counter, rejects dead or irrelevant sources, and coordinates scheduling with GLib. Invalid-entry announcements receive special ordering treatment so that error feedback follows the relevant context. These are user-visible semantic constraints, not merely queue mechanics.
- **C3:** Duplicate, obsolete, and flooding events can be discarded or deprioritized before they monopolize processing. The source explicitly discusses application event floods and tracks recent events by type and source.

Study how focus, live regions, application lifecycle, and output timing interact. The presence of locks and filters is evidence of the problem and its treatment, not a blanket claim that all races are eliminated.

### 5. [google/talkback](https://github.com/google/talkback)

**Language / role:** Primarily Java, with native braille components; Google's public Android screen-reader source.

The [TalkBack pipeline](https://raw.githubusercontent.com/google/talkback/master/talkback/src/main/java/com/google/android/accessibility/talkback/Pipeline.java) shows a concrete decomposition into monitors, interpreters, feedback mapping, and actors. This is a useful example of coordinating several sensory outputs around asynchronous mobile accessibility events.

- **C1:** Delayed feedback is grouped by interruption group and level, with explicit cancellation and failover behavior. Unbinding and shutdown handle pending output and actor state. Without those rules, a stale utterance or vibration can describe a UI state the user has already left.
- **C2:** Restricted receiver interfaces and separate interpretation/feedback stages keep event sources and output actors from depending on the whole pipeline. The implementation explicitly supports mocking those boundaries.

The selection refers to this public source distribution; it does not assume that its visible history or implementation exactly matches every currently shipped TalkBack build.

### 6. [odilia-app/odilia](https://github.com/odilia-app/odilia)

**Language / role:** Rust; an asynchronous Linux screen reader built around AT-SPI.

Odilia adds a different implementation community and concurrency model to the screen-reader selections. Its official [developer design overview](https://odilia.app/doc/devel/design/) explains the roles of caching, navigation, input, and text-to-speech components, and the use of asynchronous D-Bus communication.

- **C2:** The design separates reusable concerns such as accessibility data, navigation, input handling, and speech output, rather than coupling every event directly to a synthesizer call.
- **C3:** The overview discusses caching and the cost of copying accessibility data, together with Tokio task scheduling and zbus socket communication. Responsiveness and remote-object access are architectural concerns rather than unsupported claims of general Rust speed.

**Status limitation:** the repository explicitly calls the project beta and unsuitable for production use. The design overview is dated 2022, so use it for the documented architectural rationale and inspect the current workspace before assuming exact module boundaries.

## Braille, mathematical semantics, and speech infrastructure

### 7. [brltty/brltty](https://github.com/brltty/brltty)

**Language / role:** Primarily C; braille-display access daemon, device drivers, console integration, and BrlAPI.

BRLTTY is a strong study in sharing scarce physical output and input hardware among competing applications. Beyond its screen and braille drivers, its client API lets applications cooperate with the daemon.

- **C1:** The [BrlAPI concurrency documentation](https://brltty.app/doc/Manual-BrlAPI/English/BrlAPI-3.html) describes how terminal focus, per-client display contents, and key interests determine which client controls the display and receives a key. Layer priorities and transparent display regions introduce arbitration rules beyond ordinary exclusive device access.
- **C2:** The [BrlAPI manual](https://brltty.app/doc/Manual-BrlAPI/English/BrlAPI.html) exposes a device-independent interface, allowing applications to use braille without implementing each display's protocol. That boundary complements the daemon's driver families.

The manual also discusses prospective extensions; those proposals should not be mistaken for implemented capabilities. The selection rests on the documented terminal/client arbitration and driver/API split.

### 8. [liblouis/liblouis](https://github.com/liblouis/liblouis)

**Language / role:** C and braille rule tables; forward and backward braille translation library.

Liblouis combines a domain-specific rule system with APIs that preserve the relationship between print text and contracted braille. This makes it more interesting than a character substitution library.

- **C1:** The [`lou_translate` API](https://liblouis.io/documentation/liblouis/lou_005ftranslate.html) exposes mappings in both directions between input and output positions, cursor translation, and buffer-length contracts. Contractions make these mappings nontrivial; a screen reader needs correct routing even when text and braille lengths differ.
- **C2:** External language and translation tables supply behavior through one callable engine, supporting assistive applications with different languages, conventions, and presentation requirements.
- **C3:** The [table representation documentation](https://liblouis.io/documentation/liblouis/Data-structure-of-liblouis-tables.html) explains hash buckets, offsets into a variable rule area, and distinct forward/backward rule chains. It explicitly relates the representation to lookup speed and memory use.

The two linked documents are complementary entry points: user-visible positional semantics and the compiled representation that executes the tables.

### 9. [daisy/MathCAT](https://github.com/daisy/MathCAT)

**Language / role:** Rust and rule resources; MathML conversion to speech and braille, with structural navigation.

MathCAT is useful for studying how one mathematical representation supports linear speech, spatial braille conventions, and interactive exploration. The verified canonical repository is under **daisy**.

- **C1:** The [caller guide](https://github.com/daisy/MathCAT/blob/main/docs/callers.md) describes MathML cleanup, generated node identities, navigation state, locale-sensitive number interpretation, and configurable recovery from invalid intent annotations. In particular, the source document's decimal and grouping conventions cannot simply be inferred from the desired speech language.
- **C2:** Callers configure preferences, supply MathML, and request speech, braille, or navigation through shared engine interfaces. Language and presentation rules stay separate from the embedding screen reader. The [developer guide](https://github.com/daisy/MathCAT/blob/main/docs/developers.md) demonstrates tests expressed as MathML input and expected presentation.

The caller guide identifies limitations in some navigation offsets; the presence of a rich API should not be read as proof that every described offset mechanism is complete.

### 10. [Speech-Rule-Engine/speech-rule-engine](https://github.com/Speech-Rule-Engine/speech-rule-engine)

**Language / role:** TypeScript; semantic interpretation, speech rules, braille output, and mathematical expression navigation.

SRE has a substantive independent implementation despite its stated ChromeVox ancestry; ChromeVox is not counted separately. Its public interfaces support both browser and Node integrations, rule selection, locale loading, and semantic exploration.

- **C1:** The [semantic tree implementation](https://github.com/Speech-Rule-Engine/speech-rule-engine/blob/develop/ts/semantic_tree/semantic_tree.ts) parses MathML, rewrites particular structures, collects inferred symbol meanings, and can reparse using improved defaults. Tree replacement, parent/root relationships, and associations back to MathML create explicit consistency obligations.
- **C2:** The [repository's API documentation](https://github.com/Speech-Rule-Engine/speech-rule-engine#readme) separates semantic enrichment, speech generation, and walking an expression. Rules and locale data allow multiple presentation conventions to share the underlying mathematical analysis.

Semantic reconstruction is heuristic within the project's stated mathematical scope. This is a valuable implementation of ambiguity handling, not a claim that arbitrary notation can be interpreted unambiguously.

### 11. [brailcom/speechd](https://github.com/brailcom/speechd)

**Language / role:** C with client bindings; Speech Dispatcher, a shared speech-output service and synthesizer middleware.

Speech Dispatcher addresses a fundamental assistive-output problem: several programs may speak simultaneously, while the listener can effectively consume only one ordered audio stream. Read the primary [SSIP protocol specification](https://raw.githubusercontent.com/brailcom/speechd/master/doc/ssip.texi), especially priorities and message blocks.

- **C1:** The protocol defines distinct interruption, replacement, queuing, and dropping policies for important messages, ordinary messages, text, notifications, and progress. Progress has special final-message handling, while blocks let changes of voice or other parameters remain one logical message for scheduling.
- **C2:** A client protocol separates applications from synthesizer choice, while output modules adapt different speech systems. The [repository overview](https://github.com/brailcom/speechd#readme) explains that synthesis modules run as separate processes using a simple pipe protocol.

This is a study in scheduling around human attention and consistent cancellation semantics, as well as ordinary process isolation and backend abstraction.

### 12. [espeak-ng/espeak-ng](https://github.com/espeak-ng/espeak-ng)

**Language / role:** C and linguistic rule data; compact multilingual speech synthesis used in assistive software.

eSpeak NG is a substantive continuation of eSpeak, not a separate count for a superficial fork. Its rule machinery provides a different architectural perspective from large neural speech models.

- **C2:** The [phoneme-table language](https://github.com/espeak-ng/espeak-ng/blob/master/docs/phontab.md) supports inherited tables and conditional instructions based on context and stress. Interpretation has separate phoneme-changing and sound-production phases, allowing linguistic behavior to be reused and extended without rewriting the synthesizer core.
- **C1:** The [changelog](https://github.com/espeak-ng/espeak-ng/blob/master/ChangeLog.md) records concrete failure classes including bounds errors found through fuzzing, malformed UTF-8 loops, phoneme-table state problems, and event timing fixes. These show the adversarial-input and state-management surface of a seemingly simple speech engine.
- **C4:** The same history spans releases in 2016, 2017, 2019, and later, documenting testing and compatibility work; the repository also explicitly preserves the older eSpeak API/ABI. This is evidence of managed evolution beyond repository age.

### 13. [RHVoice/RHVoice](https://github.com/RHVoice/RHVoice)

**Language / role:** C++; speech synthesis with integrations including Speech Dispatcher, Windows SAPI, Android, and NVDA.

RHVoice contributes a statistical parametric synthesis implementation and a useful streaming-processing design. The small [speech processor implementation](https://github.com/RHVoice/RHVoice/blob/master/src/core/speech_processor.cpp) is an approachable entry point before following the linguistic and synthesis pipeline.

- **C1:** The processor explicitly handles partially filled buffers, completion propagation, downstream cancellation, and stop checks around processing stages. Correct shutdown must prevent continued output while also giving normal completion a chance to flush pending samples.
- **C2:** Processors can be chained; stages negotiate desired input amounts, pass output downstream, and propagate completion. This reusable streaming abstraction sits beneath the [repository's different assistive and operating-system integrations](https://github.com/RHVoice/RHVoice#readme).

The interesting engineering lesson is the contract between stages and their consumers, not an unsupported comparison of voice quality or real-time speed against other synthesizers.

## Alternative input and assistive interaction frameworks

### 14. [OptiKey/OptiKey](https://github.com/OptiKey/OptiKey)

**Language / role:** C#/.NET; gaze-driven keyboard, mouse, communication, and speech applications with a shared core.

OptiKey is included for its reusable input and selection machinery rather than just its on-screen keyboard. The [source layout](https://github.com/OptiKey/OptiKey/tree/main/src) exposes the common core, contracts, and distinct product applications.

- **C1:** [`InputService`](https://github.com/OptiKey/OptiKey/blob/main/src/JuliusSweetland.OptiKey.Core/Services/InputService.cs) coordinates source replacement, fixation settings, selection subscriptions, capture state, and nested suspension. Changing input sources or selection mode must update dependent triggers and dispose obsolete subscriptions, or one physical action can produce unintended selections.
- **C2:** Point sources and trigger sources are separate interfaces, alongside dictionary, audio, and key-state services. The same selection machinery can therefore accommodate different pointing devices, activation methods, and products.

This is a substantial example of separating continuous position signals from discrete user intent, with explicit lifecycle management for reactive input streams.

### 15. [asterics/AsTeRICS](https://github.com/asterics/AsTeRICS)

**Language / role:** Java runtime, native components, and supporting tools; a framework for assembling assistive sensor, processing, and actuator systems.

AsTeRICS is valuable for studying a configurable runtime connecting heterogeneous assistive devices. Its [ARE development manual](https://www.asterics.eu/develop/ARE/ARE-Development-Manual.html) goes well beyond a component catalog to explain runtime services and lifecycle contracts.

- **C2:** Plugins expose ports, properties, and lifecycle operations, while shared services provide functions such as serial communication and remote connections. OSGi and native bridges permit independent implementations to participate in one assistive model.
- **C1:** The manual describes threaded socket callbacks, synchronization requirements, queued sends that do not guarantee delivery, and model lifecycle transitions with timeout and error states. Start, stop, pause, and failure handling must remain coherent across components with different blocking behavior.

Study the tension between flexible composition and predictable teardown. Some integrations include separately supplied native or binary dependencies; the selection concerns the open framework and its documented contracts, not a claim that every attached component is equally inspectable.

### 16. [intel/acat](https://github.com/intel/acat)

**Language / role:** C#/.NET; Assistive Context-Aware Toolkit for communication and computer access.

ACAT offers an instructive example of evolving a large assistive application toward explicit service boundaries. The [dependency-injection guide](https://github.com/intel/acat/blob/master/DEPENDENCY_INJECTION_GUIDE.md) explains concrete migration choices rather than merely recommending dependency injection.

- **C2:** Manager interfaces and factories separate actuators, application agents, panels, speech output, themes, and word prediction. Extensions can participate through these service boundaries instead of rebuilding the interaction framework.
- **C1:** The guide treats singleton identity, initialization order, and compatibility with legacy `Context` access as correctness constraints. It also distinguishes structural JSON-schema validation from semantic configuration validation, and describes tests covering service lifetimes, resolution, factories, and error paths.

The study opportunity is how to introduce replaceable dependencies while preserving lifecycle behavior in an existing assistive system. Descriptions of tests are evidence of the project's validation strategy; no ACAT tests were executed for this report.

### 17. [dasher-project/DasherCore](https://github.com/dasher-project/DasherCore)

**Language / role:** C++17 with a C API; predictive text-entry engine controlled through continuous movement or switches.

This is the project's substantive modernization of the Dasher core, not an additional count for every Dasher frontend or historical fork. The repository labels version 6 **beta**.

- **C2:** The [architecture document](https://github.com/dasher-project/DasherCore/blob/main/docs/ARCHITECTURE.md) separates language models, alphabet/training machinery, input filters, view transforms, and rendering commands. Different frontends can share the predictive navigation engine while using native drawing and input.
- **C1:** The [C API guide](https://github.com/dasher-project/DasherCore/blob/main/docs/C_API.md) makes context ownership, single-thread use, borrowed draw-buffer lifetime, and temporary string lifetime explicit. These are consequential contracts at a native-language boundary.
- **C3:** The architecture follows a frame from input through model motion, visible-tree rendering, and expansion policy; the API exposes draw data without requiring a copied object graph on every frame.

The architecture document candidly identifies a central class with too many responsibilities. That makes this useful for studying ongoing complexity management, without implying that the refactoring is complete.

### 18. [dictation-toolbox/dragonfly](https://github.com/dictation-toolbox/dragonfly)

**Language / role:** Python; speech-command grammars, recognition-engine adapters, and desktop actions.

Dragonfly's relevance is programmable voice access to applications. This continuation has substantive multi-engine development beyond its original t4ngo ancestry; the original repository is not separately counted.

- **C2:** The [object-model documentation](https://github.com/dictation-toolbox/dragonfly/blob/master/documentation/object_model.txt) defines composable grammar elements such as sequences, alternatives, repetition, and rule references. Grammars, rules, dynamic lists, recognition engines, and actions have distinct responsibilities.
- **C1:** Loading, activation, context matching, recognition callbacks, and dynamic-list updates impose lifecycle and ordering obligations. The same document records backend differences, including restrictions on references between grammars, rather than assuming that all speech engines implement identical semantics.

Study how a convenient command language is translated into multiple recognition backends while retaining application context. The [repository overview](https://github.com/dictation-toolbox/dragonfly#readme) notes platform limitations, including X11-based Linux functionality; cross-platform support should not be interpreted as complete Wayland equivalence.

### 19. [asterics/FabiWare](https://github.com/asterics/FabiWare)

**Language / role:** Embedded C++; shared firmware for FABI, FlipMouse, and FlipPad alternative input devices using supported Raspberry Pi microcontrollers.

FabiWare adds the embedded end of the accessibility stack: switches and small physical actions become configurable computer input. It is the firmware repository identified by the current device projects; older FLipMouse hardware/firmware repositories are not counted again.

- **C1:** The [button state machine](https://github.com/asterics/FabiWare/blob/master/src/buttons.cpp) distinguishes raw, debounced, and stable state, then pairs held actions with the appropriate release operation. Mouse, keyboard, joystick, and infrared commands require different release semantics to avoid leaving an action engaged.
- **C2:** The [HID adaptation layer](https://github.com/asterics/FabiWare/blob/master/src/hid_hal.cpp) presents common input operations over USB and Bluetooth paths, while configuration selects behavior across device variants. The reusable unit is a shared firmware stack, not a one-off circuit demonstration.

Limitations are visible in the source: it documents unresolved Bluetooth joystick-axis mapping work, and the README says manuals need updates. These qualify the selection as an implementation study rather than a readiness endorsement for every configuration.

## Nonvisual graphics and accessibility evaluation

### 20. [Shared-Reality-Lab/IMAGE-server](https://github.com/Shared-Reality-Lab/IMAGE-server)

**Language / role:** Python services, TypeScript orchestration, and rendering components; graphics interpretation for audio, haptic, and other accessible presentations.

IMAGE supplies a less familiar research-system architecture that complements text and screen-reader engines. Counted here is the server monorepo, including its orchestrator, preprocessors, and rendering handlers—not each related client repository.

- **C2:** The [repository architecture](https://github.com/Shared-Reality-Lab/IMAGE-server#readme) uses shared schemas between model-independent preprocessing results and rendering handlers. This allows different analysis methods and output presentations to share intermediate data.
- **C3:** The [orchestrator documentation](https://github.com/Shared-Reality-Lab/IMAGE-server/blob/main/orchestrator/README.md) explains priority groups, optional parallel preprocessing, and per-preprocessor caching. It explicitly identifies GPU-memory exhaustion as a tradeoff when enabling parallel execution.
- **C1:** That orchestrator validates incoming requests against schemas and manages which intermediate results reach handlers. Schema compatibility is a substantive boundary between separately implemented services.

**Status limitation:** the project identifies the overall system as beta, with some components at an earlier research stage. Schema validation does not establish the accuracy of generated image interpretations.

### 21. [dequelabs/axe-core](https://github.com/dequelabs/axe-core)

**Language / role:** JavaScript; reusable automated web accessibility evaluation engine.

axe-core belongs here as testing infrastructure that models browser accessibility behavior, rather than as a generic test-runner wrapper. Its [developer guide](https://github.com/dequelabs/axe-core/blob/develop/doc/developer-guide.md) explains how checks become rule results and how the engine is exercised.

- **C1:** Checks have true, false, and undefined outcomes, which feed rule logic and distinguish violations from cases requiring review. Combining checks through `any`, `all`, and `none`, alongside a flattened representation of open Shadow DOM, creates semantic obligations beyond querying visible HTML tags.
- **C2:** Rules and checks are reusable units with defined execution and result interfaces. Integrations can run the engine and consume results without reimplementing the rule system.

The guide describes unit and integration testing, including ACT/APG and shadow-tree cases. Automated findings remain bounded by the engine's observable context and rule scope; this selection makes no claim that automation establishes complete accessibility or that closed shadow trees are equally inspectable.

### 22. [Siteimprove/alfa](https://github.com/Siteimprove/alfa)

**Language / role:** TypeScript; modular web analysis and accessibility evaluation libraries.

Alfa is useful for studying an accessibility engine built around its own analyzable web representations. The [repository overview](https://github.com/Siteimprove/alfa#readme) describes DOM/CSSOM modeling, CSS computation, accessibility-tree construction, and ACT-oriented evaluation.

- **C1:** Reconstructing style and accessibility semantics creates correctness obligations even when analysis runs outside a live browser. The [API design guidelines](https://github.com/Siteimprove/alfa/blob/main/docs/api.md) additionally specify structural equality and the requirement that equal values produce equal hashes—important invariants for immutable analysis data.
- **C2:** The repository separates DOM, style, accessibility semantics, rule evaluation, and supporting data abstractions into packages. Inputs can come from browser capture or constructed representations, giving the analysis machinery uses beyond one browser extension.

The API guide explicitly discusses tradeoffs between persistent structures and built-in collections in performance-sensitive code. Documentation coverage is uneven, so follow the relevant package implementation when moving from the overall design to a particular rule.

### 23. [IBMa/equal-access](https://github.com/IBMa/equal-access)

**Language / role:** TypeScript/JavaScript; shared accessibility checking engine and its browser/build-tool integrations.

This monorepo is counted once, specifically for `accessibility-checker-engine`. Its [rule-authoring documentation](https://github.com/IBMa/equal-access/blob/main-4.x/accessibility-checker-engine/README-RULES.md) is a substantial entry point into both evaluation semantics and validation fixtures.

- **C1:** Rule contexts expose different representations, including DOM and ARIA-oriented trees, while results distinguish pass, fail, potential, and manual review. Fixtures associate expected outcomes with paths through the relevant trees, exercising more than a rule's boolean return value.
- **C2:** Rules have explicit identifiers, reasons, metadata, and policy mappings. Browser and development-tool integrations consume the common engine instead of maintaining separate implementations of every accessibility check.

Study the relationship between an abstract rule, the tree on which it runs, and a result that can be explained to a developer. The multiple result categories are meaningful uncertainty handling; they should not be flattened into an unsupported binary claim of compliance.

### 24. [google/Accessibility-Test-Framework-for-Android](https://github.com/google/Accessibility-Test-Framework-for-Android)

**Language / role:** Java; reusable Android accessibility hierarchy checks.

This framework adds native-mobile testing rather than another web scanner. The repository supports checks over hierarchy information derived from Android views and accessibility-facing node data.

- **C1:** [`TouchTargetSizeCheck`](https://github.com/google/Accessibility-Test-Framework-for-Android/blob/master/src/main/java/com/google/android/apps/common/testing/accessibility/framework/checks/TouchTargetSizeCheck.java) evaluates geometry in density-normalized units and considers touch delegates, clipping, ancestors, and incomplete information. It distinguishes errors, warnings, and cases it cannot run instead of blindly treating every small reported rectangle as an equivalent failure.
- **C2:** The implementation participates in the framework's hierarchy-check and result abstractions, returning structured metadata and explanations. The same checking machinery can therefore be embedded in different Android testing or inspection workflows, as described by the [repository overview](https://github.com/google/Accessibility-Test-Framework-for-Android#readme).

This is a concise, concrete study of numerical thresholds complicated by platform semantics and imperfect observability—conditions common in real accessibility tooling.

## Coverage, search method, and limitations

Live discovery used more than six meaningfully distinct query families, followed by repository pages, source files, official documentation, and release history. Search formulations covered:

- Cross-platform accessibility trees, AccessKit, AT-SPI, D-Bus, and toolkit adapters.
- Windows, GNOME, Android, and Rust screen-reader architecture and event handling.
- Braille drivers, BrlAPI device arbitration, translation tables, and cursor mapping.
- MathML semantic enrichment, mathematical speech, braille, and expression navigation.
- Speech Dispatcher priorities, compact speech synthesis, phoneme rules, and synthesis pipelines.
- Gaze input, switch scanning, assistive component frameworks, and predictive text entry.
- Voice-command grammars and recognition backend abstractions.
- Embedded sip-and-puff/switch input, USB/Bluetooth HID, and device firmware.
- Audio/haptic/tactile graphics rendering and multimodal server pipelines.
- Web accessibility rule engines, ACT-oriented evaluation, and Android hierarchy checks.

These searches span C, C++, Rust, Python, Java, C#, JavaScript, and TypeScript; operating-system middleware, embedded firmware, native applications, libraries, and distributed research services; and disability-led, volunteer, academic, foundation, and corporate project communities. Later searches increasingly returned small prototypes, hardware construction guides, duplicate frontends, or thin wrappers. FabiWare and IMAGE-server were retained because inspection exposed distinct reusable implementation machinery.

Important exclusions and qualifications:

- Hardware-only designs, unfinished sip-and-puff demonstrations, tutorial projects, awesome lists, and generic OCR/ASR/TTS projects without a demonstrated accessibility-infrastructure role were excluded. Speech engines retained here have explicit assistive integrations.
- Accessibility wrappers and full browser or UI-toolkit monorepos were not added merely for containing accessibility code. The selection concentrates on dedicated infrastructure and substantial assistive engines.
- The current FLipMouse project directs firmware development to FabiWare; the device repository is therefore not presented as a second current engine. Historical Dasher frontends and original ancestors of SRE, eSpeak NG, and Dragonfly were likewise not counted separately.
- GNOME's GitHub repositories are clearly marked official mirrors. Beta qualifications for Odilia, DasherCore, and IMAGE-server are retained. Historical architecture documents are identified where their age affects interpretation.
- Automated checking is only one part of accessibility evaluation, and model-generated graphics interpretation remains uncertain. No user study, hardware compatibility exercise, benchmark, build, or test suite was run during this read-only research.
- Each retained repository has a verified GitHub location and additional primary implementation or design evidence. Criteria assignments are grounded in those inspected materials, but they are selective reading recommendations rather than comprehensive code audits or a comparative ranking of project quality.
