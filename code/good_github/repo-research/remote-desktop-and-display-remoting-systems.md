# Remote desktop and display remoting systems

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing remote display protocols, desktop servers and clients, browser gateways, persistent application forwarding, and interactive display streaming. It includes libraries as well as complete systems, and one explicitly bounded case of display transfer between a virtual machine and its local host. The emphasis is on code an experienced engineer can study: protocol state, capture and encoding pipelines, resource ownership, transport adaptation, and desktop integration. Repository identity and category fit were checked against primary sources; each entry also uses implementation material or technical documentation beyond its repository introduction.

Criteria used below:

- **C1 — Correctness:** demanding invariants, concurrency, numerical or pixel semantics, hostile inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and components supporting multiple applications, platforms, protocols, or integration modes.
- **C3 — Performance:** concrete bandwidth, latency, CPU, memory, or GPU constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or explicit management of accumulated complexity.

The criteria are engineering assessments grounded in the cited material, not certifications of security, performance, or uniform code quality. Branch links describe the source inspected and may change after this research date.

## RDP engines and desktop integration

### [FreeRDP/FreeRDP](https://github.com/FreeRDP/FreeRDP)

**Language / role:** Primarily C; reusable RDP implementation, clients, server support, virtual channels, and the WinPR portability layer.

FreeRDP is a useful starting point for understanding how a large protocol implementation separates its core from platform clients and channel extensions. Its connection path exposes the less visible work behind opening a desktop: validating settings, invoking application hooks, loading channels, recovering a connection, and undoing partial initialization.

- **C1:** The [connection implementation](https://github.com/FreeRDP/FreeRDP/blob/master/libfreerdp/core/freerdp.c) coordinates pre/post-connect callbacks, settings checks, abort/error state, channel setup, reconnection, and disconnect cleanup. These paths make lifecycle ordering and incomplete connection attempts concrete study subjects.
- **C2:** The same core operates through contexts and callbacks rather than a particular window toolkit; the repository separates `libfreerdp`, `client`, `server`, `channels`, and `winpr`. The [ChangeLog](https://github.com/FreeRDP/FreeRDP/blob/master/ChangeLog) also illustrates the cross-component consequences of protocol hardening: its 3.32.1 notes describe fixing fragmented static-channel handling after stricter checks disrupted large clipboard transfers.

### [Devolutions/IronRDP](https://github.com/Devolutions/IronRDP)

**Language / role:** Rust; an RDP toolkit divided into protocol, connection, session, channel, and runtime integration crates.

Study IronRDP for an explicit attempt to make protocol code independent of networking and platform policy. The [architecture document](https://github.com/Devolutions/IronRDP/blob/master/ARCHITECTURE.md) explains the crate tiers and their different guarantees rather than presenting the workspace as one undifferentiated SDK.

- **C1:** The core is designed around I/O-free parsing and state transitions, encode/decode cursors, fuzzing, and property-based test support. Keeping the protocol state machine separate from an executor makes malformed inputs and transition behavior inspectable without a live desktop.
- **C2:** Core protocol components feed connection/session layers and separate blocking, Tokio, and other integration adapters. Native, browser/WASM, and language-binding consumers can reuse those layers. The architecture also distinguishes core guarantees from community-maintained components, an important boundary when choosing a subsystem to study.

### [neutrinolabs/xrdp](https://github.com/neutrinolabs/xrdp)

**Language / role:** C; an RDP server for Unix-like systems with separate login/session management and display backends.

xrdp is particularly useful for studying the boundary between a network protocol server and an operating-system session. The repository separates the RDP engine, the main server, `sesman`, a per-session channel service, and Xorg/VNC backend integration.

- **C1:** The maintainers' [v0.10 development account](https://github.com/neutrinolabs/xrdp/discussions/3070) describes session-start failure distinctions, socket ownership changes, and a monitor-resize state machine. These are concrete examples of coordinating authentication, process lifetime, and a changing remote display.
- **C4:** The [NEWS history](https://github.com/neutrinolabs/xrdp/blob/devel/NEWS.md) records earlier clipboard, monitor, and packet-length fixes and testing work. The later v0.10 account explains replacing interprocess communication and moving `sesman` to Unix sockets, including compatibility warnings for old configuration. Together they show evolution with deliberate management of legacy behavior, rather than age alone.

### [GNOME/gnome-remote-desktop](https://github.com/GNOME/gnome-remote-desktop)

**Language / role:** C/GLib; GNOME's remote desktop service. **Official read-only GitHub mirror** of the GNOME GitLab project.

This is a desktop-service integration codebase: FreeRDP and LibVNCServer provide protocol foundations, while PipeWire, libei, and Mutter connect them to capture, input, and session policy. Supported operating modes differ by backend; it should not be read as a claim that every mode works through both protocols.

- **C1:** The [frame-clock implementation](https://github.com/GNOME/gnome-remote-desktop/blob/main/src/grd-frame-clock.c) explicitly manages timer arming, nonblocking timer descriptors, GLib source lifetime, errors, and disposal. Its invariants are a compact example of asynchronous timing inside a larger remote-display service.
- **C3:** The clock schedules monotonic deadlines at frame intervals. The surrounding [source tree](https://github.com/GNOME/gnome-remote-desktop/tree/main/src) separates frame scheduling, damage detection, encoding, and user/system daemon roles, making the latency-sensitive pipeline easier to follow than a single capture-and-send loop.

### [KDE/krdp](https://github.com/KDE/krdp)

**Language / role:** C++/Qt; RDP server library and Plasma remote desktop integration. **KDE's official GitHub mirror**, with development hosted on KDE Invent as linked by the repository.

KRdp offers a contrasting desktop integration: session and capture interfaces feed RDP connection, input, network measurement, and video-stream components. Start with the [source tree](https://github.com/KDE/krdp/tree/master/src), especially the separation between session backends and `VideoStream`.

- **C1:** [VideoStream.cpp](https://github.com/KDE/krdp/blob/master/src/VideoStream.cpp) combines a worker thread, protected frame queues, atomic state, acknowledgments, and owned FreeRDP contexts. It is a concrete study of avoiding unbounded work and unsafe object lifetime across capture and network processing.
- **C3:** The implementation derives an in-flight frame window from measured RTT and production rate, smooths measurements, and uses queue thresholds to pause production. That connects network feedback to encoding pressure rather than merely exposing a fixed frame-rate setting.

## RFB/VNC libraries, servers, and clients

### [LibVNC/libvncserver](https://github.com/LibVNC/libvncserver)

**Language / role:** C; embeddable RFB server and client libraries.

This is a strong library-oriented counterpart to complete desktop applications. An application supplies pixels and input callbacks, while the library manages RFB clients and encoding. The [server programming manual](https://libvnc.github.io/doc/html/libvncserver_doc.html) explains the object model, event-loop options, framebuffer updates, and callback contracts.

- **C1:** Client pixel formats, cursor storage/ownership, and concurrent client-list access are explicit concerns. The documented iterator protocol requires releasing iterators so other threads can safely operate on the list; framebuffer modifications also require correct region notification.
- **C2:** Screen and client objects, keyboard/pointer/clipboard hooks, and blocking, threaded, or externally driven event processing let the same library serve embedded applications, existing displays, and purpose-built graphical systems. These integration contracts are substantial enough to study independently of any one VNC server UI.

### [TigerVNC/tigervnc](https://github.com/TigerVNC/tigervnc)

**Language / role:** C++/C; VNC viewer, X-based servers, and a shared RFB implementation.

TigerVNC is useful for comparing general-purpose VNC encoding policy with more specialized descendants. The relevant subsystem is the shared `common/rfb` implementation and maintained client/Unix server paths; the repository explicitly labels its Windows `winvnc` server unmaintained.

- **C2:** [EncodeManager.cxx](https://github.com/TigerVNC/tigervnc/blob/master/common/rfb/EncodeManager.cxx) coordinates multiple encoder implementations through a common management layer, selecting among raw, palette-oriented, JPEG, Tight, and other encodings according to client capabilities and content.
- **C3:** That manager subdivides update regions, distinguishes solid/indexed/full-color content, and records encoding statistics. It also tracks lossy regions and schedules lossless refreshes. The interesting abstraction is a policy layer over interchangeable encoders, with bandwidth savings tied to framebuffer-region state.

### [TurboVNC/turbovnc](https://github.com/TurboVNC/turbovnc)

**Language / role:** C/C++ server and Java viewer; VNC specialized for image-heavy and interactive visualization workloads.

TurboVNC is a substantive independent evolution of the VNC/TightVNC lineage, especially in its Tight encoder and VirtualGL integration. The [official user guide](https://rawcdn.githack.com/TurboVNC/turbovnc/main/doc/index.html), sections 7.1–7.5, explains implementation tradeoffs unusually clearly.

- **C1:** Automatic lossless refresh tracks regions affected by lossy encoding, including damage propagated by `CopyRect`. The guide explains how unrelated updates such as blinking cursors can prevent an inactivity-triggered refresh and how eligibility rules address that problem.
- **C3:** Interframe comparison keeps a framebuffer copy per viewer and suppresses redundant updates, trading memory and comparison work for reduced encoding/network work. Tight encoding can also divide the screen among workers. The guide explicitly discusses workloads and downstream bottlenecks where those optimizations do not help.

### [novnc/noVNC](https://github.com/novnc/noVNC)

**Language / role:** JavaScript; browser RFB client library and application.

noVNC exposes the protocol engine as an embeddable client rather than requiring its bundled UI. It is especially useful for studying how binary protocol negotiation, asynchronous browser events, canvas display, and remote input fit together.

- **C2:** The [RFB API](https://github.com/novnc/noVNC/blob/master/docs/API.md) defines a connection object with events for credentials, verification, connection state, resizing, and capability changes. Applications can supply their own interface while retaining the same remote-display implementation.
- **C1:** The [RFB tests](https://github.com/novnc/noVNC/blob/master/tests/test.rfb.js) exercise protocol-version interpretation, repeater negotiation, authentication ordering, unsupported security schemes, credential events, and coordinate handling using controlled sockets and browser substitutes. These are observable protocol and event-sequencing invariants, not simply UI smoke tests.

### [any1/neatvnc](https://github.com/any1/neatvnc)

**Language / role:** C; a reusable VNC server library used in the Wayland ecosystem.

NeatVNC provides a relatively compact view of the boundary between display producers, protocol clients, and asynchronous encoding. Its [public header](https://github.com/any1/neatvnc/blob/master/include/neatvnc.h) exposes opaque server, client, framebuffer, display, and layout objects, plus input, authentication, and clipboard callbacks.

- **C2:** The API accommodates different buffer types, transforms, displays, and stream types without embedding a particular compositor or desktop UI into the server library.
- **C1 / C3:** [parallel-deflate.c](https://github.com/any1/neatvnc/blob/master/src/parallel-deflate.c) assigns compression jobs sequence numbers and consolidates completed output only in contiguous order. Mutexes, condition signaling, and explicit buffer ownership make the correctness obligation behind parallel compression visible: workers may finish out of order, but the compressed stream may not.

### [any1/wayvnc](https://github.com/any1/wayvnc)

**Language / role:** C; VNC access to existing or headless wlroots-based Wayland sessions, using NeatVNC.

WayVNC is a compositor-facing server, whereas NeatVNC is the protocol library. This distinction makes both repositories useful without counting one implementation twice. The project's stated compositor scope is wlroots; its README excludes GNOME, KDE, and Weston support.

- **C1:** [screencopy.c](https://github.com/any1/wayvnc/blob/master/src/screencopy.c) handles asynchronous capture states, negotiated buffer capabilities, pool reconfiguration, frame timestamps, allocation failures, and completion/cleanup callbacks. Buffer ownership must survive both successful capture and compositor failure.
- **C3:** The same implementation selects shared-memory or DMA-BUF capture where supported and distinguishes damage-aware copying from full-frame copying. It offers a direct study of how a compositor's capture protocol constrains the downstream VNC pipeline.

### [LibVNC/x11vnc](https://github.com/LibVNC/x11vnc)

**Language / role:** C; sharing an already-running X display through VNC. **Historical study: the repository explicitly says it is unmaintained and seeks a maintainer.**

x11vnc contributes a different problem from a virtual X/VNC server: discovering changes in an existing display while accommodating X extensions, scaling, rotation, and restricted screen regions. It was separated from LibVNCServer and contains substantial capture machinery of its own.

- **C1:** [scan.c](https://github.com/LibVNC/x11vnc/blob/master/src/scan.c) implements scaling between source and destination pixel grids, with distinct strides, interpolation weights, dimensions, and dirty-region coordinates. This exposes numerical and boundary semantics that are easy to overlook in display transport code.
- **C3:** The same module tracks changed tiles and their edges, uses XDamage hints to skip scans, and combines shared-memory capture with polling strategies. It is a useful historical comparison for modern damage and buffer APIs, with its maintenance limitation kept explicit.

## Browser desktop gateways and streaming services

### [kasmtech/KasmVNC](https://github.com/kasmtech/KasmVNC)

**Language / role:** C++/C and JavaScript; browser-oriented desktop server and client derived from VNC implementations.

KasmVNC has substantive separate protocol and encoding development. Its repository explicitly states that it is no longer compatible with ordinary RFB/VNC clients; it should not be treated as an interchangeable server for any VNC viewer.

- **C2:** The [developer API](https://docs.kasmvnc.com/docs/developer_api) exposes session users and permissions, screenshots, and per-connection measurements. It separates owner-level session management from individual viewing connections and supports embedding the server into larger desktop services.
- **C3:** That API distinguishes CPU time from elapsed time for parallel encoding and exposes stages such as analysis, capture, encoding, and client rendering. The [video-streaming documentation](https://docs.kasmvnc.com/docs/video_streaming_mode) further describes codec capability negotiation, hardware/software choices, and the requirement that a skipped frame retain previous client content. These provide concrete entry points into adaptation and observability.

### [apache/guacamole-server](https://github.com/apache/guacamole-server)

**Language / role:** C; `guacd`, `libguac`, and native protocol plugins for Apache Guacamole.

This repository is the native gateway half of Guacamole. Its architectural interest is translating several remote desktop protocols into a common drawing/input protocol that browser code can consume. The [architecture guide](https://guacamole.apache.org/doc/gug/guacamole-architecture.html) describes how `guacd` loads protocol plugins rather than implementing each protocol in the web application.

- **C2:** `libguac` provides connection, user, socket, and rendering abstractions shared by plugins. Native RDP/VNC integration can change independently of the browser-side protocol consumer.
- **C1:** The [libguac programming guide](https://guacamole.apache.org/doc/gug/libguac.html) distinguishes a shared connection from its participating users and specifies join, leave, and final-free lifetimes. Per-user sockets, connection-wide broadcasts, worker activity, and immediate destruction after leave make multi-user resource ownership an important implementation concern.

### [apache/guacamole-client](https://github.com/apache/guacamole-client)

**Language / role:** Java and JavaScript; Guacamole's web application, browser library, tunnels, and extension framework. The monorepo is counted once.

This is a separate implementation layer from `guacamole-server`, not a fork of it. The [JavaScript library guide](https://guacamole.apache.org/doc/gug/guacamole-common-js.html) is a useful entry point for embedding the client independently of the complete web application.

- **C2:** Client, tunnel, display, keyboard, mouse, and touch abstractions isolate transport and browser input concerns from the native remote desktop protocol. Consumers can supply a tunnel and UI while reusing the rendering and input model.
- **C1:** The guide explains streaming HTTP tunnel rollover using coordinated requests, including releasing old response memory while maintaining the instruction stream. It also discusses browser input translation and synthetic mouse events from touch. These details make ordering and input semantics concrete, beyond merely displaying a canvas.

### [selkies-project/selkies](https://github.com/selkies-project/selkies)

**Language / role:** Python orchestration, Rust/PyO3 capture/encoding components, and a JavaScript browser client; remote Linux desktops and applications.

The current [design document](https://github.com/selkies-project/selkies/blob/main/docs/design.md) is important here: the reviewed architecture defaults to WebSocket transport, with optional WebRTC, rather than assuming that historical descriptions of Selkies still describe the current implementation.

- **C2:** The design separates an `aiohttp` service from Pixelflux video capture/encoding, PCMFlux audio capture/encoding, and the browser's decoding path. Native extensions handle specialized work while Python coordinates sessions and integration.
- **C3:** The document explains direct GPU capture/buffer paths where supported, software fallbacks, browser WebCodecs, and transport choices. Its separation of capture, encoding, transport, and orchestration gives engineers identifiable places to investigate copies and latency. These are documented design choices, not independently measured speed claims.

### [myrtille-rdp/myrtille](https://github.com/myrtille-rdp/myrtille)

**Language / role:** C#/.NET Framework and JavaScript, integrating native FreeRDP components; Windows/IIS browser gateway.

Myrtille is useful as a distinct Windows service architecture rather than another container packaging of a Linux gateway. Its [technical documentation](https://github.com/myrtille-rdp/myrtille/blob/master/DOCUMENTATION.md), especially “Code organization” and “Communication,” describes HTTP-session correlation, remote-session processes, and transport between IIS and native components.

- **C2:** WCF service contracts manage remote-process lifecycle, while protocol adapters and browser communication occupy separate layers. This provides reusable boundaries between a hosted web application, privileged/session work, and RDP or SSH backends.
- **C3:** Media and input bypass WCF through named pipes; the documentation explains the FIFO ordering requirement for image data and the consequent same-host constraint. It is an instructive performance/architecture tradeoff, with an explicitly older Windows technology stack rather than an implied claim of current platform portability.

## Persistent applications and graphics remoting

### [Xpra-org/xpra](https://github.com/Xpra-org/xpra)

**Language / role:** Python, Cython, and native integrations; persistent remote applications, desktops, and shadow sessions.

Xpra is valuable for application-level remoting where sessions and windows outlive a particular client connection. Its [encoding documentation](https://github.com/Xpra-org/xpra/blob/master/docs/Usage/Encodings.md) explains a richer policy space than choosing one codec for the entire desktop.

- **C2:** Video encoders, decoders, and colorspace conversion are separate modules, while session/window behavior can serve seamless applications, complete desktops, or existing displays. This makes codec integration reusable across several presentation modes.
- **C3:** Encoding decisions account for window content, client/server capabilities, processing cost, and network conditions. Scroll detection, raw or shared-memory paths, image codecs, video codecs, and refresh behavior address different workloads. The useful study target is how per-window policy coordinates these mechanisms rather than any single compression algorithm.

### [ArcticaProject/nx-libs](https://github.com/ArcticaProject/nx-libs)

**Language / role:** C/C++; NX X11 compression/proxy libraries and the `nxagent` display server.

This is an independent community continuation of the legacy NX 3 codebase, not the source of modern proprietary NoMachine releases. The repository explains its X2Go/QVD/Arctica evolution and compatibility work. Study its `nxcomp` subsystem for protocol-aware X11 transport, alongside `nxagent` for the display-server side.

- **C2:** [Channel.h](https://github.com/ArcticaProject/nx-libs/blob/3.6.x/nxcomp/src/Channel.h) separates transport, encoded buffers, message stores, client/server caches, and several channel traffic types. Those interfaces support more than one fixed pixel-streaming path.
- **C3:** The same source exposes cached message encoding, split transfers, motion-event flushing, congestion handling, and buffer-size-based flush policy. It makes the bandwidth/latency tradeoff in compressing display protocol traffic inspectable at channel boundaries. Historical roadmap text is not treated here as proof that every planned modernization was completed.

### [VirtualGL/virtualgl](https://github.com/VirtualGL/virtualgl)

**Language / role:** C/C++; graphics API interposition and image transport for remotely displaying server-rendered OpenGL applications.

VirtualGL is a graphics-remoting component rather than a complete desktop/session manager. The VirtualGL Project's [technical guide](https://rawcdn.githack.com/VirtualGL/virtualgl/main/doc/index.html) explains the rendering pipeline and how it combines with remote X or VNC systems.

- **C2:** Its interposer redirects relevant GLX/EGL/OpenGL and window-system operations so applications can render on a server GPU while a separate 2D display system handles their windows. GLX and EGL backends and optional image transport make this useful across different remoting arrangements.
- **C1 / C3:** The guide explains offscreen render targets, readback at rendering synchronization points, and EGL-side emulation of buffering behavior. Preserving application-visible graphics semantics while moving the resulting images is a concrete correctness problem; separating GPU rendering from image delivery is the corresponding performance architecture.

## Interactive streaming, direct control, and many-screen operation

### [rustdesk/rustdesk](https://github.com/rustdesk/rustdesk)

**Language / role:** Rust core and Dart/Flutter UI; cross-platform remote desktop control.

RustDesk is a complete system whose repository separates platform capture, codecs, input, clipboard, connection mediation, and the UI. For a focused study, start in the server's display/video service rather than trying to understand the entire application at once.

- **C1:** [video_service.rs](https://github.com/rustdesk/rustdesk/blob/master/src/server/video_service.rs) includes bounded DXGI recovery/restart state, fallback handling, per-display connection tracking, and synchronized shared state. Recovery from capture failure must coexist with clients attached to multiple displays.
- **C2:** The repository's component layout and the same service show capture and encoder abstractions feeding service logic independently of Flutter presentation. Platform-specific recovery can therefore be studied behind a common video service, while rendezvous and relay concerns live elsewhere in the system.

### [LizardByte/Sunshine](https://github.com/LizardByte/Sunshine)

**Language / role:** C++; interactive desktop/game-streaming host for Moonlight clients.

Sunshine belongs here because it captures displays and returns remote input, and its [usage documentation](https://github.com/LizardByte/Sunshine/blob/master/docs/getting_started.md) explicitly describes a Desktop stream that starts without launching an application. It provides a useful contrast to rectangle-oriented RFB systems.

- **C2:** [video.h](https://github.com/LizardByte/Sunshine/blob/master/src/video.h) defines capture/encoder-facing types, memory and pixel-format mappings, conversion operations, and platform encoding-device interfaces. These separate hardware-specific processing from stream configuration.
- **C1 / C3:** The same interfaces represent frame ownership with managed resources, coordinate images across threads, and carry frame-rate, bitrate, color, reference-frame, and slice configuration. The engineering challenge is sustaining an interactive pipeline across heterogeneous capture and hardware-encoding paths while keeping resource lifetime explicit.

### [moonlight-stream/moonlight-common-c](https://github.com/moonlight-stream/moonlight-common-c)

**Language / role:** C; shared GameStream-compatible client protocol implementation used by several Moonlight frontends.

This repository is the reusable network/protocol core, not a platform UI. Paired with Sunshine, it supplies the receiving half of a desktop-capable interactive streaming system.

- **C1:** [RtpVideoQueue.c](https://github.com/moonlight-stream/moonlight-common-c/blob/master/src/RtpVideoQueue.c) handles duplicate and reordered packets, sequence-number wraparound, parity/recovery processing, and frame-level fast-path decisions. Once disorder is observed, the implementation cannot assume that the remainder of that frame arrives in order.
- **C2:** [Limelight.h](https://github.com/moonlight-stream/moonlight-common-c/blob/master/src/Limelight.h) defines decoder/render callbacks, lifecycle guarantees, input operations, and renderer capability contracts. Direct submission and pull-rendering modes impose explicit restrictions, allowing several platform clients to share the protocol without sharing a rendering toolkit.

### [gnif/LookingGlass](https://github.com/gnif/LookingGlass)

**Language / role:** Primarily C/C++; display transfer between a GPU-enabled VM and its local host. **Scope boundary: same-host remoting, not a network RDP/VNC replacement.**

Looking Glass contributes a different architecture: producer and consumer exchange framebuffer data through shared memory. It is relevant when studying display-remoting latency and ownership without a network video encoder in the main transfer path.

- **C1:** [framebuffer.c](https://github.com/gnif/LookingGlass/blob/master/common/src/framebuffer.c) waits on an atomically published write position before reading available chunks, checks size limits, and bounds waiting. Producer progress and consumer reads must remain correctly ordered even while a frame is still being written.
- **C3:** The [KVMFR documentation](https://github.com/gnif/LookingGlass/blob/master/doc/ivshmem_kvmfr.rst) describes shared-memory framebuffer export and direct GPU import. The design moves the optimization target from network compression to memory copies, device mappings, and synchronization between VM and host.

### [veyon/veyon](https://github.com/veyon/veyon)

**Language / role:** C++/Qt; classroom and lab remote monitoring, control, and screen demonstration.

Veyon adds a many-screen management workload: a controller observes multiple machines or broadcasts a demonstration. Its [architecture introduction](https://docs.veyon.io/en/latest/admin/introduction.html) distinguishes the system service, per-session server, master application, workers, and configuration tools.

- **C2:** Service/session separation and feature/platform plugins support remote viewing, control, and demonstration within one system. Workers isolate particular operations or work that must run in a user's context.
- **C3:** The [release notes](https://docs.veyon.io/en/latest/admin/release-notes.html) document a multithreaded demonstration server, adaptive image quality between key frames, asynchronous control processing, and framebuffer update-rate changes. These connect the multi-client workload to explicit scheduling and bandwidth mechanisms rather than relying on generic scalability claims.

## Coverage, search method, and limitations

Discovery used separate live-web formulations for broad remote desktop implementations; RDP engines and state-machine/fuzzing architecture; VNC libraries and encoder internals; Wayland/compositor capture; HTML5 gateways and WebSocket/WebRTC desktops; NX/Xpra application forwarding; GPU/shared-memory and game-derived display streaming; and Windows/IIS and classroom-management systems. Searches also targeted SPICE and Waypipe hosting, official mirrors, source trees, APIs, release notes, and compatibility documents. Later distinct queries increasingly returned already-covered projects, deployment images, thin integrations, unofficial mirrors, or small demonstrations, rather than additional independently substantial implementations.

The resulting spread includes C, C++, Rust, Java, JavaScript, Python/Cython, C#, and Dart-facing systems; library APIs and complete services; network protocol transport and local shared memory; wlroots, GNOME, KDE, Apache, educational, and independent project communities. TigerVNC, TurboVNC, and KasmVNC share ancestry but were retained for their substantive separate encoding, client, and protocol development. NeatVNC/WayVNC and the two Guacamole repositories implement distinct layers rather than duplicate forks. Each monorepo is counted once.

This GitHub requirement leaves a real gap. The [SPICE project's source/download page](https://www.spice-space.org/download.html) directs its principal server, GTK client, and HTML5 sources to freedesktop GitLab; an official substantive GitHub mirror was not established in this search. Waypipe searches likewise did not establish an official GitHub mirror, so downstream copies were not substituted. [rdesktop](https://github.com/rdesktop/rdesktop) was inspected but omitted: its explicit unmaintained status and overlap with the retained RDP engines made it less useful to this selection. x11vnc remains as an explicitly historical study because its existing-X-display scanning machinery adds a distinct implementation angle. Official GNOME and KDE mirrors are labeled above.

Source and documentation inspection was read-only. No candidate was built, benchmarked, security-audited, or exercised against a live remote session, and no dependencies were installed. Test coverage mentioned above describes tests read, not tests executed. Maintenance is not inferred from stars, creation dates, or recent pushes; explicit maintenance limitations are called out, and no blanket claim of active maintenance is made for the list. Performance discussions describe mechanisms and tradeoffs, not independently verified numerical results. This report is a selection guide for further engineering study.
