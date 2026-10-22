# VPN implementations and encrypted tunnels

Research date: **2026-10-09**

This report selects **24 GitHub repositories** implementing VPN protocols, encrypted mesh networks, reusable VPN engines, or encrypted application tunnels. It covers both packet-oriented VPNs and connection-oriented tunnels; each entry identifies which it is. Management dashboards, configuration generators, deployment scripts, and ordinary unencrypted proxies are outside the selection. The linked implementation and documentation files are suggested reading entry points.

Criteria are engineering judgments grounded in the cited primary material:

- **C1 — Difficult correctness:** protocol invariants, concurrency, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting multiple integrations or operating modes.
- **C3 — Performance with structure:** concrete throughput, latency, memory, or resource constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility work, testing, or deliberate complexity management.

Every retained repository was checked through its GitHub page or GitHub API, and implementation material beyond its top-level README was read. These are study selections, not security certifications or claims that every component is exemplary. Default-branch links describe the inspected development code and may change; development-branch and mirror caveats appear where relevant.

## Established VPN protocols and independent implementations

### 1. [OpenVPN/openvpn](https://github.com/OpenVPN/openvpn)

**Language/role:** C; OpenVPN client/server daemon.

Study how a TLS control channel coordinates a separate encrypted packet channel, including roaming peers, key selection, and optional kernel acceleration.

- **C1:** The documented receive path selects a session using packet opcode and key ID, checks that the session is active and authenticated and that the sender is appropriate, and then supplies the data-channel cryptographic parameters. Control packets instead enter session negotiation and a reliability layer. This is a concrete boundary between unauthenticated routing information and authenticated session state. See [`src/openvpn/ssl.h`](https://github.com/OpenVPN/openvpn/blob/master/src/openvpn/ssl.h).
- **C3:** Data-channel offload moves packet processing into the kernel while retaining userspace control. The documentation explains automatic fallback for incompatible options and the changed routing semantics, including reliance on kernel routes and a restricted feature set. Study the explicit performance/compatibility boundary in [`README.dco.md`](https://github.com/OpenVPN/openvpn/blob/master/README.dco.md).

### 2. [OpenVPN/openvpn3](https://github.com/OpenVPN/openvpn3)

**Language/role:** C++; reusable OpenVPN client library, distinct from the C daemon above. It does not implement an OpenVPN server.

This is a useful comparison with OpenVPN 2: the protocol family is shared, but the integration boundary is a client SDK with application and platform callbacks.

- **C2:** `OpenVPNClient` combines tunnel construction, logging, external transport factories, and external PKI integration. Applications can supply operating-system tunnel behavior and certificate signing without replacing the protocol engine. See the [`client API`](https://github.com/OpenVPN/openvpn3/blob/master/client/ovpncli.hpp).
- **C1:** The same API specifies lifecycle and concurrency contracts: configuration and credentials precede `connect()`, connection callbacks run on its worker thread, and stop/pause/resume/reconnect operations may arrive from other threads. Socket protection also prevents the VPN's own transport from being routed back into its tunnel. These are valuable integration invariants, not merely convenience methods. The [`repository overview`](https://github.com/OpenVPN/openvpn3#openvpn-3-client-api) explains the client-only scope and wrapper.

### 3. [robur-coop/miragevpn](https://github.com/robur-coop/miragevpn)

**Language/role:** OCaml; independent OpenVPN protocol implementation usable in MirageOS unikernels.

Study a functional protocol engine whose effects are explicit, rather than embedded inside socket callbacks. The project also documents a standalone unikernel server deployment in its [server handbook](https://robur-coop.github.io/miragevpn-handbook/miragevpn_server.html).

- **C2:** The core exposes an abstract connection state and an event/action interface. `handle` consumes events such as incoming data, timer ticks, and connection failures, then returns a new state, outbound packets, application payloads, and an optional action. This lets different runtimes drive the same protocol logic. See [`src/miragevpn.mli`](https://github.com/robur-coop/miragevpn/blob/main/src/miragevpn.mli).
- **C1:** The interface makes unsuccessful states visible: sending before establishment yields `Not_ready`, incoming processing returns typed errors, and server construction accepts an address-availability callback to prevent address collisions. Configuration parsing and pushed-option merging are separately represented, making protocol and configuration failure boundaries inspectable in that interface.

### 4. [strongswan/strongswan](https://github.com/strongswan/strongswan)

**Language/role:** C; IPsec/IKE implementation, with the `libcharon` key-management subsystem particularly relevant.

This is a strong study in making a concurrent protocol daemon manageable without requiring every security-association object to be independently thread-safe.

- **C1:** The IKE security-association manager gives a checked-out association exclusive ownership by one thread. It detects duplicate initial requests, provides atomic check-in/destruction, counts half-open associations, and documents an ordering condition needed to avoid deadlock during uniqueness checks. See [`ike_sa_manager.h`](https://github.com/strongswan/strongswan/blob/master/src/libcharon/sa/ike_sa_manager.h).
- **C2:** The daemon architecture separates the job processor, scheduler, sender/receiver, association manager, configuration, credentials, kernel interface, and event bus. Scheduled jobs enter the shared processor rather than executing inside the scheduler. The diagram and explanation in [`daemon.h`](https://github.com/strongswan/strongswan/blob/master/src/libcharon/daemon.h) make these reusable boundaries unusually accessible.

### 5. [libreswan/libreswan](https://github.com/libreswan/libreswan)

**Language/role:** C; IKEv1/IKEv2 implementation for IPsec, centered on the Pluto daemon. A substantive descendant of Openswan/FreeS/WAN, with its own continuing evolution.

Study a protocol implementation that makes exchange transitions, expected payloads, and operational interoperability central concerns.

- **C1:** Pluto's IKEv2 state machinery distinguishes missing, excessive, and unexpected payloads and represents transitions for initial authentication and rekeying of both IKE and child associations. Its exchange diagrams connect RFC messages to implementation state. See [`ikev2_states.c`](https://github.com/libreswan/libreswan/blob/main/programs/pluto/ikev2_states.c).
- **C4:** The inspected [`CHANGES`](https://github.com/libreswan/libreswan/blob/main/CHANGES) spans multiple years with specific compatibility and regression work: 2022 entries cover Android certificate interoperability, rekey/liveness races, replay-window arithmetic, and KDF self-tests; 2024–2026 entries continue regression fixes and malformed-input fixes, including added security regression tests. This supports sustained complexity management rather than merely an old repository creation date.

### 6. [SoftEtherVPN/SoftEtherVPN](https://github.com/SoftEtherVPN/SoftEtherVPN)

**Language/role:** Primarily C; multiprotocol VPN server/client and virtual Ethernet infrastructure.

The selected repository is the **Developer Edition**, which explicitly contains experimental changes; its separate stable edition is not counted again. Study the Cedar communication subsystem and its shared virtual-hub model.

- **C2:** The project implements several VPN protocols within one server. Cedar's hub model brings sessions, user/group databases, certificate trust, access lists, and packet adapters together, illustrating how heterogeneous protocol front ends can share virtual-network services. See the [edition/protocol overview](https://github.com/SoftEtherVPN/SoftEtherVPN#softether-vpn) and [`src/Cedar/Hub.h`](https://github.com/SoftEtherVPN/SoftEtherVPN/blob/master/src/Cedar/Hub.h).
- **C3:** The hub interface exposes bounded flooding queues, upload/download traffic limiters, broadcast-storm records, MAC-entry aging, and session limits. These are concrete resource-control mechanisms for virtual Ethernet, with the performance and overload concerns visible in named structures rather than hidden behind a throughput claim.

## WireGuard protocol engines

### 7. [WireGuard/wireguard-go](https://github.com/WireGuard/wireguard-go)

**Language/role:** Go; userspace WireGuard implementation. **Official GitHub mirror**; the upstream repository is hosted at `git.zx2c4.com` as stated on the repository page.

Study the relationship between concurrent packet processing, ordered peer state, cryptographic validation, and reusable packet buffers.

- **C1:** The sequential receive path rejects failed decryptions and replayed counters, validates inner IPv4/IPv6 lengths, and verifies that the source address maps to the authenticated peer in AllowedIPs before writing into the tunnel. Endpoint and key-refresh updates occur in the authenticated receive flow. See [`device/receive.go`](https://github.com/WireGuard/wireguard-go/blob/master/device/receive.go).
- **C3:** The same implementation batches socket receives and TUN writes and returns packet/container objects to pools. It separates incoming datagrams, decryption work, and per-peer sequential processing, providing a concrete architecture for increasing packet throughput while retaining ordering-sensitive checks. The [repository overview](https://github.com/WireGuard/wireguard-go#go-implementation-of-wireguard) also identifies platform integration limits and the distinction from the Linux kernel implementation.

### 8. [cloudflare/boringtun](https://github.com/cloudflare/boringtun)

**Language/role:** Rust; independent userspace WireGuard protocol library and CLI.

Study a protocol engine designed to be embedded without requiring its network or tunnel stack. The README currently warns that the main branch is undergoing restructuring and directs consumers toward published crates; this report treats it as source-reading material.

- **C2:** The protocol library is separate from `boringtun-cli`, with C ABI and JNI integration described in the [repository documentation](https://github.com/cloudflare/boringtun#boringtun). `TunnResult` distinguishes network output, IPv4 tunnel output, IPv6 tunnel output, completion, and errors, letting the host own I/O.
- **C1:** `Tunn` explicitly owns the in-progress handshake, a ring of recent sessions, pending packets, timers, and a shared rate limiter. Incoming parsing validates packet type, reserved fields, and exact handshake sizes before accessing fields. See [`boringtun/src/noise/mod.rs`](https://github.com/cloudflare/boringtun/blob/master/boringtun/src/noise/mod.rs).

## Encrypted overlays, mesh VPNs, and embedding libraries

### 9. [tailscale/tailscale](https://github.com/tailscale/tailscale)

**Language/role:** Go; WireGuard-based networking client, relay components, and embeddable networking packages. The study target is the public client/data-plane code, not an assumption that this repository contains the hosted service in full.

- **C2:** `tsnet` embeds a node inside a Go process, using a userspace network stack and ordinary `net.Listener`/`net.Conn` interfaces. It supports independent node identities and storage without a separate daemon. See the [`tsnet guide`](https://github.com/tailscale/tailscale/blob/main/tsnet/README.md).
- **C3:** `magicsock` abstracts a socket whose communication path can change while in use. Its source distinguishes direct IPv4/IPv6, DERP, and peer-relay paths and explicitly avoids per-packet metric lookup locks by retaining counters directly. This is useful for studying how path selection, observability, and packet-path costs interact. See [`wgengine/magicsock/magicsock.go`](https://github.com/tailscale/tailscale/blob/main/wgengine/magicsock/magicsock.go).

### 10. [NordSecurity/libtelio](https://github.com/NordSecurity/libtelio)

**Language/role:** Rust, with platform/backend integrations; client-side encrypted-network and VPN embedding library.

Study how a product-facing library organizes WireGuard backend choice, mesh connectivity, exit nodes, DNS, and firewall behavior behind a device lifecycle.

- **C2:** The documented `Device` API accepts event and socket-protection callbacks, selects WireGuard adapters, and can use an already-open tunnel descriptor. Starting/stopping the device and changing mesh configuration are separate operations, allowing applications to own their UI and operating-system setup. See the [`API walkthrough`](https://github.com/NordSecurity/libtelio#using-the-libtelio-api).
- **C1:** The endpoint state machine distinguishes disconnected, gathering, pinging, and published states. Timeouts and disappearing endpoints have explicit transitions; invalid transitions are logged rather than silently accepted. Read [`endpoint_state.rs`](https://github.com/NordSecurity/libtelio/blob/main/crates/telio-traversal/src/endpoint_state.rs). The inspected repository also contains a documented NAT/DERP/UPnP integration-test environment, although no tests were executed for this report.

### 11. [slackhq/nebula](https://github.com/slackhq/nebula)

**Language/role:** Go; certificate-authenticated encrypted overlay using Noise and lighthouse discovery.

Study how discovery, identity, host addressing, security groups, and direct peer connections fit together. The [technical overview](https://github.com/slackhq/nebula#technical-overview) explains certificates binding addresses and group membership to nodes.

- **C1:** The handshake manager documents lock ordering across the host map, handshake manager, lighthouse, and remote lists. It also rejects unknown handshake subtypes and invalid first-message indices before expensive protocol processing. See [`handshake_manager.go`](https://github.com/slackhq/nebula/blob/master/handshake_manager.go).
- **C3:** Pending handshakes have bounded packet buffering, retry limits, a trigger buffer, and a timer wheel. These structures address memory growth and retry scheduling when destinations are unreachable, while keeping the handshake lifecycle readable in one subsystem.

### 12. [gsliepen/tinc](https://github.com/gsliepen/tinc)

**Language/role:** C; decentralized VPN supporting routed IP and virtual Ethernet modes.

The inspected default branch is **`1.1`, explicitly a prerelease**; the README directs users needing a stable release to the 1.0 series. Study the development architecture with that distinction in mind.

- **C2:** Nodes learn other participants from initial peers and can forward through intermediaries when direct connections fail. Router, switch, and hub modes reuse the same network machinery. The [README](https://github.com/gsliepen/tinc/blob/1.1/README.md) describes these operating modes.
- **C1:** The Simple Peer-to-Peer Security interface models key exchange, signature, and acknowledgment states; keeps separate input/output sequence and cipher state; and exposes replay-window tracking. Its callback-based record interface supports streams and datagrams. See [`src/sptps.h`](https://github.com/gsliepen/tinc/blob/1.1/src/sptps.h).

### 13. [zerotier/ZeroTierOne](https://github.com/zerotier/ZeroTierOne)

**Language/role:** C++; encrypted network virtualization with distributed Ethernet-switch semantics.

Study the `node` subsystem, especially the boundary joining physical transport packets, virtual Ethernet frames, peer identity discovery, and per-network scheduling.

- **C1:** The switch API distinguishes locally originated packets from relayed traffic and documents the source-identity precondition for encryption. Unknown destination identities cause queuing and a WHOIS request, with explicit retry/timer work and a callback when the peer becomes known. See [`node/Switch.hpp`](https://github.com/zerotier/ZeroTierOne/blob/dev/node/Switch.hpp).
- **C3:** The same interface exposes active queue management, CoDel dequeue behavior, flow-aware policies, and per-network QoS state. It explains why each network needs independent queue state, making congestion and fairness concerns inspectable. The [`service documentation`](https://github.com/zerotier/ZeroTierOne/blob/dev/service/README.md) also makes transport and trusted-path options explicit; configurations that disable encryption on trusted paths should not be confused with the normal encrypted role.

### 14. [yggdrasil-network/yggdrasil-go](https://github.com/yggdrasil-network/yggdrasil-go)

**Language/role:** Go; experimental end-to-end encrypted IPv6 overlay. The project itself describes the implementation as early-stage.

Study the integration between cryptographic identities, IPv6 addressing, peer transports, and the underlying encrypted routing library. The current core uses Ironwood rather than implementing every routing layer in this repository.

- **C2:** The core wraps an encrypted packet connection with node identity, configurable links/listeners, peer filtering, and path notifications. This creates a clear separation from the IPv6-facing adapter. See [`src/core/core.go`](https://github.com/yggdrasil-network/yggdrasil-go/blob/develop/src/core/core.go).
- **C1:** The IPv6 adapter maps keys to addresses and subnets, buffers a packet while resolving a destination, and expires cached information under a mutex. Timeout callbacks check that the stored object is still the expected one before deletion, an instructive lifecycle detail. See [`src/ipv6rwc/ipv6rwc.go`](https://github.com/yggdrasil-network/yggdrasil-go/blob/develop/src/ipv6rwc/ipv6rwc.go).

### 15. [cjdelisle/cjdns](https://github.com/cjdelisle/cjdns)

**Language/role:** C and Rust; encrypted IPv6 networking with cryptographic address allocation.

This codebase offers unusually explicit examples of packet-processing contracts spanning protocol modules and language boundaries.

- **C1:** The replay protector requires authentication before marking a nonce as seen, explaining that otherwise forged packets could invalidate legitimate traffic. Its sliding bitfield distinguishes definite duplicates, losses, and packets outside the window. See [`crypto/ReplayProtector.h`](https://github.com/cjdelisle/cjdns/blob/master/crypto/ReplayProtector.h).
- **C2:** `Iface` connects message-processing modules through a common callback interface, with a Rust entry point and distinct send/forward operations. Debug assertions track the current message and enforce forwarding contracts, including tail-call expectations. See [`interface/Iface.h`](https://github.com/cjdelisle/cjdns/blob/master/interface/Iface.h). Study both the composability and the burden those contracts place on callers.

### 16. [neocturne/fastd](https://github.com/neocturne/fastd)

**Language/role:** C; compact UDP VPN daemon carrying IP packets or Ethernet frames in point-to-point, hub, or mesh arrangements.

Study a small implementation with a detailed wire specification and explicitly composable cryptographic methods.

- **C1:** The protocol document describes handshake TLVs, authentication tags, negotiated methods, and version-dependent framing. The v22 transition sends compatible initial handshakes while suppressing duplicate handling once L2TP-header support is known. See [`protocol.rst`](https://github.com/neocturne/fastd/blob/main/doc/source/devel/protocol.rst).
- **C2:** Method providers combine cipher and authentication components, with documented framing differences retained for historical compatibility. See [`crypto/methods.rst`](https://github.com/neocturne/fastd/blob/main/doc/source/crypto/methods.rst). The same document clearly distinguishes encrypted methods from authentication-only, null, and benchmark modes; the null L2TP offload path is not evidence of encrypted-tunnel acceleration.

### 17. [ntop/n2n](https://github.com/ntop/n2n)

**Language/role:** C; layer-2 peer-to-peer VPN with edge nodes and supernodes.

Study peer discovery and fallback forwarding under NAT, including why a socket learned from a relay may not be usable directly. Encryption is configurable; the project also supports an unencrypted transform.

- **C1:** The internal design documents pending versus known peers, acknowledgment-driven registration, endpoint-change invalidation, and asymmetric direct/relayed paths. Pending registrations prevent retry amplification when direct communication cannot succeed. See [`doc/Hacking.md`](https://github.com/ntop/n2n/blob/dev/doc/Hacking.md).
- **C3:** The cryptography documentation separates payload transforms from header processing and discusses plain-C, instruction-set-specific, and OpenSSL implementations plus the project's cipher benchmark tool. This provides a concrete path for examining portability versus processing cost. See [`doc/Crypto.md`](https://github.com/ntop/n2n/blob/dev/doc/Crypto.md). Its unusual cryptographic constructions are material for critical study, not an endorsement of equivalence to WireGuard or modern AEAD designs.

### 18. [dswd/vpncloud](https://github.com/dswd/vpncloud)

**Language/role:** Rust; encrypted UDP mesh VPN supporting TUN and TAP interfaces.

Study the boundary between message encryption and key negotiation/rotation. The repository was not archived when checked, but its GitHub API reported the latest push in **March 2024**; current maintenance is not assumed. See the [repository metadata](https://api.github.com/repos/dswd/vpncloud).

- **C1:** The crypto core documents directional nonce separation, multiple retained decryption keys, and the requirement that the receiver obtain a replacement key before the sender starts using it. Its time-based nonce acceptance rule deliberately trades reordering tolerance against rejection of older traffic; it should not be read as a claim that every within-window duplicate is rejected. See [`src/crypto/core.rs`](https://github.com/dswd/vpncloud/blob/master/src/crypto/core.rs).
- **C3:** That core encrypts and decrypts in place, reserves explicit room for authentication tags, and transmits a compact key-ID/nonce representation. It is a focused example of reducing packet-copy and framing costs while keeping key-rotation responsibilities outside the primitive.

### 19. [EasyTier/EasyTier](https://github.com/EasyTier/EasyTier)

**Language/role:** Primarily Rust; decentralized mesh VPN with several transport integrations.

The relevant monorepo subsystems are `easytier-core`, the native `easytier` composition layer, and `easytier-proto`; GUI and platform packages are not separate entries.

- **C2:** The architecture separates portable routing, peer state, packet processing, and lifecycle from host-owned sockets, TUN devices, DNS, routes, and native protocol engines. Host traits and a WASI adapter let the core be embedded without directly owning operating-system networking. See [`docs/core-architecture.md`](https://github.com/EasyTier/EasyTier/blob/main/docs/core-architecture.md).
- **C1:** The same document records a concrete mixed-version invariant: route reflection retains the encoded message and changes only permitted fields so unknown nested and top-level fields survive multihop propagation. It also assigns a single owner to peer graphs and lifecycle state, preventing platform adapters from creating competing copies. These are substantive compatibility and state-ownership concerns, independent of feature count.

## Encrypted connection tunnels and proxy transports

### 20. [mtrojnar/stunnel](https://github.com/mtrojnar/stunnel)

**Language/role:** C; TLS tunneling/offloading proxy. **Official-release mirror**, explicitly not the repository used for active development or pull requests.

Study the surprisingly difficult boundary between ordinary socket I/O and TLS's bidirectional progress and shutdown requirements.

- **C1:** The transfer loop tracks plaintext read/write openness separately from TLS operations that may want either readability or writability. It distinguishes buffered TLS data, close notifications, hangups, idle timeouts, and close timeouts. Comments explain how registering a hung-up descriptor with a full buffer could produce a busy loop. See [`src/client.c`](https://github.com/mtrojnar/stunnel/blob/master/src/client.c).
- **C2:** Service sections combine listener and connector roles with multiple upstream addresses, failover/round-robin selection, and protocol-specific negotiation. This lets the same engine secure multiple existing services without application rewrites. See the [`service-level configuration manual`](https://github.com/mtrojnar/stunnel/blob/master/doc/stunnel.md).

### 21. [sshuttle/sshuttle](https://github.com/sshuttle/sshuttle)

**Language/role:** Python; transparent connection proxy carrying traffic over SSH, rather than a general encrypted IP-packet VPN.

Study a deliberate change in abstraction: local TCP streams are reconstructed and multiplexed across SSH instead of encapsulating original TCP packets.

- **C3:** The [architecture explanation](https://github.com/sshuttle/sshuttle/blob/master/docs/how-it-works.rst) ties stream-level forwarding to avoiding nested TCP retransmission behavior. This is an architectural response to latency and loss behavior, not merely an optimization within a packet loop.
- **C1:** The stream wrappers distinguish temporary lack of data from EOF, retain unwritten bytes after partial writes, delay write shutdown until buffered data drains, and gate read/write readiness on buffer and connection state. See [`sshuttle/ssnet.py`](https://github.com/sshuttle/sshuttle/blob/master/sshuttle/ssnet.py). It is a compact study of backpressure and half-close propagation.

### 22. [jpillora/chisel](https://github.com/jpillora/chisel)

**Language/role:** Go; TCP/UDP tunnels transported over HTTP and secured using SSH.

Study how local and reverse forwarding, SOCKS behavior, reconnectable SSH transport, and per-destination access checks share one tunnel implementation.

- **C2:** Both client and server use `Tunnel`; remote endpoint descriptions map to proxy instances, while inbound/outbound and SOCKS capabilities are configuration choices. The common tunnel boundary accepts an address ACL and an externally established SSH connection. See [`share/tunnel/tunnel.go`](https://github.com/jpillora/chisel/blob/master/share/tunnel/tunnel.go).
- **C1:** The implementation synchronizes replacement of the active SSH connection, blocks consumers during connection establishment with cancellation/timeout escape paths, and closes already-created proxies when a later bind fails. These concrete failure paths complement the authentication and reconnect behavior described in the [README](https://github.com/jpillora/chisel#chisel).

### 23. [shadowsocks/shadowsocks-rust](https://github.com/shadowsocks/shadowsocks-rust)

**Language/role:** Rust; encrypted proxy/tunnel protocol implementation, service library, and binaries. Counted once for the whole workspace.

Study asynchronous authenticated framing and the separation between the reusable protocol layer and service behavior. This is an application tunnel implementation, not inherently a full IP VPN.

- **C1:** The AEAD-2022 reader authenticates a header before accepting its stream type and timestamp and before inserting the salt into replay tracking. Its comment explains why checking an unauthenticated salt earlier would let attackers poison that filter. See [`aead_2022.rs`](https://github.com/shadowsocks/shadowsocks-rust/blob/master/crates/shadowsocks/src/relay/tcprelay/aead_2022.rs).
- **C2:** The crypto-I/O layer presents a common asynchronous read/write interface over supported cipher families, maps protocol-specific errors into I/O errors, and works with generic Tokio streams. This gives services reusable protocol behavior without binding them to one socket implementation. See [`crypto_io.rs`](https://github.com/shadowsocks/shadowsocks-rust/blob/master/crates/shadowsocks/src/relay/tcprelay/crypto_io.rs).

### 24. [HyNetworks/hysteria](https://github.com/HyNetworks/hysteria)

**Language/role:** Go; QUIC-based encrypted TCP/UDP proxy with forwarding and TUN integrations. The former `apernet/hysteria` URL was opened and verified to redirect to this canonical repository.

Study how one encrypted transport carries reliable streams and unreliable datagrams with different lifecycle rules.

- **C1:** The [Hysteria 2 protocol specification](https://github.com/HyNetworks/hysteria/blob/master/PROTOCOL.md) gates proxy requests on successful authentication, assigns UDP session identifiers, defines expiry/recreation behavior, and requires complete reassembly before forwarding fragmented datagrams. Losing a fragment discards the entire datagram.
- **C3:** TCP uses independent QUIC bidirectional streams while UDP uses the unreliable datagram extension. The specification explicitly negotiates receive-rate information and defines when congestion control must determine the rate instead. Together with the [documented integration modes](https://github.com/HyNetworks/hysteria#-jack-of-all-trades), this makes the transport/application boundary useful to study. No claim of universal censorship resistance or numerical speed superiority is inferred from project marketing.

## Coverage, search process, and limitations

Discovery used more than six distinct live-search formulations, including: IPsec/IKE implementations and architecture; userspace WireGuard in Go and Rust; encrypted mesh routing; C/OpenVPN/SoftEther implementations; smaller UDP VPNs such as fastd, n2n, and VpnCloud; QUIC and encrypted proxy transports; SSH/TLS tunnels; OCaml/MirageOS VPNs; and embeddable VPN libraries and integration testing. Follow-up searches expanded the initial candidates to MirageVPN, fastd, and libtelio. Later broad architecture/testing searches mostly returned wrappers, small prototypes, or projects overlapping families already represented, producing diminishing returns.

Primary verification combined opened GitHub pages, GitHub repository metadata, source-tree inventories, actual source files, project manuals, and changelog excerpts. All 24 retained repositories were unarchived according to the metadata checked on the research date. This does not establish maintenance intensity or support commitments; VpnCloud's older push date, the two mirrors, and prerelease/development caveats are therefore stated separately. C4 is awarded only where the inspected history supports it, not simply because a project is old or recently pushed.

The selection deliberately excludes configuration-only WireGuard tooling, VPN installation scripts, GUI-only wrappers, awesome-lists, and tutorial implementations. SoftEther's stable/development repositories and the several OpenVPN integrations are not counted as duplicate implementations: SoftEther appears once, while OpenVPN 2, OpenVPN 3, and MirageVPN have substantially different implementations and integration models. WireGuard configuration/control-plane projects without inspected substantial tunnel machinery were not added merely to increase the count. A whole operating-system repository was not added just to count an in-kernel VPN subsystem; userspace engines and OpenVPN's documented offload boundary provide more focused entry points here.

This was read-only research: no candidate code was executed, dependencies installed, maintainers contacted, or large repositories cloned. Tests were inspected only where cited or described, not run. The report is not exhaustive across all VPN/proxy ecosystems, and source comments or documentation can lag behavior; conclusions about study value are grounded inference from the inspected interfaces and implementations, not a full correctness or cryptographic audit.
