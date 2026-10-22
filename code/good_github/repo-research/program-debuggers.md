# Program debuggers

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing program debuggers, substantial debugger engines or extensions, and embedded debug servers. It spans native CPU and GPU execution, managed and interpreted languages, retrospective debugging, kernel inspection, and microcontrollers. LLVM and Ghidra are counted once each, with their relevant subsystems identified. This is a source-reading guide: the criteria judgments are grounded engineering inferences from the linked implementation and documentation, not claims that every component is exemplary or that the projects were tested during this research.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, language or numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions serving multiple use cases. **C3** — real performance or resource constraints addressed through an understandable architecture. **C4** — sustained evolution supported by compatibility work, testing, or complexity management, rather than age alone.

## Native CPU and GPU debuggers

### 1. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language/role:** Primarily C++; the **LLDB** subsystem in the LLVM monorepo.

LLDB is useful for studying how a debugger separates target processes, symbols, expression evaluation, commands, and a public embedding API. Its architecture makes the relationship between compiler semantics and interactive inspection unusually explicit.

- **C1:** Symbolic breakpoints must acquire and lose locations as shared libraries load and unload. Expression evaluation combines DWARF operations and Clang, including type promotion, symbolic references, and execution of compiled expressions in the target. These are concrete semantic and lifecycle obligations. [LLDB implementation overview](https://github.com/llvm/llvm-project/blob/main/lldb/docs/resources/overview.md).
- **C2:** The public C++ API deliberately constrains object layout and virtual dispatch to allow internal evolution without changing exposed class layouts. Separate Host, Platform, Process, Thread, and formatter abstractions support local, remote, and embedded clients. The same [overview](https://github.com/llvm/llvm-project/blob/main/lldb/docs/resources/overview.md) is the best starting point.

### 2. [x64dbg/x64dbg](https://github.com/x64dbg/x64dbg)

**Language/role:** C++ and Qt; Windows user-mode binary debugger for x86 and x64.

Study a graphical debugger whose command system, plugins, and target state must remain coherent across multiple threads. The official architecture article is historical, dated 2016, so its line-number references should not be treated as current source locations.

- **C1:** The design distinguishes a debug loop, command thread, asynchronous command dispatch, and synchronous direct execution. It explicitly identifies subsystem locks as necessary to prevent races while accessing target information. [Architecture and message flow](https://x64dbg.com/blog/2016/10/04/architecture-of-x64dbg.html).
- **C2:** DBG, BRIDGE, and GUI form distinct boundaries; a function table and plugin scripting API expose debugger services, while a table-view hierarchy shares disassembly, dump, and ordinary table behavior. This is a substantial extensibility architecture, beyond a GUI around a command-line executable. [Architecture](https://x64dbg.com/blog/2016/10/04/architecture-of-x64dbg.html).

### 3. [eteran/edb-debugger](https://github.com/eteran/edb-debugger)

**Language/role:** C++ and Qt; graphical native debugger. The repository identifies Linux as its officially supported platform; other ports have varying completeness.

This smaller community codebase offers a tractable comparison with LLDB and x64dbg: a debugger-core plugin implements an explicit interface instead of spreading OS details throughout the UI.

- **C1:** The Linux backend handles `ptrace` thread-creation and exit events, including a newly created thread exiting before setup completes, and propagates hardware debug-register state to new threads. [Linux DebuggerCore implementation](https://github.com/eteran/edb-debugger/blob/master/plugins/DebuggerCore/unix/linux/DebuggerCore.cpp).
- **C2:** `IDebugger` abstracts CPU mode, register names, process enumeration, event waiting, lifecycle operations, breakpoint ownership, and state construction. This makes backend boundaries and their compromises directly inspectable. [IDebugger interface](https://github.com/eteran/edb-debugger/blob/master/include/IDebugger.h).

### 4. [EpicGames/raddebugger](https://github.com/EpicGames/raddebugger)

**Language/role:** Primarily C; native graphical debugger and associated debug-information tooling.

The repository describes the debugger as **alpha**, with Windows x64/PDB support as its established scope and further platform work in progress. It is particularly interesting for studying responsiveness when handling large debug-information datasets.

- **C2:** The codebase is organized into separable layers with acyclic dependencies, including low-level process control, the debugger engine, debug-information conversion, evaluation, and independent RDI format libraries. [Technical overview in the repository](https://github.com/EpicGames/raddebugger).
- **C3:** Debug information is converted and loaded asynchronously. The implementation exposes striped locking, path/timestamp lookup caches, reference-counted entries, and queued load requests with priorities; these make the resource and latency strategy concrete. [Debug-information implementation](https://github.com/EpicGames/raddebugger/blob/master/src/dbg_info/dbg_info.c).

Some overview terminology trails the evolving source layout; start with the verified `dbg_info` file rather than assuming every layer mentioned in older prose still exists under the same name.

### 5. [ROCm/ROCgdb](https://github.com/ROCm/ROCgdb)

**Language/role:** C/C++; AMD's GDB-derived heterogeneous CPU/GPU debugger for Linux.

This is a substantive vendor implementation, not a second listing of a plain GDB mirror. Concentrate on the AMD Debugger API target and GPU-specific tests within the larger binutils/GDB tree.

- **C1:** GPU wave lifetime extends beyond apparent execution termination: the target tracks resume mode and pending stop requests so it does not delete a wave before its promised termination event arrives. Wave coordinates are cached because they may be needed after the wave exits. [AMD target implementation](https://github.com/ROCm/ROCgdb/blob/amd-staging/gdb/amd-dbgapi-target.c).
- **C2:** The target integrates agents, queues, dispatches, waves, runtime state, and hardware feature requests with GDB's inferior and event abstractions. The same implementation is a useful study of extending a CPU-oriented debugger model.

The [testing guide](https://github.com/ROCm/ROCgdb/blob/amd-staging/TESTING.md) explains CPU/GPU validation, capability gates, and serialized device access. It also candidly states that performance tests are not routinely enforced by CI.

## Replay, kernel inspection, and debugger frameworks

### 6. [rr-debugger/rr](https://github.com/rr-debugger/rr)

**Language/role:** C++; Linux record/replay engine that supplies reverse debugging through GDB.

rr is a strong choice for studying reproducibility at the system-call, signal, process, and thread boundaries. Its role is the execution-recording backend, not merely a debugger frontend.

- **C1:** Replay explicitly distinguishes syscall entry/exit, deterministic signals, asynchronous signal delivery, buffered syscall flushes, and task termination. State cloned with a session must avoid pointers into session-specific storage; some syscall states cannot be checkpointed. [ReplaySession contracts](https://github.com/rr-debugger/rr/blob/master/src/ReplaySession.h).
- **C2:** Session cloning promises independent copies of the entire tracee tree and associated state, while diversion sessions permit exploratory execution. This provides reusable machinery for reverse execution and inspection.
- **C3:** Checkpoint clones are partially initialized to reduce resources while inactive, and replay records whether fast-forwarding completed a whole instruction or only part of a repeated instruction. These optimizations retain explicit semantic contracts in the same source.

The repository documents CPU, kernel, and virtualized-performance-counter requirements; portability is constrained by those requirements.

### 7. [osandov/drgn](https://github.com/osandov/drgn)

**Language/role:** C core with Python interfaces and helpers; programmable inspection of Linux kernels, core dumps, and userspace programs.

drgn emphasizes traversing program state through scripts. It is especially useful for engineers interested in typed memory inspection rather than interactive stepping.

- **C1:** Its object layer explicitly defines behavior for cases where C arithmetic is undefined or implementation-defined: modular signed arithmetic, two's-complement bitwise operations, and arithmetic right shifts. It also models bit fields and target endianness. [Object implementation contracts](https://github.com/osandov/drgn/blob/main/libdrgn/object.h).
- **C2:** The library supports custom module and debug-information discovery, object/type finders, and plugin hooks. These allow applications to supply their own memory and symbol environment instead of depending entirely on the default CLI discovery path. [Advanced usage and extension APIs](https://github.com/osandov/drgn/blob/main/docs/advanced_usage.rst).

### 8. [HyperDbg/HyperDbg](https://github.com/HyperDbg/HyperDbg)

**Language/role:** C/C++ and low-level assembly; hypervisor-assisted Windows user/kernel debugger.

HyperDbg provides a different execution-control boundary from OS debugging APIs: Intel virtualization and EPT. The repository describes Linux support as under development; do not infer general cross-platform support.

- **C1:** Its message-tracing design explains how VM exits can interrupt code that already holds a non-root-mode lock, causing deadlock if root-mode tracing takes that same lock. Separate message pools and context-appropriate synchronization address this problem. [VMX-root-compatible tracing design](https://github.com/HyperDbg/docs/blob/master/design/features/vmm-module/vmx-root-mode-compatible-message-tracing.md).
- **C2:** Debugging facilities are expressed as events with associated actions, covering memory access, hidden hooks, and system-call transitions. This is a common programmable model across several hardware mechanisms. [Event abstraction](https://github.com/HyperDbg/docs/blob/master/design/debugger-internals/events.md).

The tracing document is a design exposition with code examples; it should be read alongside current implementation when changing the system.

### 9. [NationalSecurityAgency/ghidra](https://github.com/NationalSecurityAgency/ghidra)

**Language/role:** Primarily Java with Python debugger agents; the **Ghidra Debugger**, Trace RMI, and p-code emulation subsystems.

Counted for its substantive dynamic-debugging infrastructure, not merely its disassembler or decompiler. It is useful for studying a shared analysis UI above multiple existing debugger engines.

- **C1:** Debugger-agent updates must manage trace-database transactions and object insertion correctly. The emulation guide further explains why forcing abstract values into concrete integers loses information for augmented models, and why control transfers should remain visible to execution engines. [Agent construction](https://github.com/NationalSecurityAgency/ghidra/blob/master/GhidraDocs/GhidraClass/Debugger/B5-AddingDebuggers.md) and [p-code modeling](https://github.com/NationalSecurityAgency/ghidra/blob/master/GhidraDocs/GhidraClass/Debugger/B4-Modeling.md).
- **C2:** Agents expose schema-defined objects over a protobuf-based trace protocol. Separately, parameterized p-code arithmetic, state, and user-operation interfaces permit concrete emulation to be combined with taint or other auxiliary models. The two guides are complementary entry points into these abstractions.

### 10. [pwndbg/pwndbg](https://github.com/pwndbg/pwndbg)

**Language/role:** Python; substantial GDB and LLDB extension for low-level program inspection.

Pwndbg is retained because its debugger abstraction and state-management layer go well beyond command aliases. Study how a plugin makes consistent promises across two host debugger APIs.

- **C1:** A selection context manager restores global debugger selection even on failure. Temporary stop points clean themselves up, and event-handler priorities place cache invalidation before consumers of target state. Event documentation identifies operations that are invalid during exit or continuation. [Debugger abstraction implementation](https://github.com/pwndbg/pwndbg/blob/dev/pwndbg/dbg_mod/__init__.py).
- **C2:** Common Process, Thread, Value, breakpoint/watchpoint, memory-map, and event interfaces isolate higher-level inspection commands from GDB/LLDB differences. Read the same source for explicit contracts on partial memory reads, cancellation, and temporary execution control.

## Runtime-specific engines and adapters

### 11. [go-delve/delve](https://github.com/go-delve/delve)

**Language/role:** Go; native Go debugger with CLI, service APIs, and DAP support.

Delve is particularly instructive where Go runtime behavior, DWARF, and host OS control meet. Its porting guide explains architectural constraints with examples rather than just listing supported platforms.

- **C1:** Cross-platform core-file inspection requires target pointer size, architecture, and OS to remain independent of the debugger host. The guide also explains breakpoint removal/single-step/reinsertion and explicitly identifies concurrent stepping tests that ports should not skip. [Porting and correctness notes](https://github.com/go-delve/delve/blob/master/Documentation/internal/portnotes.md).
- **C2:** `pkg/proc` provides a symbolic layer over native, core-file, and GDB-serial backends, while services and DAP live above it. This provides a clear case study in sharing debugger semantics across live execution and postmortem targets. The same guide maps the packages and test boundaries.

### 12. [microsoft/debugpy](https://github.com/microsoft/debugpy)

**Language/role:** Primarily Python; Python debugger and DAP implementation incorporating pydevd.

Study process topology and session lifecycle: an IDE, adapter, optional launcher, and in-process debug server have different lifetimes and shutdown responsibilities. PyDev.Debugger is not separately counted here, avoiding duplication of the incorporated engine lineage.

- **C1:** Session code coordinates recursive locks, condition waits, component disconnection, process replacement, and termination. Finalization distinguishes launched processes from attached processes and drains pending messages before declaring a session over. [Session implementation](https://github.com/microsoft/debugpy/blob/main/src/debugpy/adapter/sessions.py).
- **C2:** The adapter/server split supports launch, attach, subprocesses, and reconnecting IDEs through a shared session model. [Subprocess design diagrams](https://github.com/microsoft/debugpy/blob/main/doc/Subprocess%20debugging.md) explain the topology; some terminology retains historical `ptvsd` names, so use current session code for exact behavior.

### 13. [ruby/debug](https://github.com/ruby/debug)

**Language/role:** Ruby with native support; MRI debugger exposed as `rdbg` and an embeddable library.

This is a useful implementation of tracing-based debugging that must avoid tracing itself. The repository distinguishes this implementation from the unrelated abandoned pre-1.0 `debug` gem.

- **C1:** `ThreadClient` checks running/waiting transitions, excludes management threads, and captures distinct state for ordinary stops, postmortem inspection, and replay. Stepping handles TracePoint reentry and uses thread-targeted hooks when available, with a fallback filter. [ThreadClient implementation](https://github.com/ruby/debug/blob/master/lib/debug/thread_client.rb).
- **C2:** The shared execution-control machinery serves a console, remote connections, VS Code, and Chrome DevTools, while applications can enter through command-line loading or explicit Ruby calls. [Repository integration overview](https://github.com/ruby/debug) together with ThreadClient shows how those interfaces share the engine.

Thread and Ractor support have documented limitations; the report does not assume complete Ractor debugging.

### 14. [xdebug/xdebug](https://github.com/xdebug/xdebug)

**Language/role:** C; PHP extension implementing step debugging and other development instrumentation.

Focus on the DBGp command handler and runtime compatibility history. This exposes the work involved in safely inspecting a live language engine through a remote protocol.

- **C1:** Commands are classified by whether they remain legal after execution, and the dispatcher separates ordinary operations, continuation, and stopping. Breakpoint, variable, evaluation, and path-mapping behavior meet in the handler. [DBGp implementation](https://github.com/xdebug/xdebug/blob/master/src/debugger/handler_dbgp.c).
- **C4:** The package changelog records releases across many years and concrete compatibility/failure work: PHP-version transitions, variable-fetching crashes, malformed protocol options, DBGp buffer limits, and path-mapping errors. This is evidence of accumulated complexity management, not merely longevity. [Package manifest and release history](https://github.com/xdebug/xdebug/blob/master/package.xml).

### 15. [microsoft/vscode-js-debug](https://github.com/microsoft/vscode-js-debug)

**Language/role:** TypeScript; DAP debugger for JavaScript runtimes including Node.js and browsers.

The breakpoint subsystem is a good study of reconciling source-level locations with generated scripts that arrive asynchronously.

- **C1:** Breakpoints have both DAP and runtime identities; source maps can reveal additional executable locations after a request is made. The manager reacts to new scripts and source-mapped stepping changes, while launch blockers coordinate setup with execution. [Breakpoint manager](https://github.com/microsoft/vscode-js-debug/blob/main/src/adapter/breakpoints.ts).
- **C2:** Source containers, condition factories, breakpoint predictors, and distinct breakpoint classes are injected into a common manager. This supports multiple runtime launchers and clients without embedding every concern in the DAP request handler. The same file provides concrete entry points into these collaborators.

The repository also provides a standalone DAP server, so the implementation is relevant beyond VS Code itself.

### 16. [microsoft/java-debug](https://github.com/microsoft/java-debug)

**Language/role:** Java; JDI-based debug server with a separate Eclipse/JDT integration layer.

Study the boundary between asynchronous DAP requests and JVM debugging operations. Its core/plugin split is explicit in the repository, and the thread handler exposes real remote-debugging failure cases.

- **C1:** Thread enumeration can race with thread collection or VM termination. The handler filters terminated threads, handles collection/cancellation failures, and routes pause/continue operations through session and thread state. [ThreadsRequestHandler](https://github.com/microsoft/java-debug/blob/main/com.microsoft.java.debug.core/src/main/java/com/microsoft/java/debug/core/adapter/handler/ThreadsRequestHandler.java).
- **C3:** Thread names are cached, and uncached JDI queries can be issued through asynchronous JDWP work before joining their results. This makes round-trip reduction and responsiveness visible in a small, understandable implementation, without relying on a benchmark claim.

The [repository overview](https://github.com/microsoft/java-debug) explains how the reusable server is packaged as a JDT Language Server plugin.

### 17. [Samsung/netcoredbg](https://github.com/Samsung/netcoredbg)

**Language/role:** Primarily C++; CoreCLR managed-code debugger with CLI, GDB/MI, and DAP interfaces.

This is a useful alternative implementation for examining how one debugger engine serves different client protocols.

- **C1:** Continue and step reject execution while expression evaluation leaves thread state inconsistent. Before resuming, the implementation clears variable/frame identities and emits the continued event before processing can produce another stop. These ordering rules are documented directly in code. [ManagedDebugger implementation](https://github.com/Samsung/netcoredbg/blob/master/src/debugger/manageddebugger.cpp).
- **C2:** A protocol boundary fronts shared thread, frame, variable, evaluator, callback-queue, breakpoint, and stepping components. The same file shows their composition; the [repository overview](https://github.com/Samsung/netcoredbg) verifies the three supported client interfaces.

Its test suite includes remote protocol scenarios, but the test README contains older SDK-specific setup; it should not be treated as a complete current compatibility matrix.

### 18. [dnSpyEx/dnSpy](https://github.com/dnSpyEx/dnSpy)

**Language/role:** C#; .NET assembly debugger/editor and **unofficial continuation** of dnSpy.

Retained as a substantive continuation; the original dnSpy repository is not counted separately. Study debugger-engine coordination inside a rich assembly-inspection application.

- **C1:** The debugger manager dispatches engine messages onto a designated debugger thread, verifies thread access, checks engine ownership, and manages process/runtime/thread/module events. [DbgManagerImpl](https://github.com/dnSpyEx/dnSpy/blob/master/Extensions/dnSpy.Debugger/dnSpy.Debugger/Impl/DbgManagerImpl.cs).
- **C2:** Engine and debugger contracts support different runtime backends while sharing breakpoints, exceptions, evaluation, and UI state.
- **C4:** The [release history](https://github.com/dnSpyEx/dnSpy/releases) demonstrates continued work across 2024–2026, including .NET-version migration, CoreCLR debugging configuration, incorrect thread-exit-code fixes, and defensive handling of problematic metadata. These changes establish a separate development history rather than a renamed snapshot.

### 19. [JuliaDebug/JuliaInterpreter.jl](https://github.com/JuliaDebug/JuliaInterpreter.jl)

**Language/role:** Julia; interpreter and stepping/breakpoint engine used by Julia debugger frontends.

This is intentionally an engine selection. Debugger.jl and the VS Code integration are not separately counted for the same underlying interpreter.

- **C1:** Frames represent lowered code, locals, and SSA values. Top-level definitions require special world-age handling so subsequent expressions can see newly defined methods; module initialization also has distinct execution semantics. [Interpreter internals](https://github.com/JuliaDebug/JuliaInterpreter.jl/blob/master/docs/src/internals.md).
- **C2:** Frontends share conditional breakpoints, frame execution through `debug_command`, and breakpoint-update hooks, instead of independently reimplementing interpretation. [Debugger API introduction](https://github.com/JuliaDebug/JuliaInterpreter.jl/blob/master/docs/src/index.md).

The API documentation explicitly warns that global frame, cache, and breakpoint state is **not thread-safe**. This limitation matters when considering reuse, and the C1 assessment does not imply it has been solved.

### 20. [WhatsApp/edb](https://github.com/WhatsApp/edb)

**Language/role:** Erlang; BEAM step debugger with a DAP interface.

This offers a distinct concurrency model: pausing a target node's processes while preserving the debugger and required system components.

- **C1:** The server tracks suspended processes and explicit exclusion/override sets. On termination it unregisters the debugger, clears breakpoints, and resumes processes. The public API documents module-loading timeouts that can occur when the process doing the loading is suspended. [Server state and cleanup](https://github.com/WhatsApp/edb/blob/main/apps/edb_core/src/edb_server.erl).
- **C2:** A typed Erlang API exposes attach/reverse-attach, subscriptions, pause/continue, process filters, stepping, stack inspection, and evaluation independently of a particular IDE. [Core API](https://github.com/WhatsApp/edb/blob/main/apps/edb_core/src/edb.erl).

The checked README requires OTP 29 for building current sources and describes separate prebuilt OTP 28 support. This is a runtime-specific implementation, not evidence of support for all deployed BEAM versions.

### 21. [pkulchenko/MobDebug](https://github.com/pkulchenko/MobDebug)

**Language/role:** Lua; embeddable remote debugger, substantially extended from RemDebug.

MobDebug is a compact counterpoint to the large native engines. Its implementation exposes the interaction between debug hooks, coroutines, stack variables, evaluated expressions, and socket polling.

- **C1:** LuaJIT's hook behavior differs from ordinary Lua, including hooks affecting multiple coroutines and imperfect call/return pairing. The debugger guards against debugging itself and captures locals/upvalues as both an evaluation environment and state to restore. [Debugger implementation](https://github.com/pkulchenko/MobDebug/blob/master/src/mobdebug.lua).
- **C3:** Configurable polling frequency trades command responsiveness against socket-check overhead; hook enable/disable controls also limit instrumentation cost. These choices are described in the repository and visible in the implementation.
- **C4:** The [changelog](https://github.com/pkulchenko/MobDebug/blob/master/CHANGELOG.md) documents years of Lua/LuaJIT/OpenResty compatibility changes, serialization safeguards, and tests. Its newest dated entry is 2021; that history supports C4 but does not establish a current maintenance cadence.

## Retrospective language debugging

### 22. [flow-storm/flow-storm-debugger](https://github.com/flow-storm/flow-storm-debugger)

**Language/role:** Primarily Clojure/ClojureScript; tracing and retrospective execution explorer with a desktop debugger.

Study the alternative to stop/inspect/continue debugging: collect execution records, then navigate or query them. Compiler-assisted instrumentation lives in related repositories and is not separately counted here.

- **C1:** Retaining object references does not preserve historical mutable state. The guide explains `SnapshotP`, automatic dereferencing, nested-mutable-value limitations, and concurrent mutation hazards. This makes the boundary of its time-travel semantics explicit. [User guide: mutable values](https://flow-storm.github.io/flow-storm-debugger/user_guide.html).
- **C2:** Runtime indexes expose timelines and entries through ordinary Clojure collection interfaces, allowing programmatic analysis beyond the GUI. Custom visualizers and snapshot protocols extend the data model.
- **C3:** Per-thread trace limits and heap limits bound recording growth; selective instrumentation and replacement snapshots offer additional resource controls. The same [guide](https://flow-storm.github.io/flow-storm-debugger/user_guide.html) contains the programmable-debugging and trace-limit sections.

## Embedded debug servers and libraries

### 23. [probe-rs/probe-rs](https://github.com/probe-rs/probe-rs)

**Language/role:** Rust; embedded debugging library and tools for multiple probe families and ARM, RISC-V, and Xtensa targets.

The Session implementation is an accessible example of representing exclusive hardware access while supporting several debugger consumers and heterogeneous cores.

- **C1:** A session owns access to a probe. Sharing it between consumers such as GDB and RTT requires synchronized turn-taking; the documentation explicitly warns that clients must yield opportunities for other consumers. Core attachment also distinguishes architecture-specific interfaces and mixed ARM/RISC-V access. [Session implementation and contracts](https://github.com/probe-rs/probe-rs/blob/master/probe-rs/src/session.rs).
- **C2:** Probe, target, architecture-interface, combined-core-state, and session abstractions are composed into the same library used by command-line tools, GDB, and DAP tooling. The code shows the boundary between transport access and per-core behavior rather than hiding it behind one device-specific driver.

### 24. [openocd-org/openocd](https://github.com/openocd-org/openocd)

**Language/role:** C with Tcl configuration; on-chip debugger and GDB remote server. **Official read-only GitHub mirror**, as identified by the repository.

OpenOCD is useful for studying broad hardware support through target and transport abstractions. The mirror is substantive source code; development contribution workflows are upstream rather than GitHub pull requests.

- **C1:** The target model distinguishes running user code, halted state, reset, unavailable hardware, and execution of algorithms on behalf of the debugger. It documents that debugger-run algorithms must maintain cached-state correctness, and models saved working areas, register caches, breakpoints, and watchpoints. [Target state and interface definitions](https://github.com/openocd-org/openocd/blob/master/src/target/target.h).
- **C2:** The repository separates JTAG/TAP support, target operations, flash drivers, and Tcl scripting, exposing the result through GDB, Tcl, and telnet interfaces. [Repository architecture overview](https://github.com/openocd-org/openocd) and the target definitions provide complementary reading entry points.

### 25. [pyocd/pyOCD](https://github.com/pyocd/pyOCD)

**Language/role:** Python; Arm Cortex-M debugging library, GDB server, and target-control tools.

pyOCD combines a readable object model with a concrete example of cache correctness across expensive hardware accesses.

- **C1:** Memory caching is invalidated when the target runs or its run token changes. Region boundaries and cacheability are checked; writes reach the target before updating the cache, so failed writes cannot create fictitious cached state. [MemoryCache implementation](https://github.com/pyocd/pyOCD/blob/main/pyocd/cache/memory.py).
- **C2:** A Session composes probe and board objects; CoreSight targets own debug-port/access-port machinery and individual cores, with memory regions linking to flash implementations. [Architecture guide](https://pyocd.io/docs/architecture.html).
- **C3:** An interval tree splits reads into cached and uncached ranges, reducing target transfers while preserving the invalidation rules above. The source connects the optimization directly to its correctness conditions.

## Coverage, search process, and limitations

Discovery used more than six distinct live search formulations, including native-debugger architecture; record/replay and reverse execution; Go/Python/Ruby internals; Java/.NET/JavaScript DAP engines; embedded probes and GDB servers; Clojure/Julia retrospective debugging; hypervisor/kernel inspection; Lua coroutine debugging; Erlang/Haskell/OCaml implementations; GPU debuggers; and official GDB mirror provenance. Later searches increasingly returned already represented engines, their editor integrations, and thin wrappers. The final GPU pass added ROCgdb because its wave lifecycle and hardware-specific validation added a distinct architecture family.

Each retained canonical GitHub URL was opened as a repository page or checked through the GitHub API. Each entry also has independently read primary implementation or architecture material beyond the repository landing-page description. GitHub API rate limiting was worked around using public repository HTML, official documentation, and raw source files; no repositories were cloned and no candidate code was executed. Links generally follow the inspected default branch and can change after the research date.

Important boundaries and exclusions:

- **Black Magic Debug** was excluded after its [GitHub page](https://github.com/blackmagic-debug/blackmagic) identified the repository as archived and moved to Codeberg. OpenOCD was retained because its GitHub repository explicitly identifies itself as an official source mirror.
- **Upstream GDB** is central to this ecosystem, but its [official source instructions](https://www.sourceware.org/gdb/current/) point to Sourceware. This search did not establish an officially endorsed standalone GitHub mirror, so an arbitrary mirror is not listed. ROCgdb is included for its separately evidenced GPU implementation.
- Plain editor adapters, command collections, tutorial debuggers, awesome lists, and duplicate engine lineages were not added to inflate coverage. Pwndbg, debugpy, and Ghidra were retained for the substantial abstractions and correctness responsibilities specifically described above.
- The report is selective rather than exhaustive: it does not provide dedicated coverage of HDL debugging, proprietary debugger engines, or every browser/VM debugger embedded in a larger runtime. Maintenance cadence was not exhaustively audited for every project; no general “actively maintained” label is inferred from an unarchived flag or recent push.
- Criteria assessments come from source contracts, architecture, and documented evolution. No performance claims were benchmarked, and no assumption is made that documented invariants are perfectly enforced in every execution path. Historical design documents and explicit limitations are identified where material to reuse.
