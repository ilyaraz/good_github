# Terminal emulators

Research date: 2026-10-09.

This selection covers 26 GitHub repositories implementing terminal emulation: desktop applications, browser terminals, mobile and toolkit components, headless screen engines, a Linux userspace console, and IBM 3270 emulators. It emphasizes parsers, screen-state invariants, rendering, I/O boundaries, and compatibility engineering. Shells, terminal UI frameworks, themes, and simple wrappers are outside the selection. Monorepos are counted once; the relevant subsystem is identified below.

The criteria are evidence-based selection judgments, not certification that every component is exemplary. Implementation and documentation were inspected, but candidate code and benchmarks were not run. Links generally follow the verified default branch and may change after this research date.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial input, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or components serving multiple use cases.
- **C3 — Performance:** concrete resource or latency constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development evidenced by compatibility work, testing, or complexity management across years.

## GPU-oriented desktop implementations

### 1. [alacritty/alacritty](https://github.com/alacritty/alacritty)

**Language/role:** Rust; cross-platform OpenGL terminal application with a separate terminal-engine crate.

Alacritty is useful for studying how a deliberately focused application makes its screen storage efficient without exposing unsafe container operations to the rest of the codebase.

- **C1:** `Storage<T>` distinguishes the physical allocation, logical length, visible rows, and ring origin. It deliberately omits `Deref` because ordinary vector operations could violate its indexing model; equality also requires normalized storage. These are explicit representation invariants, not just a generic buffer abstraction. See [grid storage implementation](https://github.com/alacritty/alacritty/blob/master/alacritty_terminal/src/grid/storage.rs).
- **C3:** The same implementation scrolls by changing the ring origin instead of moving every row, grows storage in batches, and retains a bounded cache of unused rows to reduce allocation churn. The cost model and tradeoffs are explained beside the implementation. The [grid directory](https://github.com/alacritty/alacritty/tree/master/alacritty_terminal/src/grid) also separates resizing, row storage, and tests.

### 2. [kovidgoyal/kitty](https://github.com/kovidgoyal/kitty)

**Language/role:** C, Python, and Go; GPU terminal and extensible terminal environment.

The interesting boundary is between a performance-sensitive terminal engine and programmable layouts, tools, and automation.

- **C2:** The documented design assigns performance-sensitive work to C, application extensibility to Python, and command-line kittens to Go. Layouts, kittens, event watchers, and remote control provide distinct extension surfaces for window management, image tools, and remote workflows. Start with the [design and extension overview](https://github.com/kovidgoyal/kitty/blob/master/docs/overview.rst).
- **C3:** The [performance document](https://github.com/kovidgoyal/kitty/blob/master/docs/performance.rst) explains glyph caching in GPU memory, separating child-program interaction from rendering, SIMD parsing, and configurable batching delays. It explicitly distinguishes throughput, typing latency, and CPU usage, making this a useful study in competing performance goals. Its comparative benchmark rankings are not adopted here.

### 3. [wezterm/wezterm](https://github.com/wezterm/wezterm)

**Language/role:** Rust with Lua configuration; terminal application and multiplexer. Relevant subsystem: `term`.

WezTerm offers an unusually explicit model of positions that survive scrollback changes.

- **C1:** The engine distinguishes physical, visible, scrollback-relative, and stable row indices. The comments explain why stable indices retain their identity when old history is purged and why different integer representations help catch accidental mixing. See the [terminal crate's types and rationale](https://github.com/wezterm/wezterm/blob/main/term/src/lib.rs).
- **C2:** That crate contains parsing, screen state, input encoding, and image-related terminal behavior without prescribing a GUI or owning a PTY. Hosts provide an output writer and feed bytes through `advance_bytes`. This is a concrete reusable engine boundary suitable for applications with different transports and renderers, rather than merely a collection of internal modules.

### 4. [ghostty-org/ghostty](https://github.com/ghostty-org/ghostty)

**Language/role:** Zig with platform-native application code; GPU terminal and terminal core.

Ghostty's paged screen storage is especially valuable for engineers interested in memory ownership and history retention.

- **C1:** `PageList` records whether memory belongs to a pool or an independent allocation; the comments explicitly prohibit inferring ownership from allocation length because doing so can corrupt the pool. Resident versus compressed pages and borrowed versus owned read views have separate representations and destruction rules. See [PageList.zig](https://github.com/ghostty-org/ghostty/blob/main/src/terminal/PageList.zig).
- **C3:** The same source documents demand-paged preallocation, small initial node and pin pools, and compressed pages whose virtual mapping remains reserved so restoration does not need a new virtual allocation. These are concrete memory-versus-access-cost decisions in a terminal screen abstraction. They complement the repository's documented separation of terminal I/O and rendering.

### 5. [raphamorim/rio](https://github.com/raphamorim/rio)

**Language/role:** Rust; desktop/browser terminal with an embeddable C ABI. Relevant subsystems: `rio-vt` and `librio`.

Rio is a useful case study in extracting an application engine for hosts written in other languages.

- **C2:** The [librio design](https://github.com/raphamorim/rio/blob/main/specs/librio.md) separates an engine, individual PTY-owning surfaces, and host-pulled render snapshots. The host supplies rendering and receives a small callback interface; Rust consumers can use `rio-vt` directly while C-compatible hosts use `librio`.
- **C1:** The design specifies panic containment at the C boundary, callbacks that may originate on an I/O thread, input delivery through a channel, and snapshot updates under the terminal lock. These contracts expose the actual lifetime and concurrency issues of embedding a terminal. Per-row dirty flags also make update costs visible to the host. This assessment concerns the documented interface and contracts, not a guarantee that every proposed host integration is shipped.

### 6. [contour-terminal/contour](https://github.com/contour-terminal/contour)

**Language/role:** C++ and Qt/QML; terminal application with dedicated parser, PTY, shaping, model, and rasterizer modules.

Contour is particularly instructive about when architectural separation helps and when it adds cost.

- **C2:** Its [architecture guide](https://github.com/contour-terminal/contour/blob/master/docs/internals/software-architecture/index.md) separates parser events from execution, PTY platform differences from terminal state, and shaping backends from rasterization. The terminal model exposes a render-buffer vocabulary rather than requiring the renderer to own the screen.
- **C3:** The guide explains glyph-atlas ownership and a specific rejected refactoring: moving builders behind a broad context interface would add indirect calls on a per-cell path while holding the state mutex, increasing contention with the parser thread. It also candidly identifies boundaries that are conventions rather than build-enforced layers. This makes it a strong source for studying concrete architectural tradeoffs without assuming perfect modularity.

## Platform integration and established compatibility implementations

### 7. [microsoft/terminal](https://github.com/microsoft/terminal)

**Language/role:** Primarily C++; Windows Terminal and the Windows console host in one monorepo. Relevant subsystems: TerminalCore, TerminalControl, connections, VT parser/adapter, and console host.

The codebase exposes the difficulty of adding modern terminal behavior while maintaining an operating-system console API.

- **C2:** The [code organization guide](https://github.com/microsoft/terminal/blob/main/doc/ORGANIZATION.md) describes a UI-independent terminal core, embeddable controls, interchangeable connection implementations, renderer interfaces, and a parser/adapter split. It also identifies legacy coupling that has not yet been removed.
- **C1:** The same guide maps functional tests for console APIs, CJK handling, and resizing alongside unit tests. The separate [fuzzing guide](https://github.com/microsoft/terminal/blob/main/doc/fuzzing.md) documents an OpenConsole fuzzing build and CI integration. These are concrete responses to malformed streams and compatibility-sensitive state transitions; their presence is not a claim that the entire monorepo is exhaustively tested.

### 8. [gnachman/iTerm2](https://github.com/gnachman/iTerm2)

**Language/role:** Objective-C, Objective-C++, and Swift; macOS terminal application.

The scrollback interface is a productive starting point for understanding how selection, search, rendering, and resizing share one text model.

- **C1:** The [LineBuffer interface](https://github.com/gnachman/iTerm2/blob/master/sources/LineBuffer/LineBuffer.h) distinguishes raw and wrapped lines, tracks dropped characters, exposes double-width-character handling, and documents the cursor's valid position just beyond the final column. Its read interface includes explicit sanity checking and position conversion.
- **C3:** The same interface provides bulk wrapped-line access and retrieves row contents and cache identity in one traversal. Generation plus mutation counters distinguish in-place changes that a generation alone would miss, supporting correct reuse of per-row drawing results. Study these contracts together with the implementation in the [LineBuffer source directory](https://github.com/gnachman/iTerm2/tree/master/sources/LineBuffer).

### 9. [mintty/mintty](https://github.com/mintty/mintty)

**Language/role:** C; native Windows terminal for Cygwin/MSYS environments, with WSL-related integration.

Mintty provides a compact example of sophisticated text storage within a platform-specific terminal.

- **C1:** [termline.c](https://github.com/mintty/mintty/blob/master/src/termline.c) maintains combining-character chains and an internal free list. Cell comparison traverses those chains instead of comparing only the base character, while allocation and destruction preserve a deliberately unusual index-minus-one convention.
- **C3:** The same file uses an RLE-based scrollback representation. Its rationale is specific: historical rows are numerous and rarely modified, so compression prevents additions to the live cell structure from proportionally increasing history memory. This is a useful contrast with paged and uncompressed ring-buffer designs elsewhere in the list.

### 10. [ConEmu/ConEmu](https://github.com/ConEmu/ConEmu)

**Language/role:** C++; Windows console emulator and multi-console host. This is the canonical GitHub location reached from the former `Maximus5/ConEmu` location.

ConEmu is best approached as a compatibility study. Its checked release changelog's newest dated entry is July 2023; this report does not characterize it as a rapidly maintained contemporary terminal.

- **C1:** [ConAnsi.h](https://github.com/ConEmu/ConEmu/blob/master/src/ConEmuCD/ConAnsi.h) exposes handling for multibyte characters split across writes, conversion between code pages, synchronized primary/alternate screen state, and separate pipe threads. These are concrete consequences of bridging ANSI streams and the Windows console model.
- **C4:** The [release changelog](https://github.com/ConEmu/ConEmu/blob/master/Release/ConEmu/WhatsNew-ConEmu.txt) records compatibility and regression work across years: PseudoConsole integration in 2021, line-wrapping corrections in 2022, and title-report filtering fixes in 2022–2023. Its evolution is evidenced by specific behavior changes, not repository age or stars.

### 11. [ThomasDickey/xterm-snapshots](https://github.com/ThomasDickey/xterm-snapshots)

**Language/role:** C; X11 terminal emulator. **Official maintainer-published snapshot export**, rather than the primary development system. The maintainer explains the [RCS-to-GitHub publication process](https://invisible-island.net/personal/git-exports.html).

Xterm is valuable for studying compatibility decisions and their accumulated consequences, even where the implementation carries substantial historical complexity.

- **C1:** [Control-sequence documentation](https://github.com/ThomasDickey/xterm-snapshots/blob/master/ctlseqs.txt) explains modal parsing, recovery, and the distinction between raw C1 controls and UTF-8 continuation bytes. Correct interpretation depends on processing order and encoding state, not simply matching escape strings.
- **C4:** The [dated patch history](https://github.com/ThomasDickey/xterm-snapshots/blob/master/xterm.log.html) spans 1996–2026. Recent entries include variation-selector index fixes, C1 validity checks, signal cleanup, terminfo corrections, and improved character-width test tooling. Together, the compatibility specification and patch record show sustained management of terminal semantics and portability.

## Desktop toolkit engines and the Linux console

### 12. [KDE/konsole](https://github.com/KDE/konsole)

**Language/role:** C++/Qt; terminal application and embeddable KDE component. **Official read-only GitHub mirror**; the [KDE organization identifies its mirror status](https://github.com/KDE), and development is hosted on KDE Invent.

- **C2:** [Emulation.h](https://github.com/KDE/konsole/blob/master/src/Emulation.h) explains the separation among stream decoding, history storage, movable `ScreenWindow` views, and graphical rendering. Multiple consumers can observe screen changes while keyboard translators independently produce bytes for the child process. The repository README identifies embedding in Kate and KDevelop.
- **C1:** [ScreenTest.cpp](https://github.com/KDE/konsole/blob/master/src/autotests/ScreenTest.cpp) exercises block selections after reflow, long-line copying, and both precomposed and decomposed Hangul alongside Japanese text. These tests make the interaction between cell coordinates, Unicode representation, and selection behavior concrete. Prefer these current interfaces and tests to the developer README, which explicitly warns that it dates from 2007.

### 13. [GNOME/vte](https://github.com/GNOME/vte)

**Language/role:** C++ with a GTK-facing API; embeddable terminal widget. **Official read-only mirror** of GNOME's GitLab repository, explicitly identified on the repository page.

- **C1:** The [rewrapping design](https://github.com/GNOME/vte/blob/master/doc/rewrap.txt) works through hard versus soft breaks, double-width characters, tabs, cursor preservation, and different normal/alternate-screen policies. It explicitly identifies cases where perfect reconstruction is impossible or undesirable, making it especially useful for specification work.
- **C2:** VTE packages this behavior as a terminal widget for GTK applications. Internally, [ring.hh](https://github.com/GNOME/vte/blob/master/src/ring.hh) gives scrollback its own representation, with row records, hyperlink management, stream-backed storage support, and marker-aware rewrapping. The public widget boundary and internal storage boundary offer different levels of reusable abstraction; the latter is expressly not a stable public API.

### 14. [lxqt/qtermwidget](https://github.com/lxqt/qtermwidget)

**Language/role:** C++/Qt; embeddable terminal widget. A substantive independent evolution from KDE4 Konsole, not merely a repackaged current Konsole checkout.

- **C2:** [qtermwidget.h](https://github.com/lxqt/qtermwidget/blob/master/lib/qtermwidget.h) exposes local shell startup, a terminal-teletype mode for externally supplied data, configurable history, key/input forwarding, and Qt plugin integration. The API makes local consoles and remote-terminal frontends separate consumers of the same widget.
- **C4:** The [changelog](https://github.com/lxqt/qtermwidget/blob/master/CHANGELOG) documents 2020–2026 work including Qt5-to-Qt6 migration, PTY lifecycle fixes, combining-character support, width calculations, and control-sequence compatibility. This provides direct evidence of continued adaptation and complexity management after the original fork. It is a better target for studying reusable Qt terminal embedding than counting every application built around it separately.

### 15. [kmscon/kmscon](https://github.com/kmscon/kmscon)

**Language/role:** C; userspace Linux console using KMS/DRM and libtsm. The README documents the project's return from the Aetf fork in 2025; that fork is not counted again.

Kmscon broadens the selection to terminals that manage display hardware and seats rather than relying on a desktop windowing toolkit.

- **C2:** [The text-renderer interface](https://github.com/kmscon/kmscon/blob/main/src/render/text.h) separates initialization, font/display setup, preparation, drawing, rendering, and abort. It supports interchangeable renderer implementations; the README documents accelerated, software DRM, and framebuffer configurations.
- **C3:** [terminal.c](https://github.com/kmscon/kmscon/blob/main/src/terminal.c) coordinates screen updates with display swapping, marks work pending when a swap is in progress, and suppresses drawing for inactive sessions or sleeping terminals. This provides a concrete study of scheduling around display constraints. Its distinctive contribution here is device/display integration; libtsm's emulation engine is evaluated separately below.

## Browser and DOM implementations

### 16. [xtermjs/xterm.js](https://github.com/xtermjs/xterm.js)

**Language/role:** TypeScript; browser terminal component with a headless variant and addons.

- **C1:** [EscapeSequenceParser.ts](https://github.com/xtermjs/xterm.js/blob/master/src/common/parser/EscapeSequenceParser.ts) encodes VT parser actions and states in a transition table, including cancellation, string terminators, non-ASCII handling, and state-specific control behavior. It is a concrete alternative to an ad hoc collection of regular expressions.
- **C2:** The repository documents the same component being embedded in editors and terminal applications, with API-based addons for transport, rendering, search, images, and serialization. The headless package can track state for reconnecting clients.
- **C3:** The [flow-control guide](https://xtermjs.org/docs/guides/flowcontrol/) explains bounded event-loop processing, producer backpressure, high/low watermarks, and acknowledgments across WebSockets. Its discussion of overflow and permanently stalled streams is particularly useful for remote-terminal integrators; benchmark figures and historical buffer sizes are not treated as current guarantees here.

### 17. [PerBothner/DomTerm](https://github.com/PerBothner/DomTerm)

**Language/role:** JavaScript with native/backend components; DOM-based terminal emulator and rich REPL console.

DomTerm takes a meaningfully different approach from cell-grid canvas renderers: terminal output lives in a document that can also contain rich HTML and graphics. Its [feature documentation](https://domterm.org/Features.html) describes reflow, hard-newline-preserving copying, and browser/embedded-browser frontends.

- **C1:** [terminal.js](https://github.com/PerBothner/DomTerm/blob/master/hlib/terminal.js) maintains mappings from terminal lines to DOM boundaries, distinguishes local line editing from character input, and preserves serializable session state. Keeping cursor operations, document structure, and application input modes consistent is the central engineering problem.
- **C3:** The same implementation schedules display work through animation frames, limits update deferral, and accounts for received versus acknowledged bytes with paging/replay conditions. These mechanisms address browser rendering and streaming pressure explicitly. The large terminal module is a useful study target, not evidence that every concern is cleanly separated.

## Mobile and cross-platform embedding

### 18. [termux/termux-app](https://github.com/termux/termux-app)

**Language/role:** Primarily Java with native integration; Android terminal application. Relevant subsystems: `terminal-emulator` and `terminal-view`, not the separate package collection.

- **C1:** [TerminalBuffer.java](https://github.com/termux/termux-app/blob/master/terminal-emulator/src/main/java/com/termux/terminal/TerminalBuffer.java) maps logical screen/history coordinates onto a circular buffer. Selection translates cell columns into character-array positions, accounts for wide characters, and treats wrapped trailing spaces differently from ordinary line endings. These distinctions matter directly for correct copied text.
- **C2:** The [Termux Libraries documentation](https://github.com/termux/termux-app/wiki/Termux-Libraries) describes separately consumable emulator, view, and shared libraries, including how third-party apps obtain the terminal components. This makes the project useful for studying Android UI integration around a reusable screen engine rather than treating the whole Linux environment as one indivisible application.

### 19. [migueldeicaza/SwiftTerm](https://github.com/migueldeicaza/SwiftTerm)

**Language/role:** Swift; VT engine with AppKit, UIKit, and headless frontends.

- **C2:** The [repository overview](https://github.com/migueldeicaza/SwiftTerm) distinguishes the UI-independent engine from Apple-platform views and identifies multiple independent application consumers. It also documents its XtermSharp/xterm.js ancestry and a separate 2.0 API migration; this is a substantial port and continuing implementation, not a wrapper around the JavaScript runtime.
- **C1:** [TerminalIOPipeline.swift](https://github.com/migueldeicaza/SwiftTerm/blob/main/Sources/SwiftTerm/TerminalIOPipeline.swift) specifies delegate-buffer lifetimes, synchronized weak references, EOF handling, and shutdown paths that cannot wait on their own worker thread. It explains why closing a PTY beneath a live read is unsafe.
- **C3:** The same pipeline separates gathering from parsing, batches reads into a bounded ring, and uses blocking delivery as backpressure. The explicit lifecycle and scheduling contracts are more instructive than a simple claim of fast rendering.

### 20. [TerminalStudio/xterm.dart](https://github.com/TerminalStudio/xterm.dart)

**Language/role:** Dart; terminal engine and Flutter terminal widget for mobile and desktop applications.

- **C1:** [reflow.dart](https://github.com/TerminalStudio/xterm.dart/blob/master/lib/src/core/reflow.dart) moves anchors as cells migrate between physical lines and prevents a double-width character from being split at the right edge. These are concrete invariants for preserving positions during terminal resizing.
- **C2:** The [integration guide in the README](https://github.com/TerminalStudio/xterm.dart) separates `Terminal` from `TerminalView`, documents a frontend-independent core, and supplies an output callback for connecting a transport. This supports both embedded Flutter terminals and uses of the engine without Flutter rendering.
- **C3:** Reflow has explicit empty-line fast paths and reuses existing line buffers when possible to avoid copying and allocations. The implementation is a small, approachable comparison with the larger native engines. No particular frame rate is endorsed here.

## Headless engines and reusable terminal-state libraries

### 21. [kmscon/libtsm](https://github.com/kmscon/libtsm)

**Language/role:** C; renderer-independent terminal-emulator state machine.

- **C2:** [libtsm.h](https://github.com/kmscon/libtsm/blob/main/src/tsm/libtsm.h) exposes terminal screens, modes, history, selection, and emulation without prescribing fonts or a graphics system. Its documentation explicitly identifies capture and control-code interpretation as additional uses beyond graphical terminals.
- **C3:** [tsm-render.c](https://github.com/kmscon/libtsm/blob/main/src/tsm/tsm-render.c) supplies callbacks and cell/line/screen age information for renderer-side reuse. It combines relevant age values and includes style attributes in glyph identifiers to avoid cache confusion. This is an instructive way to let a reusable model support efficient rendering while keeping graphics dependencies outside the library.

### 22. [selectel/pyte](https://github.com/selectel/pyte)

**Language/role:** Python; in-memory VT-compatible emulator for inspection, scraping, and custom frontends.

- **C2:** [streams.py](https://github.com/selectel/pyte/blob/master/pyte/streams.py) separates a stream state machine and named event dispatch from the receiving screen. `Stream` and byte-oriented input handling serve different integrations; strict attachment checks that a screen implements the required events.
- **C1:** [screens.py](https://github.com/selectel/pyte/blob/master/pyte/screens.py) makes scrolling margins, coordinate conversion, wide-character display, and reset semantics explicit. It even records a VT220-versus-vttest behavior disagreement instead of claiming universal conformance. That candor makes the smaller Python implementation useful for learning how terminal specifications and observed behavior diverge.

The source also exposes dirty rows to callers and documents static event binding as a performance decision, although correctness and reusable separation are the main reasons for inclusion.

### 23. [asciinema/avt](https://github.com/asciinema/avt)

**Language/role:** Rust; headless terminal-state interpreter used by asciinema components.

- **C2:** The [repository overview](https://github.com/asciinema/avt) identifies use by the CLI, player, server, and GIF generator. The scope is deliberately parsing and virtual buffers; keyboard input and rendering are excluded. [vt.rs](https://github.com/asciinema/avt/blob/main/src/vt.rs) exposes feeding, resizing, visible lines, cursor state, changed lines, and drained scrollback through one facade.
- **C1:** The same source checks restoration by dumping terminal state, feeding that representation into another emulator, and comparing states. It includes generated control/escape-sequence inputs and regression checks around changes and scrollback limits. The key study question is whether state serialization preserves behavior and visible state across streaming boundaries.

This is a substantive emulator engine, not merely a terminal recording format or a video player.

### 24. [TragicWarrior/libvterm](https://github.com/TragicWarrior/libvterm)

**Language/role:** C; ROTE-derived VT library with curses-oriented embedding. **Distinct from Paul Evans's similarly named libvterm and Neovim's former fork.**

- **C2:** The [API document](https://github.com/TragicWarrior/libvterm/blob/master/API) separates the opaque terminal object, PTY access, input, offscreen state, and output window. A host can drive I/O from its event loop and choose when to repaint. The [repository overview](https://github.com/TragicWarrior/libvterm) also documents stream-buffer output and embedder-controlled clipboard handling.
- **C1:** The API specifies nonblocking read outcomes, short-write and interruption retries for bulk input, bracketed-paste framing, and the distinction between resizing emulator state and resizing the curses window. Clipboard requests become data/events for the host to interpret, rather than silently controlling the host clipboard.

The API text contains older versioned material alongside newer additions, so check declarations when implementing an integration; the study value is the explicit boundary and failure contracts.

### 25. [charmbracelet/x](https://github.com/charmbracelet/x)

**Language/role:** Go; monorepo entry limited to the `vt` terminal-emulator package. **Experimental API:** the repository explicitly promises no backward compatibility.

- **C2:** [emulator.go](https://github.com/charmbracelet/x/blob/main/vt/emulator.go) composes ANSI parsing, primary/alternate screens, callbacks, terminal replies through I/O pipes, cell access, and styled snapshots. The emulator implements terminal and screen interfaces, making the state machine usable within broader terminal tooling. The unrelated utility packages are not being evaluated here.
- **C1:** The implementation tracks phantom cursor positions and grapheme assembly, bounds parser storage, and keeps mode-dependent width behavior explicit. [safe_emulator.go](https://github.com/charmbracelet/x/blob/main/vt/safe_emulator.go) adds read/write locking around operations such as write, resize, and render. This provides a concrete concurrency boundary to inspect; it is not a blanket guarantee about the lifetime of mutable objects returned to callers.

## Mainframe terminal protocols

### 26. [pmattes/x3270](https://github.com/pmattes/x3270)

**Language/role:** Primarily C with Python test/support code; family of IBM 3270 emulators. The entire family is counted once.

This adds a different protocol and application model from the Unix VT stream tradition.

- **C1:** [Common/telnet.c](https://github.com/pmattes/x3270/blob/main/Common/telnet.c) represents local and remote option state, partial input/suboption buffers, connection timeouts, response requirements, transmission sequence numbers, and TN3270E submodes. Coordinating negotiation with record-oriented terminal operation is a substantial state-machine problem.
- **C2:** The [b3270 manual](https://github.com/pmattes/x3270/blob/main/b3270/b3270.man) documents a frontend-independent host-access backend: it handles 3270, Telnet, and TLS while exchanging XML with a separate UI through standard input/output. The broader source tree shares implementation among graphical, console, and scripting-oriented family members. This is a particularly useful example of a protocol engine reused through a process boundary rather than only a linked library.

## Coverage, search process, and limitations

Discovery used live web searches followed by repository-page or GitHub API verification and direct reading of implementation/documentation sources. Meaningfully different search formulations covered:

- GPU terminal architecture: Alacritty, kitty, WezTerm, Ghostty, Rio, and Contour.
- Browser emulation, DOM representation, parser hooks, and stream backpressure.
- Qt/C++ terminal widgets and GTK/KDE official mirrors.
- Windows console architecture, Cygwin terminals, and ConEmu compatibility.
- Android terminal buffers and reusable Termux libraries.
- Swift and Flutter terminal engines, resizing, and embedding APIs.
- Headless Python/Rust/C/Go engines, libtsm, and virtual-terminal capture.
- KMS/DRM consoles and the availability of authoritative GitHub mirrors for Wayland terminals.
- IBM 3270/TN3270 implementations and frontend-independent backends.
- Repository moves, forks, archives, release histories, and maintainer-published source snapshots.

Later searches increasingly returned thin xterm.js wrappers, frontend reskins, duplicate forks, and projects with insufficient implementation evidence; these did not justify expanding the selection further. The extra entry beyond the usual 25-project guide preserves xterm's distinct compatibility and historical value.

Important boundaries and exclusions:

- **Official mirrors are labeled:** GNOME VTE and KDE Konsole remain substantive GitHub mirrors; xterm is the maintainer's snapshot export. Mirror visibility does not imply that development or contribution handling occurs on GitHub.
- **Moved/archive handling:** [neovim/libvterm](https://github.com/neovim/libvterm) was inspected and excluded as a separate recommendation: it is archived, and its README says the implementation moved into Neovim. The unrelated ROTE-derived library above is explicitly distinguished.
- **Non-GitHub upstreams:** Searches for foot found Codeberg upstream references and unofficial GitHub copies; no authoritative GitHub mirror was established, so it was omitted. The same conservative GitHub-evidence requirement limits coverage of some traditional and Chromium-associated terminals. This is not a finding that those projects lack engineering merit.
- **Avoiding duplicate layers:** QTermWidget's independent evolution is documented; kmscon and libtsm are retained for different integration and engine concerns. Individual shells, recording frontends, terminal themes, raw PTY helpers, and every application embedding xterm.js are not counted as separate emulators.
- **Maintenance and evidence limits:** Archive status and canonical paths were checked through repository pages/API. All retained repositories were unarchived at inspection, but that alone is not evidence of active maintenance. C4 is claimed only where dated compatibility/change evidence was read. ConEmu's older release history and Charm's experimental API are called out explicitly. No star counts, unsupported performance multipliers, or creation dates were used as quality criteria.

The suggested study angles are grounded interpretations of the cited designs and code. They do not establish complete protocol conformance, absence of vulnerabilities, suitability for every integration, or superiority in a particular workload.
