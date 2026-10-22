# Process supervisors and service managers

Research date: **2026-10-09**

This report selects **21 GitHub repositories** implementing operating-system service management, Unix process supervision, application process management, or native Windows service hosting. It covers system and user services, embedded systems, container initialization, and local development stacks. Actor-only supervision, cluster schedulers, service discovery, monitoring without lifecycle control, and thin installation wrappers are outside the selection. The systemd repository is counted once, specifically for its core service-management subsystem.

The criteria are judgments grounded in the linked implementation and documentation, not certifications of correctness or recommendations to deploy every project. Repository pages were opened to verify identities; every selection also has independently inspected primary material beyond its README. Maintenance is not inferred from stars or a recent crawl. Official mirrors and historical source distributions are identified explicitly.

## Criteria legend

- **C1 — Difficult correctness:** lifecycle invariants, concurrency, signals, dependency ordering, process identity, or failure handling.
- **C2 — Reusable abstractions:** substantial mechanisms that support different applications, service types, or operating environments.
- **C3 — Performance with structure:** concrete resource or responsiveness constraints addressed through understandable architectural choices.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or management of accumulated complexity.

## System and operating-system service managers

### 1. [systemd/systemd](https://github.com/systemd/systemd)

**Language/role:** C; Linux system and user service manager within a larger system-software monorepo.

Study the core service representation to see how one manager accommodates daemon conventions with different definitions of successful startup and termination. The relevant scope is the core service engine, rather than every utility shipped by systemd.

- **C1:** The service model distinguishes timeout, protocol, watchdog, signal, exit-code, start-limit, and out-of-memory failures. It separately tracks main and control commands, startup/stop/abort deadlines, and whether termination means the main process or the entire cgroup has exited. These distinctions expose the correctness burden behind apparently simple start/stop operations.
- **C2:** `Service` builds on `Unit` and composes execution, killing, and cgroup contexts. Its service types cover forking daemons, one-shot commands, D-Bus activation, explicit readiness notification, and execution completion, making the lifecycle machinery reusable across different daemon contracts.

**Entry point:** [`src/core/service.h`](https://github.com/systemd/systemd/blob/main/src/core/service.h), including the documented service types, result enums, contexts, and runtime state supporting both criteria.

### 2. [OpenRC/openrc](https://github.com/OpenRC/openrc)

**Language/role:** C and POSIX shell; dependency-based service management with selectable supervision backends.

Study how a service-script ecosystem separates dependency orchestration from persistent supervision. OpenRC's orchestration command can finish after starting services; supervision can be supplied by its own `supervise-daemon` or s6. The documented historical default, `start-stop-daemon`, does not itself supervise processes. [Supervisor selection contract](https://github.com/OpenRC/openrc/blob/master/man/openrc-run.8).

- **C1:** Startup follows the dependency graph, shutdown reverses the relevant relationships, and services retain state so repeated starts are meaningful. The guide also handles orphaned service processes through cgroup cleanup.
- **C2:** Named runlevels, separate service scripts and configuration, and replaceable supervisors support different operating policies without requiring each service to implement an entire manager.
- **C3:** Parsed service metadata is cached and invalidated using modification times; parallel startup is optional. This is a concrete way to retain shell-based extensibility while controlling repeated parsing and startup work.

**Entry points:** [User guide](https://github.com/OpenRC/openrc/blob/master/user-guide.md), which supports the graph, caching, and cleanup claims; [service-script manual](https://github.com/OpenRC/openrc/blob/master/man/openrc-run.8).

### 3. [davmac314/dinit](https://github.com/davmac314/dinit)

**Language/role:** C++; dependency-aware service supervisor usable as PID 1 or a user service manager.

Dinit is particularly useful for studying a compact event-driven manager whose design explicitly addresses allocation failure and blocking I/O.

- **C1:** Service actions propagate through queues instead of uncontrolled recursive transitions. Essential operation must survive allocation failures and exceptions; the design also explains mockable system-call wrappers used to isolate lifecycle tests.
- **C2:** A `service_record` hierarchy distinguishes internal, triggered, foreground-process, background-process, and scripted services. Placeholder services preserve references when ordering relationships exist before a service is loaded.
- **C3:** The event loop uses nonblocking operations, while per-sink circular log buffers discard excess messages with an overflow indication instead of stalling supervision. This makes the responsiveness tradeoff explicit.

**Entry point:** [Design document](https://github.com/davmac314/dinit/blob/master/doc/DESIGN), which explains these mechanisms and maps them to source files and test directories.

### 4. [finit-project/finit](https://github.com/finit-project/finit)

**Language/role:** C; Linux init and service supervisor with event-driven conditions.

Study a manager that expresses readiness and environmental dependencies as conditions, including dependencies on network interfaces, devices, PID files, and other service states.

- **C1:** Conditions are not merely startup ordering hints: losing a prerequisite can stop a dependent service. Reconfiguration introduces an explicit unknown state, `flux`, and distinguishes pausing/resuming dependents from propagating a reload or restart. PID-file readiness has a documented reassertion requirement and limitations.
- **C2:** A common condition model applies to services, tasks, and run commands. Built-in condition producers and user-defined conditions let the same engine coordinate boot, network availability, device appearance, and application-specific events.

**Entry point:** [Conditions and their internals](https://github.com/finit-project/finit/blob/master/doc/conditions.md). Its filesystem representation and three-state model make a useful starting point for comparing event dependencies with explicit service graphs.

### 5. [openwrt/procd](https://github.com/openwrt/procd)

**Language/role:** C; OpenWrt's embedded service/process manager. **Official OpenWrt GitHub mirror**, explicitly labeled as such by the repository.

Study the service-instance implementation for a router-oriented manager that combines process lifecycle, configuration changes, resource limits, and optional isolation.

- **C1:** The instance exit path distinguishes requested stops, restarts, and respawns; counts rapid failures against a crash-loop policy; cancels watchdog timers; and handles remaining cgroup members before finalizing a jailed instance. Stop timeouts escalate from termination to killing.
- **C2:** A structured instance configuration carries commands, environment, watched files and network devices, limits, credentials, watchdogs, and jail settings. Configuration comparison and lifecycle operations operate on this shared representation rather than application-specific scripts alone.

**Entry point:** [`service/instance.c`](https://github.com/openwrt/procd/blob/main/service/instance.c), especially `instance_exit_done`, `instance_stop`, cgroup-draining callbacks, and `instance_config_changed`. These are concrete examples of lifecycle policy meeting embedded-system integration.

### 6. [apple-oss-distributions/launchd](https://github.com/apple-oss-distributions/launchd)

**Language/role:** C; Apple's published Darwin launchd sources. **Historical official source distribution**: the inspected tag list includes imported releases through `launchd-842.92.1`, dated August 2014. This is not presented as the current macOS implementation. [Release-source tags](https://github.com/apple-oss-distributions/launchd/tags).

Study an on-demand service model in which IPC endpoints help coordinate availability, instead of a conventional explicit dependency graph.

- **C1:** The documented contract prohibits double-fork daemonization, specifies termination timeouts and restart throttling, and describes process-group cleanup. Mach-service port recycling and atomic recreation expose subtle client/server lifecycle requirements.
- **C2:** Property-list jobs share a framework for system daemons and user agents, socket and Mach-service activation, resource policies, timers, and keep-alive conditions. The manual explicitly delegates dependency coordination to IPC.

**Entry points:** [`man/launchd.plist.5`](https://github.com/apple-oss-distributions/launchd/blob/main/man/launchd.plist.5) for the architectural contract; [source-distribution tags](https://github.com/apple-oss-distributions/launchd/tags) for the historical boundary.

## Composable Unix supervision suites and container initialization

### 7. [g-pape/runit](https://github.com/g-pape/runit)

**Language/role:** C; portable Unix init and service supervision. This is the upstream GitHub repository linked by the [official project site](https://www.smarden.org/runit/), rather than one of the numerous downstream copies. The repository distinguishes released software from its experimental `next` branch.

Study the division between a small three-stage PID 1, a directory supervisor, individual service supervisors, and logging processes.

- **C1:** `runsv` sequences `run` and `finish`, delays immediate restart loops, passes exit status to cleanup, and distinguishes permanent down, run-once, and supervisor exit. Exiting supervision waits for the associated logger after closing its input, making shutdown ordering explicit.
- **C2:** Service directories, control FIFOs, optional log services, and custom control hooks provide a general protocol for supervising arbitrary foreground programs. The same supervision components can run under another init system.

**Entry points:** [`runsv` manual](https://smarden.org/runit/runsv.8) for lifecycle and control semantics; [project architecture overview](https://www.smarden.org/runit/) for the three-stage init design.

### 8. [skarnet/s6](https://github.com/skarnet/s6)

**Language/role:** C; low-level Unix supervision and process-administration toolkit. **Official GitHub mirror**, listed on the [upstream download page](https://skarnet.org/software/s6/).

Study supervision as a tree of small cooperating processes: `s6-svscan` maintains supervisors, while each `s6-supervise` remains the direct parent of its service.

- **C1:** Stable service-directory identity avoids treating a recycled PID as the service identity. Readiness is separately communicated through a notification descriptor; the documented waiting interfaces distinguish a running process from a ready service and from completed cleanup.
- **C2:** Supervision, control, log processing, privilege changes, environment setup, and resource limits are composable tools. The overview explains chain-loading and how supervised logger processes fit into the same model.

**Entry points:** [Architectural overview](https://skarnet.org/software/s6/overview.html), covering the parent relationship, readiness protocol, logging pipes, and composition; [upstream reference index](https://skarnet.org/software/s6/).

### 9. [skarnet/s6-rc](https://github.com/skarnet/s6-rc)

**Language/role:** C; dependency and machine-state management above s6. **Official GitHub mirror**, identified by the [upstream project page](https://skarnet.org/software/s6-rc/).

This is a separate implementation layer from s6: it computes and applies service-state changes rather than duplicating the low-level supervisor.

- **C1:** Dependency ordering applies both when starting and stopping services. A one-shot is considered up after its activation command succeeds, whereas a long-running service incorporates process liveness and optional readiness. Updating a live system to a different compiled database has its own operation.
- **C2:** Longruns, oneshots, and bundles let the same dependency engine model daemons, filesystem setup, and named collections of services. Offline compilation separates definition analysis from live transitions, while the update interface supports package-driven changes.

**Entry points:** [Architecture and live-state overview](https://skarnet.org/software/s6-rc/overview.html); [command/reference index](https://skarnet.org/software/s6-rc/). The compile/live split is worth comparing with Dinit's dynamically loaded service descriptions.

### 10. [bruceg/daemontools-encore](https://github.com/bruceg/daemontools-encore)

**Language/role:** C; compatibility-oriented derivative of D. J. Bernstein's daemontools.

This is retained as a substantive derivative, not an extra copy of daemontools: its repository documents distinct lifecycle hooks, process-group control, status extensions, and logging changes while preserving the original interface model.

- **C1:** The change history records fixes for a race when controlling logger and main service, status-file removal before acquiring the service lock, descriptor leakage, and shutdown ordering. It also specifies permanent-failure handling through exit code 100.
- **C2:** Added `start`, `stop`, and notification hooks extend the service lifecycle; process-group signals, environment helpers, and integrated logger piping generalize the tools to services needing initialization or coordinated cleanup.

**Entry point:** [`CHANGES`](https://github.com/bruceg/daemontools-encore/blob/master/CHANGES), which documents both the independent evolution and the concrete failure modes. Study it alongside the repository's compact C source tree; release recency is not established here.

### 11. [just-containers/s6-overlay](https://github.com/just-containers/s6-overlay)

**Language/role:** Shell/execline orchestration and packaged utilities; container init and service lifecycle built on s6.

The substantive subject is its container-specific initialization contract, not a second implementation of s6 supervision. Its staged design generates runtime infrastructure, assembles service definitions, starts the supervision tree, and connects container termination to the foreground command.

- **C1:** `s6-svscan` becomes PID 1, service initialization follows a defined sequence, and completion of the container `CMD` initiates shutdown and returns that command's exit status to the host. These mechanics connect internal service failures to the container's external lifecycle.
- **C2:** System and user s6-rc definitions, user bundles, legacy initialization scripts, and legacy service directories share a defined integration path. The design explicitly chooses runtime compilation for configurability, exposing a useful startup-flexibility tradeoff.

**Entry point:** [How the init works](https://github.com/just-containers/s6-overlay/blob/master/doc/init.txt), which traces the stages and the handling of `CMD`, legacy services, and the user bundle.

## Application process supervisors and monitoring frameworks

### 12. [Supervisor/supervisor](https://github.com/Supervisor/supervisor)

**Language/role:** Python; client/server process control for Unix.

Study a well-specified lifecycle state machine and the maintenance cost of preserving its behavior across Python versions, RPC clients, and operating-system interfaces.

- **C1:** The process model distinguishes startup backoff from an already-running process exiting, and separates bounded startup retries from potentially unlimited configured restarts. Foreground-child ownership and `SIGCHLD` handling ground these states in operating-system process relationships. [Subprocess and state-transition documentation](https://supervisord.org/subprocess.html).
- **C4:** The dated changelog documents the 2019 Python 3 transition, subsequent compatibility fixes, a 2021 process-state event race, and 2025 poller/restart fixes plus a Python 3.13 test adjustment. This is sustained evolution backed by specific compatibility and test work. [Changelog](https://supervisord.org/changes.html).

**Entry points:** [Subprocess lifecycle](https://supervisord.org/subprocess.html); [changelog](https://supervisord.org/changes.html). The separation between startup success and long-term restart policy is especially useful to compare with other supervisors.

### 13. [circus-tent/circus](https://github.com/circus-tent/circus)

**Language/role:** Python; process and socket manager with ZeroMQ control and event interfaces.

Circus is useful for studying worker-pool management in which sockets, process groups, command handling, and observation have separate abstractions.

- **C1:** The watcher implementation coordinates reaping, desired worker counts, respawning, graceful stop timeouts, optional child signaling, and worker expiration. It checks whether a watcher is stopping before replenishing its workers, an essential interaction between shutdown and recovery. [`circus/watcher.py`](https://github.com/circus-tent/circus/blob/master/circus/watcher.py).
- **C2:** Watchers represent groups running the same command. Separate ZeroMQ request/reply and publish/subscribe channels distinguish commands from events, while statistics run in a separate process and plugins use these interfaces. [Architecture](https://circus.readthedocs.io/en/latest/design/architecture/).

**Entry points:** [Architecture](https://circus.readthedocs.io/en/latest/design/architecture/); [`watcher.py`](https://github.com/circus-tent/circus/blob/master/circus/watcher.py). The published documentation identifies itself as version 0.17.2; its existence is not taken as proof of current release activity.

### 14. [Unitech/pm2](https://github.com/Unitech/pm2)

**Language/role:** JavaScript; application process manager with Node-oriented clustering and support for other executable workloads.

Study how application cooperation changes the semantics of restarting a service. PM2's readiness and shutdown protocols are more instructive than an unconditional claim of zero-downtime reloads.

- **C1:** A process may explicitly send `ready` after dependencies initialize. Shutdown begins with a catchable signal and escalates after a deadline; Windows can use a shutdown message. Correct reload behavior therefore depends on the application honoring the protocol and draining its work. [Graceful start/shutdown guide](https://pm2.keymetrics.io/docs/usage/signals-clean-restart/).
- **C2:** A common process-management interface handles application declarations, multiple instances, generic interpreter/binary workloads, persisted process lists, and integration with host init systems. Cluster mode supplies another execution mode within this framework. [Repository overview and examples](https://github.com/Unitech/pm2).

**Entry point:** [Readiness, signal flow, and shutdown protocol](https://pm2.keymetrics.io/docs/usage/signals-clean-restart/), followed by the repository's application and cluster examples.

### 15. [ochinchina/supervisord](https://github.com/ochinchina/supervisord)

**Language/role:** Go; independently implemented Supervisor-style process manager.

This is a reimplementation, not a fork of the Python code. It is useful for comparing familiar configuration and lifecycle concepts with a concurrent Go runtime; the README explicitly notes partial support for Supervisor events, so compatibility should not be assumed complete.

- **C1:** The process implementation uses atomic lifecycle state and a mutex-protected health checker. A compare-and-swap guard prevents overlapping liveness checks, while consecutive success/failure thresholds and transition callbacks govern recovery actions. [`process/process.go`](https://raw.githubusercontent.com/ochinchina/supervisord/master/process/process.go).
- **C2:** Reusable process configuration supports groups, dependency ordering, liveness actions, restart policies, file-change monitoring, logs, and control interfaces. The shared `Process` and `LivenessChecker` types make the connection between configuration and runtime policy visible. [Configuration contract](https://github.com/ochinchina/supervisord).

**Entry points:** [`process.go`](https://raw.githubusercontent.com/ochinchina/supervisord/master/process/process.go); [process package](https://github.com/ochinchina/supervisord/tree/master/process), which also exposes manager and command-parser tests.

### 16. [bluepill-rb/bluepill](https://github.com/bluepill-rb/bluepill)

**Language/role:** Ruby; application-oriented process monitor and lifecycle controller. A legacy Ruby-ecosystem study; present-day maintenance and modern Ruby compatibility were not established.

Study how a configuration DSL can be kept outside the monitoring core, and how sampled resource checks can drive state transitions without recomputing every observation for every process.

- **C1:** The design specifies sequential processing of user commands to avoid races, state-machine notifications to triggers, and bounded historical observation structures. The README explains grace periods, flapping checks, and staged stop signals.
- **C2:** Applications, groups, processes, and configurable conditions form a reusable hierarchy. The DSL maps to ordinary initializers rather than becoming entangled with the monitoring logic.
- **C3:** The design memoizes `ps` output per monitoring tick for applications with many processes and uses rotational arrays for observation history, addressing concrete collection and storage costs.

**Entry points:** [Design notes](https://github.com/bluepill-rb/bluepill/blob/master/DESIGN.md); [configuration and lifecycle examples](https://github.com/bluepill-rb/bluepill). The design notes are brief, so these claims describe the documented design, not a full implementation audit.

### 17. [kostya/eye](https://github.com/kostya/eye)

**Language/role:** Ruby with Celluloid; process monitoring, lifecycle control, and coordinated process chains. Another legacy ecosystem example whose current maintenance was not established.

Study the separation between actor-backed process objects, explicit state transitions, monitoring checks, and configuration inheritance.

- **C1:** The state machine handles crashes during starting, stopping, or restarting, and a failed kill can return a service to `up`. Entering and leaving `up` adds or removes watchers; crash handling clears process identity and schedules a follow-up check. [State implementation](https://github.com/kostya/eye/blob/master/lib/eye/process/states.rb).
- **C2:** The process object composes distinct modules for configuration, commands, monitoring, children, triggers, notification, and scheduling. This supports inherited application/group/process settings, child monitoring, and sequential chains without one monolithic lifecycle class. [Process composition](https://github.com/kostya/eye/blob/master/lib/eye/process.rb).

**Entry points:** [`process.rb`](https://github.com/kostya/eye/blob/master/lib/eye/process.rb); [`process/states.rb`](https://github.com/kostya/eye/blob/master/lib/eye/process/states.rb). The [change history](https://github.com/kostya/eye/blob/master/CHANGES.md) additionally documents process-identity and child-iteration race fixes.

## Local application-stack orchestration

### 18. [F1bonacc1/process-compose](https://github.com/F1bonacc1/process-compose)

**Language/role:** Primarily Go; scheduler and supervisor for non-containerized application stacks.

Study how a Compose-like declaration represents processes whose prerequisites may be completion, successful completion, liveness/readiness, or a particular log message. The selected subsystem is the Go process-management implementation and its documented lifecycle model.

- **C1:** Dependency conditions distinguish started, healthy, completed, and successful states. Shutdown can signal a whole process group or invoke a custom command, then force termination on timeout. The documentation also specifies that log-line readiness and readiness probes cannot both be configured for one process.
- **C2:** Process replicas, dependency groups, environment/working-directory settings, restart policies, and configurable shutdown share one declaration model. It can express development servers, supporting daemons, setup jobs, and test-stack lifecycles.

**Entry points:** [Process lifetime contract](https://f1bonacc1.github.io/process-compose/launcher/), which supports both criteria; [source map](https://github.com/F1bonacc1/process-compose/tree/main/src), showing separate application, configuration, health, scheduling, API, and terminal-interface packages.

### 19. [DarthSim/overmind](https://github.com/DarthSim/overmind)

**Language/role:** Go; Procfile process manager using tmux sessions and control mode.

Overmind provides a distinct terminal-oriented design: preserving interactive process access and terminal output is part of the process-management contract, not just a log-viewer feature.

- **C1:** Its lifecycle implementation distinguishes explicit restart, interruption, automatic recovery, and processes allowed to exit. Stop and kill operate on process groups; the observation path decides whether to respawn or finish and closes/recreates output pipes accordingly. [`start/process.go`](https://raw.githubusercontent.com/DarthSim/overmind/master/start/process.go).
- **C2:** Procfile commands map to tmux-backed process objects with shared output handling and per-process policy. Scaling, individual reconnection, stop/restart commands, and layered environment configuration support different development stacks. [Repository behavior guide](https://github.com/DarthSim/overmind).

**Entry points:** [`process.go`](https://raw.githubusercontent.com/DarthSim/overmind/master/start/process.go); [start package](https://github.com/DarthSim/overmind/tree/master/start). Its concurrent observation code is a useful review subject, not evidence that every shared-state interaction has been proved race-free.

## Native Windows service hosting

### 20. [winsw/winsw](https://github.com/winsw/winsw)

**Language/role:** C#/.NET; native Windows service host for arbitrary applications.

Study the translation from Windows Service Control Manager operations to the lifecycle of an ordinary executable. Although called a wrapper, WinSW implements meaningful lifecycle policy rather than merely generating service-install commands. The repository distinguishes stable 2.x releases from the `v3` development branch and 3.x prereleases; the entry below uses v3 documentation.

- **C1:** Stop first attempts a console Ctrl+C event or window-close message, waits for a configured interval, and then terminates the process. A separate stop executable has a different completion contract, and preshutdown handling addresses operating-system shutdown deadlines.
- **C2:** XML configuration abstracts executable arguments, dependency relationships, environment, logging, lifecycle commands, and startup mode. Those settings let unrelated application runtimes participate in Windows service management through a common host.

**Entry point:** [XML configuration and lifecycle specification](https://github.com/winsw/winsw/blob/v3/docs/xml-config-file.md), especially stop behavior, hooks, dependencies, and preshutdown. Consult the repository's version-status note before comparing these semantics with 2.x.

### 21. [mtkennerly/shawl](https://github.com/mtkennerly/shawl)

**Language/role:** Rust; Windows service host for arbitrary commands.

Study a smaller service host that makes restart decisions from child exit status and translates service-control callbacks into process supervision.

- **C1:** The service loop receives stop/shutdown requests over a channel, checks for cancellation during restart delays, distinguishes normal exit from termination, and optionally uses a Windows Job Object to clean up a process tree. The source also explains why it allocates a console for Ctrl+C delivery. [Service implementation](https://raw.githubusercontent.com/mtkennerly/shawl/master/src/service.rs).
- **C4:** The dated 2019–2026 changelog records fixes for quoting, negative exit codes, incompatible restart options, UNC paths, 32-bit/runtime distribution, and Ctrl+C behavior. That is concrete evidence of evolving Windows compatibility rather than simply an old project date. [Changelog](https://github.com/mtkennerly/shawl/blob/master/CHANGELOG.md).

**Entry points:** [`src/service.rs`](https://raw.githubusercontent.com/mtkennerly/shawl/master/src/service.rs); [changelog](https://github.com/mtkennerly/shawl/blob/master/CHANGELOG.md).

## Coverage, search method, and limitations

Discovery used more than six distinct live-search formulations, including:

- Unix init/service-manager architecture: systemd, OpenRC, Dinit, and Finit.
- Python and Go process supervisors, including Circus and Supervisor-compatible implementations.
- Windows service hosting and Rust alternatives to WinSW/NSSM.
- Ruby resource monitors and lifecycle frameworks: Eye, Bluepill, and God.
- Procfile and Compose-style host-process orchestration.
- s6, s6-rc, daemontools derivatives, and container initialization.
- Embedded OpenWrt and historical Darwin service managers.
- Upstream-versus-mirror checks for runit, GNU Shepherd, and Monit.

Search results were discovery aids; retained claims come from opened repository pages, manuals, architecture documents, source files, or change histories. Where browser retrieval returned only GitHub navigation or failed to load source, GitHub's read-only connector supplied the actual file text. No candidate repositories were cloned, built, or executed. Later searches increasingly returned projects already covered, downstream copies, unrelated AI-agent “supervisors,” and recently introduced managers with less established evidence; a final upstream check added runit.

**Important exclusions:** GNU Shepherd fits the technical category, but the search found its current upstream outside GitHub and unofficial GitHub copies, without establishing a qualifying official GitHub mirror. Monit's discovered GitHub copy explicitly identifies itself as an [unofficial mirror](https://github.com/arnaudsj/monit). NSSM likewise was not included through an unverified third-party copy. God, Foreman/Honcho variants, and smaller Procfile runners were not added merely to repeat already-covered approaches. Tiny PID-1 reapers, generic service-installation libraries, container orchestrators, and actor-runtime supervision were outside the chosen boundary. Void's runit derivative was not counted separately from upstream runit.

The selection spans C, C++, Python, Go, JavaScript, Ruby, C#, Rust, and shell/execline, but does not cover the whole service-management ecosystem. The absence of a verified official GitHub home limits coverage of some Scheme and non-GitHub communities. Historical launchd sources and legacy Ruby frameworks are useful engineering studies, not assertions of current platform support. Documentation and default-branch source can describe different development stages, particularly for WinSW; links should be treated as entry points rather than immutable snapshots. C1–C4 assessments identify concrete study value and do not imply that every component is uniformly exemplary.
