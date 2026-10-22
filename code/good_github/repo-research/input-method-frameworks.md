# Input method frameworks

Research date: **2026-10-09**.

Scope: 18 repositories covering system input-method buses, reusable composition and conversion frameworks, scriptable keyboard engines, browser input libraries, and mobile/embedded integration. Shared engine libraries are included when their abstractions support building multiple input methods; individual dictionaries, keyboard themes, and small adapters are outside scope. Monorepos count once, with the relevant subsystem identified below. This is a source-reading selection guide, not a claim that every component is exemplary or that every project is currently maintained.

Criteria legend:

- **C1 — Correctness:** demanding state invariants, concurrency, Unicode semantics, malformed inputs, or failure recovery.
- **C2 — Abstractions:** substantial reusable interfaces or components supporting different input methods, applications, or platforms.
- **C3 — Performance:** concrete mechanisms addressing interactive latency, memory, or search costs within an understandable architecture.
- **C4 — Evolution:** documented changes over years together with compatibility, testing, or complexity management.

The criteria are engineering judgments grounded in the linked material. Performance observations describe mechanisms, not measured speed guarantees. The implementation and documentation links in each entry are suggested reading entry points.

## Desktop input buses and toolkit integration

### [ibus/ibus](https://github.com/ibus/ibus)

**Language/role:** C/GObject, with Python and Vala components; Linux/Unix input-method bus. Study the boundary between application input contexts, the bus, and independently implemented engines. This is the project repository linked by the IBus wiki; the older `phuang/ibus` origin is not counted separately.

- **C1:** The input-context API distinguishes synchronous and asynchronous key processing, cancellation, timeouts, and error completion. It also specifies who commits preedit text during focus loss, a subtle source of dropped or duplicated text. These are explicit contracts in [ibusinputcontext.h](https://raw.githubusercontent.com/ibus/ibus/main/src/ibusinputcontext.h).
- **C2:** The same proxy interface carries physical keycodes versus layout-dependent key symbols, handwriting strokes, surrounding text, client capabilities, and content-purpose hints. The header makes the reusable application-to-engine boundary concrete rather than tying the bus to a particular language.

### [fcitx/fcitx5](https://github.com/fcitx/fcitx5)

**Language/role:** C++; generic input-method framework with X11/Wayland frontends. Particularly useful for studying how an extensible framework keeps engine state separate from frontend transport and user-interface responsibilities.

- **C1:** `InputContext` explicitly supports delaying client events so synchronous and asynchronous operations retain their order; an RAII event blocker manages that boundary. It also defines lifecycle notifications and character units for surrounding-text deletion. See [inputcontext.h](https://raw.githubusercontent.com/fcitx/fcitx5/master/src/lib/fcitx/inputcontext.h).
- **C2:** Addon factories, engine interfaces, on-demand loading, required/optional dependencies, and separately registered input-method identities let one addon implement multiple methods. The official [engine-development guide](https://fcitx-im.org/wiki/Develop_an_simple_input_method) explains those relationships with implementation code.

### [uim/uim](https://github.com/uim/uim)

**Language/role:** C and Scheme, with toolkit bridges; multilingual input-method framework. A useful alternative to a primarily bus-centered design: examine its callback-based embedding interface and the separation between input-method state and toolkit-managed presentation.

- **C1:** Reset, focus, placement, and displacement have deliberately different commit/preedit rules. For example, reset must not commit text, and bridge-level preedit clearing belongs to the bridge. The API also distinguishes character counts from byte counts and documents borrowed-string lifetimes. See [uim.h](https://raw.githubusercontent.com/uim/uim/master/uim/uim.h).
- **C2:** Context construction accepts language, engine, client encoding, a replaceable character converter, and callbacks. Candidate selection, properties, and surrounding-text operations use the same reusable interface across bridges. The header is also candid that its API/ABI is unstable; do not infer an unconditional compatibility promise.

### [scim-im/scim](https://github.com/scim-im/scim)

**Language/role:** C++; Smart Common Input Method platform. Included as a legacy desktop-framework architecture. Its inspected [NEWS entry](https://raw.githubusercontent.com/scim-im/scim/master/NEWS) is dated 2017; that alone does not establish the date of its last maintenance work.

- **C1:** An engine instance supports one client encoding at a time, encoding changes require reset, and optional surrounding-text/helper capabilities must be checked before use. These explicit invariants are documented in [scim_imengine.h](https://raw.githubusercontent.com/scim-im/scim/master/src/scim_imengine.h).
- **C2:** The factory owns shared input-method data while instances own per-context state. Signals connect those instances to interchangeable frontends for preedit, lookup tables, properties, commits, and helper-process events. This is a substantial example of separating shared resources from interactive sessions.

### [hamonikr/nimf](https://github.com/hamonikr/nimf)

**Language/role:** C/GObject; multilingual desktop input framework. The repository identifies itself as the HamoniKR continuation of the original Nimf project, with additional toolkit support; only this continuation is counted. Study an explicit engine/service/input-context split.

- **C1:** Input contexts retain preedit text, attributes, cursor position, and start/end state. Switching between inline preedit and separate presentation replays or ends the appropriate callbacks; engine switching resets state, and focus loss hides separate preedit UI. See [nimf-service-ic.c](https://raw.githubusercontent.com/hamonikr/nimf/master/libnimf/nimf-service-ic.c).
- **C2:** The [NimfEngine interface](https://raw.githubusercontent.com/hamonikr/nimf/master/libnimf/nimf-engine.h) standardizes filtering, reset/focus, method selection, candidate paging, commits, and surrounding-text access. Multiple language engines can share these services without each reimplementing toolkit integration.

### [Riey/kime](https://github.com/Riey/kime)

**Language/role:** Rust with native toolkit integration; Korean-focused input system with reusable engine/backend/frontend layers. It is narrower linguistically than IBus or Fcitx, but its complete input infrastructure makes it useful for comparing framework designs.

- **C1:** The [engine core](https://raw.githubusercontent.com/Riey/kime/develop/src/engine/core/src/lib.rs) handles the different modifier-state timing of X11 and Wayland. It also requires mode exit to reset a Hanja candidate subprocess so switching modes does not leave an orphaned popup or unreaped process.
- **C2:** `InputEngine` exposes uniform commit/preedit/result handling over separate Latin and Hangul engines and optional Hanja, emoji, and math modes. The same core sits behind the repository's XIM, Wayland, GTK, and Qt frontends. Study the [engine crate organization](https://github.com/Riey/kime/tree/develop/src/engine) alongside the core implementation.

## Reusable conversion and keyboard-rule engines

### [rime/librime](https://github.com/rime/librime)

**Language/role:** C++; cross-platform, schema-driven input-method engine. Study a configurable processing pipeline capable of implementing phonetic, shape-based, and other input schemes without embedding platform UI logic.

- **C1:** Composition distinguishes selected/confirmed segments, caret boundaries, synthetic versus externally delivered keys, and schema-change cleanup. Segmentation stops if a component makes no progress, and translation avoids rebuilding already advanced segments. These details are visible in [engine.cc](https://raw.githubusercontent.com/rime/librime/master/src/rime/engine.cc).
- **C2:** The same implementation constructs configurable processor, segmentor, translator, filter, and formatter components through a common registration mechanism, then combines their results into composition and candidate menus.
- **C4:** The [changelog](https://raw.githubusercontent.com/rime/librime/master/CHANGELOG.md) spans 2012–2026 and documents ABI changes/fixes, Unicode compatibility updates, plugin-build coverage, and test repairs. This supports an evolution criterion beyond merely having an old repository.

### [fcitx/libime](https://github.com/fcitx/libime)

**Language/role:** C++; reusable input-method implementation library, distinct from the Fcitx application framework. Study how dictionary lookup and language-model scoring are organized around a common decoding problem.

- **C2:** The [decoder interface](https://raw.githubusercontent.com/fcitx/libime/master/src/libime/core/decoder.h) composes dictionary and language-model abstractions with segmentation graphs, lattices, model state, and configurable N-best output. This separates input spelling/segmentation from scoring and candidate search.
- **C3:** The [decoder implementation](https://raw.githubusercontent.com/fcitx/libime/master/src/libime/core/decoder.cpp) uses bounded frames, heap selection, cached scores, beam-limited forward search, and a capped backward-search pool. Existing lattice nodes can be reused between calls. These are concrete ways to control work on interactive candidate generation; no absolute latency claim is implied.

### [keymanapp/keyman](https://github.com/keymanapp/keyman)

**Language/role:** C++, TypeScript, and platform-specific code; cross-platform keyboard system and developer tooling. Counted once, focusing on `core/` and its platform boundary rather than treating each operating-system product as an independent repository.

- **C1:** A keyboard must outlive every state referring to it; actions are owned by their state object. The API distinguishes Unicode scalar values, UTF-16 strings, and code-point deletion, and reports malformed UTF and invalid keyboard data. See [keyman_core_api.h](https://raw.githubusercontent.com/keymanapp/keyman/master/core/include/keyman/keyman_core_api.h).
- **C2:** The [Core design overview](https://help.keyman.com/developer/core/current-version/) explains the C-compatible interface, caller-managed state, format-independent processor boundary, and platform-layer execution of text actions. It is explicitly an internal Keyman Engine API, not a promise of a stable public embedding SDK. Study how multiple platform products share semantics while retaining OS-specific integration.

### [fodydev/afrim](https://github.com/fodydev/afrim)

**Language/role:** Rust; configurable input-method library with roots in African phonetic input, including Amharic and Ge'ez. A smaller framework with independently useful preprocessing, memory, translation, and service components.

- **C1:** The [preprocessor](https://raw.githubusercontent.com/fodydev/afrim/main/engine/preprocessor/src/lib.rs) models replacement and backspace as queued pause/delete/commit/resume commands, with rollback over a bounded input cursor. Executable documentation checks the exact command sequences, exposing the synchronization problem between internal input history and already displayed text.
- **C2:** The separate [translator](https://raw.githubusercontent.com/fodydev/afrim/main/engine/translator/src/lib.rs) returns structured candidates containing remaining input and commit eligibility. Dictionary completion, optional similarity matching, and registered Rhai scripts share this interface, with feature switches for different deployment needs. These layers make the repository more than a fixed language keyboard.

### [thantthet/keymagic-3](https://github.com/thantthet/keymagic-3)

**Language/role:** Rust core/compiler with native platform integrations; newer KeyMagic rewrite. Focus on `keymagic-core`, `kms2km2`, and their shared rule format. The original KeyMagic repository is archived and is not counted as another entry. No C4 claim is made for the rewrite.

- **C1:** The [engine-logic document](https://raw.githubusercontent.com/thantthet/keymagic-3/master/docs/ENGINE_LOGIC.md) specifies rule precedence, persistent composing context, explicit reset when synchronizing external text, and the separation of physical-key matching from recursive text matching. [KM2 validation tests](https://raw.githubusercontent.com/thantthet/keymagic-3/master/keymagic-core/tests/km2_validation_tests.rs) distinguish legal modifier combinations from invalid standalone predefined-key elements.
- **C2:** A compiled keyboard representation feeds a platform-independent matcher/state/action pipeline; callers apply insertion/deletion actions to their editor. The repository supplies a compiler and C-compatible integration boundary for several OS backends. This is a useful study of a keyboard-rule runtime; the inspected tests do not establish exhaustive parser or FFI safety.

## Windows and macOS framework layers

### [EasyIME/PIME](https://github.com/EasyIME/PIME)

**Language/role:** C++ text-service frontend with scripting backends; Windows input-method framework. Study the architecture that lets input-method authors work outside the host application's native Text Services Framework implementation.

- **C1:** The [architecture guide](https://raw.githubusercontent.com/EasyIME/PIME/master/HACKING.txt) explains that Windows loads the text-service DLL inside client applications, requiring matching CPU architecture, while a launcher supervises and restarts crashed backend processes. Failure handling crosses host-process, IPC, and interpreter boundaries.
- **C2:** The same guide traces TSF events through a named pipe to a launcher and then through standard input/output to backend services, using UTF-8 JSON messages. Engine authors can share the native composition plumbing. Treat the guide's bundled-runtime version examples as historical; its architecture is the relevant reading material.

### [openvanilla/openvanilla](https://github.com/openvanilla/openvanilla)

**Language/role:** C++/Objective-C++ framework code with macOS application components; configurable table-based input-method suite. Relevant subsystem: `Packages/OpenVanilla`. Study the reusable services beneath the end-user input methods.

- **C2:** [OVEventHandlingContext](https://raw.githubusercontent.com/openvanilla/openvanilla/master/Packages/OpenVanilla/Sources/OpenVanilla/include/OVEventHandlingContext.h) separates sessions, key/direct-text processing, candidate callbacks, text filters, reading/composing buffers, and loader services. This supports different input modules against shared presentation and resource interfaces.
- **C3:** [OVCINDataTable](https://raw.githubusercontent.com/openvanilla/openvanilla/master/Packages/OpenVanilla/Sources/OpenVanilla/include/OVCINDataTable.h) combines a documented table grammar with sorted key/value storage, binary search for the first matching key, and prefix-bounded wildcard scans. The performance criterion is an inference from these explicit lookup mechanisms, not a benchmark or endorsement of every legacy memory-management choice.

## Mobile, embedded, and system-service frameworks

### [maliit/framework](https://github.com/maliit/framework)

**Language/role:** C++/Qt; input-method server and plugin framework, especially relevant to virtual keyboards. This entry covers the framework, not the separately packaged Maliit keyboard.

- **C1:** The [host contract](https://raw.githubusercontent.com/maliit/framework/master/src/maliit/plugins/abstractinputmethodhost.h) defines replacement ranges, cursor placement after commit, selection anchors, and the possibility that application validators change the resulting cursor location. Keyboard input regions and areas the application should avoid are deliberately separate concepts.
- **C2:** [MAbstractInputMethod](https://raw.githubusercontent.com/maliit/framework/master/src/maliit/plugins/abstractinputmethod.h) receives framework-to-plugin commands, while the host interface handles the reverse direction. Plugins can expose multiple language/layout subviews, process hardware keys, and coordinate visualization. This is a useful bidirectional plugin contract with both text and window-management responsibilities.

### [qt/qtvirtualkeyboard](https://github.com/qt/qtvirtualkeyboard)

**Language/role:** C++ and QML; extensible virtual-keyboard framework. **Official Qt GitHub mirror:** development contributions go through Qt's Gerrit, as its [contribution document](https://raw.githubusercontent.com/qt/qtvirtualkeyboard/dev/CONTRIBUTING.md) explains.

- **C1:** The [architecture overview](https://doc.qt.io/qt-6/qtvirtualkeyboard-overview.html) specifies that virtual key actions occur on release, interrupted presses require cancellation, reset must preserve user text, and input-context updates can require committing current composition. Input-method lifetime also depends on whether it is layout-local, shared, or the default.
- **C2:** Input context, input engine, abstract input method, QML plugin, and selection-list model are separate extension points. The same overview explains third-party input methods, runtime keyboard layouts, and handwriting traces. Study how QML presentation and C++/QML language engines share those contracts.

### [aosp-mirror/platform_frameworks_base](https://github.com/aosp-mirror/platform_frameworks_base)

**Language/role:** Primarily Java for the selected subsystem; Android's system input-method framework. **Official AOSP GitHub mirror, treated as a study snapshot:** the [mirror organization is marked archived](https://github.com/aosp-mirror). Do not assume its branch tracks current Android development. Counted once; relevant code is `core/java/android/view/inputmethod` and its associated service interfaces.

- **C1:** [InputConnection](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/view/inputmethod/InputConnection.java) specifies deletion in UTF-16 units versus code points, malformed surrogate handling, overflow checks, edit/selection races, invalid connections, and batch-edit notification ordering. It is a particularly detailed text-editing protocol contract.
- **C2:** [InputMethodManager](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/view/inputmethod/InputMethodManager.java) documents the three-party architecture of manager, IME service, and client editors. Focus arbitration, per-client sessions, and system-mediated binding let independent editors and input services interoperate through a common framework.

### [fcitx5-android/fcitx5-android](https://github.com/fcitx5-android/fcitx5-android)

**Language/role:** Kotlin and C++; Android adaptation of Fcitx5 with engine/plugin integration. Included for its substantial Android execution and lifecycle layer; the reused Fcitx core is not credited again as a new engine implementation.

- **C1:** [FcitxDispatcher](https://raw.githubusercontent.com/fcitx5-android/fcitx5-android/master/app/src/main/java/org/fcitx/fcitx5/android/core/FcitxDispatcher.kt) coordinates a native event loop with a single-thread coroutine dispatcher, concurrent job queue, atomic running flag, and shutdown mutex. Dispatch wakes the native loop; stopping waits for cleanup and returns leftover jobs.
- **C2:** [FcitxAPI](https://raw.githubusercontent.com/fcitx5-android/fcitx5-android/master/app/src/main/java/org/fcitx/fcitx5/android/core/FcitxAPI.kt) presents coroutine callers with a shared event stream and uniform methods for engine selection, addon configuration, focus/capability changes, preedit, and candidate actions. It hides native-thread dispatch behind this common interface, letting Android components work with multiple engines through the same boundary.

## Browser input methods

### [wikimedia/jquery.ime](https://github.com/wikimedia/jquery.ime)

**Language/role:** JavaScript; browser input-method library with multilingual rule definitions. Useful for studying input methods inside editable web elements, where the surrounding application cannot rely on installing an operating-system IME.

- **C1:** The [technical specification](https://github.com/wikimedia/jquery.ime/wiki/Technical-Specification) distinguishes previously typed keystrokes from their already-transliterated output. Its context-sensitive rules can therefore distinguish identical visible text with different input histories. [Test documentation](https://github.com/wikimedia/jquery.ime/blob/master/test/README.md) covers rule fixtures, extended keys, and newline normalization.
- **C2:** Input methods are registered JavaScript objects with pattern tables, optional function replacements, context lengths, and dependencies. Methods load on demand, while selection and preference persistence are separate APIs. The same specification explains how these pieces support multiple languages and independently supplied editable elements.

## Coverage, exclusions, and limits

Discovery used **17 distinct live search formulations**, followed by repository, source-file, API-documentation, and release-history inspection. Search angles included Linux buses and XIM/Wayland/toolkit bridges; Windows TSF and macOS frameworks; cross-platform composition libraries; Android and Qt virtual keyboards; browser transliteration; minority-language/Indic/African input tooling; Rust implementations; and searches excluding the familiar framework names. The final rounds mostly returned already covered projects, platform ports, narrow adapters, and examples, giving diminishing returns for this scope.

The selection spans C, C++, Scheme, Rust, Kotlin, Java, JavaScript, and mixed native/scripted systems. Fcitx5 Android was retained because its concurrency/lifecycle adaptation is substantive. Thin engine bindings, schema/dictionary collections, tutorials, generic key remappers, and simple visual keyboards were excluded. Language-specific conversion applications without a substantial reusable framework boundary were not systematically catalogued.

The archived [Fcitx 4 repository](https://github.com/fcitx/fcitx) and archived [original KeyMagic repository](https://github.com/thantthet/keymagic) were inspected but omitted in favor of their separate successor implementations. SCIM is explicitly presented for legacy architecture. The Qt and AOSP mirror situations are identified above. m17n was investigated, but an official substantive GitHub repository/mirror was not verified, so third-party copies were not substituted merely to increase the count.

Every retained repository's GitHub page was opened, and at least one additional primary implementation or architectural source was read. Source links follow the inspected branches and may change. No candidate code was run, dependencies installed, or large repositories cloned. Test references describe inspected test material, not test runs. GitHub API rate limiting and occasional web-renderer failures were handled by reading public repository HTML and raw source directly. This is a selective architectural review, not an exhaustive security, compatibility, maintenance, or performance audit.
