# Terminal UI frameworks

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories for building interactive terminal interfaces: application frameworks, reusable widget systems, declarative renderers, and a smaller set of substantial terminal rendering foundations. It excludes terminal emulators, individual TUI applications, command-line argument parsers, and styling-only packages. The emphasis is on what an experienced engineer can learn from the implementation, rather than popularity or a recommendation to adopt every project.

Canonical repository identities, default branches, and archive flags were checked through the GitHub API. Each entry also draws on an inspected source file or substantive design/API document. Links generally follow the inspected default branch, which may contain unreleased work; notably, Terminal.Gui was inspected on `develop`. None of the retained repositories was marked archived at the time of checking. Specific mirror, experimental, and limited-activity cases are identified below. Criteria are engineering judgments grounded in the linked material, not independent performance measurements or guarantees of correctness.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, adversarial input, Unicode/numerical semantics, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and components that support different applications.
- **C3 — Performance with structure:** concrete work to reduce rendering, allocation, computation, or terminal I/O costs within an understandable design.
- **C4 — Sustained evolution:** dated history coupled with compatibility work, regression testing, or complexity management.

## Python: application frameworks, editing, and animation

### [Textualize/textual](https://github.com/Textualize/textual)

**Python — asynchronous application and widget framework.** Study how a terminal application combines a widget tree, message dispatch, and background work without requiring every application author to manage an event loop directly.

- **C1:** The worker API addresses out-of-order results with exclusive workers, ties worker lifetime to the originating DOM node, and distinguishes coroutine cancellation from cooperative cancellation of threads. UI mutation from worker threads must pass through the appropriate main-thread mechanism. These are concrete concurrency contracts, including an example where an older search result would otherwise overwrite a newer one. [Worker guide](https://github.com/Textualize/textual/blob/main/docs/guide/workers.md).
- **C2:** Messages and events give custom widgets a communication protocol, including handlers and propagation through the DOM; applications can compose controls without hard-wiring every interaction into one global callback. [Events and messages guide](https://github.com/Textualize/textual/blob/main/docs/guide/events.md).

### [urwid/urwid](https://github.com/urwid/urwid)

**Python — compositional widget library with interchangeable event loops and displays.** A particularly useful study in keeping a retained widget hierarchy responsive while preserving cache correctness.

- **C2, C3:** Widgets render canvases, while containers form composite canvases referencing their children's content. Cached canvases avoid repeated rendering; invalidation propagates to parents, and weak references allow invisible canvases to disappear. Pending input is processed before the final redraw, preventing the display from continually falling behind. [Canvas-cache design](https://github.com/urwid/urwid/blob/master/docs/manual/canvascache.rst).
- **C1, C4:** The dated changelog spans, among other years, 2015, 2020, and 2024 and records terminal-reset, resize, Unicode input, and regression-test work. More recent entries address cyclic trees, terminal write failures, unsafe drawn control characters, and signal handling during rendering. This is evidence of continuing failure-mode and compatibility management, rather than age alone. [Changelog](https://github.com/urwid/urwid/blob/master/docs/changelog.rst).

### [prompt-toolkit/python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)

**Python — interactive editing, REPLs, dialogs, and full-screen applications.** Its architectural value extends beyond readline-style prompts to editable buffers, controls, windows, processors, and layout.

- **C2, C3:** `BufferControl` adapts editable state into `UIContent`; a `Window` handles scrolling and placement. Lexing and processor transformations are requested lazily for visible lines, making the separation of text state, transformations, and viewport rendering directly relevant to large documents. [Rendering-flow guide](https://github.com/prompt-toolkit/python-prompt-toolkit/blob/main/docs/pages/advanced_topics/rendering_flow.rst).
- **C1, C4:** Release notes from 2015 through subsequent major versions document threading and invalidation changes, signal fixes, and handling of closed stdin, `/dev/null`, and stdout without a usable file descriptor. They also track API and typing evolution. [Changelog](https://github.com/prompt-toolkit/python-prompt-toolkit/blob/main/CHANGELOG).

The separate older architecture diagram labels itself outdated; the rendering-flow document and repository history are better starting points for this selection.

### [peterbrittain/asciimatics](https://github.com/peterbrittain/asciimatics)

**Python — terminal widgets and animation under a shared scene model.** Study a framework that supports forms and animated effects through the same scheduling machinery.

- **C2:** Widgets belong to layouts, layouts belong to frames, and a frame is itself an effect usable inside a scene. The widget guide explicitly explains why persistent application data must be separated from presentation objects that are recreated on resize. [Widget architecture](https://github.com/peterbrittain/asciimatics/blob/master/doc/source/widgets.rst).
- **C3:** Refresh scheduling consults when effects next need drawing; `reduce_cpu` and `force_update` expose the responsiveness-versus-work tradeoff. The framework also permits another asynchronous runtime to drive individual frame steps. This is a concrete scheduling design, not a throughput claim. [Animation and CPU considerations](https://github.com/peterbrittain/asciimatics/blob/master/doc/source/animation.rst).

## Rust and Zig: explicit rendering and widget contracts

### [ratatui/ratatui](https://github.com/ratatui/ratatui)

**Rust — immediate-mode widget rendering and layout.** Ratatui is the substantially evolved continuation of `tui-rs`, forked in 2023; the predecessor is not counted separately. The relevant monorepo subsystems are `ratatui-core`, built-in widgets, and backend crates.

- **C2:** The workspace separates foundational widget traits, buffers, layout, and text from widgets and terminal backends. The architecture explains the dependency boundary intended to let third-party widgets depend on a smaller, more stable core. [Architecture](https://github.com/ratatui/ratatui/blob/main/ARCHITECTURE.md).
- **C1, C3:** Buffer diffing handles more than unequal characters: wide glyphs can leave stale trailing styles, and emoji presentation sequences may occupy different widths on different terminals. The iterator includes explicit trailing-cell handling and tests, illustrating the correctness cost of minimizing output. [Buffer diff implementation and tests](https://github.com/ratatui/ratatui/blob/main/ratatui-core/src/buffer/diff.rs).

### [gyscos/cursive](https://github.com/gyscos/cursive)

**Rust — retained views, dialogs, layers, and multiple terminal backends.** Study the contract between reusable views and the runner that owns rendering and input processing.

- **C2, C3:** `View` separates drawing, required-size negotiation, layout, focus, and event consumption. Its layout key has an explicit invariant: an unchanged key must imply unchanged size answers, allowing containers to reuse calculations. [View trait](https://github.com/gyscos/cursive/blob/main/cursive-core/src/view/view_trait.rs).
- **C1:** A refresh captures terminal size once so layout and drawing cannot observe different dimensions. The runner includes a mock backend whose size changes between queries and a regression test checking layout/draw consistency. This is a compact example of turning an intermittent resize race into an executable invariant. [Runner and resize tests](https://github.com/gyscos/cursive/blob/main/cursive-core/src/cursive_run.rs).

### [rockorager/libvaxis](https://github.com/rockorager/libvaxis)

**Zig — terminal engine plus the `vxfw` widget framework.** Counted once, covering both the low-level API and the higher-level runtime. It provides a useful comparison with Rust ownership-oriented designs and Flutter-style layout.

- **C2:** `vxfw` defines type-erased widgets, event and drawing contexts, constrained sizes, surfaces, and commands for focus, redraw, clipboard, and notifications. The drawing context supplies a frame-scoped arena, making temporary allocation lifetime part of the API. [Framework types and contracts](https://github.com/rockorager/libvaxis/blob/main/src/vxfw/vxfw.zig).
- **C1:** The terminal layer discovers capabilities through query responses rather than assuming a terminfo description. Its integration example separates capability replies from application events and shows platform-specific reading, parser state, resize delivery, and error handling. Applications supplying their own event loop must preserve those responsibilities. [Low-level usage and event-loop integration](https://github.com/rockorager/libvaxis/blob/main/USAGE.md).

## Go: state machines, widgets, and screen backends

### [charmbracelet/bubbletea](https://github.com/charmbracelet/bubbletea)

**Go — Elm-style model/update/view application runtime.** Study the boundary between serialized model updates and effects executed in goroutines; the inspected branch uses the v2 `View` API.

- **C1:** The program coordinates message channels, context cancellation, panic recovery, input shutdown, and terminal restoration. A revealing limitation is documented in `handleCommands`: already-running commands cannot automatically be cancelled, so their goroutines may remain until the commands return. [Program implementation](https://github.com/charmbracelet/bubbletea/blob/main/tea.go).
- **C2:** `Model`, messages, and commands form reusable application machinery. The v2 migration guide shows a substantive redesign in which terminal modes and cursor state become declarative fields of a view, replacing scattered imperative commands. [v2 upgrade and design guide](https://github.com/charmbracelet/bubbletea/blob/main/UPGRADE_GUIDE_V2.md).

### [rivo/tview](https://github.com/rivo/tview)

**Go — conventional interactive widgets over tcell.** Useful for studying the contrast between mutable widget objects and Bubble Tea's message-driven application model.

- **C2:** Widgets share `Box` functionality and implement `Primitive`; the package combines forms, tables, trees, text areas, and grid/flex/page layouts under an application loop. The package documentation explains the common type hierarchy and rendering dependency. [Package architecture and API overview](https://github.com/rivo/tview/blob/master/doc.go).
- **C1:** Cross-goroutine mutations are serialized with `QueueUpdate` or `QueueUpdateDraw`, which wait for execution. The documentation explicitly warns that invoking them from a main-loop key callback can deadlock; it separately identifies the thread-safe `TextView` writer path. Compare that contract with the queue implementation. [Application event loop and update queue](https://github.com/rivo/tview/blob/master/application.go).

### [gdamore/tcell](https://github.com/gdamore/tcell)

**Go — reusable screen/input foundation rather than a complete widget framework.** Included because it exposes the terminal correctness and performance contracts on which higher-level frameworks depend. The inspected default branch is v3; tview's inspected documentation refers to v2.

- **C1, C2:** The screen abstraction specifies logical versus physical contents, wide-character behavior at the last column, incremental `Show`, and recovery through `Sync`. Its contract makes platform-independent drawing reusable while retaining explicit terminal limitations. [Screen interface](https://github.com/gdamore/tcell/blob/main/screen.go).
- **C1, C3:** The cell buffer tracks current and previously displayed content, dirties wide-character trailing cells together, reuses previously measured widths for identical content, and has an ASCII fast path before grapheme segmentation. [Cell-buffer implementation](https://github.com/gdamore/tcell/blob/main/cell.go).

## JavaScript, TypeScript, and Kotlin: component runtimes

### [vadimdemedes/ink](https://github.com/vadimdemedes/ink)

**TypeScript/JavaScript — React renderer with Yoga layout.** Study how a component system maps to terminal output while mixing permanent log content and a changing interactive region.

- **C2:** The renderer separates static output from interactive output and offers a distinct screen-reader path. It checks ancestor visibility even for separately rendered static nodes, showing how browser-like composition rules survive a different output medium. [Renderer](https://github.com/vadimdemedes/ink/blob/master/src/renderer.ts).
- **C1, C3:** The update layer tracks cursor state as well as text. Its incremental path skips unchanged lines, aggregates output chunks, and clears surplus lines when a frame shrinks. Cursor positions are invalidated across renders to prevent stale state after component removal. [Output-update implementation](https://github.com/vadimdemedes/ink/blob/master/src/log-update.ts).

### [chjj/blessed](https://github.com/chjj/blessed)

**JavaScript — DOM-like widgets with an integrated terminal capability layer.** A valuable historical design study, especially for scroll-region optimization. It is unarchived, but GitHub metadata reported the most recent repository push as **2024-03-22**; this report does not imply current active maintenance. [Status metadata](https://api.github.com/repos/chjj/blessed).

- **C2:** The repository combines a `Program` abstraction for terminal sequences with a separate high-level widget API and screen hierarchy. This exposes both terminal-dependent behavior and reusable application components. [Repository design introduction](https://github.com/chjj/blessed#blessed).
- **C3:** The screen implementation maintains old/new line buffers and damage state, emits terminal insert/delete-line operations, and checks whether a widget's sides permit scrolling-region optimization. It documents the CPU-versus-output tradeoff of that check, making this a useful case study in optimization conditions. [Screen implementation](https://github.com/chjj/blessed/blob/master/lib/widgets/screen.js).

### [anomalyco/opentui](https://github.com/anomalyco/opentui)

**Zig and TypeScript — native rendering core with imperative, React, and Solid interfaces.** Count the monorepo once: the relevant implementation is in `packages/native`, with application APIs in `packages/core` and the framework adapters.

- **C1:** The native buffer invariant checker verifies that continuation cells belong to matching grapheme starts, tracker counts agree with cells, pooled IDs remain live, and cells do not contain control code points. This is unusually direct evidence of correctness obligations at the text-storage boundary. [Buffer invariant checker](https://github.com/anomalyco/opentui/blob/main/packages/native/src/tests/buffer-invariants.zig).
- **C2, C3:** The output transport abstracts a buffered backend and a feed backend that stages complete frames for atomic publication to TypeScript consumers, including SSH streams. A single tagged-union dispatch selects a writer implementation, keeping transport variation outside the rendering logic; nearby tests cover write ordering and observable failures. [Output backends](https://github.com/anomalyco/opentui/blob/main/packages/native/src/renderer-output.zig).

### [JakeWharton/mosaic](https://github.com/JakeWharton/mosaic)

**Kotlin — terminal UI using the Jetpack Compose compiler/runtime.** The repository explicitly describes itself as experimental. Study how a declarative runtime is adapted to terminal lifecycle and rendering instead of treating it as a mature drop-in widget suite.

- **C1, C2:** `MosaicComposition` coordinates a recomposer, coroutine job, frame clocks, terminal events, and snapshot observers. State reads during layout and drawing are tracked separately so a change can request the appropriate phase. [Composition runtime](https://github.com/JakeWharton/mosaic/blob/trunk/mosaic-runtime/src/commonMain/kotlin/com/jakewharton/mosaic/mosaic.kt).
- **C3:** Rendering reuses a string builder, preserves permanent output, clears stale lines, and uses synchronized output when supported. The code explicitly chooses a broader clear for unmeasured static strings rather than paying to parse their exact dimensions. [Rendering implementations](https://github.com/JakeWharton/mosaic/blob/trunk/mosaic-runtime/src/commonMain/kotlin/com/jakewharton/mosaic/rendering.kt).

## C and C++: widgets, compositors, and terminal machinery

### [ArthurSonzogni/FTXUI](https://github.com/ArthurSonzogni/FTXUI)

**C++ — functional terminal elements and interactive components.** Study the separation between a one-frame visual description and a persistent component that responds to events.

- **C2:** Components expose rendering, event handling, and parent/child relationships; the component tree also determines navigation. Renderer and event-catching decorators let applications change appearance or intercept behavior without replacing the underlying control. [Component architecture](https://github.com/ArthurSonzogni/FTXUI/blob/main/doc/module-component.md).
- **C1, C3:** The string layer distinguishes control, combining, and full-width characters, accounts for emoji presentation selectors, and uses generated Unicode property tables. ASCII shortcuts bypass more expensive decoding on common paths. This makes character-width semantics and optimization visible in one tractable subsystem. [String and width implementation](https://github.com/ArthurSonzogni/FTXUI/blob/main/src/ftxui/screen/string.cpp).

### [gansm/finalcut](https://github.com/gansm/finalcut)

**C++ — Qt-influenced text widgets and overlapping windows.** Useful for studying a conventional object-oriented toolkit with its own terminal machinery rather than an ncurses widget wrapper.

- **C2:** `FApplication` owns the event loop; `FObject` and `FWidget` route event objects into typed handlers. Direct delivery, queued events, timers, and application-defined events provide several extension seams. [Event-processing design](https://github.com/gansm/finalcut/blob/main/doc/event-processing.md).
- **C4:** The dated changelog connects 2016 terminal-specific cursor fixes and API reduction, 2022 input buffering and `FVTerm` unit tests, and 2025 work on string copying and rendering internals. This supports sustained compatibility and complexity management rather than simply asserting that the library is old. [ChangeLog](https://github.com/gansm/finalcut/blob/main/ChangeLog).

### [magiblot/tvision](https://github.com/magiblot/tvision)

**C++ — substantive modern port of Turbo Vision 2.0.** This is the modern port, not Borland's original repository or an unchanged mirror. Its documented work includes cross-platform support and integration of Unicode into the inherited architecture.

- **C2:** The framework supplies overlapping resizable windows, menus, dialogs, and controls while preserving substantial source compatibility with older Turbo Vision applications. The README explains both the compatibility goal and limitations of the legacy design. [Port rationale and API discussion](https://github.com/magiblot/tvision#turbo-vision).
- **C1, C3:** `DisplayBuffer` tracks row damage, delays flushes to respect a configured rate, and separates display adapters from buffered updates. It also handles overlapping memory copies and cursor placement on trailing cells of wide characters—details that complicate otherwise straightforward redraw optimization. [Display-buffer implementation](https://github.com/magiblot/tvision/blob/master/source/platform/dispbuff.cpp).

### [dankamongmen/notcurses](https://github.com/dankamongmen/notcurses)

**C, with C++ interfaces — plane compositor, widgets, and terminal graphics.** Study layered composition and the distinction between producing a scene and emitting a terminal-specific update.

- **C1:** Multiple plane piles may be rendered concurrently, but rasterization is exclusive; a pile must not be mutated while it is rendered. The manual also explains how a failed partial output can desynchronize later frames and require refresh. [Rendering contracts and algorithm](https://github.com/dankamongmen/notcurses/blob/master/doc/man/man3/notcurses_render.3.md).
- **C2, C3:** Cells, planes, piles, and higher-level controls provide reusable composition units. Rendering resolves glyphs and foreground/background channels down the z-order, then rasterization converts the result plus current screen state into optimized terminal sequences. [Usage and API guide](https://github.com/dankamongmen/notcurses/blob/master/USAGE.md).

The documented concurrency restrictions matter: the general thread-safety motivation is not permission to mutate every object concurrently.

### [termbox/termbox2](https://github.com/termbox/termbox2)

**C — compact single-header terminal I/O and cell-buffer foundation.** Included as a smaller implementation for studying the machinery beneath frameworks. It substantially extends original termbox with error checking, escape parsing, tests, and optional extended-character storage; the original is not counted separately.

- **C1:** `tb_present` handles wide characters at the right edge and marks covered front-buffer cells invalid so replacing a wide glyph with a narrow one redraws the remaining cells. Input parsing distinguishes a complete event from a sequence needing more bytes. [Implementation and API contracts](https://github.com/termbox/termbox2/blob/master/termbox2.h).
- **C2, C3:** The reusable boundary is deliberately small: initialization, cells, presentation, events, and file descriptors for external polling. Front/back comparison limits output to changed cells. The same header explicitly warns that its convenience printing performs only approximate grapheme grouping; this is a useful limitation to study, not full Unicode-layout correctness. [API and design introduction](https://github.com/termbox/termbox2#api).

### [leonerd/libtickit](https://github.com/leonerd/libtickit)

**C — window hierarchy, event integration, and render buffers. Official GitHub mirror.** The upstream site identifies Bazaar as primary and this repository as its GitHub import mirror. [Upstream provenance](https://www.leonerd.org.uk/code/libtickit/).

- **C2:** Nested, overlapping windows and independently replaceable event-loop and terminal-driver interfaces form a reusable toolkit. The source map identifies these boundaries, including mock terminals for tests. [Code map](https://github.com/leonerd/libtickit/blob/master/CODE-MAP).
- **C1, C3:** Render-buffer regions distinguish skipped cells, text, and erase operations; translation, clipping, masking, and a saved-state stack let nested renderers operate independently. Drawing order can differ from the eventual efficient screen-order flush, and intersecting line segments are resolved into the appropriate Unicode junctions. [Render-buffer design](https://github.com/leonerd/libtickit/blob/master/man/tickit_renderbuffer.7).

This is a substantive C implementation, not merely the Perl binding associated with the Tickit ecosystem.

### [ThomasDickey/ncurses-snapshots](https://github.com/ThomasDickey/ncurses-snapshots)

**C — curses implementation, terminfo machinery, and panel/menu/form libraries. Official maintainer snapshot export.** The upstream project links this repository as development history reconstructed from patches and releases; it is not a separate fork of ncurses. [Upstream repository provenance](https://invisible-island.net/ncurses/ncurses.html).

- **C1, C3:** The terminal updater combines wide-character state, cursor tracking, background-erase capabilities, and cost comparisons between erasing, repeating, and emitting characters. The implementation even documents where a cursor-cost estimate is only an upper bound. [Terminal update engine](https://github.com/ThomasDickey/ncurses-snapshots/blob/master/ncurses/tty/tty_update.c).
- **C2, C4:** The monorepo contains the reusable curses/window layer and higher-level panel, menu, and form subsystems. Its dated history documents 2006 reentrancy/static-state work, 2016 terminal and build compatibility fixes, and 2026 screen-state and terminal-description fixes. [NEWS history](https://github.com/ThomasDickey/ncurses-snapshots/blob/master/NEWS).

The internal hacking guide was also inspected; its compatibility-first design and diagnostic workflow help explain why this code carries more historical complexity than newer frameworks.

## Java and C#: layered desktop-style terminal toolkits

### [mabe02/lanterna](https://github.com/mabe02/lanterna)

**Java — terminal access, buffered screens, and a window/widget layer.** An approachable codebase for studying successive abstraction layers and development through an embedded Swing terminal.

- **C2:** The repository explicitly separates low-level `Terminal`, buffered `Screen`, and `gui2` controls. Applications can choose a layer without adopting the complete window toolkit. Its introduction also explains terminal input-profile portability. [Design introduction](https://github.com/mabe02/lanterna/blob/master/docs/introduction.md).
- **C1, C3:** Screen refresh compares the back buffer with the visible screen, while resize notifications are recorded until the application chooses a safe point to resize internal buffers. Keeping dimensions fixed during drawing is an explicit consistency contract. [Buffered-screen guide](https://github.com/mabe02/lanterna/blob/master/docs/using-screen.md).

Some introductory platform discussion is historical; the selection relies on its layer and buffer contracts, not every implementation detail mentioned there as a current guarantee.

### [tui-cs/Terminal.Gui](https://github.com/tui-cs/Terminal.Gui)

**C#/.NET — full widget toolkit and cross-platform driver architecture.** GitHub resolves the former `gui-cs` location to this canonical owner. The inspected development branch is useful for studying a substantial driver redesign.

- **C2, C3:** Component factories assemble input readers, input processors, output buffers, outputs, and size monitors. A dedicated input thread queues events for the UI loop; dirty-region tracking belongs to the output-buffer layer rather than individual platform drivers. [Driver architecture and threading model](https://github.com/tui-cs/Terminal.Gui/blob/develop/docfx/docs/drivers.md).
- **C1:** Concurrency tests exercise writes, rectangle fills, and buffer replacement/resizing from separate threads. They specifically target the hazard of locking on a `Contents` object whose reference can change. This provides concrete material for studying synchronization ownership and regression design; inspecting tests alone does not establish that every concurrent use is supported. [Output-buffer concurrency tests](https://github.com/tui-cs/Terminal.Gui/blob/develop/Tests/UnitTestsParallelizable/Drivers/Output/OutputBufferImplConcurrencyTests.cs).

## Haskell and OCaml: declarative composition

### [jtdaugherty/brick](https://github.com/jtdaugherty/brick)

**Haskell — declarative application framework over Vty.** Study how application state and pure-looking drawing descriptions coexist with event handling, scrolling, and named rendering resources.

- **C2:** An `App` packages drawing and event functions, while combinators express boxes, padding, attributes, and viewports. Applications choose the resource-name type used for cursor locations, extents, and viewport state. [User guide](https://github.com/jtdaugherty/brick/blob/main/docs/guide.rst).
- **C1, C3:** The guide explains bounded event channels as a memory bound with producer-blocking tradeoffs. It also requires unique names within resource namespaces and explicit invalidation of cached Vty images when relevant state or terminal size changes. Those obligations make the interaction between purity, retained state, and performance unusually clear. [Bounded-channel and rendering-cache sections](https://github.com/jtdaugherty/brick/blob/main/docs/guide.rst#bounded-channels).

### [pqwy/notty](https://github.com/pqwy/notty)

**OCaml — pure image-composition and terminal codec foundation.** It offers a different abstraction from a conventional widget tree: immutable descriptions of rectangular images, with Unix and Lwt integration outside the core. It is unarchived, but the API reported its latest repository push as **2024-04-06**; active maintenance is not assumed. [Status metadata](https://api.github.com/repos/pqwy/notty).

- **C2:** Horizontal, vertical, and overlay composition have explicit geometry laws. Transparent `void` regions differ semantically from spaces, and rendering/parsing are separated from environmental I/O. [Core interface and image algebra](https://github.com/pqwy/notty/blob/master/src/notty.mli).
- **C1:** Image constructors reject malformed UTF-8 and control characters. The implementation maps segmented text to terminal-cell positions and represents cropping and composition as structured image nodes, exposing the relationship between Unicode boundaries and geometric operations. [Core implementation](https://github.com/pqwy/notty/blob/master/src/notty.ml).

## Coverage, search process, and limitations

Discovery used 18 distinct live search formulations. Search angles included Rust immediate-mode versus retained views; Python widgets, editing, and event loops; Go Elm-style versus imperative frameworks; React renderers; C/C++ window systems and compositors; Java/.NET toolkits; Zig capability negotiation; Kotlin Compose; Haskell and OCaml composition; Ruby/Perl alternatives; and official ncurses/Tickit mirror provenance. Representative formulations included “terminal UI frameworks architecture Rust ratatui cursive GitHub,” “C C++ terminal user interface library FTXUI notcurses finalcut turbo vision GitHub,” “terminal UI OCaml Notty library image algebra GitHub,” and “ncurses official github mirror Thomas Dickey.” Follow-up searches increasingly returned the same architectural families, individual applications, thin bindings, or newer alternatives without adding a comparably distinct study target to this selection.

Primary verification combined GitHub repository metadata and source-tree listings with direct reads of READMEs, source implementations, regression tests, guides, and dated histories. Star counts were not used as quality evidence. No candidate code was executed, dependencies installed, or large repositories cloned. The evidence supports the stated study topics; it is not a complete audit, a benchmark comparison, or proof that the checked-in tests currently pass.

Important boundaries and exclusions:

- Ratatui and termbox2 are retained for substantive continuation work; their predecessors are not separate entries. Turbo Vision's modern port and the two official mirrors are explicitly identified. The OpenTUI and ncurses monorepos each count once.
- tcell, termbox2, Notty, and the C compositors are intentional foundational inclusions. Pure escape-sequence helpers, styling packages, generated language bindings, and terminal emulators are outside the chosen boundary.
- Bubbles, Rich, Lip Gloss, and similar companion libraries were not added as extra entries to inflate the framework count. Discovered applications and awesome-lists were used only as discovery leads, not evidence of code quality.
- Additional candidates surfaced in Swift, Ruby, Nim, and Rust, including newer declarative frameworks. They were not all subjected to the same depth of verification, so their omission is a coverage limit rather than a judgment that they fail the criteria. This report is strongest across the Python, Go, Rust, C/C++, and JavaScript ecosystems and deliberately adds Kotlin, Zig, Haskell, and OCaml perspectives.
- GitHub archive status and latest push are only repository metadata. C4 is assigned where dated evolution is tied to concrete compatibility, testing, or complexity-management work; recent pushes alone do not earn it.
