# Terminal multiplexers

Research date: **2026-10-09**.

This selection covers 14 GitHub repositories that implement terminal multiplexing: managing multiple terminal processes, arranging their views, or sharing their session state. It includes terminal-native programs, text desktops, a browser client, and the multiplexing subsystem of a larger terminal emulator. Session persistence alone, configuration collections, and thin wrappers are outside this report. Small and historical implementations are included when their mechanisms provide substantial engineering material; inclusion is not a recommendation to deploy every project.

Criteria legend:

- **C1 — Correctness:** difficult state invariants, concurrency, hostile or fragmented input, and failure handling.
- **C2 — Abstractions:** substantial reusable models or interfaces supporting multiple workflows or implementations.
- **C3 — Performance:** concrete resource or latency constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or explicit complexity management.

The criteria below are assessments grounded in the linked primary material. They identify what can be studied, rather than certify that the implementations are free of defects. Source and documentation links double as reading entry points.

## General-purpose terminal-native implementations

### [tmux/tmux](https://github.com/tmux/tmux)

**Language / role:** C; a portable terminal multiplexer with detachable sessions and a scriptable command interface.

Study how interactive commands, scripts, asynchronous jobs, and client lifetimes share one execution model. The particularly useful unit is the command queue: it exposes the machinery behind behavior that looks synchronous at the command line.

- **C1:** Queue entries have separate fired and waiting states; external events resume suspended entries, and an error removes subsequent commands in the same group. Reference-counted command context and client references make ordering and lifetime invariants visible in [cmd-queue.c](https://github.com/tmux/tmux/blob/master/cmd-queue.c).
- **C2:** The same queue supports commands and callbacks, shared target/format context, hooks, and control-mode framing. This is a reusable execution abstraction across many commands, not a collection of unrelated key handlers.
- **C3:** The [CHANGES file](https://github.com/tmux/tmux/blob/master/CHANGES) records concrete control-client pressure problems: bounding buffered replies when a client stops reading, avoiding shutdown hangs, and preventing notifications from appearing inside command-response frames. These are useful examples of resource bounds interacting with protocol correctness. The development changelog also distinguishes compatibility behavior for old and new layout formats; its unreleased section should not be mistaken for a released version.

### [zellij-org/zellij](https://github.com/zellij-org/zellij)

**Language / role:** Rust; a terminal workspace with panes, layouts, and an extensible application structure.

Study the boundary between layout management and terminal emulation, especially when a resize changes both geometry and the interpretation of stored text.

- **C1:** The [grid tests](https://github.com/zellij-org/zellij/blob/main/zellij-server/src/panes/unit/grid_tests.rs) exercise erasure through double-width characters, width preservation, wrapping and unwrapping on resize, saved cursor state, scroll regions, and captured VT-test fixtures. These expose correctness obligations beyond drawing a rectangle around a process.
- **C2:** The [architecture guide](https://github.com/zellij-org/zellij/blob/main/docs/ARCHITECTURE.md) separates screen coordination, terminal panes, scroll/grid state, character styling, boundaries, and PTY input routing. That decomposition supports multiple pane arrangements while keeping terminal state separate from the layout that displays it. Treat this high-level guide as orientation and the current tests as the more concrete reference.

### [Gaurav-Gosain/tuios](https://github.com/Gaurav-Gosain/tuios)

**Language / role:** Go; a terminal window manager and multiplexer built around Bubble Tea, with daemon-owned PTYs.

Study replicated terminal state: the daemon and each client maintain emulators that must converge after attaching, switching workspaces, or recovering from missed output.

- **C1:** The unusually specific [pane rehydration contract](https://github.com/Gaurav-Gosain/tuios/blob/main/docs/REHYDRATION.md) pairs snapshots with stream sequence positions to prevent duplicate replay. It specifies grid, history, cursor, modes, latent drawing state, and the normal screen beneath an alternate screen. It also explains why a route test can miss serialization loss and describes separate wire-fidelity tests.
- **C2:** The [architecture guide](https://github.com/Gaurav-Gosain/tuios/blob/main/docs/ARCHITECTURE.md) separates the window model, workspace/layout logic, PTY layer, compositor, and a terminal interface with alternative emulator backends.
- **C3:** The same guide documents dirty-state rendering, sequence-based cache invalidation, reusable buffers, and off-screen culling. These are inspectable optimization mechanisms; its numerical performance claims were not independently benchmarked here. Some diagrams predate daemon mode, a limitation the guide explicitly acknowledges.

### [aaronjanse/3mux](https://github.com/aaronjanse/3mux)

**Language / role:** Go; an i3-inspired multiplexer with pane movement, resizing, search, and detachable sessions.

This is a smaller alternative for studying a window manager independently of the terminal processes it hosts. Its checked history is sparse, with a July 2026 commit following a long gap; that is not evidence of a sustained current maintenance cadence.

- **C1:** The [fuzz harness](https://github.com/aaronjanse/3mux/blob/master/fuzz/main.go) feeds random data through the ECMA-48 parser and virtual terminal, and launches randomized window-manager operations concurrently while recording states for diagnosis. This directly targets both input handling and structural/concurrency failures, although the harness is not a proof of race freedom.
- **C2:** [wm/universe.go](https://github.com/aaronjanse/3mux/blob/master/wm/universe.go) models workspaces above renderer and pane-factory interfaces. The fuzz harness supplies fake panes and a fake renderer, demonstrating that window operations can be exercised separately from actual PTYs. The decomposition is especially useful for comparing with a monolithic multiplexer.

## Small implementations and deliberately limited scope

### [martanne/dvtm](https://github.com/martanne/dvtm)

**Language / role:** C; a dynamic tiling manager for multiple console applications. Detach/reattach is delegated to abduco rather than implemented here.

Study composition as a complexity-management choice: layout stays in dvtm, persistence belongs to another program, and copy-mode selection can be delegated to an external editor. The repository is not archived, but its release-news list ends in 2016; it should be approached as an established, slowly changing codebase.

- **C1:** [vt.c](https://github.com/martanne/dvtm/blob/master/vt.c) documents the relationship between the visible rows and circular scrollback, including logical iteration across wrapped buffer boundaries. It also contains terminal parsing, alternate state, dirty rows, and platform-specific PTY compatibility code.
- **C2:** [config.def.h](https://github.com/martanne/dvtm/blob/master/config.def.h) registers layout functions and action/key-binding tables. Tiling, grid, bottom-stack, fullscreen, tagging, and navigation reuse this machinery. The abstraction is compact enough to trace without studying a large plugin system.

### [deadpixi/mtm](https://github.com/deadpixi/mtm)

**Language / role:** C with curses; a deliberately small terminal multiplexer. Its README describes the feature set as finished, allowing fixes and compatibility work rather than continued feature expansion.

Study the minimum practical structural model for nested terminal splits and the costs that remain even after removing most user-facing features.

- **C1:** [mtm.c](https://github.com/deadpixi/mtm/blob/master/mtm.c) handles pane closure, focus transfer, recursive tree changes, PTY EOF/error paths, partial writes interrupted by signals, and resizing of both primary and alternate screens. These interactions make useful exercises in lifetime and geometry reasoning.
- **C2:** The same file uses horizontal-split, vertical-split, and view nodes, with parent/child links and per-view terminal state. Recursive operations reuse this model for nested layouts, directional selection, reshape, and cleanup; it is an internal abstraction rather than a public library.

The [manual](https://github.com/deadpixi/mtm/blob/master/mtm.1) is the companion entry point for understanding the intentionally small command surface. This is a study of disciplined scope, not evidence that a small implementation offers every modern terminal capability.

### [prompt-toolkit/pymux](https://github.com/prompt-toolkit/pymux)

**Language / role:** Python; a tmux-like multiplexer built with prompt_toolkit and ptterm.

**Historical / maintenance limitation:** the README explicitly says the project requires maintenance. Its default branch depends on old library versions, and its prompt_toolkit 3 branch only supports standalone operation at the documented state.

- **C2:** [pymux/main.py](https://github.com/prompt-toolkit/pymux/blob/master/pymux/main.py) separates per-client application state from the shared multiplexer and its arrangement/layout models. Clients have independent input/output, color depth, command buffers, and focus state while using common pane-management commands. This is useful for studying composition of a TUI framework with a terminal-hosting application.
- **C3:** That implementation deliberately postpones rendering during output bursts so repainting does not always receive highest priority. The repository candidly describes throughput limitations under heavy output. Together these provide a concrete responsiveness tradeoff rather than an unsupported claim that Python matches a C multiplexer.

## Native Windows and experimental architectures

### [psmux/psmux](https://github.com/psmux/psmux)

**Language / role:** Rust implementation with substantial PowerShell tooling/tests; a native Windows multiplexer using ConPTY and a tmux-like command surface. This is a separate implementation, not a tmux source fork.

Study how a Unix-oriented interaction model maps onto Windows process, console, and handle lifetimes.

- **C1:** The [architecture document](https://github.com/psmux/psmux/blob/master/docs/architecture.md) explains per-session servers, authenticated loopback connections, ordered readiness-file publication, PID plus creation-time checks, and a named mutex for session-name ownership. It also describes making accepted sockets non-inheritable so child processes cannot keep completed connections alive.
- **C3:** Reader, parser, and input-writer responsibilities are separated so a blocked child or busy parser does not monopolize the server loop. [src/pane.rs](https://github.com/psmux/psmux/blob/master/src/pane.rs) additionally shows bounded background warm-spawn concurrency and cancellation during teardown. These are concrete latency/resource mechanisms; no speedup numbers are endorsed here.

The architecture documents compatibility and platform fallbacks, but this relatively new project is not credited with C4 merely for pursuing tmux compatibility.

### [rockorager/prise](https://github.com/rockorager/prise)

**Language / role:** Zig and Lua; a multiplexer targeting modern terminal protocols, built with Ghostty terminal machinery and Vaxis.

**Archived:** GitHub's live repository banner states that the owner archived it on **2026-08-11**. The README's description of active alpha development is stale. Retain it as an architectural study, not as a currently maintained recommendation.

- **C1:** The [architecture document](https://github.com/rockorager/prise/blob/main/ARCHITECTURE.md) separates blocking PTY reads from the server event loop and specifies cleanup of pending render timers. Client surfaces use front/back screen buffers so incoming incremental updates are separated from a stable rendered frame.
- **C3:** Per-PTY nonblocking pipes signal dirty state; a full pipe represents an already-pending notification. The event loop drains signals and coalesces rendering through a timer, while Vaxis performs final screen differencing. This is a small, explicit example of decoupling producer throughput from display frequency.

Its replaceable Lua UI is also interesting, but the selection rests on the documented concurrency and frame-scheduling mechanisms rather than on aspirations in the README.

## Multiplexing inside larger terminal and text-desktop systems

### [wezterm/wezterm](https://github.com/wezterm/wezterm)

**Language / role:** Rust; a terminal-emulator monorepo, counted once here for its **mux/domain subsystem and mux-server integration**.

Study how local and remote terminal processes can appear through one native interface while retaining distinct lifecycle and transport behavior.

- **C2:** [mux/src/domain.rs](https://github.com/wezterm/wezterm/blob/main/mux/src/domain.rs) defines a domain interface for spawning, splitting, moving, attaching, and detaching panes. A local domain can use different PTY systems; higher layers work through pane, tab, window, and domain identities.
- **C1:** The same implementation handles missing targets and recalculates a destination pane index after removing a source pane from the same tab. This is a concrete structural invariant that becomes easy to violate when moving panes across a mutable layout.
- **C3:** The [multiplexing guide](https://wezterm.org/multiplexing.html) describes Unix, SSH, and TLS domains, ownership checks, version compatibility requirements, and optional latency-triggered predictive local echo. These make transport and responsiveness tradeoffs inspectable without conflating GPU rendering with multiplexing performance.

### [directvt/vtm](https://github.com/directvt/vtm)

**Language / role:** C++; a virtual terminal multiplexer and text desktop with multiple client views. Older links under netxs-group lead to this canonical repository; it is one project.

Study a broader model than fixed rectangular panes: a shared text desktop, per-user viewports and focus, nested applications, and gateways between ordinary terminals and a binary display protocol.

- **C2:** The [architecture guide](https://github.com/directvt/vtm/blob/master/doc/architecture.md) distinguishes desktop server, desktop client, gateway, and applet process modes. The same executable supports these roles, with classic terminal applications hosted through gateway/app processes.
- **C1:** The guide spells out multi-client focus, window locking, administrator lifetime, session identity, and disconnection behavior. These are concrete shared-state rules whose implementation and edge cases an engineer can trace.
- **C3:** DirectVT transports structured events/render state to avoid repeatedly interpreting classic escape streams for DirectVT-aware applications. That is an architectural performance rationale, not an independently verified throughput comparison. The guide also identifies platform limitations of GUI rendering.

### [cosmos72/twin](https://github.com/cosmos72/twin)

**Language / role:** C and C++; a text window environment with terminal emulation, overlapping windows, networked clients, and attachable displays.

Study a terminal multiplexer organized like a small display server: windows and applications are distinct from the display backend, and client libraries support more than shell panes.

- **C2:** The [developer/user tutorial](https://github.com/cosmos72/twin/blob/main/docs/Tutorial) explains window management, dynamically loaded terminal/socket modules, client message ports, multiple display drivers, nesting, and display attachment. It provides a concrete model for separating application connections from display connections.
- **C4:** The dated [Changelog.txt](https://github.com/cosmos72/twin/blob/main/Changelog.txt) records work across 2003–2016 on 64-bit portability, keyboard handling, compiler compatibility, library interfaces, mouse failures, and the transition to Unicode-only builds. This is evidence of accumulated compatibility engineering, rather than merely an old repository creation date.

The tutorial and changelog contain historical material and are not complete descriptions of the latest implementation. The current README reports a newer version and additional tested platforms; avoid treating the tutorial's old release header as the current release.

## Remote sharing and browser-based multiplexing

### [tmate-io/tmate](https://github.com/tmate-io/tmate)

**Language / role:** C; a **substantively differentiated tmux fork** for terminal sharing. It is counted separately for its replication protocol and recovery machinery, not for inherited tmux code.

**Operational limitation:** the current README says the public tmate servers shut down in July 2025. Out-of-the-box hosted sharing is unavailable in the documented state; users must configure their own server while a replacement is tracked upstream.

- **C1:** [tmate-encoder.c](https://github.com/tmate-io/tmate/blob/master/tmate-encoder.c) reconstructs reconnection state by resetting the encoder, sending protocol/session information, replaying selected commands, synchronizing layout, and snapshotting pane state. Screens, saved grids, cursor positions, and history limits must agree across the connection.
- **C2:** The same file separates layout, PTY-data, status, copy-mode, command, and snapshot messages. These provide a replication model for remote consumers rather than simply forwarding a single terminal byte stream.
- **C3:** PTY output is chunked, duplicate status updates are suppressed, and reconnect snapshots bound history. The source also admits the cost of sending whole layouts on name changes—useful evidence of an unresolved optimization tradeoff.

### [tuzig/terminal7](https://github.com/tuzig/terminal7)

**Language / role:** TypeScript; a browser/mobile terminal multiplexer client using WebRTC, with SSH fallback on native clients. Persistent remote execution relies on the separate webexec backend; that dependency is not counted as another entry here.

Study multiplexing with client-owned layout and transport-independent terminal channels, rather than a server-rendered character display.

- **C1:** [src/layout.ts](https://github.com/tuzig/terminal7/blob/master/src/layout.ts) handles nested layout replacement, pane deletion, redistribution of neighboring space, proportional resizing, and clamped divider movement. Closure, zoom, focus, and geometry changes interact, making this more substantial than an xterm.js demonstration.
- **C2:** [src/session.ts](https://github.com/tuzig/terminal7/blob/master/src/session.ts) defines common session/channel contracts for connection, reconnection, pane-channel creation, resize, payloads, and failures. Alongside the recursive layout model, this supports multiple transports and client form factors. The interfaces describe obligations; their presence alone does not prove every recovery path is correct.

## Coverage, search process, and limits

Discovery used more than six distinct formulations, including: general tmux/Zellij alternatives; independent Go/Rust/C++ implementations; Python multiplexers; minimal C tilers; detach/reattach tools; text desktops and libcaca-era projects; native Windows/ConPTY implementations; WebRTC/browser clients; Zig and Haskell searches; and i3-style multiplexers. Later searches mostly repeated established projects or surfaced young agent-workspace frontends. Two useful later additions were Prise's frame-scheduling architecture and 3mux's independently testable window manager.

Canonical repository pages were opened for every selection. Public GitHub API metadata also checked the first twelve repositories' identities, default branches, and non-archived status; live GitHub HTML supplied the later Prise archive check. Each retained project has additional implementation or design material actually read. Selected tests were inspected, but no candidate code was run, cloned, or benchmarked. GitHub API rate limiting and occasional web-fetch failures were handled by reading public raw files and repository HTML; the report does not depend on search snippets alone.

Important boundaries and exclusions:

- **GNU Screen** is central to the category, but an official substantive GitHub mirror was not established. Searches led to GNU/Savannah and other-host mirrors. It is omitted under the GitHub-only requirement, not judged technically unworthy.
- **abduco, dtach, and shpool** informed the session-persistence boundary. This report favors implementations that multiplex terminal views or terminal state, and includes dvtm while explaining its composition with abduco.
- **Byobu, tmux configuration managers, session launchers, and theme/plugin collections** were not used to inflate the implementation list. Emulator-only libraries and terminals without a distinct multiplexing subsystem were likewise excluded.
- **Neercs, splitvt, tab-rs, and newer projects such as openmux/hexe** were discovery leads rather than retained entries. This pass did not establish an equally complete combination of scope, provenance, and implementation evidence for each. Their omission is a research limitation, not a blanket quality verdict.
- **Maintenance is uneven.** Prise is explicitly archived; Pymux requests maintenance; mtm intentionally limits evolution. Release age, recent pushes, and star counts were not used as substitutes for the criteria. Tmate's hosted-service shutdown is separate from the availability of its source.

This is a diverse selection guide rather than an exhaustive inventory or a claim that every subsystem in these repositories is exemplary.
