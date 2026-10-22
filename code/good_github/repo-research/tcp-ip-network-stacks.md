# TCP/IP network stacks

Research date: **2026-10-09**.

This report selects **26 GitHub repositories** containing substantive TCP/IP implementations: portable embedded libraries, native RTOS and general-purpose kernel subsystems, userspace acceleration stacks, and alternative-language or legacy implementations. Specialized accelerators that share responsibilities with the host stack are identified explicitly. OS monorepos count once, for their named networking subsystem. The selection concerns engineering material worth studying; it does not certify protocol completeness, security, production suitability, or uniformly exemplary code.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial input, or failure handling. **C2** — substantial reusable abstractions serving multiple use cases. **C3** — real performance or resource constraints addressed through an understandable architecture. **C4** — sustained evolution demonstrated through compatibility work, testing, or complexity management, rather than age alone. Each entry explicitly supports at least two criteria. Linked implementation files and documentation are reading entry points, not merely discovery snippets.

## Portable and embedded stacks

### 1. [lwip-tcpip/lwip](https://github.com/lwip-tcpip/lwip)

**Language/role:** C; portable embedded IPv4/IPv6 stack. **Official GitHub mirror of the Savannah project**, as identified by its repository description and development instructions.

Study how a small stack exposes TCP directly to applications while retaining socket-style interfaces. The connection lifecycle is particularly instructive: callbacks, advertised receive space, delayed acceptance, and allocation failures all affect whether an application may continue using a protocol control block.

- **C1:** `tcp.c` documents and enforces backlog accounting, core-lock requirements, deferred connection destruction, and the special return contract when aborting from a callback. Close can also be deferred when memory is unavailable. These are concrete ownership and failure-mode problems. [TCP lifecycle and callback implementation](https://github.com/lwip-tcpip/lwip/blob/master/src/core/tcp.c).
- **C2:** The raw callback API separates enqueueing, output, acknowledgement, reception, and application polling; the stack also supports sequential/socket integrations. The upgrade guide explains how packet-buffer abstractions, per-thread completion semaphores, core locking, and compatibility headers evolved together. [Integration and migration guide](https://github.com/lwip-tcpip/lwip/blob/master/UPGRADING).

### 2. [smoltcp-rs/smoltcp](https://github.com/smoltcp-rs/smoltcp)

**Language/role:** Rust; event-driven stack for bare-metal and other environments that may avoid heap allocation.

This is a strong entry point for studying the distinction between safe access to packet bytes and semantically meaningful protocol representations. Its public layers are useful individually, rather than being hidden implementation details of a socket API.

- **C1:** The packet layer provides safe field access, while the representation layer reduces malformed or unsupported packet states. The device layer also provides fault injection. This explicitly separates bounds safety from protocol validity. [Layering and representation design](https://docs.rs/smoltcp/latest/smoltcp/).
- **C2:** Physical devices, interfaces, sockets, storage, and wire representations are exposed as reusable layers; interface-independent socket state machines can be attached to different devices. The same architectural documentation explains these boundaries.
- **C4:** Releases from 2022 through 2026 document retransmission-timer fixes, sequence-overflow fixes, fixture-based testing, API/type migrations, and supported-Rust-version changes. These provide evidence of maintained complexity and compatibility decisions. [Changelog](https://github.com/smoltcp-rs/smoltcp/blob/main/CHANGELOG.md).

### 3. [FreeRTOS/FreeRTOS-Plus-TCP](https://github.com/FreeRTOS/FreeRTOS-Plus-TCP)

**Language/role:** C; scalable TCP/IP library integrated with FreeRTOS, with Berkeley-style sockets.

Study the interaction between a TCP state machine, application wakeups, stream-buffer accounting, and configurable embedded features. It also offers unusually explicit evidence about the scope of automated verification.

- **C1:** The state-handling implementation checks acknowledgement and FIN acceptance against transmit/receive completion, adjusts window scaling after negotiation, and advances stream-buffer tails only for acknowledged bytes. [TCP state handling](https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/blob/main/source/FreeRTOS_TCP_State_Handling.c).
- **C2:** Configurable footprint, portable network interfaces, and socket APIs support both small microcontrollers and larger processors. These are actual integration boundaries, not just protocol names.
- **C4:** The README records 2022 and 2024 LTS inclusion, the V3 split into smaller testable modules, a compatibility-layout generator, and retention of legacy STM32 interfaces during consolidation. It also describes CBMC checking of network-input parsing functions and protocol testing; that is not a claim that the whole stack is formally proven. [Verification and migration documentation](https://github.com/FreeRTOS/FreeRTOS-Plus-TCP/blob/main/README.md).

### 4. [eclipse-threadx/netxduo](https://github.com/eclipse-threadx/netxduo)

**Language/role:** C; ThreadX-integrated dual IPv4/IPv6 stack, now under Eclipse ThreadX.

The packet-oriented receive API makes a useful comparison with byte-stream-oriented socket implementations. Follow how an application receives ownership of a packet while the stack restores advertised window space and coordinates waiting threads.

- **C1:** The receive path protects IP state with a mutex, releases it through carefully defined suspension paths, refuses inappropriate blocking from the IP thread, and updates packet queue markers and counts before returning a packet. Window-update generation incorporates silly-window-syndrome avoidance. [TCP receive implementation](https://github.com/eclipse-threadx/netxduo/blob/master/common/src/nx_tcp_socket_receive.c).
- **C2:** The repository separates the shared network core, architecture/compiler ports, protocol add-ons, and security modules. Its IP instances and packet-based APIs support integration across vendor SDKs and application protocols. [Repository structure and integration documentation](https://github.com/eclipse-threadx/netxduo/blob/master/README.md).

### 5. [Oryx-Embedded/CycloneTCP](https://github.com/Oryx-Embedded/CycloneTCP)

**Language/role:** C; embedded dual IPv4/IPv6 stack with numerous device drivers and application protocols.

Useful for following an explicitly organized protocol implementation: segment processing, state transitions, timers, and miscellaneous TCP operations are separate source units. The receive interface carries a network interface, IP pseudo-header, multipart packet buffer, offset, and ancillary information.

- **C1:** Incoming-segment processing rejects broadcast/multicast destinations where required, validates segment/header availability, and dispatches using socket state. The checks show how RFC requirements meet fragmented buffer access and hostile packet lengths. [TCP finite-state-machine implementation](https://github.com/Oryx-Embedded/CycloneTCP/blob/master/core/tcp_fsm.c).
- **C2:** `NetInterface`, per-interface `NetContext`, `NetBuffer`, and socket objects separate device-specific input from shared TCP logic across IPv4 and IPv6. The same implementation is the starting point for tracing those abstractions; the [core source directory](https://github.com/Oryx-Embedded/CycloneTCP/tree/master/core) exposes the surrounding socket, IP, timer, and buffer components.

### 6. [tass-belgium/picotcp](https://github.com/tass-belgium/picotcp)

**Language/role:** C; small-footprint modular embedded stack. **Historical/infrequently updated reference**: GitHub metadata reported its last push in October 2023 at the research date; it was not marked archived.

Study an implementation that makes queue storage costs unusually visible. Its receive queue stores payload-oriented segments, while output and Nagle holding queues retain other frame representations.

- **C1:** TCP queues maintain tree ordering using sequence-number comparison, byte/frame counters, allocation-failure handling, and optional mutex protection. Enqueueing checks configured capacity before modifying the queue. [TCP implementation](https://github.com/tass-belgium/picotcp/blob/master/modules/pico_tcp.c).
- **C3:** The distinction between an input segment and a complete frame is explicitly motivated by retaining only needed receive data. Bounded queue sizes and separate input/output/holding queues make memory-versus-protocol-behavior tradeoffs inspectable in the same file.

Maintenance evidence: [GitHub repository metadata](https://api.github.com/repos/tass-belgium/picotcp). The observation is about repository activity, not a conclusion that every deployment is unsupported.

### 7. [cesanta/mongoose](https://github.com/cesanta/mongoose)

**Language/role:** C; embedded networking library with its **own built-in TCP/IP stack**, as well as modes that use an external host stack. This entry concerns the built-in implementation, not just its HTTP server.

Study how packet processing, connection buffers, event dispatch, and application protocols fit within one polling-oriented integration model. The distributed amalgamation is large, but its layer functions remain recognizable.

- **C1:** The built-in layer code checks received Ethernet and PPP header lengths before interpreting fields. At the application boundary, the documentation explicitly requires calls from one thread/task because the core is not protected against concurrent access. [Implementation, including built-in link/network processing](https://github.com/cesanta/mongoose/blob/master/mongoose.c).
- **C2:** A common manager/connection/event model serves TCP, UDP, HTTP, MQTT, and WebSocket applications across bare-metal, RTOS, and host-socket configurations. The documentation explains send/receive buffer ownership and the ordering of protocol and application handlers. [Manager, buffer, and event architecture](https://mongoose.ws/documentation/).

## Native RTOS networking subsystems

### 8. [zephyrproject-rtos/zephyr](https://github.com/zephyrproject-rtos/zephyr)

**Language/role:** C; native networking under `subsys/net`, within the Zephyr RTOS monorepo.

Particularly useful for understanding ownership across interrupt, network-worker, and application contexts. Its documentation explains the data path closely enough to map architectural decisions back to buffers and scheduling boundaries.

- **C1:** A packet has exclusive mutable ownership; FIFO handoff transfers it, while shallow clones share reference-counted read-only data. The documentation explicitly distinguishes reference counting from protection against concurrent mutation. [Packet ownership and memory management](https://docs.zephyrproject.org/latest/services/connectivity/networking/api/net_pkt.html).
- **C2:** BSD sockets, network-interface abstractions, and common L2 interfaces connect the same IP/TCP machinery to Ethernet and constrained-network technologies. [Network stack architecture](https://docs.zephyrproject.org/latest/services/connectivity/networking/net-stack-architecture.html).
- **C3:** RX/TX queues separate interrupt work from protocol processing and permit traffic-priority classes; slab-backed packet allocation and bounded buffers expose the RTOS resource budget. These mechanisms are covered by the two entry points above.

### 9. [RIOT-OS/RIOT](https://github.com/RIOT-OS/RIOT)

**Language/role:** C; the GNRC stack, particularly `sys/net/gnrc` and its TCP transport, in the RIOT monorepo.

Study protocol composition through inter-thread messages and registration rather than a single deeply nested call graph. The TCP configuration also makes the costs of implementing reliable streams on constrained devices explicit.

- **C2:** GNRC's protocol registry and communication interface let modules subscribe by protocol/demultiplexing context and exchange packets through a common mechanism. Network-interface, packet-buffer, and socket abstractions support different protocol combinations. [GNRC architecture and packet flow](https://api.riot-os.org/group__net__gnrc.html).
- **C1:** TCP's retransmission calculation exposes smoothed RTT, variance, clock granularity, and bounded timeout values; receive-window capacity and preallocated receive buffers are coupled. The documentation clearly marks dynamic maximum-segment-lifetime behavior as experimental and deviating from the RFC. [TCP configuration and timing semantics](https://api.riot-os.org/group__net__gnrc__tcp__conf.html).

### 10. [apache/nuttx](https://github.com/apache/nuttx)

**Language/role:** C; native `net` subsystem of Apache NuttX, including TCP and BSD sockets.

NuttX is worth studying as a substantially evolved descendant of uIP rather than counting it as another unchanged uIP port. Its own documentation explains that acknowledgement accounting moved to higher layers and that the resulting design can send multiple outstanding segments.

- **C1:** TCP write/read buffering and delayed-ACK interactions expose the relationship among retained application data, acknowledgement, retransmission, and successful completion. The historical design discussion, preserved in the 12.8.0 documentation, should be read with current configuration in mind. [uIP divergence and TCP buffering discussion](https://nuttx.apache.org/docs/12.8.0/components/net/delay_act_and_tcp_perf.html).
- **C2:** The newer network-driver architecture divides generic upper-half work from platform-specific lower-half operations, reducing duplicated receive/transmit machinery; the document explicitly notes that not every driver uses it yet. [Network-driver architecture](https://nuttx.apache.org/docs/latest/components/net/netdriver.html).
- **C3:** That driver guide connects RX quotas, thread priorities, shared I/O-buffer budgets, advertised TCP windows, and out-of-order buffering to backpressure and lossy-link throughput. This is concrete resource-management guidance, not a generic speed claim.

### 11. [contiki-ng/contiki-ng](https://github.com/contiki-ng/contiki-ng)

**Language/role:** C; low-power IPv6/uIP subsystem under `os/net`, with optional TCP, 6LoWPAN, and RPL.

This entry represents the evolved Contiki-NG implementation, not a second copy of the original uIP repository. It offers a contrasting design point to larger socket-oriented RTOS stacks. TCP must be enabled for relevant configurations; a default IoT build need not include it.

- **C1:** `uip6.c` implements TCP sequence-window acceptability, including zero-length segments and zero receive windows, and contains explicit portable checksum arithmetic. It even documents a compiler workaround affecting small-CPU checksum calculation. [IPv6 and TCP implementation](https://github.com/contiki-ng/contiki-ng/blob/develop/os/net/ipv6/uip6.c).
- **C2:** Independently selected MAC, network, and routing components support CSMA, scheduled TSCH, IPv6, and different RPL configurations. Layered configuration files control inclusion and resource bounds, including `UIP_CONF_TCP`. [Stack composition and configuration](https://github.com/contiki-ng/contiki-ng/blob/develop/doc/getting-started/The-Contiki-NG-configuration-system.md).

## General-purpose operating-system stacks

### 12. [torvalds/linux](https://github.com/torvalds/linux)

**Language/role:** C; Linux's networking subsystem, especially `net/ipv4`, `net/ipv6`, and the shared networking core. Linus Torvalds's GitHub source tree is an official publication of the kernel, not a standalone TCP library.

Study the coexistence of protocol correctness and machine-level scaling. Narrow the reading to TCP input/recovery and CPU steering first; the whole networking monorepo is far too broad to assess uniformly.

- **C1:** TCP input distinguishes cumulative ACK progress, SACK information, retransmitted data, loss signals, window updates, and timer changes. The implementation and its development commentary make the interaction among retransmission, sequence accounting, receive capacity, and congestion recovery concrete. [TCP input implementation](https://github.com/torvalds/linux/blob/master/net/ipv4/tcp_input.c).
- **C3:** RSS/RPS/RFS documentation explains hardware versus software steering, per-CPU backlog queues, inter-processor interrupts, cache locality, and queue-count tradeoffs. It also discusses preserving packet ordering when moving processing toward the consuming application. [Scaling in the Linux networking stack](https://docs.kernel.org/networking/scaling.html).

### 13. [freebsd/freebsd-src](https://github.com/freebsd/freebsd-src)

**Language/role:** C; FreeBSD kernel networking in `sys/netinet` and `sys/netinet6`. **Official publish-only GitHub source repository.**

A distinctive study target is the interaction between alternative TCP implementations, precise output pacing, and queued input. This is more informative than treating FreeBSD simply as the historical origin of other stacks.

- **C3:** The high-precision timer system schedules future transport output and coordinates it with queued segments and large-receive-offload behavior. Its source comments explain when a stack should defer ordinary output calls and how pacing avoids unnecessary wakeups. [HPTS design and implementation](https://github.com/freebsd/freebsd-src/blob/main/sys/netinet/tcp_hpts.c).
- **C1:** The same design documents the lock-preserving segment-processing contract: callers must know whether processing kept the connection alive or destroyed its control block. Queued input, reset handling, and timer callbacks therefore share explicit lifetime rules.
- **C2:** Transport function hooks and the separate [TCP stack implementations directory](https://github.com/freebsd/freebsd-src/tree/main/sys/netinet/tcp_stacks) support multiple implementations sharing surrounding kernel networking infrastructure.

### 14. [openbsd/src](https://github.com/openbsd/src)

**Language/role:** C; OpenBSD's `sys/netinet`/`sys/netinet6` networking. **Read-only Git conversion of the project's official CVS source repository.**

Study input validation, reassembly, and the boundary between TCP connection state and socket buffering. This independently evolved BSD implementation is useful beside FreeBSD's pacing-oriented reading path.

- **C1:** Reassembly trims partially overlapping data, drops complete duplicates, handles sequence wraparound, and advances the receive sequence only through contiguous queued segments. Input also contains explicit reset/ACK rate-limit machinery. [TCP input and reassembly](https://github.com/openbsd/src/blob/master/sys/netinet/tcp_input.c).
- **C2:** The same input path serves IPv4 and IPv6 and bridges reusable `mbuf`, connection-control-block, socket-buffer, and network-stack queue abstractions. `tcp_flush_queue` shows the handoff from ordered protocol data to locked socket storage and reader notification. The cited source is a concrete entry point into these boundaries.

### 15. [NetBSD/src](https://github.com/NetBSD/src)

**Language/role:** C; NetBSD's native TCP/IP subsystem. **Official automatic CVS-to-Git mirror**; the repository warns that Git commit links can change, so the links here use the `trunk` branch.

NetBSD adds a particularly useful testing/reuse perspective: kernel networking can be exercised through rump instances connected by virtual interfaces, rather than requiring a complete guest OS for every protocol test.

- **C1:** TCP input connects acknowledgement behavior to path-MTU state, sequence-number comparisons, and address-family-specific neighbor reachability. For example, acknowledgement of referenced data invalidates a pending ICMP-related PMTU indication. [TCP input implementation](https://github.com/NetBSD/src/blob/trunk/sys/netinet/tcp_input.c).
- **C2:** The TCP shutdown tests instantiate a rump server and shared-memory interface, then reuse kernel socket behavior to test operations after shutdown, including bind, connect, listen, and socket options. This demonstrates a substantial reusable kernel/testing boundary rather than a test-only protocol imitation. [Rump-backed TCP shutdown tests](https://github.com/NetBSD/src/blob/trunk/tests/net/tcp/t_tcp_shutdown.sh).

### 16. [haiku/haiku](https://github.com/haiku/haiku)

**Language/role:** C++; Haiku's native TCP implementation under `src/add-ons/kernel/network/protocols/tcp`. The project publishes this GitHub source mirror and directs contributions to its own review service.

An instructive C++ alternative to the C-heavy kernel implementations. Follow `TCPEndpoint` and `BufferQueue` together: one owns connection behavior, while the other distinguishes stored data from the contiguous portion that can be delivered.

- **C1:** Queue insertion removes obsolete or duplicate bytes, trims overlapping segments, and maintains contiguous-byte and sequence boundaries. [TCP buffer queue](https://github.com/haiku/haiku/blob/master/src/add-ons/kernel/network/protocols/tcp/BufferQueue.cpp).
- **C2:** `TCPEndpoint` builds on the protocol-socket abstraction and composes send/receive queues, conditions, routing, and several independent timers. Its destructor cancels and waits for timers, making the interface between reusable timer services and connection lifetime visible. [TCP endpoint implementation](https://github.com/haiku/haiku/blob/master/src/add-ons/kernel/network/protocols/tcp/TCPEndpoint.cpp).

## Userspace isolation and acceleration

### 17. [google/gvisor](https://github.com/google/gvisor)

**Language/role:** Go; the independently reusable `pkg/tcpip` netstack inside the gVisor application-kernel monorepo.

Study how a stack can support a sandbox boundary while remaining usable outside the sandbox. The architectural guide distinguishes packet ingress, transport processing, socket delivery, and batched egress.

- **C1:** Link endpoints run receive goroutines; TCP packets enter asynchronous transport processing, while other protocols may run inline. Egress can originate on several goroutines before reaching the queuing discipline. These boundaries create concrete concurrency and packet-ownership responsibilities. [Netstack architecture and threading](https://gvisor.dev/docs/architecture_guide/networking/).
- **C2:** Interchangeable link endpoints support packet sockets, AF_XDP, shared memory, and Go channels, and the guide explicitly describes standalone reuse. It also says the API does not guarantee stability or conventional Go-module versioning. That qualification matters when treating it as a reusable library.
- **C3:** Batched egress and selectable queuing disciplines provide a clear performance/scheduling design alongside the isolation boundary. The same guide explains the optional host-networking tradeoff.

### 18. [F-Stack/f-stack](https://github.com/F-Stack/f-stack)

**Language/role:** C; a substantively adapted FreeBSD-derived userspace stack over DPDK. Included separately because its process model, integration layer, APIs, and deployment evolution are substantial, not because vendored FreeBSD code is a second independent invention.

Study which assumptions change when a kernel stack becomes a userspace service framework. The development guide describes removal/adaptation of kernel scheduling and locking machinery and its replacement with a multiprocess architecture.

- **C2:** The `ff_*` API, epoll/kqueue integration, microthread interface, and application adapters support different event-driven and stateful server styles. [Development architecture and application interfaces](https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_Development_Guide.md).
- **C3:** Port/core binding and separate process instances seek to reduce scheduling and shared-resource overhead; packet routing between the accelerated path and host kernel is explicit. These are architectural mechanisms, not an endorsement of README benchmark numbers.
- **C4:** Release notes across 2023–2025 and later development record glibc/compiler compatibility fixes, socket-API alignment, imported stack updates, and increasingly complex reload/receive-ownership handling. [Release and compatibility history](https://github.com/F-Stack/f-stack/blob/dev/doc/F-Stack_Release_Note.md).

### 19. [mtcp-stack/mtcp](https://github.com/mtcp-stack/mtcp)

**Language/role:** C; multicore userspace TCP stack with multiple packet-I/O backends. This is the research mTCP, unrelated to Michael Brutman's DOS project of the same name.

Study how per-core state, batched packet I/O, timers, and an epoll-like interface are brought into one processing loop. Treat the published driver/toolchain requirements as part of the artifact's historical context.

- **C3:** The repository requires a one-to-one mapping between RSS queues and configured CPUs. The main loop receives batches, processes packets, services retransmission/TIME_WAIT/connection timers, flushes application events, and sends queued packets. [Core processing loop](https://github.com/mtcp-stack/mtcp/blob/master/mtcp/src/core.c).
- **C2:** An I/O-module interface separates protocol processing from DPDK, PacketShader, netmap, and other supported backends; the application-facing library and internal stack headers are distinct. The core source shows the `iom` dispatch boundary, while the repository README explains backend choices.

**Status:** Research/reference implementation; [repository metadata](https://api.github.com/repos/mtcp-stack/mtcp) showed a July 2024 last push and no archive flag. Current maintenance or compatibility with modern DPDK is not inferred from its older performance results.

### 20. [tcp-acceleration-service/tas](https://github.com/tcp-acceleration-service/tas)

**Language/role:** C; TCP Acceleration Service, a DPDK-based research stack with client libraries and socket emulation.

TAS is distinctive for its explicit fast-path/slow-path service split and its handling of flow movement between processing cores. It is useful for understanding why accelerating TCP requires more than a quick packet parser.

- **C3:** Common flow processing lives in a fast path that prefetches flow state and transmit buffers before queue-manager output. The separate slow path and client/socket layers make the optimization boundary visible. [Developer code map](https://github.com/tcp-acceleration-service/tas/blob/master/doc/devel.rst); the flow implementation below contains the prefetch operations.
- **C1:** The fast flow path locks shared flow state, checks the current steering owner, forwards work if a flow moved cores, clears old queue-manager state, and notifies the destination core. Ring exhaustion and inconsistent queue updates have explicit failure paths. [Fast flow processing](https://github.com/tcp-acceleration-service/tas/blob/master/tas/fast/fast_flows.c).

**Status:** Historical research artifact with documented older DPDK assumptions; [repository metadata](https://api.github.com/repos/tcp-acceleration-service/tas) showed a July 2023 last push, without an archive flag.

### 21. [bytedance/libtpa](https://github.com/bytedance/libtpa)

**Language/role:** C; application-embedded TCP acceleration over DPDK. **Specialized partial-stack scope:** it accelerates selected TCP connections and coexists with the host's networking, rather than replacing every IP/transport service.

Study a run-to-completion design that creates no datapath thread itself, together with the consequences of zero-copy application buffers and userspace process failure.

- **C1:** A zero-copy write buffer must remain alive until acknowledged; zero-copy reads require an explicit completion callback before their packet storage can be reclaimed. The internals also describe a helper daemon that sends resets when an instance dies, addressing connections the host stack does not own. [Ownership and failure handling](https://github.com/bytedance/libtpa/blob/main/doc/internals.rst).
- **C3:** The same guide explains transmit descriptors, external-buffer attachment, worker-local packet pools, and timestamps separating submission from actual transmission. Combined with NIC flow bifurcation, these form an understandable performance architecture.

**Status:** The README's development claims are historical text: [repository metadata](https://api.github.com/repos/bytedance/libtpa) showed a March 2024 last push and no archive flag. Its documented NIC constraints and host-stack dependency should remain part of any evaluation.

### 22. [Xilinx-CNS/onload](https://github.com/Xilinx-CNS/onload)

**Language/role:** C; OpenOnload's userspace TCP/UDP stack, syscall interposition, and supporting kernel modules.

Study the compatibility burden of accelerating existing Linux binaries. Fork/exec behavior, descriptor replacement, blocking calls, process exit, and socket passing make this materially different from stacks with a newly designed application API.

- **C1:** The descriptor table maps operating-system descriptors to userspace state. Its code coordinates duplicate-descriptor operations with blocked calls, signal restart semantics, atomic exit-state updates, and stack locking during teardown. [Descriptor lifetime and synchronization](https://github.com/Xilinx-CNS/onload/blob/master/src/lib/transport/unix/fdtable.c).
- **C2:** The shared library implements network syscalls while kernel support preserves behavior when applications are not scheduled. This serves existing socket applications rather than only purpose-written clients. The [repository overview](https://github.com/Xilinx-CNS/onload/blob/master/README.md) explains this architecture and the distinction between community source-head support and supported packaged releases.
- **C3:** Native Solarflare access and an AF_XDP path expose different hardware integration choices. The README explicitly identifies AF_XDP support as work in progress; no uniform release-readiness claim is made here.

## Alternative-language, unikernel, and legacy designs

### 23. [mirage/mirage-tcpip](https://github.com/mirage/mirage-tcpip)

**Language/role:** OCaml; MirageOS's protocol stack, with direct packet-processing implementations and host-socket implementations behind related interfaces.

Study composable protocol modules and how a functional-language codebase isolates mutable transport state. The direct implementation is the relevant TCP/IP stack; the host-socket implementation is useful for integration and testing, not a second implementation of the host kernel's protocols.

- **C1:** The window module explicitly represents send/receive sequence progress, scaled windows, congestion state, fast recovery, RTT measurement, and retransmission backoff. [TCP window and timing state](https://github.com/mirage/mirage-tcpip/blob/main/src/tcp/window.ml).
- **C2:** IP, ICMP, UDP, and TCP implementations conform to module boundaries, with the direct stack using a `NETIF` device abstraction. This makes device and execution-environment substitution central to the design, as documented in the repository overview.
- **C4:** Changes from 2022 through 2025 document fixes for several connection-close leaks, shutdown-interface changes, virtual-interface test adaptations, and replacement of some time/clock functor parameters with Dune variants. [Compatibility and correctness history](https://github.com/mirage/mirage-tcpip/blob/main/CHANGES.md).

### 24. [includeos/IncludeOS](https://github.com/includeos/IncludeOS)

**Language/role:** C++; native TCP/IP subsystem in the IncludeOS unikernel, primarily `api/net` and `src/net`.

Study an application-facing connection object that exposes asynchronous establishment, reads, writes, disconnect, and final close while encapsulating transport state. It offers a compact comparison with full desktop/server kernel socket machinery.

- **C2:** `Connection` composes packet views, read requests, write queues, RTT measurement, SACK support, timers, and delegate callbacks. These are reusable parts of the stack rather than application-specific handlers. [Connection interface and composition](https://github.com/includeos/IncludeOS/blob/main/api/net/tcp/connection.hpp).
- **C1:** The API distinguishes peer disconnect from the final event after which a connection is unusable, documents failed outgoing establishment, and explains when unread data remains buffered. This makes asynchronous lifetime and backpressure contracts directly inspectable in the same header.

**Scope limitation:** The repository explicitly cautions that its public API should not be considered stable. Its 2026 repository activity was checked; that does not establish the maintenance level of every networking component.

### 25. [GaloisInc/HaNS](https://github.com/GaloisInc/HaNS)

**Language/role:** Haskell; substantive network stack associated with the HaLVM/Xen ecosystem. **Historical reference**, not presented as a currently maintained deployment choice.

Its receive-window code is especially useful for comparing explicit algebraic state transformation with the mutable queues in C implementations. The project goes beyond an echo demonstration: its transport modules include input/output, control blocks, timers, and send/receive windows.

- **C1:** `RecvWindow` states two invariants: queued segments remain within the receive window and do not overlap. It implements trimming, SYN/FIN sequence-space adjustments, overlap resolution, and controlled movement of the receive boundary. [Receive-window representation and invariants](https://github.com/GaloisInc/HaNS/blob/master/src/Hans/Tcp/RecvWindow.hs).
- **C2:** Separate listening, active, and TIME_WAIT control blocks share state, send/receive, timer, and buffering abstractions. The API separates admission-slot management from active connection operations. [TCP control-block abstractions](https://github.com/GaloisInc/HaNS/blob/master/src/Hans/Tcp/Tcb.hs).

**Status:** [Repository metadata](https://api.github.com/repos/GaloisInc/HaNS) showed a January 2018 last push and no archive flag; the README itself marks its Xen example instructions as out of date. Neither type safety nor explicit invariants is a proof of complete TCP correctness.

### 26. [gvanem/Watt-32](https://github.com/gvanem/Watt-32)

**Language/role:** C; Watt-32 TCP/IP library for DOS-family and other supported environments, with traditional socket APIs and samples. GitHub labels this repository a fork of `sezero/watt32`; **only this one representative of the Watt-32 family is counted**.

Study an independently useful legacy portability design, including packet-driver integration and a table-driven TCP state machine. This is not the similarly named mTCP research stack or a modern OS socket wrapper.

- **C1:** TCP states dispatch through a function table; connection establishment handles full listening queues and temporary allocation shortages without replacing the original control block. The state machine also explicitly integrates ARP resolution and BSD-socket callbacks. [TCP state machine](https://github.com/gvanem/Watt-32/blob/master/src/tcp_fsm.c).
- **C2:** The installation guide documents different compiler/runtime targets and real reuse by BSD-style utilities such as netcat, DNS tools, syslog, and file/network measurement programs. This is evidence of a library boundary supporting multiple applications, not merely one bundled demonstration. [Portability and application integration](https://github.com/gvanem/Watt-32/blob/master/INSTALL).

The legacy subject matter should not be confused with an archived repository: GitHub metadata showed activity in June 2026. No claim is made that all documented legacy toolchains were retested recently.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations, including: embedded TCP/IP libraries; Rust and OCaml stacks; multicore userspace TCP; BSD/Linux implementation sources; native RIOT/Zephyr/NuttX/Contiki networking; unikernel stacks; DOS/WatTCP implementations; Haskell protocol stacks; DPDK alternatives; and transparent syscall-compatible acceleration. Follow-up queries targeted architectural documents, packet ownership, TCP state machines, and exact source paths. Later broad searches increasingly returned the same established projects, instructional stacks, and forks. The final acceleration pass added OpenOnload because its syscall-compatibility architecture was a distinct omission; the resulting 26 entries slightly exceed the usual broad-category guide.

Every retained canonical repository URL was opened or checked through the GitHub API. Each entry additionally uses opened/read implementation or architecture material. Where the web reader could not retrieve a source file, public raw GitHub files and directory APIs were read directly. An API rate limit occurred after the main canonical-URL/status checks; remaining source reads used public raw URLs. No candidate code was executed, dependencies installed, or large repositories cloned.

The selection intentionally excludes socket wrappers without their own transport implementation, packet-I/O frameworks by themselves, protocol tutorials/course submissions, awesome lists, and redundant ports of already represented stacks. DOS mTCP search results primarily exposed third-party source copies, so it was not retained without an established official GitHub home. TLDK discovery material described a transport-processing library rather than a complete network stack; it was left out of this selection. Additional BSD/uIP forks are not counted simply for sharing an implementation. F-Stack and NuttX are retained because the inspected primary material documents substantial architectural changes.

Maintenance observations are snapshots, not support guarantees. None of the 25 repositories queried through the GitHub API had the archived flag set; OpenOnload was verified by its live repository page. Nevertheless picoTCP, mTCP, TAS, libtpa, and HaNS have older recorded push dates and are labeled accordingly. Official mirrors and source conversions are identified in their entries. Links generally follow current development branches, so details can change after the research date.

The list spans C, C++, Rust, Go, OCaml, and Haskell, but reflects an ecosystem strongly weighted toward C. It is not exhaustive of router dataplanes, proprietary stacks, hardware TCP offload, or every OS network subsystem. Performance criteria refer to inspected mechanisms, not independently reproduced throughput or latency measurements. Statements about what an engineer can learn are grounded interpretations of those mechanisms; numerical benchmark superiority, complete RFC conformance, and security guarantees are deliberately not inferred.
