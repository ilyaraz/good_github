# Cross-platform GUI toolkits

Research date: **2026-10-09**.

This selection covers 25 repositories implementing reusable GUI systems across operating systems: native controls, retained scene graphs, declarative frameworks, immediate-mode interfaces, and embedded or engine-integrated toolkits. It emphasizes code that an experienced engineer can study for layout, event delivery, object lifetime, rendering, platform adaptation, and state management. A toolkit need not provide its own operating-system window backend to qualify, but it must provide substantial UI behavior beyond window creation or graphics primitives. Each repository is counted once; relevant subsystems are identified for larger monorepositories.

Criteria used below:

- **C1 — Correctness:** demanding invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and mechanisms supporting varied applications.
- **C3 — Performance and structure:** concrete resource or responsiveness constraints addressed through understandable architecture.
- **C4 — Evolution:** documented development over years together with compatibility, testing, or complexity management; age alone does not qualify.

Repository pages and the additional primary sources linked below were opened during research. Criteria assignments are engineering judgments grounded in those sources, not claims that every component has been audited or is uniformly exemplary.

## Native and desktop foundations

### [qt/qtbase](https://github.com/qt/qtbase)

**Language / role:** C++; Qt Base, particularly Core, Gui, and Widgets. This is an official GitHub mirror of the Qt development infrastructure, whose [repository documentation describes Gerrit-to-GitHub replication](https://wiki.qt.io/Requesting_New_Repositories). The entry concerns Qt Base rather than treating the entire Qt family as one repository.

Study the interaction between object ownership, thread affinity, event loops, and signal delivery:

- **C1:** A `QObject` and its children must obey thread-affinity rules; GUI objects have stronger main-thread restrictions. Direct, queued, and blocking queued connections have different execution semantics. The documentation explicitly identifies same-thread blocking-connection deadlock and explains why deferred deletion depends on the owning event loop. These are useful examples of concurrency contracts that affect object lifetime. [Threads and QObjects](https://doc.qt.io/qt-6/threads-qobject.html).
- **C2:** The same object, event, and signal/slot abstractions support widgets, timers, asynchronous networking, and worker objects. They provide a reusable coordination model across application domains, with platform-specific behavior beneath it. [Threads and QObjects](https://doc.qt.io/qt-6/threads-qobject.html).

**Entry point:** [threading, event loops, and connection semantics](https://doc.qt.io/qt-6/threads-qobject.html).

### [GNOME/gtk](https://github.com/GNOME/gtk)

**Language / role:** C; retained widget toolkit. The repository explicitly identifies itself as the official read-only GitHub mirror; development is hosted on GNOME GitLab.

GTK is particularly instructive for separating operating-system surfaces, widget snapshots, and rendering:

- **C2:** GDK handles surfaces and platform events, GTK widgets produce snapshots, and GSK represents drawing as render nodes such as text, textures, clips, and gradients. A widget hierarchy need not correspond to a hierarchy of native windows. These boundaries let widget authors and rendering backends evolve independently. [GTK drawing model](https://docs.gtk.org/gtk4/drawing-model.html).
- **C3:** The frame clock orders event, update, layout, and paint phases. Pointer motion can be compressed, inactive applications need not continuously redraw, and cached render nodes are invalidated when widgets request drawing. The architectural lesson is how to bound frame work while retaining a high-level widget API. [GTK drawing model](https://docs.gtk.org/gtk4/drawing-model.html).

**Entry point:** [frame clock, snapshots, and render-node caching](https://docs.gtk.org/gtk4/drawing-model.html).

### [wxWidgets/wxWidgets](https://github.com/wxWidgets/wxWidgets)

**Language / role:** C++; desktop toolkit using native platform controls, including Windows, macOS, and GTK implementations.

Study how a portable API exposes the difficult parts of native event-loop integration instead of assuming every platform behaves identically:

- **C1:** Modal dialogs create nested event loops. Only the active loop can exit immediately; an outer loop may need deferred termination. `wxEventLoopActivator` restores the previous loop, while selective yielding documents reentrancy and platform-specific event-loss hazards. [Event-loop interface and contracts](https://raw.githubusercontent.com/wxWidgets/wxWidgets/master/interface/wx/evtloop.h).
- **C2:** Shared event handling, dialogs, controls, and layout abstractions are implemented by multiple native ports. The event-loop interface provides a concrete boundary between that common API and platform dispatch. [Event-loop interface](https://raw.githubusercontent.com/wxWidgets/wxWidgets/master/interface/wx/evtloop.h).
- **C4:** The project's introduction records releases spanning 1992, 1999, and 2013, and specifically discusses source compatibility between early 2.0 applications and version 3. This supports studying compatibility management across major architectural generations, rather than inferring maturity from a creation date. [Project history and compatibility](https://github.com/wxWidgets/wxWidgets/blob/master/docs/doxygen/mainpages/introduction.h).

**Entry points:** [event-loop contracts](https://raw.githubusercontent.com/wxWidgets/wxWidgets/master/interface/wx/evtloop.h); [history and compatibility policy discussion](https://github.com/wxWidgets/wxWidgets/blob/master/docs/doxygen/mainpages/introduction.h).

### [fltk/fltk](https://github.com/fltk/fltk)

**Language / role:** C++; compact desktop widget toolkit for Windows, macOS, and Unix window systems.

FLTK provides a comparatively approachable place to examine custom widgets and explicit worker-to-UI coordination:

- **C1:** Window creation and destruction belong on the main thread. Workers accessing widgets must follow FLTK's locking rules, and `Fl::awake` callbacks introduce data-lifetime requirements: callback data must remain valid until consumed. The documentation also warns against mixing incompatible wakeup-message mechanisms. These details expose races that a superficially simple GUI API can otherwise conceal. [Advanced FLTK programming](https://www.fltk.org/doc-1.4/advanced.html).
- **C2:** Custom drawing and event handling integrate with a common widget and callback model, while event-loop integration and cross-thread wakeups remain shared services. This makes FLTK useful for studying extension of a small toolkit without requiring each application to reinvent dispatch and platform plumbing. [Advanced FLTK programming](https://www.fltk.org/doc-1.4/advanced.html).

**Entry point:** [customization, threading, locking, and wakeups](https://www.fltk.org/doc-1.4/advanced.html).

### [tcltk/tk](https://github.com/tcltk/tk)

**Language / role:** C and Tcl; Tk's cross-platform desktop widgets and geometry managers. This is the official GitHub mirror of the Tcl/Tk project's source repository.

The grid geometry manager is a focused example of UI correctness beneath a familiar scripting API:

- **C1:** `tkGrid.c` limits excessively large row or column indices because storage follows the highest index. Its structures also account for windows being deleted while layout still holds references, and an abort mechanism stops an arrangement pass when reentrant changes invalidate it. These are concrete resource-exhaustion and lifetime concerns. [Grid implementation](https://raw.githubusercontent.com/tcltk/tk/main/generic/tkGrid.c).
- **C2:** Geometry management is separated from individual widgets through `Tk_GeomMgr` callbacks. Row and column weights, minimum sizes, padding, uniform groups, and spanning constraints form reusable layout machinery for many widget combinations. [Grid implementation](https://raw.githubusercontent.com/tcltk/tk/main/generic/tkGrid.c).

**Entry point:** [grid data structures, layout scheduling, and geometry-manager callbacks](https://raw.githubusercontent.com/tcltk/tk/main/generic/tkGrid.c).

### [openjdk/jfx](https://github.com/openjdk/jfx)

**Language / role:** Java with native platform code; JavaFX's cross-platform scene graph and controls.

Study a retained scene graph whose public API specifies invalid structural edits and thread ownership precisely:

- **C1:** A node cannot occupy multiple scene-graph positions or introduce cycles, including through clipping relationships. Some reparenting operations automatically detach the old parent; other invalid modifications throw and restore the previous graph. Attached, visible scene graphs also impose JavaFX application-thread restrictions. [Node contracts](https://openjfx.io/javadoc/25/javafx.graphics/javafx/scene/Node.html).
- **C2:** The same `Node` foundation supports controls, layout regions, groups, shapes, images, and text, with shared transforms, properties, clipping, and event behavior. The implementation is useful for understanding how a scene graph serves both conventional widgets and custom graphics. [Node API](https://openjfx.io/javadoc/25/javafx.graphics/javafx/scene/Node.html).

**Entry point:** [Node ownership, graph invariants, properties, and event APIs](https://openjfx.io/javadoc/25/javafx.graphics/javafx/scene/Node.html).

### [juce-framework/JUCE](https://github.com/juce-framework/JUCE)

**Language / role:** C++; cross-platform application framework. The relevant subsystem here is JUCE's GUI components and graphics, including interfaces embedded in audio plug-ins, rather than its signal-processing library.

The component API exposes useful tradeoffs between a simple custom-painting interface and efficient redraw:

- **C2:** Components share parent/child composition, drawing, input, focus, and layout hooks. The same foundation can implement ordinary application windows and specialized interactive controls. [Component reference](https://docs.juce.com/master/classjuce_1_1Component.html).
- **C3:** `repaint` marks work for later drawing instead of synchronously repainting. Region invalidation, buffered component images, and `CachedComponentImage` provide explicit caching boundaries; repainting a child invalidates the affected cached region. This offers a concrete study of cache lifetime and incremental painting. [Component repaint and buffering documentation](https://docs.juce.com/master/classjuce_1_1Component.html).

**Entry point:** [Component composition, repaint, and cached images](https://docs.juce.com/master/classjuce_1_1Component.html).

## .NET frameworks and native adapters

### [AvaloniaUI/Avalonia](https://github.com/AvaloniaUI/Avalonia)

**Language / role:** C#; XAML-based retained GUI framework spanning desktop and additional mobile, browser, and embedded targets.

Study how familiar control, styling, and binding APIs connect to a toolkit-owned rendering pipeline:

- **C2:** The architecture separates controls and templates, measure/arrange layout, visuals, rendering, and platform backends. Logical and visual trees serve different purposes, allowing a control's semantic hierarchy to differ from its template-generated drawing hierarchy. [Architecture](https://docs.avaloniaui.net/docs/fundamentals/architecture).
- **C3:** Layout invalidations are coalesced, and changed visuals drive selective scene-graph updates. The architecture makes the relationship between a property change, layout work, and repaint work inspectable, which is valuable when diagnosing an expensive custom control. [Architecture](https://docs.avaloniaui.net/docs/fundamentals/architecture).

**Entry point:** [framework layers, trees, layout, and rendering](https://docs.avaloniaui.net/docs/fundamentals/architecture).

### [unoplatform/uno](https://github.com/unoplatform/uno)

**Language / role:** C# with platform-specific integration; cross-platform implementation of WinUI-style application APIs.

Uno is a useful comparison with frameworks that define an entirely separate control API:

- **C2:** It carries WinUI concepts such as templates, panels, and measure/arrange layout across platforms. Native rendering can associate elements with platform views, while the Skia path draws a toolkit-owned visual tree. The Windows target can use Microsoft's original WinUI implementation. [How Uno works](https://platform.uno/docs/articles/how-uno-works.html).
- **C3:** XAML is transformed into C# during compilation, moving construction work out of runtime parsing. Native and Skia rendering also expose distinct platform-integration and drawing-cost tradeoffs. These are architectural mechanisms, not evidence that either path universally outperforms the other. [How Uno works](https://platform.uno/docs/articles/how-uno-works.html).

The documentation explicitly describes incomplete APIs and analyzer warnings for unsupported members; API familiarity should not be mistaken for identical support on every target.

**Entry point:** [compilation, native/Skia rendering, and API compatibility](https://platform.uno/docs/articles/how-uno-works.html).

### [picoe/Eto](https://github.com/picoe/Eto)

**Language / role:** C#; common desktop API over native implementations such as WPF, Windows Forms, Cocoa, and GTK. Mobile support is not the basis for inclusion.

Study a smaller, explicit widget-to-handler adaptation layer:

- **C1:** The shared `Control` implementation checks UI-thread access before returning its handler. It also distinguishes load completion from initial loading, guards duplicate lifecycle transitions in debug builds, and coordinates gesture ownership with platform-handler changes. These details reveal invariants that span managed objects and native controls. [Control implementation](https://raw.githubusercontent.com/picoe/Eto/develop/src/Eto/Forms/Controls/Control.cs).
- **C2:** The WPF platform registers factories against typed handler interfaces for controls, drawing, dialogs, and application services. Capability flags and alternative implementations make platform variation explicit rather than spreading native conditionals through application code. [WPF platform registration](https://raw.githubusercontent.com/picoe/Eto/develop/src/Eto.Wpf/Platform.cs).

**Entry points:** [shared Control contracts](https://raw.githubusercontent.com/picoe/Eto/develop/src/Eto/Forms/Controls/Control.cs); [native handler registry](https://raw.githubusercontent.com/picoe/Eto/develop/src/Eto.Wpf/Platform.cs).

## Declarative frameworks across mobile, desktop, and web

### [flutter/flutter](https://github.com/flutter/flutter)

**Language / role:** Dart framework with a C++ engine and platform embedders; cross-platform widgets and rendering. The framework and engine subsystems in this monorepository are counted together.

Flutter is especially useful for distinguishing declarative descriptions from the persistent machinery that makes them practical:

- **C2:** Immutable widgets describe configuration, elements retain identity and state, and render objects perform layout, painting, hit testing, and related services. The framework/engine/embedder boundaries separate UI composition from rendering and host-platform integration. [Architectural overview](https://docs.flutter.dev/resources/architectural-overview).
- **C3:** Element reuse and selective traversal avoid rebuilding all persistent rendering machinery whenever an application produces new widget descriptions. The constraints-down, sizes-up layout protocol provides a structured account of how layout work propagates. Study these mechanisms together to understand the cost of an apparently small state change. [Architectural overview](https://docs.flutter.dev/resources/architectural-overview).

**Entry point:** [widget, element, render-object, engine, and embedder architecture](https://docs.flutter.dev/resources/architectural-overview).

### [react/react-native](https://github.com/react/react-native)

**Language / role:** JavaScript/TypeScript, C++, and native platform languages; React-based native UI, principally iOS and Android in the core repository. The former `facebook/react-native` URL redirected to this canonical repository during verification.

Study the boundary between declarative application updates and native view mutation:

- **C1:** The renderer uses immutable C++ structures to support sharing across threads, while host-view mutation remains on the UI thread. Rendering work can shift or be interrupted according to update priority, making thread ownership and snapshot consistency central design concerns. [Threading model](https://reactnative.dev/architecture/threading-model).
- **C2:** React element descriptions become a shadow tree, layout is computed during the render/commit pipeline, and mounting turns that result into platform host views. This separates component composition, layout representation, and native integration into reusable layers. [Render pipeline](https://reactnative.dev/architecture/render-pipeline).

**Entry points:** [renderer threading](https://reactnative.dev/architecture/threading-model); [render, commit, and mount phases](https://reactnative.dev/architecture/render-pipeline).

### [JetBrains/compose-multiplatform-core](https://github.com/JetBrains/compose-multiplatform-core)

**Language / role:** Kotlin; Compose implementation adapted for desktop, iOS, and web. This is JetBrains' substantive AndroidX fork. The selection concerns its Compose subsystem, not every library inherited into the repository. The separate Compose Multiplatform repository documents [where this implementation lives and how Skiko connects rendering and platform integration](https://github.com/JetBrains/compose-multiplatform/blob/master/compose/README.md); it is not counted as another toolkit.

- **C1:** `ComposeScene` owns composition and a layout-node tree with explicit lifetime rules. Closing it disposes resources and subscriptions and cancels composition effects; cancellation need not finish immediately, and subsequent scene use is forbidden. This is a concrete integration problem involving UI lifetime and coroutine cleanup. [ComposeScene contract](https://raw.githubusercontent.com/JetBrains/compose-multiplatform-core/jb-main/compose/ui/ui/src/skikoMain/kotlin/androidx/compose/ui/scene/ComposeScene.skiko.kt).
- **C2:** The scene abstraction combines content, density, constraints, focus, and input in a container used by platform windows and testing infrastructure. It demonstrates how reusable composition can be embedded into different hosts. The source marks this internal integration API as unstable. [ComposeScene contract](https://raw.githubusercontent.com/JetBrains/compose-multiplatform-core/jb-main/compose/ui/ui/src/skikoMain/kotlin/androidx/compose/ui/scene/ComposeScene.skiko.kt).

**Entry points:** [implementation map](https://github.com/JetBrains/compose-multiplatform/blob/master/compose/README.md); [scene lifecycle and integration interface](https://raw.githubusercontent.com/JetBrains/compose-multiplatform-core/jb-main/compose/ui/ui/src/skikoMain/kotlin/androidx/compose/ui/scene/ComposeScene.skiko.kt).

## Rust toolkits with distinct state and rendering models

### [emilk/egui](https://github.com/emilk/egui)

**Language / role:** Rust; immediate-mode UI usable in native and browser applications, with the `eframe` application framework and multiple rendering integrations.

- **C1:** Immediate-mode calls still require persistent identity. The `Id` implementation explains how identities preserve dragging and widget state across frames, why position-derived IDs are insufficient for movable stateful widgets, and how parent-derived IDs scope repeated content. Engineers can study the correctness boundary between transient declarations and persistent interaction state. [Widget identity implementation](https://raw.githubusercontent.com/emilk/egui/main/crates/egui/src/id.rs).
- **C2:** The architecture separates UI logic, math, shape/text tessellation, window-event integration, rendering backends, and application hosting. The architecture document also identifies an AccessKit-based testing layer. These boundaries make it possible to reuse egui inside an existing renderer or adopt a complete host. [Architecture](https://raw.githubusercontent.com/emilk/egui/main/ARCHITECTURE.md).

**Entry points:** [crate and integration architecture](https://raw.githubusercontent.com/emilk/egui/main/ARCHITECTURE.md); [persistent widget IDs](https://raw.githubusercontent.com/emilk/egui/main/crates/egui/src/id.rs).

### [iced-rs/iced](https://github.com/iced-rs/iced)

**Language / role:** Rust; declarative GUI organized around state, messages, views, and updates. The repository describes the toolkit as experimental; this entry does not assume a stable API.

- **C1:** Asynchronous subscriptions have identity and lifetime semantics beyond simply spawning a future. Subscription descriptions are inert until passed to the runtime; identity lets the runtime retain an existing stream, and ceasing to return a subscription causes that stream to be stopped. This is valuable material for studying long-lived background work tied to changing UI state. [Subscription implementation and contract](https://raw.githubusercontent.com/iced-rs/iced/master/futures/src/subscription.rs).
- **C2:** The repository's state/message/update model separates application transitions from view construction, while renderer and runtime layers support different integrations. Subscriptions extend that model to events and asynchronous streams without requiring each widget to own its own event loop. [Repository architecture overview](https://github.com/iced-rs/iced); [subscription API](https://raw.githubusercontent.com/iced-rs/iced/master/futures/src/subscription.rs).

**Entry point:** [subscription identity, runtime tracking, and stream integration](https://raw.githubusercontent.com/iced-rs/iced/master/futures/src/subscription.rs).

### [slint-ui/slint](https://github.com/slint-ui/slint)

**Language / role:** Rust implementation with a declarative UI language and integrations for several application languages; desktop, embedded, and other platform targets.

Slint exposes unusually instructive low-level machinery beneath a high-level reactive property model:

- **C1:** Its property implementation maintains dependency structures involving pinned allocations and raw pointers. The source documents why relocation would invalidate references, implements automatic dependency unlinking, and uses iterative destruction to avoid recursive-drop stack exhaustion on long lists, with a corresponding large-list test. These are substantive ownership and failure-mode problems. [Reactive property internals](https://raw.githubusercontent.com/slint-ui/slint/master/internal/core/properties.rs).
- **C2:** That dependency engine is reusable infrastructure for declarative properties and component bindings rather than logic tied to one control. Together with the compiler and language integrations described in the repository, it supports separating application logic from a shared UI component system. [Property implementation](https://raw.githubusercontent.com/slint-ui/slint/master/internal/core/properties.rs); [repository overview](https://github.com/slint-ui/slint).

**Entry point:** [property storage, dependency tracking, pinning, and destruction](https://raw.githubusercontent.com/slint-ui/slint/master/internal/core/properties.rs).

### [linebender/xilem](https://github.com/linebender/xilem)

**Language / role:** Rust; experimental reactive UI, with native retained widgets in the Masonry subsystem. Xilem and Masonry are counted once as parts of this monorepository.

- **C2:** The architecture separates lightweight view descriptions from persistent elements. `View` build, rebuild, and message operations connect application data to retained widgets; related abstractions can target a different backend such as a web DOM. Generic view sequences and optional type erasure make the reuse boundary explicit. [Architecture document](https://raw.githubusercontent.com/linebender/xilem/main/xilem/ARCHITECTURE.md).
- **C3:** Rebuilding a declarative description does not imply recreating every retained element. Typed reconciliation and memoization let unchanged application data bypass subtree construction or rebuilding. The document makes the costs of eagerly rebuilding descriptions visible, providing a useful study of performance tradeoffs in a strongly typed reactive design. [Architecture document](https://raw.githubusercontent.com/linebender/xilem/main/xilem/ARCHITECTURE.md).

The architecture notes contain unfinished sections; treat them as a design guide alongside the evolving implementation, not a stable specification.

**Entry point:** [view/element separation, reconciliation, and memoization](https://raw.githubusercontent.com/linebender/xilem/main/xilem/ARCHITECTURE.md).

## Go and Python implementations

### [fyne-io/fyne](https://github.com/fyne-io/fyne)

**Language / role:** Go; desktop and mobile GUI framework with toolkit-drawn widgets.

- **C1:** The documented UI-goroutine model requires background work to marshal UI changes through `fyne.Do`. `DoAndWait` is needed when the caller must wait before reusing data such as a drawing buffer. Separately, the renderer contract distinguishes layout from refresh and forbids a layout implementation from recursively initiating refresh. These are concrete concurrency and reentrancy constraints. [Goroutine guidance](https://docs.fyne.io/started/goroutines/); [widget/renderer interfaces](https://raw.githubusercontent.com/fyne-io/fyne/develop/widget.go).
- **C2:** A widget exposes behavior while a renderer supplies its canvas objects, layout, minimum size, refresh, and cleanup. The interface makes one renderer responsible for each widget and specifies when its resources cease to be reusable. This is a compact example of reusable presentation machinery with explicit lifetime rules. [Widget/renderer interfaces](https://raw.githubusercontent.com/fyne-io/fyne/develop/widget.go).

**Entry points:** [UI scheduling](https://docs.fyne.io/started/goroutines/); [Widget and WidgetRenderer contracts](https://raw.githubusercontent.com/fyne-io/fyne/develop/widget.go).

### [gioui/gio](https://github.com/gioui/gio)

**Language / role:** Go; immediate-mode GUI and graphics. The GitHub repository is an official mirror of the project's SourceHut repository, as its README states.

Gio offers a different architecture from both native-widget bindings and conventional retained trees:

- **C2:** Applications consume window events, build operation lists, and submit a frame. Those operations represent drawing and other UI work behind platform-specific window drivers, allowing common UI code to participate in different host environments. [Window and operation architecture](https://gioui.org/doc/architecture/window).
- **C3:** Operation lists serialize work into reusable storage. The documentation explains why operations use `operation.Add(&ops)` rather than passing arbitrary operation interfaces: that API shape helps avoid allocation overhead. The frame-event boundary also makes rendering work and buffer reset points explicit. [Window and operation architecture](https://gioui.org/doc/architecture/window).

**Entry point:** [window drivers, frame events, operation buffers, and allocation-conscious APIs](https://gioui.org/doc/architecture/window).

### [kivy/kivy](https://github.com/kivy/kivy)

**Language / role:** Python and Cython/C; cross-platform graphical applications with multi-touch input and an OpenGL-based rendering layer.

- **C2:** Core providers isolate services such as windows, text, and media, while input providers translate device-specific data into events that widgets can consume. Widget and layout layers sit above these services. This architecture is useful for studying how a dynamic-language UI handles heterogeneous devices without embedding every platform distinction into widgets. [Architecture guide](https://kivy.org/doc/stable/guide/architecture.html).
- **C3:** Graphics instructions are implemented below the Python application layer and collected into canvas operations. The architecture describes optimization of drawing instructions, showing how a high-level interactive framework can move repeated graphics work into lower-level implementation while retaining composable UI objects. [Architecture guide](https://kivy.org/doc/stable/guide/architecture.html).

**Entry point:** [providers, input normalization, graphics instructions, and UI layers](https://kivy.org/doc/stable/guide/architecture.html).

### [beeware/toga](https://github.com/beeware/toga)

**Language / role:** Python; native-widget GUI toolkit with platform-specific implementations and a non-graphical testing backend.

- **C1:** Application lifecycle code handles exit requests that may be asynchronous and may veto termination, for example while dealing with unsaved work. Startup also enforces contracts around the main window and application type. These paths show how apparently simple application APIs must coordinate event-loop work and resource lifetime. [Application implementation](https://raw.githubusercontent.com/beeware/toga/main/core/src/toga/app.py).
- **C2:** Toga distinguishes a public interface, a platform implementation, and native widgets. One logical widget may require multiple native objects. A dummy backend implements the interface without drawing, providing a testing seam for the same abstraction. [Architecture](https://toga.beeware.org/en/stable/topics/architecture/).

The architecture documentation explicitly cautions that not every widget is implemented on every platform; native adaptation is substantive work, not automatic API parity.

**Entry points:** [interface/implementation/native layers](https://toga.beeware.org/en/stable/topics/architecture/); [application startup and exit coordination](https://raw.githubusercontent.com/beeware/toga/main/core/src/toga/app.py).

## Embedded and engine-integrated GUI systems

### [lvgl/lvgl](https://github.com/lvgl/lvgl)

**Language / role:** C; portable GUI toolkit for embedded devices and other display environments.

Study how a widget system exposes rendering policy when memory and display bandwidth are application-level constraints:

- **C2:** The display API abstracts resolution, rotation, pixel density, and transfer callbacks, separating widget behavior from a particular display controller or framebuffer arrangement. Multiple display configurations can reuse the toolkit's UI machinery. [Display interface](https://raw.githubusercontent.com/lvgl/lvgl/master/include/lvgl/display/lv_display.h).
- **C3:** Partial rendering permits buffers smaller than a frame; direct rendering uses frame-sized buffers and updates changed areas, with synchronization implications for multiple buffers; full rendering redraws the frame. These explicit policies expose RAM, redraw, and buffer-management tradeoffs instead of assuming a desktop-sized GPU framebuffer. [Rendering-mode definitions](https://raw.githubusercontent.com/lvgl/lvgl/master/include/lvgl/display/lv_display.h).

**Entry point:** [display abstraction and partial/direct/full rendering modes](https://raw.githubusercontent.com/lvgl/lvgl/master/include/lvgl/display/lv_display.h).

### [ocornut/imgui](https://github.com/ocornut/imgui)

**Language / role:** C++; Dear ImGui, an immediate-mode toolkit frequently embedded in engines, editors, and development tools.

- **C1:** Widget calls need stable, correctly scoped IDs to preserve active state and distinguish repeated labels. The FAQ explains collisions, ID stacks, label/identity separation, and diagnostics. Studying these rules reveals why recomputing UI every frame does not eliminate persistent interaction invariants. [ID-stack guidance](https://raw.githubusercontent.com/ocornut/imgui/master/docs/FAQ.md).
- **C2:** The core produces rendering data independently of an application's platform and renderer backends. This allows a substantial widget library to be embedded in an existing application loop rather than requiring ownership of its entire windowing architecture. [Repository integration overview](https://github.com/ocornut/imgui).

Its own README identifies limitations including accessibility and full bidirectional text support; the strongest fit here is engine and tool UI rather than assuming parity with general desktop accessibility stacks.

**Entry point:** [identity, integration, and common failure modes](https://raw.githubusercontent.com/ocornut/imgui/master/docs/FAQ.md).

### [Immediate-Mode-UI/Nuklear](https://github.com/Immediate-Mode-UI/Nuklear)

**Language / role:** C89; embeddable immediate-mode widget library. The application supplies windowing, input integration, and rendering of generated commands.

- **C1:** The buffer implementation manages aligned allocations from both ends, distinguishes fixed-buffer exhaustion from dynamic growth, and relocates the trailing region when storage grows. These mechanisms expose bounds, alignment, pointer relocation, and allocation-failure concerns within a compact UI codebase. [Buffer implementation](https://github.com/Immediate-Mode-UI/Nuklear/blob/master/src/nuklear_buffer.c).
- **C2:** Input consumption and draw-command generation are separated from operating-system and renderer ownership. Applications can reuse controls and layout while choosing their own integration and memory policy. [Repository design and integration overview](https://github.com/Immediate-Mode-UI/Nuklear).
- **C3:** Fixed or dynamic storage, caller-controlled allocation, and resettable buffer markers make memory predictability and reuse explicit. They are useful study material for constrained or tightly integrated interfaces. [Buffer implementation](https://github.com/Immediate-Mode-UI/Nuklear/blob/master/src/nuklear_buffer.c).

**Entry point:** [allocation, alignment, growth, and buffer reuse](https://github.com/Immediate-Mode-UI/Nuklear/blob/master/src/nuklear_buffer.c).

### [mikke89/RmlUi](https://github.com/mikke89/RmlUi)

**Language / role:** C++; retained HTML/CSS-like UI for applications and engines. It is a substantive evolution of libRocket, not a second listing of an unchanged fork, and it is not a general web browser.

- **C1:** The renderer interface specifies geometry-handle lifetime and conventions for premultiplied alpha, color representation, clipping, coordinate systems, and triangle winding. A backend can appear to work while violating one of these contracts on a different renderer, making this a useful cross-platform numerical and resource-lifetime boundary. [Render-interface contract](https://mikke89.github.io/RmlUiDoc/pages/cpp_manual/interfaces/render.html).
- **C2:** UI layout and document behavior are separated from application-owned render, system, file, and other integration interfaces. The render contract supports basic geometry and more advanced effects without requiring RmlUi to own the application's rendering engine. [Render interface](https://mikke89.github.io/RmlUiDoc/pages/cpp_manual/interfaces/render.html); [repository overview](https://github.com/mikke89/RmlUi).

Its own changelog documents continued independent changes, including stylesheet variables and additional backends, supporting the distinction from its ancestor. [Changelog](https://raw.githubusercontent.com/mikke89/RmlUi/master/changelog.md).

**Entry points:** [renderer integration and correctness conventions](https://mikke89.github.io/RmlUiDoc/pages/cpp_manual/interfaces/render.html); [implementation evolution](https://raw.githubusercontent.com/mikke89/RmlUi/master/changelog.md).

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, covering native C/C++ controls and event loops; Rust declarative and immediate-mode toolkits; Go GUI architecture; .NET native adapters versus toolkit-owned rendering; Python native-widget and touch-oriented frameworks; JavaFX and Kotlin Compose; embedded display libraries; and engine-integrated interfaces. Follow-up searches targeted source files, threading rules, render pipelines, layout algorithms, testing seams, compatibility history, and less prominent C/C++ candidates such as Nana, Agar, NanoGUI, and NAppGUI. Later searches increasingly returned already-covered families, wrappers, or integration projects rather than distinct implementations with stronger evidence.

The retained set includes both large framework communities and smaller libraries with inspectable internals. Every entry has a verified GitHub repository page plus an opened additional primary source containing implementation or architectural detail. Official mirrors are identified for Qt Base, GTK, Tk, and Gio. Compose's AndroidX fork and RmlUi's libRocket ancestry are disclosed; their substantive implementation work justifies inclusion. Experimental status is stated for Iced and Xilem. Repository inclusion does not assert a particular maintenance cadence or equal support across advertised targets.

Low-level window/context libraries such as GLFW and SDL, renderer-only libraries, generated language bindings, awesome lists, and application-shell frameworks were outside this report's toolkit focus. Ancestors, backend packages, and monorepository subsystems were not counted again as independent toolkits. NAppGUI was investigated but omitted because the attempted documentation/source retrievals did not establish the required second substantive primary source; this is a research limitation, not a judgment on its engineering quality. Other omissions likewise should not be read as rankings.

This is a source-based selection guide. No candidate code was executed, no benchmarks were reproduced, and no security or compatibility certification is implied. Performance assessments concern documented mechanisms and tradeoffs, not unsupported throughput claims. Some entry points follow moving development branches and some documentation is versioned; future readers should match those sources to the release they intend to study. C4 is used conservatively where explicit history and compatibility evidence were inspected, rather than awarded to every long-established project.
