# Time synchronization daemons

Research date: **2026-10-09**

This report selects 19 substantive GitHub codebases that synchronize operating-system or hardware clocks, or run the network time services used by those synchronizers. It covers NTP/SNTP, PTP/gPTP, cloud and GNSS clock discipline, and alternative authenticated or fault-tolerant approaches. Server-only Roughtime, specialized research systems, and historical implementations are identified explicitly. Client-only libraries, monitoring dashboards, and thin service wrappers are outside the selection.

The criteria below identify concrete engineering material worth studying. They are selection judgments grounded in the linked sources, not an audit, a benchmark comparison, or a claim that every component is exemplary.

- **C1 — Difficult correctness:** numerical and clock semantics, concurrency, invariants, hostile inputs, or failure recovery.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting different sources, platforms, algorithms, or deployment roles.
- **C3 — Performance with structure:** explicit latency, throughput, resource, or polling constraints addressed through an understandable architecture.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility work, tests, or deliberate complexity management.

## General-purpose NTP and SNTP

### 1. [mlichvar/chrony](https://github.com/mlichvar/chrony)

**Language/role:** C; `chronyd` NTP client/server and reference-clock synchronizer. This is the maintainer's substantive GitHub mirror; the repository identifies GitLab as its upstream.

An experienced engineer can study how a daemon turns heterogeneous, imperfect measurements into a defensible clock estimate. **C1:** source selection explicitly distinguishes stale, unreachable, excessively noisy, untrusted, and inconsistent sources; leap-second voting and sample rejection interact with source statistics. **C2:** a common source representation accommodates NTP peers, hardware reference clocks, and manual measurements, with shared statistics, selection, and reachability machinery. Both are visible in the implementation, rather than inferred from the protocol name. Start with [sources.c](https://github.com/mlichvar/chrony/blob/master/sources.c).

The [NEWS history](https://github.com/mlichvar/chrony/blob/master/NEWS) supplies useful companion cases: late hardware timestamps, 32/64-bit time representations, NTS compatibility, and platform-specific clock adjustments. These make it a particularly useful study of the boundary between estimation algorithms and operating-system behavior.

### 2. [ntp-project/ntp](https://github.com/ntp-project/ntp)

**Language/role:** C; the NTP reference implementation, including `ntpd`, reference-clock drivers, and supporting tools.

Study the interaction between control theory and the messy lifecycle of a system clock. **C1:** the [clock loop filter](https://github.com/ntp-project/ntp/blob/stable/ntpd/ntp_loopfilter.c) combines adaptive phase/frequency control with explicit startup, frequency-acquisition, synchronization, and spike states. It distinguishes stepping from slewing, applies panic/step limits, and coordinates kernel discipline and PPS capabilities; unit conversions and state transitions are central correctness concerns.

**C4:** the [stable NEWS history](https://github.com/ntp-project/ntp/blob/stable/NEWS) spans releases from 2003 through the inspected 4.2.8p18 entry in 2024. It documents dynamic interface handling, reference-clock changes, Windows threading fixes, cryptographic checks, and portability corrections. This is evidence of sustained compatibility and complexity management, rather than merely an old repository. That inspected history is not a claim about the date of the latest development anywhere in the project.

### 3. [ntpsec/ntpsec](https://github.com/ntpsec/ntpsec)

**Language/role:** C with Python tooling; security-focused NTP daemon. The GitHub repository is a mirror of the project's GitLab development repository.

This is a substantive independently evolved NTP fork, useful for studying deliberate reduction of inherited protocol and platform complexity. **C1:** the project's [implementation differences](https://docs.ntpsec.org/latest/ntpsec.html) explain removal of Autokey and other risky or obsolete facilities, restrictions on remote configuration, safer buffer handling, and changes to clock and timestamp behavior. These are concrete design choices, not evidence that the entire implementation is vulnerability-free.

**C2:** the [architecture description](https://docs.ntpsec.org/latest/warp.html) separates per-source peer/poll processing from sanity checks, filtering, source selection, clustering, and clock discipline. That pipeline accommodates network sources and reference clocks while keeping source-level measurements separate from the system-wide estimate. Read the architecture alongside the differences document: the interesting comparison with classic NTP is what can be removed or consolidated while retaining the estimation pipeline and necessary compatibility.

### 4. [openntpd-portable/openntpd-openbsd](https://github.com/openntpd-portable/openntpd-openbsd)

**Language/role:** C; OpenNTPD's OpenBSD source import mirror, including the actual daemon under `src/usr.sbin/ntpd`. The portable build framework is a companion repository, not a second independent daemon in this list.

**C1:** [ntpd.c](https://github.com/openntpd-portable/openntpd-openbsd/blob/master/src/usr.sbin/ntpd/ntpd.c) shows separate NTP, DNS, and constraint-processing roles, checked IPC message lengths, and privileged clock adjustment through the parent. The engineering lesson is how network-facing work, HTTPS-derived time constraints, and privileged state changes are divided across process boundaries.

**C4:** the companion [portable ChangeLog](https://github.com/openntpd-portable/openntpd-portable/blob/master/ChangeLog) traces the 5.7–7.9 release series, including fork/exec and IPC fixes, drift-file interoperability, 32-bit overflow handling, and corrections when another peer changes the adjustment between request and reply. The [official project page](https://www.openntpd.org/) confirms the continuing OpenBSD release relationship and a July 2026 portable release. This is a useful compact implementation for examining security boundaries and portability together.

### 5. [pendulum-project/ntpd-rs](https://github.com/pendulum-project/ntpd-rs)

**Language/role:** Rust; NTP/NTS synchronization daemon and server, with control and observability tools.

**C2:** the [code-structure guide](https://docs.ntpd-rs.pendulum-project.org/development/code-structure/) explains the separation of protocol/estimation decisions from asynchronous execution and small OS-facing timestamp, clock-steering, and PPS interfaces. Source tasks feed a central steering task, making the ownership of per-source and combined clock state a useful study target.

**C1:** the [changelog](https://github.com/pendulum-project/ntpd-rs/blob/main/CHANGELOG.md) records specific difficult cases: NTS cookie-size denial of service, unbounded key-exchange connections, incorrect dispersion growth, server-to-server packet loops, and leap-state handling. These provide concrete review targets alongside the architectural account.

**Version caveat:** the inspected changelog includes a 2.0 alpha undergoing major internal restructuring, alongside the 1.x history. Treat the published architectural guide as a description to compare with the chosen release; do not assume every crate layout or control interface is identical on current `main`.

### 6. [systemd/systemd](https://github.com/systemd/systemd)

**Language/role:** C; specifically the `systemd-timesyncd` subsystem, counted once within this monorepo. Its scope is SNTP client synchronization.

Study a deliberately constrained time client integrated with boot and network lifecycle. **C1:** the [service documentation](https://github.com/systemd/systemd/blob/main/man/systemd-timesyncd.service.xml) distinguishes establishing a roughly monotonic boot-time clock from attaining synchronization with a reference. Persistent timestamps, machines without a reliable RTC, and separate ordering targets make that distinction operationally important.

**C3:** the [manager implementation](https://github.com/systemd/systemd/blob/main/src/timesync/timesyncd-manager.c) uses an event-driven manager, adaptive poll intervals, bounded retransmission growth, and server rotation. These address the tradeoff between network traffic, convergence, and failure recovery. The same source exposes request nonces, clock readings near transmission, and response/root-distance checks, giving additional C1 material. This entry is about the time daemon, not a blanket assessment of systemd's unrelated subsystems.

## PTP, gPTP, and hardware clock topologies

### 7. [richardcochran/linuxptp](https://github.com/richardcochran/linuxptp)

**Language/role:** C; `ptp4l`, `phc2sys`, and related Linux PTP tools. This is the maintainer-hosted GitHub mirror; the project also maintains its SourceForge development infrastructure.

**C1:** the [ptp4l manual](https://www.linuxptp.org/documentation/ptp4l/) explains the hardware-clock invariant behind a boundary clock: ports normally share one PHC, while the JBOD option requires external synchronization of the distinct PHCs. It also describes delay mechanisms, timeout behavior, timestamp compensation, and profile settings whose changes can affect clock-tree correctness.

**C2:** [servo.h](https://github.com/richardcochran/linuxptp/blob/master/servo.h) exposes a common interface for PI, linear-regression, shared-memory, and reference-clock-socket servo types. Inputs include sample reliability and timestamp mode; outputs carry both frequency adjustment and explicit unlocked/jump/locked states, with hardware adjustment limits. This is an unusually clear place to study how a protocol engine, clock device, and interchangeable control algorithm meet without collapsing into one implementation.

### 8. [ptpd/ptpd](https://github.com/ptpd/ptpd)

**Language/role:** C; PTPd's IEEE 1588-2008 daemon. Retained as a substantial older implementation lineage; current maintenance is not established by the inspected historical material.

**C1:** the [servo implementation](https://github.com/ptpd/ptpd/blob/master/src/dep/servo.c) handles invalid or excessive delays, leap-related pauses, filtering, and the ordering between offset and delay updates. Consecutive rejected samples can trigger recovery rather than leaving the servo permanently stuck. It is useful for examining how control code behaves when measurements stop satisfying its assumptions.

**C2:** the [ChangeLog](https://github.com/ptpd/ptpd/blob/master/ChangeLog) documents a generic timing-domain API replacing special-case NTP failover handling, allowing different time controllers to participate. It also records unicast negotiation, configuration processing, and operating-system clock-adjustment adaptations. A further concrete performance case is the minimum POSIX timer interval added to prevent an unserviceable signal queue. The selection rests on the implementation and these architectural changes, not on treating old release notes as proof of present-day support.

### 9. [Xilinx-CNS/sfptpd](https://github.com/Xilinx-CNS/sfptpd)

**Language/role:** C; host synchronization daemon coordinating PTP, PPS, NTP, the system clock, and NIC hardware clocks. Although PTPd-derived, its multi-clock orchestration and subsequent evolution justify a separate entry.

**C2:** the [sfptpd manual](https://github.com/Xilinx-CNS/sfptpd/blob/master/doc/sfptpd.8) describes synchronization-module instances and topologies that distribute a reference to the system clock and other PHCs. PPS, PTP, NTP fallback, and freerunning modes have distinct responsibilities; PPS also needs a time-of-day source. Study the abstraction of a host containing several clocks rather than only one network-facing servo.

**C1:** the [changelog](https://github.com/Xilinx-CNS/sfptpd/blob/master/CHANGELOG.md) exposes clock ownership and lifecycle problems: PHC locks, source flapping after fallback, freshness of offsets after a clock step, and hotplug cleanup. These are concrete failure modes created by coordinating multiple synchronization mechanisms. Some inspected entries are explicitly unreleased; they are evidence of engineering work, not a promise that a packaged release contains every fix.

### 10. [Avnu/gptp](https://github.com/Avnu/gptp)

**Language/role:** C++; gPTP/802.1AS reference daemon for AVB and automotive-oriented systems, with Linux and Windows adaptation code.

**C1:** the inherited [implementation history](https://github.com/Avnu/gptp/blob/master/history.md) records deadlock on synchronization timeout, a signal-thread race, stale transmit timestamps, negative clock jumps, and message association using both type and sequence ID. These make the code a useful study of event ordering and hardware timestamp delivery.

**C2:** the same history describes separating common port behavior from Ethernet behavior and removing the clock's dependence on a single timestamper to enable multiple ports. The [automotive-profile notes](https://github.com/Avnu/gptp/blob/master/README_AVNU_AP.txt) explain persistence, link recovery, and interval-related behavior around that structure.

This is a reference implementation with explicit limitations: the profile notes identify unfinished behavior and platform differences. Its older imported history is valuable evidence, but this report does not infer current maintenance or complete profile conformance from it. OpenAvnu's ancestor copy is not counted separately.

### 11. [pendulum-project/statime](https://github.com/pendulum-project/statime)

**Language/role:** Rust; PTP implementation with the `statime-linux` daemon and a portable, `no_std`-capable core.

**C1:** the [core API documentation](https://docs.rs/statime/latest/statime/) describes ports in `InBmca` and `Running` states. All relevant ports must be brought into the appropriate state before running the best-master-clock algorithm. The state types make a global protocol sequencing requirement visible in the API. Timestamp callbacks and timer actions expose other ordering obligations to the embedding platform.

**C2:** the same API separates `Clock`, `Filter`, port processing, and returned actions from socket and timer execution. Overlay and shared clocks show that these abstractions support more than one arrangement of the underlying time source. Study the library alongside the Linux daemon identified in the repository, especially if comparing embedded integration with a host daemon. The inspected API page reports version 0.4.0; the `latest` documentation URL can change, so release-specific study should preserve that distinction.

### 12. [facebook/time](https://github.com/facebook/time)

**Language/role:** Primarily Go for the relevant subsystems; the `sptp` synchronization client and `ptp4u` time server, counted once within Meta's time-infrastructure monorepo.

**C1:** the [SPTP design](https://github.com/facebook/time/tree/main/ptp/sptp) specifies how a delay request, synchronization packet, and announce packet convey four timestamps and two correction fields. Message sequence association, transmit timestamps, path-delay estimation, and best-master selection remain important even with a smaller exchange.

**C3:** that design removes per-client subscriptions from the server while preserving PTP packet layouts for NIC timestamping. This is a concrete response to server-state and protocol-complexity costs, not an unsupported throughput claim. The documented transparent-clock support is specifically for one-step devices. The [PTP subsystem overview](https://github.com/facebook/time/tree/main/ptp) locates the client and server implementations. Engineers can study how a specialized data-center protocol trades standard PTP negotiation for a smaller exchange while retaining hardware-assisted timestamping; SPTP should not be confused with unrestricted standard-PTP interoperability.

### 13. [Orolia2s/oscillatord](https://github.com/Orolia2s/oscillatord)

**Language/role:** C; GNSS-referenced oscillator and PHC disciplining daemon, particularly for the Atomic Reference Time Card. The numerical disciplining algorithm is supplied by a separate library; this repository owns substantial hardware and daemon orchestration.

**C1:** the [main control loop](https://github.com/Orolia2s/oscillatord/blob/main/src/oscillatord.c) coordinates GNSS validity, survey completion, phase measurements, oscillator readback, calibration, and phase jumps. It deliberately ignores a subsequent measurement after a phase jump and orders phase-error acquisition before reading control values. This is useful for studying measurement/actuation consistency in a physical clock-control system.

**C2:** [oscillator.h](https://github.com/Orolia2s/oscillatord/blob/main/src/oscillator.h) defines an oscillator class with callbacks for control, calibration, attributes, phase error, persistence, and GNSS information. That interface accommodates different devices and separates hardware behavior from the algorithm and service loop. The repository documents simulator and card integration tests. Device scope matters: its README distinguishes mRO50 control from SA3X/SA5X monitoring-only support.

## Cloud and feed-forward synchronization

### 14. [aws/clock-bound](https://github.com/aws/clock-bound)

**Language/role:** Rust with client/FFI components; the inspected 3.0 alpha includes an actual clock-synchronization daemon and bounded-time client interfaces. This is a version-specific expansion beyond the project's earlier clock-bound reporting role.

**C1:** the [daemon design](https://github.com/aws/clock-bound/blob/main/docs/clockbound-daemon.md) uses a feed-forward algorithm based on oscillator counters and reference timestamps, separating estimation from changes to the system clock. VMClock input addresses disruption events that can invalidate assumptions about the local oscillator. Study how an uncertainty-aware service handles virtualization alongside ordinary network measurements.

**C2:** the design separates input acquisition, synchronization calculations, and clock state. NTP, supported PHCs, and VMClock feed the estimator; clock state both disciplines the system clock and publishes time/error information through shared memory for clients. Those boundaries support distinct acquisition and consumption paths. The inspected documentation is **3.0.0-alpha.0**, and PHC support is explicitly limited to the ENA-provided device. Neither stable-release availability of this architecture nor generic PHC support is assumed.

### 15. [RADicalsync/RADclock](https://github.com/RADicalsync/RADclock)

**Language/role:** C; research-oriented feed-forward clock daemon, library, and kernel-facing integration.

Study a design that estimates time from a raw counter rather than using the already-adjusted system clock as its only timebase. **C2:** the [user/developer guide](https://github.com/RADicalsync/RADclock/blob/master/Documentation/RADclockDoc_guide.md) describes live synchronization, stored measurement processing, library consumption, and supported kernel interfaces. The same estimation machinery can therefore serve online clocks and offline trace analysis.

**C1:** the [threading design](https://github.com/RADicalsync/RADclock/blob/master/Documentation/RADclockDoc_threads.txt) follows packet capture, processing, parameter dissemination, shutdown, and configuration reload. On reload it preserves the processing thread that holds clock history while restarting other roles, making state continuity an explicit requirement.

This is a specialized study target with kernel/platform dependencies and incomplete documentation. The threading document explicitly limits its NTP-serving implementation and identifies unfinished behavior; do not treat it as a fully conformant drop-in replacement for a general-purpose NTP server. No comparative accuracy claim is adopted from project publicity.

## Alternative trust and failure models

### 16. [marcfrei/scion-time](https://github.com/marcfrei/scion-time)

**Language/role:** Go; experimental SCION-based time service and synchronization implementation, also exposing conventional IP/NTP/NTS paths.

The repository is a research implementation of reliable global synchronization, not evidence that a production deployment satisfies all Byzantine-fault assumptions. **C1:** [sync.go](https://github.com/marcfrei/scion-time/blob/main/core/sync/sync.go) validates relationships among timeout, interval, and correction-impact parameters; measures reference and peer clocks concurrently; and limits corrections using clock-drift estimates. The [measurement aggregation implementation](https://github.com/marcfrei/scion-time/blob/main/core/measurements/measurement.go) makes its trimmed fault-tolerant midpoint calculation directly inspectable.

**C2:** synchronization accepts abstract system clocks, reference-clock clients, and adjustment strategies. This separates measurement transport and clock actuation from aggregation and correction policy, supporting the repository's different network and reference arrangements. Engineers can compare these interfaces with the SCION path-diversity design described in the repository. The strongest learning opportunity is tracing an algorithm's explicit assumptions into executable state and validation rules; this review does not independently prove the advertised fault-tolerance properties.

### 17. [Kicksecure/sdwdate](https://github.com/Kicksecure/sdwdate)

**Language/role:** Python and shell with a C clock-adjustment helper; periodically obtains time through Tor/onion HTTP sources and adjusts the local clock.

**C1:** [remote_times.py](https://github.com/Kicksecure/sdwdate/blob/master/usr/lib/python3/dist-packages/sdwdate/remote_times.py) performs concurrent retrieval, bounded subprocess waits, strict returned-value checks, elapsed-time accounting, replay-bound checks, and comparison against Tor consensus validity. Study how a clock service handles bootstrap and trust constraints when UDP/NTP is not its transport. These checks do not eliminate uncertainty or dependence on the configured sources and Tor environment.

**C4:** the [upstream change history](https://github.com/Kicksecure/sdwdate/blob/master/changelog.upstream) records development from 2014 through 2026 with concrete compatibility and testing work: AppArmor adaptations, system-call filters, suspend/resume integration, Debian layout changes, and regression tests. This supports sustained evolution without relying on repository age alone. The architecture is particularly relevant to privacy-oriented operating systems; it is not presented as an interchangeable high-precision substitute for hardware-timestamped PTP.

### 18. [int08h/roughenough](https://github.com/int08h/roughenough)

**Language/role:** Rust; authenticated Roughtime server and client components. Included for its long-running time-source server; it does not itself provide continuous kernel clock discipline.

**C1:** the server's [request handler and tests](https://github.com/int08h/roughenough/blob/master/crates/roughenough-server/src/requests.rs) validate request size, framing, server-key commitments, and mutually supported protocol versions. Tests exercise malformed, oversized, mismatched-key, and unsupported-version requests, making trust-boundary behavior inspectable.

**C3:** the [worker loop](https://github.com/int08h/roughenough/blob/master/crates/roughenough-server/src/worker.rs) batches work but limits batches per wakeup so shutdown and maintenance deadlines are revisited under load. It uses nonblocking metric publication and staggers key replacement to avoid all workers pausing together. Network handling, request processing, and response generation remain separate components. This is a useful contrast with servo-oriented daemons: its difficult engineering lies in serving authenticated time efficiently and predictably rather than controlling the host oscillator.

### 19. [ioerror/tlsdate](https://github.com/ioerror/tlsdate)

**Language/role:** C; historical TLS/HTTPS time retrieval and the `tlsdated` synchronization daemon.

**C1:** the [hardening notes](https://github.com/ioerror/tlsdate/blob/master/HARDENING) describe privilege separation and platform-specific confinement. The [changelog](https://github.com/ioerror/tlsdate/blob/master/CHANGELOG) explains bounded treatment of certificate-time errors during bootstrap, rejecting slow time retrieval, and detecting RTC corruption after suspend/resume. It is useful for examining the circular dependency between knowing the time and validating certificates.

**C4:** the same changelog documents 2012–2015 evolution: event-loop and subprocess-watching refactors, integration tests, and portability/confinement fixes across supported systems. These changes provide real historical engineering material.

Treat this as a historical case study. The inspected changelog ends in 2015, and its TLS ServerHello time assumptions and alternate HTTPS-header mode require separate contemporary interoperability assessment. The report does not establish present maintenance or recommend deploying that historical configuration. Unimplemented hardening plans in the notes are not counted as implemented protections.

## Search coverage and limitations

Discovery used live web searches across more than six distinct formulations, followed by opening every selected canonical GitHub repository and reading additional primary implementation or design material. Search families included:

- NTP daemon/reference implementations, security-focused forks, portable OpenBSD code, and Rust NTS implementations.
- Linux PTP, PTPd-derived host orchestration, gPTP/AVB, automotive profiles, and embedded Rust PTP.
- Go/data-center time servers, simplified PTP, AWS clock bounds, PHCs, and virtualization disruptions.
- Feed-forward/RADclock designs and SCION-based fault-tolerant synchronization.
- Tor/HTTPS time retrieval, TLS time bootstrap, and Roughtime server implementations.
- GNSS/PPS oscillator discipline and timing cards, plus Windows time services and White Rabbit/PPSi candidates.

Later broad searches mostly rediscovered the established daemons, simple NTP query libraries, launch wrappers, and tutorials. The final hardware-oriented search added `oscillatord`, which contributed a genuinely different physical-clock control architecture. The list exceeds the narrow-category guideline because the retained projects span distinct protocol, hardware, and trust models rather than filling a quota with forks.

Client-only packages such as `beevik/ntp`, GPS data feeders, monitoring-only tools, and application-level logical-clock services were excluded. Windows PTPSync was inspected but omitted because its documented service primarily integrates an underlying PTPd executable. White Rabbit/PPSi searches did not establish an appropriate substantive official GitHub mirror for retention; this is a hosting/verification limitation, not a judgment on those projects. OpenNTPD's build framework and imported daemon source are one project here; the same rule avoids counting ancestor OpenAvnu copies or superseded RADclock copies again. NTPsec and sfptpd are retained separately because their inspected designs show substantive independent evolution.

Some GitHub HTML/source requests failed or returned incomplete views; the corresponding public file contents were read through a GitHub connector or raw source endpoint. A second rendering of a README was not counted as an additional source. Links generally follow the inspected branches or documentation channels and can change. Historical, mirror, research, hardware-limited, and prerelease status is called out where material. No candidate was cloned, installed, executed, benchmarked, or externally modified; documented tests were inspected rather than run. Claims about what engineers can learn are reasoned interpretations of the cited code and documentation, and maintenance is not inferred from stars or a recent push alone.
