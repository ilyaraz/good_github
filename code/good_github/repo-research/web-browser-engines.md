# Web browser engines

Research date: **2026-10-09**.

This report selects **17 GitHub repositories** implementing substantial browser-engine behavior: HTML/CSS layout and rendering, browser document runtimes, or specialized engine integrations. It includes full engines, deliberately smaller embeddable renderers, non-visual document engines, and terminal renderers. These roles are distinguished below; they are not interchangeable implementations of the whole modern web. Browser monorepos count once, with the relevant subsystem identified. The engineering assessments are grounded in the linked implementation and architecture material, not stars or claimed benchmark rankings.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial input, or failure modes. **C2** — substantial reusable abstractions serving multiple use cases. **C3** — concrete performance constraints addressed through understandable architecture. **C4** — sustained evolution with evidence of compatibility work, testing, or complexity management. Each entry explicitly supports at least two criteria. These are selection judgments, not claims that every component is exemplary.

## Large general-purpose engines

### 1. [chromium/chromium](https://github.com/chromium/chromium)

**Language/role:** Primarily C++; Blink, the content layer, and compositor within the Chromium monorepo. **Official GitHub mirror**, as identified by the repository; upstream development is on Chromium's infrastructure.

Study how a very large engine constrains dependencies and publishes a consistent visual state while layout, rasterization, and user input proceed at different rates.

- **C1:** Blink separates security-sensitive V8 bindings from ordinary engine code and specifies message passing for cross-thread communication. Its architecture document explains why shared-memory patterns have produced lifetime and security bugs. [Blink architecture](https://github.com/chromium/chromium/blob/main/third_party/blink/renderer/README.md).
- **C2:** The same document defines the responsibilities and dependency direction of `core`, `modules`, `platform`, and the public interfaces. These boundaries support numerous web APIs and embedders without exposing all renderer internals.
- **C3:** The compositor maintains pending and active trees so raster work can finish before updates become visible atomically, while the previous frame remains scrollable. Invalidation and damage tracking limit rasterization and display work. [Compositor architecture](https://github.com/chromium/chromium/blob/main/cc/README.md).

**Entry points:** The two architecture documents above; follow their links into `third_party/blink/renderer` and `cc`.

### 2. [mozilla-firefox/firefox](https://github.com/mozilla-firefox/firefox)

**Language/role:** C++, Rust, and JavaScript; Gecko, DOM, layout, and graphics within the Firefox monorepo. This is the official repository reached by the checked `mozilla/firefox` redirect.

The asynchronous panning and zooming subsystem is a particularly focused route into the engine: it exposes the consequences of making input responsive while page scripts and layout run independently.

- **C1:** Main-thread and compositor scroll positions can both change legitimately. APZ reconciles them with generation counters and flags, transforms input coordinates back into the content coordinate system, and arbitrates `preventDefault()` against delayed content responses. These are observable consistency requirements, not merely threading mechanics.
- **C3:** APZ allows compositing to continue while the main thread is busy. Its displayport heuristics explicitly trade memory against unpainted areas during fast scrolling. The WebRender integration explains when display lists and accompanying scroll metadata become usable together.

**Entry point and evidence:** [Asynchronous Panning and Zooming](https://firefox-source-docs.mozilla.org/gfx/AsyncPanZoom.html). The document marks some older flow descriptions as outdated; its historical Layers discussion should not be mistaken for the present WebRender architecture.

### 3. [WebKit/WebKit](https://github.com/WebKit/WebKit)

**Language/role:** Primarily C++, with C, assembly, and Objective-C integration; WebCore, JavaScriptCore, and WebKit embedding layers. The repository identifies itself as the home of WebKit.

Study the separation between document semantics, platform services, and embedding APIs, including the coexistence of legacy and multi-process interfaces.

- **C1:** WebContent processes execute web content under a sandbox; the UI process brokers privileged capabilities, while the network process owns network access and structured storage. This makes hostile scripts and hung pages concrete architectural concerns. [Multi-process architecture](https://docs.webkit.org/Deep%20Dive/Architecture/WebKit2.html).
- **C2:** WebCore implements the web platform above platform abstraction layers, while WebKit supplies application-facing integration. The introduction distinguishes DOM and render trees and explains the separate roles of WebCore, PAL, JavaScriptCore, and embedding layers. [WebKit introduction](https://docs.webkit.org/Getting%20Started/Introduction.html).
- **C4:** That introduction documents a multi-year migration from `WebCore/platform` toward PAL to remove reverse dependencies—specific evidence of architectural complexity management over time.

**Entry points:** The introduction and multi-process document above, which map directly to the repository's `Source` subsystems.

## Independent engines and alternative architectures

### 4. [servo/servo](https://github.com/servo/servo)

**Language/role:** Rust; an embeddable web engine with its own document/layout pipeline and integration with SpiderMonkey and WebRender.

Study how document ownership and communication boundaries support concurrency without assuming every stage can profitably run in parallel.

- **C1:** The constellation manages content processes and frame pipelines; script threads own DOM execution and communicate with the embedder and renderer through defined channels. The architecture discussion also identifies IPC file-handle exhaustion and third-party library synchronization as real failure modes.
- **C3:** Layout produces box and fragment trees before display lists reach WebRender. Rendering is separated from layout for responsiveness, while style matching and suitable layout work can use parallelism. The documentation discusses limits imposed by sequential dependencies, thread proliferation, and font-library locks.

**Entry point and evidence:** [Servo architecture](https://book.servo.org/design-documentation/architecture.html). Some sections describe intended directions; use its current pipeline description and linked implementation rather than treating every design goal as shipped behavior.

### 5. [LadybirdBrowser/ladybird](https://github.com/LadybirdBrowser/ladybird)

**Language/role:** Primarily C++; the independent LibWeb engine, LibJS runtime, and browser services. The repository explicitly describes Ladybird as **pre-alpha and developer-oriented**.

Study a newer engine's object model alongside its separation of web execution, networking, image decoding, and application UI.

- **C1:** The repository describes separate content, request, and image-decoder processes to contain failures and malicious input. The [process architecture document](https://github.com/LadybirdBrowser/ladybird/blob/master/Documentation/ProcessArchitecture.md) explains these responsibilities, but is explicitly partly aspirational; its platform-specific sandbox details are not treated here as universally implemented guarantees.
- **C2:** LibWeb's [Page interface](https://github.com/LadybirdBrowser/ladybird/blob/master/Libraries/LibWeb/Page/Page.h) separates a `PageClient` from page behavior and exposes structured navigation, input, screenshot, coordinate-conversion, and compositor operations. Local and remote navigable state make this a substantial engine boundary, beyond the browser's window controls.

**Entry points:** The process document and `Libraries/LibWeb/Page/Page.h` above. The report counts Ladybird once and does not separately count its SerenityOS ancestry.

### 6. [netsurf-browser/netsurf](https://github.com/netsurf-browser/netsurf)

**Language/role:** C; NetSurf's browser core, HTML content handling, and platform frontends. **Official project GitHub mirror**; the [NetSurf organization](https://github.com/netsurf-browser) identifies its repositories as mirrors and points to the authoritative NetSurf source server.

Study portable engine integration at a smaller scale, especially the connection between C-based document libraries, a JavaScript interpreter, and multiple GUI implementations.

- **C1:** The [JavaScript binding guide](https://github.com/netsurf-browser/netsurf/blob/master/docs/jsbinding.md) explains Duktape stack conventions, execution timeouts, generated argument checks, and the extra validation required for overloaded methods. It also identifies unimplemented DOM/CSSOM bindings, avoiding an implication of complete modern-web compatibility.
- **C2:** The [GUI window interface](https://github.com/netsurf-browser/netsurf/blob/master/include/netsurf/window.h) uses a function table with mandatory and optional operations for creation, invalidation, scrolling, dimensions, carets, and forms. Its invalidation contract deliberately leaves redraw scheduling to the frontend, enabling different platform toolkits to share the core.

**Entry points:** `docs/jsbinding.md` and `include/netsurf/window.h` above.

### 7. [gosub-io/gosub-engine](https://github.com/gosub-io/gosub-engine)

**Language/role:** Rust; a modular, asynchronous browser engine. The checked README says **page scripting is not yet wired into the engine**, despite the presence of JavaScript-related crates.

Study how an engine makes profile isolation, tab ownership, and host-application control explicit in its API.

- **C1:** Zones carry storage and cookie services, with sharing made explicit. Each tab owns a worker and browsing state; navigation uses identifiers and cancellation tokens so replacement navigation can cancel earlier asynchronous work. This provides concrete material on isolation and stale-work management.
- **C2:** `GosubEngine<C>` accepts configured rendering, compositor, and font components. The host controls tabs through commands and receives tagged events; a GUI and a headless host can use the same boundary.
- **C3:** The design separates network I/O from tab work and provides rate-controlled drawing that the host can suspend. This connects resource control to an intelligible ownership model.

**Entry point and evidence:** [Zones and tabs](https://github.com/gosub-io/gosub-engine/blob/main/docs/zones-and-tabs.md). Claims about isolation describe the documented design, not an independently verified security boundary.

## Embeddable renderers and specialized web runtimes

### 8. [DioxusLabs/blitz](https://github.com/DioxusLabs/blitz)

**Language/role:** Rust; modular HTML/CSS rendering for browser-like applications and native Dioxus integration. The README calls it **beta** and deliberately excludes substantial portions of the full browser platform.

Study the integration of Stylo for styling, Taffy for box layout, and Parley for text layout around a shared DOM abstraction.

- **C2:** The repository's architecture separates `blitz-dom`, interoperability traits, HTML parsing, networking, painting, and window integration. HTML and Dioxus frontends can compose these pieces differently. [Repository architecture](https://github.com/DioxusLabs/blitz#architecture).
- **C1:** The [style/layout resolver](https://github.com/DioxusLabs/blitz/blob/main/packages/blitz-dom/src/resolve.rs) documents why rendering must wait for critical stylesheets to avoid spurious CSS transitions. It also orders hover refresh after dirty-flag clearing so new invalidations survive into the next pass.
- **C3:** The same implementation propagates damage, reconstructs affected layout structures, and limits cleanup to damaged subtrees. Stage timers make the cost of individual phases visible.

**Entry points:** The architecture section and `packages/blitz-dom/src/resolve.rs` above.

### 9. [litehtml/litehtml](https://github.com/litehtml/litehtml)

**Language/role:** C++; a compact HTML/CSS layout engine whose host supplies graphics and platform services. The README explicitly warns that it is not a full-featured replacement for a mainstream browser engine.

Study a relatively accessible separation between CSS layout calculations and the drawing system.

- **C2:** The [document container interface](https://github.com/litehtml/litehtml/blob/master/include/litehtml/document_container.h) delegates font measurement, text and image drawing, resource loading, clipping, media features, and interaction to the host. This is a reusable layout library boundary rather than a binding around another browser.
- **C1:** The [table renderer](https://github.com/litehtml/litehtml/blob/master/src/render_table.cpp) calculates intrinsic minimum and maximum widths, distributes requirements across spanning cells, incorporates collapsed borders, and reconciles row spans after cell layout. These interdependent size constraints make the smaller codebase useful for studying real CSS correctness.

**Entry points:** `include/litehtml/document_container.h` and `src/render_table.cpp` above. Its intentionally limited compatibility is part of the selection, not evidence that web layout is simple.

### 10. [openwebf/webf](https://github.com/openwebf/webf)

**Language/role:** C++, Dart, and JavaScript; a web application runtime with custom HTML/CSS/DOM rendering on Flutter. The project describes itself as an **application runtime, not a general-purpose browser**.

Study how DOM mutations cross a language boundary and become native render-tree updates.

- **C1:** The [architecture document](https://github.com/openwebf/webf/blob/main/docs/ARCHITECTURE.md) distinguishes the JavaScript thread from the Dart UI isolate, asynchronous and synchronous calls, and memory ownership across FFI. String copies, persistent callback handles, and explicit native cleanup are concrete lifetime concerns.
- **C2:** DOM elements pass through widget adapters into specialized flow, flex, replaced-element, and custom-widget render objects. The same machinery supports web content and embedded Flutter widgets.
- **C3:** UI commands are batched at frame boundaries; incremental layout and computed-style caching reduce repeated work. The report relies on these mechanisms, not the repository's numerical speed claims.

**Entry point:** `docs/ARCHITECTURE.md` above, especially the command pipeline, thread model, and render-object specialization sections.

### 11. [youtube/cobalt](https://github.com/youtube/cobalt)

**Language/role:** Primarily C++; specialized HTML application engine integration. **The checked `main` tree is Chromium-derived**. It is retained for substantive Starboard/platform work, not counted as another independent Blink implementation.

Study how an existing browser engine is adapted to native media hardware and resource-constrained application environments.

- **C2:** The [Starboard renderer design](https://github.com/youtube/cobalt/blob/main/media/starboard/README.md) keeps the generic media renderer contract separate from optional Starboard extensions. Geometry commands and video-plane callbacks connect browser layout to a platform player without making the player depend directly on Mojo.
- **C3:** The [Starboard defaults implementation](https://github.com/youtube/cobalt/blob/main/cobalt/app/cobalt_switch_defaults_starboard.cc) selects low-end-device behavior, tile reclamation, texture-format exceptions, and V8 memory-related options. Its comments describe platform-specific tradeoffs rather than a single universal optimization.

**Entry points:** Those two files. The defaults include single-process operation, and the design document explicitly says some “process” terminology refers to threads in this configuration; it must not be read as a multi-process sandbox guarantee.

## Managed and non-visual document engines

### 12. [LoboEvolution/LoboEvolution](https://github.com/LoboEvolution/LoboEvolution)

**Language/role:** Java; the `LoboHTML` rendering subsystem within the LoboEvolution browser monorepo. It is a substantive continuation of LoboBrowser. The related CobraEvolution packaging is **not counted separately**.

Study browser layout expressed through Java objects and Swing integration. The README's published test summary includes failures, so this is an implementation-study candidate rather than a claim of broad compatibility.

- **C1:** The [RBlock implementation](https://github.com/LoboEvolution/LoboEvolution/blob/master/LoboHTML/src/main/java/org/loboevolution/html/renderer/RBlock.java) reconciles box sizing, minimum/maximum dimensions, floats, margins, and automatic scrollbars. Overflow can force layout to run again with a changed available width; temporary render-thread state is restored with `finally`.
- **C2:** [HtmlRendererContext](https://github.com/LoboEvolution/LoboEvolution/blob/master/LoboHTML/src/main/java/org/loboevolution/gui/HtmlRendererContext.java) abstracts navigation, dialogs, parent/opener windows, scrolling, user-agent services, and host interactions. This separates reusable renderer behavior from the surrounding browser application.

**Entry points:** `RBlock.java` and `HtmlRendererContext.java` above.

### 13. [HtmlUnit/htmlunit](https://github.com/HtmlUnit/htmlunit)

**Language/role:** Java; a non-visual browser engine for programmatic navigation, forms, DOM manipulation, and JavaScript execution. It simulates browser behavior rather than producing a graphical page.

Study compatibility-driven host-object implementation and an engine API designed for testing and extraction.

- **C1:** HtmlUnit binds Java DOM nodes to Rhino-backed JavaScript host objects, including dynamic property lookup before ordinary prototype traversal and scope/window resolution. Script execution can mutate a document during parsing, as its `document.write()` example demonstrates. [JavaScript architecture](https://htmlunit.org/javascript.html).
- **C2:** `HtmlUnitScriptable` centralizes node binding and host-object construction; `WebClient`, page objects, and dialog/event handlers expose reusable browser operations to Java applications. The architecture guide explains both the shared machinery and configurable execution behavior.
- **C4:** The [release history](https://htmlunit.org/changes-report.html) records years of browser-version compatibility changes, parser and JavaScript fixes, API additions, and runtime migrations, including releases from 2022 through 2026.

**Entry points:** The JavaScript architecture guide and release history above. Its default handling of unhandled script errors intentionally differs from a normal browser for testing purposes.

### 14. [jsdom/jsdom](https://github.com/jsdom/jsdom)

**Language/role:** JavaScript; a Node.js implementation of DOM/HTML and related browser behavior. **It does not implement visual layout or rendering**, as its README explicitly states; it belongs here as a document/runtime engine at the category boundary.

Study the hidden complexity of DOM operations independently of a native graphics stack.

- **C1:** [Node-impl.js](https://github.com/jsdom/jsdom/blob/main/lib/jsdom/living/nodes/Node-impl.js) coordinates document ID/name caches, live collections, shadow-tree distinctions, mutation observers, ranges, and custom-element machinery. Its subtree-cache ordering ensures element-specific steps observe updated document state.
- **C2:** The [JSDOM API](https://github.com/jsdom/jsdom#basic-usage) exposes configurable document environments, resource loading, and script execution for testing and scraping, while implementing standard interfaces inside the environment.
- **C3:** The node implementation lazily allocates observer/range bookkeeping and memoizes queries, invalidating the relevant caches after mutations. These optimizations are tied directly to DOM consistency requirements.

**Entry points:** The API documentation and `lib/jsdom/living/nodes/Node-impl.js` above. Its script-execution environment is not equivalent to a browser security sandbox.

## Terminal and accessibility-oriented rendering

### 15. [edbrowse/edbrowse](https://github.com/edbrowse/edbrowse)

**Language/role:** C and JavaScript; an independent, command-oriented browser engine that renders documents into editable text buffers. The relevant subsystem is its HTML/CSS/DOM and JavaScript synchronization code, not its unrelated editor or mail features.

Study a browser in which the displayed document is also an editing surface, making representation consistency especially visible.

- **C1:** The [development guide](https://github.com/edbrowse/edbrowse/blob/master/doc/developing.md) explains three copies of form state: editor text, HTML nodes, and JavaScript objects. `jSyncup()` transfers edits before script execution; `jSideEffects()` imports changes afterward, followed by rerendering and comparison of text buffers.
- **C3:** Update notifications are throttled for continuously changing pages. The [change history](https://github.com/edbrowse/edbrowse/blob/master/CHANGES) records removal of quadratic parsing behavior for hyperlink-heavy pages, HTTP-cache optimization, and parallel stylesheet downloads—specific performance work connected to identifiable subsystems.

**Entry points:** `doc/developing.md` and `CHANGES` above. A recently documented optional headless-Chrome plugin does not replace the native engine studied here.

### 16. [rkd77/elinks](https://github.com/rkd77/elinks)

**Language/role:** Primarily C, with optional scripting integrations; an HTML-to-terminal engine inside the ELinks browser. The README identifies this repository as the continuing fork, formerly called felinks, and explains its separate release policy and development history.

Study asynchronous browser lifetimes and reuse of formatted documents across views with limited display resources.

- **C1:** The [implementation guide](https://github.com/rkd77/elinks/blob/master/doc/hacking.txt) highlights that a connection can outlive its attached session after navigation. It distinguishes cached documents, shorter-lived document views, and longer-lived history state—lifetimes that callbacks must respect.
- **C2:** Parsing emits through callbacks, separating formatting state from output operations. Document, view, and history structures also separate shared content from per-tab interaction state.
- **C3:** Formatted documents can be shared by multiple views. The [document structure](https://github.com/rkd77/elinks/blob/master/src/document/document.h) records cache validity, CSS-import state, terminal lines, and link/search indexes, exposing how rendering reuse is managed.

**Entry points:** `doc/hacking.txt` and `src/document/document.h` above. The guide contains historical filenames and candidly describes legacy complexity; the current header provides a useful cross-check.

## Historical engine architecture

### 17. [KDE/khtml](https://github.com/KDE/khtml)

**Language/role:** C++/Qt; KHTML's historical HTML engine. **Official KDE GitHub mirror of its Invent project**, consistent with the [KDE organization's mirror notice](https://github.com/KDE). The default README says KHTML was removed for KF6 and that **`kf5` contains the last maintained state**. The entry therefore targets that branch, not the nearly empty default tree, and makes no claim of current engine maintenance.

Study a component-oriented browser engine and compatibility decisions preserved in a compact historical implementation.

- **C2:** [KHTMLPart](https://github.com/KDE/khtml/blob/kf5/src/khtml_part.h) separates the document-owning part from its view and supports URL loading, streamed HTML input, DOM access, browser extensions, and host-controlled capability settings. This is a substantial embedding API.
- **C1:** The [table renderer](https://github.com/KDE/khtml/blob/kf5/src/rendering/render_table.cpp) switches between fixed and automatic layout according to width semantics, creates anonymous sections for otherwise invalid render-tree children, handles collapsed borders, and documents a Gecko-compatibility exception for inline-table baselines.

**Entry points:** `kf5/src/khtml_part.h` and `kf5/src/rendering/render_table.cpp` above. Historical usefulness should not be confused with suitability for exposing the engine to today's unrestricted web.

## Coverage, search method, and limitations

Discovery used more than six distinct live search formulations, including: independent browser-engine architecture; lightweight C/C++ renderers; Rust engines and modular layout; official Blink/Chromium source; Firefox repository migration; WebKit architecture; Java/Cobra/HtmlUnit engines; Flutter web runtimes; terminal-browser rendering; Cobalt/Starboard integration; and C#/Go/Nim alternatives. Follow-up searches and repository links supplied less prominent candidates such as Gosub, Blitz, LoboEvolution, edbrowse, and ELinks. Later broad searches increasingly returned already-covered families, thin integrations, and early research projects, so the list stops at substantive entries with inspected evidence rather than filling a quota.

Every retained canonical repository page was opened, including the Firefox redirect. Additional architecture, API, or implementation material was read for every entry; source files inaccessible through the web cache were retrieved through the GitHub connector. Every retained entry has substantive implementation or architecture evidence beyond its project description. Branches are intentionally specified where relevant. Linked default-branch files can evolve after the research date.

Important boundaries and exclusions:

- **Dillo:** Excluded despite its relevant independent engine. Its [GitHub repository](https://github.com/dillo-browser/dillo) explicitly says it is no longer updated and lists its maintained mirrors on Codeberg and SourceHut, not GitHub. NetSurf is retained as a project mirror; KHTML is retained as an explicitly historical official mirror with substantive branch contents.
- **Duplicate lineages:** No separate count for old Gecko mirrors, SerenityOS's related LibWeb tree, individual engines bundled inside a selected monorepo, or CobraEvolution packaging. Cobalt is explicitly a specialized derivative, justified by its separate Starboard implementation rather than inherited Chromium code alone.
- **Adjacent software:** Browser shells, WebView language bindings, automation clients, standalone JavaScript engines, standalone CSS layout libraries, PDF-only renderers, and repository lists were not used to inflate the engine count. jsdom and HtmlUnit are explicitly non-visual; WebF is explicitly an application runtime.
- **Emerging projects:** The final language-diversity search also surfaced FenBrowser, Starling, and other experimental engines. They were not promoted from their discovery descriptions into the verified selection; their implementation and compatibility claims would need a separate deeper review. This report consequently has stronger C/C++, Rust, and Java coverage than C# or Go coverage.

No candidate was cloned, built, benchmarked, or executed. Compatibility and performance statements are limited to observed mechanisms and documented scope; they are not independent conformance measurements. C4 is awarded only where the inspected evidence establishes evolution and complexity/compatibility management, rather than merely an old copyright date or a recent commit.
