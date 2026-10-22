# Window systems and display compositors

Research date: 2026-10-09.

This selection covers display servers, compositor construction libraries, desktop and embedded compositors, remote window presentation, and the window-management policy layer of X11. It includes 25 repositories, from compact kiosk implementations to desktop infrastructure and OS window-server subsystems. Application GUI toolkits, terminal emulators, configuration collections, and ordinary display-server clients are outside scope. Each linked repository was verified through its GitHub page or public API; the implementation and documentation links below are suggested reading entry points.

The criteria are selection judgments grounded in the cited material, not certifications of correctness or uniformly exemplary code. Development-branch links describe the inspected tree and may change. No candidate code was built or executed, and no performance comparisons were measured.

- **C1 — Correctness:** difficult state invariants, concurrency, numerical semantics, untrusted inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or models that serve multiple policies, platforms, or use cases.
- **C3 — Performance:** concrete rendering, latency, bandwidth, or resource constraints addressed through identifiable architecture.
- **C4 — Evolution:** sustained development with evidence of compatibility management, testing, or controlled architectural change; repository age alone does not qualify.

## Libraries for constructing compositors

### 1. [Smithay/smithay](https://github.com/Smithay/smithay)

**Rust; reusable Wayland compositor components.** Study how a compositor library takes responsibility for protocol state without dictating window placement or rendering policy.

- **C1:** Surface commits have an explicit ordering: validation hooks, application or caching of pending state, synchronized-child updates, and compositor callbacks. Surface roles may be assigned only once during a surface's lifetime. These are protocol invariants rather than merely Rust memory-safety claims. See the [compositor module and state model](https://github.com/Smithay/smithay/blob/master/src/wayland/compositor/mod.rs).
- **C2:** The same module exposes typed per-surface data, double-buffered extensible state, tree traversal, and hooks for protocol extensions. It explicitly leaves drawing and relative window placement to consumers, making the boundary useful for different compositor designs. The [published module documentation](https://smithay.github.io/smithay/smithay/wayland/compositor/index.html) is a navigable API entry point; it describes the same implementation, not independent corroboration.

### 2. [canonical/mir](https://github.com/canonical/mir)

**C++; compositor libraries and shell integration.** A useful study in separating shell policy, scene ownership, protocol frontends, and hardware adaptation.

- **C2:** The architecture routes state changes through Shell while other components observe Scene. Display, input, and rendering platforms are separate adapters, and MirAL shields shell authors from less stable internal interfaces. See the [architecture document](https://github.com/canonical/mir/blob/main/doc/sphinx/contributing/explanation/architecture.md).
- **C1:** The compositor tests exercise reentrant display notifications, scene updates triggered during rendering, repeated start/stop calls, and per-buffer thread ownership. These expose the actual deadlock and lifecycle obligations of multi-output composition. Start with [multi-threaded compositor tests](https://github.com/canonical/mir/blob/main/tests/unit-tests/compositor/test_multi_threaded_compositor.cpp).

### 3. [qt/qtwayland](https://github.com/qt/qtwayland)

**C++ and QML; Qt Wayland Compositor subsystem. Official Qt GitHub mirror.** Counted once despite containing both compositor APIs and a client platform plugin. The repository's [Gerrit configuration](https://github.com/qt/qtwayland/blob/dev/.gitreview) identifies the upstream review project; Qt documents its [GitHub replication process](https://wiki.qt.io/Requesting_New_Repositories).

- **C2:** C++ and QML APIs let an application manager embed a compositor, display client surfaces through Qt Quick, and add custom shell/protocol extensions. This provides a different abstraction level from lower-level compositor libraries. See the [compositor overview](https://github.com/qt/qtwayland/blob/dev/src/compositor/doc/src/qtwaylandcompositor-overview.qdoc).
- **C3:** Client-buffer integrations separate GPU buffer sharing from the shared-memory fallback. The overview explains why fallback copies can become expensive on dense displays or constrained hardware and makes integration selection a first debugging step. The [module README](https://github.com/qt/qtwayland/blob/dev/README) connects buffer and shell integration plugins to that architecture.

### 4. [CuarzoSoftware/Louvre](https://github.com/CuarzoSoftware/Louvre)

**C++; compositor library with overridable object factories.** Particularly useful for comparing a default-rich object-oriented API with Smithay's component approach.

- **C2:** LCompositor owns the event loop and backends and provides virtual object construction plus anticipated-destruction hooks. Consumers override selected surface, input, and output behavior while retaining defaults. Read [LCompositor](https://github.com/CuarzoSoftware/Louvre/blob/main/src/CZ/Louvre/LCompositor.h).
- **C1, C3:** Each initialized output has a rendering thread, but the documented contract serializes user callbacks across those threads. Repaint requests are coalesced, output unplugging tears down rendering resources, and scene rendering can use damage and opaque regions. [LOutput](https://github.com/CuarzoSoftware/Louvre/blob/main/src/CZ/Louvre/Seat/LOutput.h) explains the concurrency contract and why output presentation waits need not stall all other work. These are architectural mechanisms, not a verified throughput advantage over competing libraries.

## Desktop compositors

### 5. [GNOME/mutter](https://github.com/GNOME/mutter)

**C; GNOME display server and compositor library. Official read-only GitHub mirror of GNOME GitLab.** Study the boundaries between hardware rendering, scene-graph composition, and desktop window management.

- **C2:** Cogl handles GPU resources and drawing abstractions; Clutter supplies actors, render nodes, input routing, and animation; Mutter supplies display-server and window-management behavior. The [code overview](https://github.com/GNOME/mutter/blob/main/doc/code-overview.md) maps these subsystems. Some historical X11 descriptions remain in that overview, so it should not alone establish current standalone-X11 support.
- **C1, C3:** The [frame-clock state diagram](https://github.com/GNOME/mutter/blob/main/doc/clutter-frame-scheduling.md) distinguishes scheduled work, one or two dispatched frames, inhibition, presentation, and aborted frames. It is a compact entry into the correctness conditions behind triple buffering and responsiveness.

### 6. [KDE/kwin](https://github.com/KDE/kwin)

**C++ and QML; KDE Plasma's Wayland compositor. Official KDE GitHub mirror; upstream development is on KDE Invent.** The DRM backend makes a strong study of kernel-facing display scheduling and hardware restrictions.

- **C1:** Commit reordering must preserve ordering for shared planes, and output-frame destruction has main-thread ownership requirements. Failed reordered commits can be merged and retested; page-flip timeouts are distinguished from a stalled main thread. These obligations are visible in [drm_commit_thread.cpp](https://github.com/KDE/kwin/blob/master/src/backends/drm/drm_commit_thread.cpp).
- **C3:** The same scheduler merges ready commits and adjusts safety margins to balance missed presentation deadlines against latency. The [DRM/GBM overview](https://github.com/KDE/kwin/blob/master/src/backends/drm/overview.md) explains connectors, planes, atomic testing, modifiers, and multi-GPU buffer constraints. Treat its API-history statements as background and the implementation as the more current guide.

### 7. [swaywm/sway](https://github.com/swaywm/sway)

**C; i3-compatible Wayland compositor.** Study asynchronous clients behind an apparently atomic layout operation.

- **C1:** Sway configures affected clients, waits for their responses or a timeout, and applies the new layout together. Wayland clients acknowledge by serial, whereas Xwayland views require geometry-based matching. The [transaction interface](https://github.com/swaywm/sway/blob/master/include/sway/desktop/transaction.h) states this contract explicitly.
- **C2:** Transactions represent output, workspace, and container states through a common instruction model, including parent/child changes and deferred destruction while transaction references remain. This unifies several layout operations rather than special-casing each command. Read the [transaction implementation](https://github.com/swaywm/sway/blob/master/sway/desktop/transaction.c).

### 8. [niri-wm/niri](https://github.com/niri-wm/niri)

**Rust; scrollable-tiling Wayland compositor.** The canonical repository is under niri-wm, rather than the older YaLTeR owner found in some search results. Study how explicit interaction principles become layout and rendering constraints.

- **C1:** Cross-client transactions use commit blockers, completion notifications, weak references, and deadline timers so an unresponsive client cannot hold a layout indefinitely. The [transaction utility](https://github.com/niri-wm/niri/blob/main/src/utils/transaction.rs) also documents timer-removal races and completion on final-handle drop.
- **C3:** The [design principles](https://github.com/niri-wm/niri/blob/main/docs/wiki/Development%3A-Design-Principles.md) require disabled visual effects to avoid extra rendering, preserve direct scanout when clipping permits it, and distinguish temporary animation cost from continuously active effects. The same document explains focus stability and monitor-reconnection state, making the performance choices understandable in terms of user behavior.

### 9. [pop-os/cosmic-comp](https://github.com/pop-os/cosmic-comp)

**Rust; compositor for the COSMIC desktop.** Study a full desktop consumer of Smithay with explicit backend and timing layers.

- **C1, C3:** [KMS surface timings](https://github.com/pop-os/cosmic-comp/blob/master/src/backend/kms/surface/timings.rs) separate pending and presented frames, track render/submission durations, handle early vblank observations, account for variable refresh, and include a vendor-specific case where submission timestamps cannot support the intended latency optimization. This is concrete numerical and hardware-facing scheduling work.
- **C2:** [Backend initialization](https://github.com/pop-os/cosmic-comp/blob/master/src/backend/mod.rs) separates KMS, X11, and winit paths while feeding common compositor state and seat creation. Its fallback behavior is useful for studying the boundary between nested development sessions and direct hardware operation.

### 10. [mahkoh/jay](https://github.com/mahkoh/jay)

**Rust; independent Wayland compositor with Vulkan/OpenGL rendering.** A less famous implementation worth comparing with the Smithay-based desktop compositors.

- **C1:** The [transaction documentation](https://github.com/mahkoh/jay/blob/master/book/src/configuration/transactions.md) distinguishes waiting for a configure acknowledgment from waiting to display the coordinated result. It explicitly describes the mismatch between immediately updated input geometry and delayed visible geometry, and bounds waits for unresponsive applications.
- **C3:** [Damage handling](https://github.com/mahkoh/jay/blob/master/src/damage.rs) maps regions through rotations, reflections, scaling, and viewports, rounding outward to retain affected pixels. Its optional damage visualization supplies a practical way to inspect repaint behavior. Together these are useful for studying selective repainting without losing edge pixels.

### 11. [hyprwm/Hyprland](https://github.com/hyprwm/Hyprland)

**C++; dynamic tiling Wayland compositor.** The current repository describes an independent compositor; labeling current Hyprland simply as a wlroots frontend would be inaccurate. A manageable starting point is output damage rather than the entire renderer.

- **C1:** Damage is captured in move-only transactions. Commit advances history; rollback, including destruction without commit, restores pending damage. Unknown buffer ages require a full repaint. See [DamageRing.cpp](https://github.com/hyprwm/Hyprland/blob/main/src/output/DamageRing.cpp).
- **C3:** Damage regions are clipped and accumulated across buffer ages. Excessively fragmented damage is replaced with its bounding rectangle only when that rectangle does not add too much area, explicitly balancing draw overhead against unnecessary shading. The [damage-ring tests](https://github.com/hyprwm/Hyprland/blob/main/tests/helpers/DamageRing.cpp) are a second entry point for checking these boundaries.

### 12. [WayfireWM/wayfire](https://github.com/WayfireWM/wayfire)

**C++; extensible wlroots-based compositor with scene transformations and effects.** Study how a plugin-friendly scene graph retains useful repaint and visibility information.

- **C2:** Scene nodes are instantiated as render trees whose instances encapsulate transformations, damage, presentation feedback, and scanout attempts. This lets effects compose without every caller understanding every transformation. See the [scene-render API](https://github.com/WayfireWM/wayfire/blob/master/src/api/wayfire/scene-render.hpp).
- **C1, C3:** That API defines a damage pass, front-to-back instruction scheduling, and reverse-order drawing. Opaque regions remove work; blur can expand damage; direct-scanout results distinguish harmless skipped nodes from occlusion. The [plugin author guide](https://github.com/WayfireWM/wayfire/blob/master/docs/wayfire-plugin-author.md) adds an entry into extending the system and selecting plugin revisions for different Wayfire versions.

### 13. [labwc/labwc](https://github.com/labwc/labwc)

**C; stacking Wayland compositor.** A comparatively compact codebase for studying traditional desktop behavior over asynchronous surface protocols.

- **C1:** [Shared view implementation](https://github.com/labwc/labwc/blob/master/src/view-impl-common.c) documents an Xwayland unmap/focus race and handles resize commits arriving after the mouse button is released. Its geometry fallback is explicitly heuristic, making this an instructive account of imperfect client coordination rather than a proof of universal correctness.
- **C2:** Mapping, first-map rules, foreign-toplevel lifetime, visibility, and geometry application are centralized behind the view implementation interface. Separately, [output-state handling](https://github.com/labwc/labwc/blob/master/src/output-state.c) encapsulates conversion to pending output state and resets it only after successful commit. These boundaries keep protocol and output lifecycle details out of many policy operations.

### 14. [qtile/qtile](https://github.com/qtile/qtile)

**Python plus C; programmable X11 window manager and Wayland compositor.** Study how making the live window system scriptable also makes it testable. The current changelog records a C rewrite of the Wayland backend; older descriptions of an entirely Python Wayland implementation are incomplete.

- **C2:** The [command graph](https://github.com/qtile/qtile/blob/master/docs/manual/commands/command_graph.rst) uniformly addresses windows, groups, layouts, screens, widgets, bars, and backend state. Object traversal underpins interactive control and automation, with defined errors for objects that are not currently present.
- **C4:** The [changelog](https://github.com/qtile/qtile/blob/master/CHANGELOG) records releases across 2021–2026, configuration migrations, deprecation removal, and the backend rewrite. The [testing guide](https://github.com/qtile/qtile/blob/master/docs/manual/hacking.rst) explains nested Xephyr tests driven through the same client API and testing both X11 and Wayland backends. Suggested first entry points are the command graph and testing guide; the changelog supplies evolution evidence.

## Gaming, kiosk, embedded, and alternative display systems

### 15. [ValveSoftware/gamescope](https://github.com/ValveSoftware/gamescope)

**C++; SteamOS session and nested gaming compositor.** GitHub marks this repository as a fork, but its documented evolution from steamcompmgr includes a substantive Wayland/Xwayland and Vulkan architecture, so it is counted as its own project.

- **C3:** The [project overview](https://github.com/ValveSoftware/gamescope/blob/master/README.md) explains direct DRM/KMS presentation, avoiding intermediate X copies, asynchronous Vulkan composition, and the cost of effects that move work onto other GPU queues. It also explains virtual game displays in nested sessions. These mechanisms are retained without adopting numerical latency claims.
- **C1:** [Commit handling](https://github.com/ValveSoftware/gamescope/blob/master/src/commit.cpp) coordinates fence polling, mutex-protected completion lists, destruction, presentation-feedback discard, and Wayland buffer release. It exposes exactly why frame lifetime extends beyond a rendering call.

### 16. [cage-kiosk/cage](https://github.com/cage-kiosk/cage)

**C; focused Wayland kiosk compositor.** A small, real deployment-oriented system for understanding what remains necessary when desktop policy is deliberately restricted.

- **C1:** [View lifecycle code](https://github.com/cage-kiosk/cage/blob/master/view.c) handles map/unmap/destruction, signal-listener removal, scene nodes, previous-view focus restoration, and the exception for Xwayland override-redirect windows. Even a kiosk must coordinate client lifetimes and special window types.
- **C2:** A view implementation interface abstracts activation, geometry, maximization, transient relationships, and destruction across supported window types. [Output handling](https://github.com/cage-kiosk/cage/blob/master/output.c) separately connects output configuration, layout, scenes, and swapchains. This is a useful smaller-scale comparison with desktop compositors, not a general desktop framework.

### 17. [rdkcentral/rdk-window-manager](https://github.com/rdkcentral/rdk-window-manager)

**C++; window management and composition for embedded video devices.** Study the integration layer above Westeros and Essos rather than treating a smart-TV compositor as a desktop with fewer features. The verified development branch is develop.

- **C2:** The [architecture guide](https://github.com/rdkcentral/rdk-window-manager/blob/develop/docs/architecture.md) separates the compositor controller, individual/nested compositors, Essos integration, and Firebolt protocol extensions. It traces both direct embedded composition and framebuffer-backed virtual-display rendering.
- **C1:** The same guide identifies the main rendering thread, application and extension workers, compositor-list locking, per-compositor input/state locks, queued extension events, and ownership of compositor contexts and framebuffers. These are concrete concurrency and lifecycle concerns. The [repository overview](https://github.com/rdkcentral/rdk-window-manager/blob/develop/README.md) supplies subsystem navigation. The documentation is evidence of design intent, not proof that all locking is correct.

### 18. [letoram/arcan](https://github.com/letoram/arcan)

**Zig implementations, C-ABI interfaces, and Lua policy; alternative display/multimedia framework. Official synchronized GitHub mirror.** The README says development moved to self-hosted Fossil while synchronization to GitHub continues. The inspected tree contains Zig engine/shared-memory implementations; older documentation still reflects the project's C implementation history.

- **C2:** The [project architecture overview in the README](https://github.com/letoram/arcan/blob/master/README.md) describes native and nested display-server operation, Lua-controlled environments, a Wayland/Xwayland bridge, and network forwarding. This supports comparison with systems organized entirely around the Wayland protocol.
- **C1, C3:** The [A12 protocol document](https://github.com/letoram/arcan/blob/master/doc/a12.md) specifies channel and stream lifetimes, cancellation, prohibited simultaneous streams, event-category filtering, and interleaving video with other traffic according to interaction priority. It exposes both protocol failure modes and responsiveness tradeoffs. Read code and documentation together: the mirror's language transition makes historical implementation assumptions especially risky.

## X11 composition and window-management policy

### 19. [yshui/picom](https://github.com/yshui/picom)

**C; standalone X11 compositor.** A substantive continuation of Compton, with a renderer organized around explicit commands and damage calculation. It composes windows; a separate window manager supplies placement policy.

- **C1:** [Damage calculation](https://github.com/yshui/picom/blob/next/src/renderer/damage.c) distinguishes changes to window geometry, shadows, command identity, animated shaders, rounded corners, and opacity. Damage must remain conservative even when the visible result changes without new client pixels.
- **C2, C3:** The [backend command representation](https://github.com/yshui/picom/blob/next/src/backend/backend.h) separates blits, blur, masks, symbolic sources, and backend execution. The damage pass removes opaque coverage and combines client damage with rendering-state changes, allowing selective repainting without mixing all backend details into window tracking.

### 20. [XQuartz/xorg-server](https://github.com/XQuartz/xorg-server)

**C and Objective-C; XQuartz development branches of the X.Org server.** Counted for the macOS-specific X server and generic rootless subsystem, not as a second independent copy of upstream Xorg.

- **C2:** The [generic rootless layer design](https://github.com/XQuartz/xorg-server/blob/master/miext/rootless/README.txt) maps top-level X windows to native frames through an implementation interface for creation, drawing, movement, and resizing. This is a substantial compatibility boundary between two window systems.
- **C1, C3:** Backing-buffer addresses may change between drawing sessions; destruction requires drawing to stop and updates to flush; native alpha bits must survive X drawing operations. The design also explains full backing-store memory versus visibility-bookkeeping complexity and thresholds for accelerated operations. [Darwin event handling](https://github.com/XQuartz/xorg-server/blob/master/hw/xquartz/darwinEvents.c) is the companion platform entry point. The rootless design document is historical; its old paths are background rather than current build instructions.

### 21. [i3/i3](https://github.com/i3/i3)

**C with Perl integration tests; X11 tiling window manager.** Included as the policy and client-protocol layer of a window system, not as a pixel compositor.

- **C2:** The [hacking guide](https://github.com/i3/i3/blob/next/docs/hacking-howto) models windows, splits, workspaces, and outputs as containers in a layout tree and maps that representation to command handling, geometry, focus, and IPC. This is useful for studying an inspectable shared model instead of many disconnected layout commands.
- **C1:** The guide describes suppressing configure/enter events caused by the window manager's own changes while publishing stacking order to other clients. Focus must also remain coherent when container orientation and stacking mode change independently: the [stacking-order regression test](https://github.com/i3/i3/blob/next/testcases/t/131-stacking-order.t) checks these transitions. The guide warns that some later sections are outdated; use current tests and source when resolving behavioral details.

### 22. [awesomeWM/awesome](https://github.com/awesomeWM/awesome)

**Lua and C; programmable X11 window-manager framework.** Study an extensible policy system in which layout and configuration are executable abstractions.

- **C2:** [Client-layout documentation](https://github.com/awesomeWM/awesome/blob/master/docs/08-client-layout-system.md) describes layouts per tag, selection across multiple tags, shared layout parameters, and stateful strategies that can mix floating and tiling. This is a reusable policy model rather than one fixed tiling algorithm.
- **C4:** [NEWS](https://github.com/awesomeWM/awesome/blob/master/docs/89-NEWS.md) records four years of the 3.5 API before the 4.0 migration, required changes for extensions, and subsequent 4.3 compatibility work. It also discusses input-handler refactoring and integration-test requirements. The 4.4 section is explicitly a draft and is not treated here as evidence of a completed stable release.

## Remote presentation and OS-native window servers

### 23. [Xpra-org/xpra](https://github.com/Xpra-org/xpra)

**Python and Cython; persistent remote applications and display forwarding.** Included for remote window/display-server infrastructure, not as a conventional local desktop compositor.

- **C1:** The [protocol specification](https://github.com/Xpra-org/xpra/blob/master/docs/Network/Protocol.md) makes record-size validation, decompression limits, typed packet schemas, raw-chunk assembly, capability negotiation, and connection states explicit. These are adversarial-input and state-machine obligations at the display transport boundary.
- **C2, C3:** The [encoding subsystem](https://github.com/Xpra-org/xpra/blob/master/docs/Subsystems/Encoding.md) separates client, server, and per-client connection responsibilities. Codec, colorspace, size, speed/quality, and damage-batching capabilities let the system adapt to different decoders and networks. Study how presentation constraints are negotiated instead of assuming every endpoint can consume the same stream.

### 24. [haiku/haiku](https://github.com/haiku/haiku)

**C++; app_server and drawing subsystem within the Haiku OS monorepo. Official GitHub mirror; review occurs on Haiku infrastructure.** Counted once, specifically for server-side windowing and drawing. It should not be described as a conventional Wayland-style compositor.

- **C2:** [ServerWindow](https://github.com/haiku/haiku/blob/master/src/servers/app/ServerWindow.cpp) is the per-BWindow messaging endpoint and routes requests to Desktop, Window, and View. [DrawingEngine](https://github.com/haiku/haiku/blob/master/src/servers/app/drawing/DrawingEngine.cpp) separates drawing/clipping from the hardware interface and painter. This exposes a window system where the server executes drawing requests rather than only receiving completed client surfaces.
- **C1:** DrawingEngine distinguishes parallel and exclusive access, asserts required lock modes, and constrains dirty regions to clipping. ServerWindow contains explicit lock-order and possible-deadlock comments around event dispatch. Those unresolved comments are part of its study value and a limitation; the entry does not claim those concerns are all solved.

### 25. [SerenityOS/serenity](https://github.com/SerenityOS/serenity)

**C++; WindowServer subsystem within the SerenityOS monorepo.** Counted once. A useful software-composition counterpart to GPU-centered Linux desktop systems.

- **C1, C3:** [Compositor.cpp](https://github.com/SerenityOS/serenity/blob/master/Userland/Services/WindowServer/Compositor.cpp) propagates dirty regions through transparency, separates opaque and transparent painting, checks that flush regions do not overlap incorrectly, and handles devices with and without buffer flipping. It also distinguishes logical coordinates from direct physical-pixel access.
- **C2:** [ConnectionFromClient](https://github.com/SerenityOS/serenity/blob/master/Userland/Services/WindowServer/ConnectionFromClient.cpp) provides the IPC-facing window lifecycle and backing-store layer, leaving composition and window policy in other components. Together these files show how a desktop server organizes client state, shared image storage, occlusion, and output presentation.

## Coverage, search method, and limitations

Discovery used more than six distinct live-search formulations, including: Wayland compositor-library architecture; X11 compositing and damage backends; embedded/Westeros/RDK systems; Rust compositors; alternative display protocols and Arcan; Haiku and Serenity window servers; XQuartz rootless integration; programmable Python/Lua/Haskell window managers; kiosk compositors; C++ compositor factories; Zig display servers; and remote-display architecture. Later language- and role-specific queries increasingly returned already-covered families, configuration projects, prototypes, or third-party mirrors. Louvre and RDK's window manager were useful less-obvious additions from those searches.

All 25 canonical GitHub identities, default branches, and archive flags were checked through the public GitHub API. None of the retained repositories was marked archived at inspection time; this is not a claim about support commitments or release cadence. Additional primary documents or source files were read for every entry. Source-tree inventories were used to verify paths, with a targeted directory query replacing an incomplete large Haiku tree response. No stars were used as quality evidence.

Important boundaries and exclusions:

- The old [swaywm/wlroots repository](https://github.com/swaywm/wlroots) is archived and explicitly points to its GitLab migration. It was excluded as a stale GitHub location, while its ecosystem is represented by substantive consumers. Weston/libweston was searched, but an official substantive GitHub mirror was not established during this research.
- [rdkcmf/westeros](https://github.com/rdkcmf/westeros) is marked deprecated and archived. RDK's current GitHub window-manager code provides a directly relevant retained study instead. This does not imply that Westeros itself ceased development.
- Official project mirrors are flagged for Mutter, KWin, Qt Wayland, Arcan, and Haiku. Arcan explicitly documents continued synchronization after moving development elsewhere. XQuartz is identified as a specialized development branch, and Gamescope/Picom are included for substantive separate evolution rather than counted alongside their ancestors.
- Some project-site pages were blocked or timed out, notably parts of KDE and Haiku documentation. Direct repository sources supplied the implementation evidence. Historical design documents and current code occasionally differ, as called out in the affected entries.
- The list emphasizes open Unix-like and independent OS implementations because proprietary Windows/macOS compositor internals are not available as comparable canonical GitHub projects. X11 policy-only managers are clearly labeled. Experimental language diversity alone was insufficient to retain a project, and OS monorepos were assessed only for their named window-server subsystems.

The report is a reading and selection guide. Criteria summarize grounded engineering inferences from the cited mechanisms; they do not establish complete protocol conformance, security, production readiness, or a ranking of performance.
