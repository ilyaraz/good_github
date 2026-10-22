# Deterministic record-and-replay debuggers

Research date: **2026-10-09**.

This selection covers 14 GitHub repositories implementing deterministic execution recording and replay for debugging, including substantial replay engines and debugger integrations. It spans Linux processes, FreeBSD applications, whole-system emulation, managed runtimes, and parallel programs. Determinism is always relative to a system's supported inputs and execution model; restricted coverage is called out below. Monorepos are counted once, and their relevant subsystems are identified. Historical implementations are included for architectural study, without implying present-day usability or ongoing maintenance of their replay components.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, semantics, or failure modes. **C2** — substantial reusable abstractions supporting multiple use cases. **C3** — real performance constraints addressed through an understandable architecture. **C4** — sustained evolution with concrete compatibility, testing, or complexity-management evidence. Criterion assignments are engineering judgments grounded in the cited material, not certifications of every component.

## Native process recording and replay

### 1. [rr-debugger/rr](https://github.com/rr-debugger/rr)

**Language / role:** C++; Linux process-tree recorder and deterministic replay engine, normally used through GDB.

The strongest general starting point for studying deployable native replay. rr preserves instruction-level execution, memory, registers, and recorded kernel inputs. Its scope includes multiple processes and threads, but execution is serialized; shared memory with processes outside the recording tree is a documented limitation. These boundaries matter when evaluating whether a particular concurrency failure can be captured. [Project explanation and limitations](https://rr-project.org/).

- **C1:** Replay positions are more subtle than a single event number. `ReplayTimeline` combines trace time, ticks, step state, registers, and return-address information, and keeps breakpoint state separate from checkpoint state.
- **C2 / C3:** The same timeline abstraction supports explicit checkpoints, seeking, reverse continuation, and reverse stepping. Lazy marks and different checkpoint-density strategies address the cost of navigating long recordings. [Implementation entry point: `ReplayTimeline.h`](https://github.com/rr-debugger/rr/blob/master/src/ReplayTimeline.h).
- **C4:** Releases from 2018 through 2025 document trace portability, syscall coverage, AMD and AArch64 support, unexpected-exit fixes, release-testing infrastructure, and adaptation to Linux performance-counter permissions. This is compatibility work across years, rather than simply an old repository. [Release history](https://github.com/rr-debugger/rr/releases).

### 2. [sidkshatriya/rr.soft](https://github.com/sidkshatriya/rr.soft)

**Language / role:** C++ with compiler instrumentation; a substantively modified rr implementation using software progress counters.

Study this alongside rr to understand the consequences of replacing a hardware assumption. The `software-counters-mode` branch supports Linux x86-64 and AArch64 recording without hardware performance counters, using dynamic instrumentation and optional GCC/Clang instrumentation. It is counted separately because it implements a different progress-measurement mechanism, not merely packaging or editor integration. [Repository explanation](https://github.com/sidkshatriya/rr.soft#readme).

- **C1:** Instrumentation must preserve guest state while supplying deterministic ticks. The patcher contains architecture-specific branch stubs, jump-range and nearby-memory allocation handling, and exclusions for mappings that cannot safely be interpreted as ordinary instructions. [Implementation entry point: `Monkeypatcher.cc`](https://github.com/sidkshatriya/rr.soft/blob/software-counters-mode/src/Monkeypatcher.cc).
- **C2 / C3:** Software counting integrates into rr's existing performance-counter abstraction. Static instrumentation can reduce the fragility and cost of dynamic instrumentation, which remains the fallback for uninstrumented code. [Counter integration: `PerfCounters.cc`](https://github.com/sidkshatriya/rr.soft/blob/software-counters-mode/src/PerfCounters.cc).

The README explicitly acknowledges instrumentation overhead and fragility. Treat the inspected branch as a specialized variant with its own compatibility envelope; no speed equivalence to ordinary rr is claimed here.

### 3. [rrnewton/hermit](https://github.com/rrnewton/hermit)

**Language / role:** Rust; deterministic Linux execution environment with experimental recording, replay, and GDB integration.

This is the continued Hermit fork identified by the [original project's installation instructions](https://github.com/facebookexperimental/hermit#readme); the two repositories are not counted separately. Its scope goes beyond replay into reproducible scheduling and concurrency-failure analysis. The current README distinguishes deterministic execution from experimental record/replay and documents the tested limits of its debugger adapter. [Repository guide](https://github.com/rrnewton/hermit#readme).

- **C1:** The architecture requires each intercepted syscall effect to occur exactly once. It distinguishes emulation, injection, and tail injection, and explains ownership of per-thread, per-process, and global scheduling state. Replay checks trace-version compatibility; full raw-syscall comparison is enabled by `HERMIT_VERIFY`, not by every ordinary replay.
- **C2:** Reverie's execution-control mechanism is separated from Detcore's policy, while recorder and replayer sub-tools handle remaining external inputs. That division supports deterministic runs, recorded runs, seeded schedule exploration, and debugger access.
- **C3:** Selective seccomp interception avoids stopping on every syscall, and thread-local state avoids unnecessary global ordering. The architecture explicitly distinguishes implemented ptrace behavior from experimental alternative backends. [Architecture entry point](https://github.com/rrnewton/hermit/blob/main/docs/ARCHITECTURE.md).

Compatibility is workload- and mode-specific; the project's own experimental labels should be retained when considering deployment.

### 4. [fred-dbg/fred](https://github.com/fred-dbg/fred)

**Language / role:** Python plus C/C++; historical FReD reversible debugger built around DMTCP checkpoints and a custom record/replay layer.

FReD is particularly useful for studying how to add reverse operations to an existing debugger. Its published design searches an execution timeline for an expression's transition using checkpoints as landmarks. The paper reports debugger personalities for GDB, MATLAB, Perl, and Python. [Authors' architecture summary](https://arxiv.org/abs/1703.10864).

- **C1:** Its synchronization layer distinguishes recording, replay, and disabled modes; it manages per-process synchronization and input-data logs while avoiding accidental interception of the debugger itself or recursive allocation effects. [Implementation entry point: `synchronizationlogging.cpp`](https://github.com/fred-dbg/fred/blob/master/record-replay/synchronizationlogging.cpp).
- **C2 / C3:** `ReversibleDebugger` builds on debugger personalities and explicitly models branches, checkpoints, command histories, and reverse operations. These abstractions support timeline search without hard-coding every underlying debugger's interface. [Implementation entry point: `freddebugger.py`](https://github.com/fred-dbg/fred/blob/master/fred/freddebugger.py).

**Historical status:** GitHub metadata showed the last push in 2015. The source contains acknowledged command-expansion limitations, and the README requires a matching DMTCP record/replay build. It is a research implementation to study, not a verified installation recipe for current systems. [Repository metadata](https://api.github.com/repos/fred-dbg/fred).

### 5. [rcslab/castor](https://github.com/rcslab/castor)

**Language / role:** C/C++; FreeBSD application recorder/replayer with an LLVM pass and separate runtime libraries.

Castor offers a different native design from rr: instrumented applications communicate with the recording/replay process through shared memory. The replay manual describes replacing intercepted calls with logged results, stopping a replayed child for debugger attachment, and adding replay-time diagnostic calls when they introduce no new nondeterminism. [Replay manual entry point](https://github.com/rcslab/castor/blob/master/documentation/man/replay.txt).

- **C1:** Correctness crosses compiler instrumentation and runtime ordering: the LLVM pass handles atomic read-modify-write, compare-exchange, and atomic/volatile accesses; the thread runtime records creation and synchronization events and checks expected replay events. [Compiler pass](https://github.com/rcslab/castor/blob/master/lib/Pass/CastorPass.cc), [thread-event implementation](https://github.com/rcslab/castor/blob/master/lib/ThreadRuntime/events_thread.c).
- **C2 / C3:** Compiler pass, application runtime, thread runtime, and replay controller are separate components. Per-thread shared queues and configurable ordering modes expose concrete tradeoffs between serialization, multicore execution, and recording cost. The README distinguishes its global-counter development mode from TSX/TSC configurations. [Build and mode documentation](https://github.com/rcslab/castor#readme).

The inspected README targets FreeBSD 13.1 and Clang 15. The older manual contains stale compatibility text, so its architecture is useful evidence but its version guidance should defer to the README. Direct syscalls and code outside the instrumentation boundary can prevent faithful replay.

## Whole-system emulation

### 6. [qemu/qemu](https://github.com/qemu/qemu)

**Language / role:** Primarily C; the record/replay, instruction-counting, snapshot, and GDB-stub subsystems of QEMU. **Official GitHub mirror**; upstream contribution workflows live elsewhere.

QEMU's replay facility reproduces a virtual machine's execution, including guest memory and device state. It is valuable for understanding deterministic debugging below the operating-system boundary and across instruction sets. The repository is counted once, specifically for these subsystems.

- **C1:** Instruction counting supplies deterministic progress, while device inputs, clocks, and other nondeterministic events are logged. Block operations need the replay block driver; network backends need replay filters. These are correctness conditions, not incidental launch options.
- **C2:** Replay composes with the emulator's device stack, virtual-machine snapshots, monitor commands, and GDB remote protocol, supporting guest applications and system software.
- **C3:** Deterministic execution is recomputed instead of exhaustively logged. Reverse stepping restores a nearby snapshot and runs forward; reverse continuation searches snapshot intervals for earlier breakpoint hits. [Architecture and debugging entry point: official record/replay manual](https://www.qemu.org/docs/master/system/replay.html).

The mirror identifies itself as official. The replay documentation, rather than QEMU's much broader virtualization feature set, defines this entry's category fit.

### 7. [panda-re/panda](https://github.com/panda-re/panda)

**Language / role:** C/C++ and Python-facing tooling; a QEMU-derived whole-system analysis platform with its own replay and analysis infrastructure.

PANDA records a starting VM snapshot and a nondeterministic-input log, then allows repeated analysis of the same execution. It merits a separate entry from QEMU because its substantial plugin system, instrumentation interfaces, and replay-oriented analysis workflow have evolved into an independent platform. [Manual entry point](https://github.com/panda-re/panda/blob/dev/panda/docs/manual.md).

- **C1:** Replay depends on matching machine state, including memory size. Instrumentation changes can require translation-cache invalidation; the manual explains why failing to invalidate translated blocks can violate assumptions used by interrupt handling.
- **C2:** Analysis callbacks around translation and execution support taint tracking, operating-system introspection, string searching, and custom analyses over one recording. This is reusable execution-analysis machinery rather than a fixed trace viewer.
- **C3:** Memory callbacks and precise-PC tracking are optional because they impose overhead. The manual makes the relationship between translated-block caching, instrumentation, and replay explicit.

For interactive reverse debugging, the `checkpoint` plugin enables GDB reverse-step and reverse-continue, with instruction-count breakpoints available as well. [Time-travel debugging entry point](https://github.com/panda-re/panda/blob/dev/panda/docs/time-travel.md). PANDA's supported replay configurations are narrower than all architectures inherited from QEMU; the README also documents address-length restrictions on trace portability.

## Language runtimes and concurrent-program replay

### 8. [chakra-core/ChakraCore](https://github.com/chakra-core/ChakraCore)

**Language / role:** C++; the JavaScript engine's Time Travel Debugging subsystem, particularly `lib/Runtime/Debug/TT*` and the JsRT debugging API.

ChakraCore is a useful example of implementing replay inside a garbage-collected language runtime. Its host API exposes creation of recording and replay runtimes, stream callbacks, navigation modes, snapshot intervals, and retained snapshot history. [API entry point: `ChakraDebug.h`](https://github.com/chakra-core/ChakraCore/blob/master/lib/Jsrt/ChakraDebug.h).

- **C1:** Restoring execution requires reconstructing objects, types, closures, function bodies, debugger scopes, and promise-related state. Inflation maps reconnect identities, while pin sets prevent garbage collection of objects during restoration. [Implementation entry point: `TTInflateMap.h`](https://github.com/chakra-core/ChakraCore/blob/master/lib/Runtime/Debug/TTInflateMap.h).
- **C2:** JsRT makes recording storage and replay control available to embedding hosts through callbacks and explicit runtime operations, rather than tying the mechanism to one graphical debugger.
- **C3:** Configurable snapshot frequency and retained history make the tradeoff between storage, replay distance, and rewind coverage explicit in the API.

**Status:** This is the canonical successor to the former Microsoft repository. Its README describes the transition to a community project and Microsoft's support ending in 2021. That does not establish current support for every TTD embedding scenario. [Project status](https://github.com/chakra-core/ChakraCore#future-of-chakracore).

### 9. [pypy/pypy](https://github.com/pypy/pypy)

**Language / role:** RPython/Python and C; the historical RevDB translation and interpreter-support subsystems retained in the PyPy monorepo.

RevDB demonstrates implementing recording as a systematic translation transformation. It reexecutes deterministic managed-memory operations while replacing external operations and raw-memory reads with recorded results. The original PyPy announcement explains the reverse-debugger workflow and the separation between interpreter and controller. [Project's architectural explanation](https://pypy.org/posts/2016/07/reverse-debugging-for-python-8854823774141612670.html).

- **C1:** `gencsupp.py` distinguishes raw pointers from garbage-collected object identities and handles external callbacks and GIL transitions specially. This exposes the exact semantic boundary required for replay when object addresses can differ. [Translation entry point](https://github.com/pypy/pypy/blob/main/rpython/translator/revdb/gencsupp.py).
- **C2:** The translation support is separated from Python-specific debugger commands. The interpreter layer registers printing, backtraces, locals, breakpoints, object identities, and watch-expression operations against a command interface. [Interpreter entry point](https://github.com/pypy/pypy/blob/main/pypy/interpreter/reverse_debugging.py).

**Historical subsystem:** Inclusion is for substantial source still present in the official GitHub monorepo. It is not a claim that current PyPy distributions provide a supported RevDB product. The old standalone controller repository is not separately counted, and limitations in the early announcement should not be treated as a current compatibility matrix.

### 10. [bitslab/jmvx](https://github.com/bitslab/jmvx)

**Language / role:** Java; JMVX bytecode instrumentation and runtime supporting record/replay and multi-version execution.

JMVX records above the JVM implementation boundary, avoiding incidental differences caused by garbage collection and JIT compilation. Its README includes attaching a remote JVM debugger to the replayer, so replay is directly usable for diagnosis. The documented setup uses JDK 8. [Usage and debugging guide](https://github.com/bitslab/jmvx#readme).

- **C1:** Replaying application-level nondeterminism while allowing VM internals to vary requires careful interception boundaries. The replayer reconstructs class-loading data, static-initializer data, manifests, and recorded JAR mappings; these are concrete sources of divergence beyond simple method-return logging. [Implementation entry point: `Replayer.java`](https://github.com/bitslab/jmvx/blob/master/src/main/java/edu/uic/cs/jmvx/runtime/strategy/Replayer.java).
- **C2:** The replayer derives from the follower strategy, sharing execution machinery between offline replay and live multi-version execution.
- **C3:** The research artifact separates instrumentation, synchronization, recording, and replay experiments, and varies thread and buffer configurations. It explicitly warns that containerized performance may differ from the original bare-metal experiments. [Architecture and evaluation entry point](https://github.com/bitslab/jmvx/blob/master/artifact/artifact-readme.md).

This is a research system with explicit JDK assumptions, not a claim of transparent compatibility with arbitrary modern Java applications.

### 11. [smarr/SOMns](https://github.com/smarr/SOMns)

**Language / role:** Java/Truffle with Newspeak programs and TypeScript tooling; replay and Kómpos debugging infrastructure in a concurrency-research language implementation.

SOMns adds diversity at the programming-model level. Its replay implementation and tests address actors, CSP-style communication, threads and locks, and software transactional memory. The relevant research code inspected here is on `dev`; the repository's default branch is `release`. [Project and associated research](https://github.com/smarr/SOMns#readme).

- **C1:** External results are associated with actor and data identities, and the trace parser checks that an entity's replay events are not retrieved twice. Activity context must survive buffer switches so events remain associated with the correct concurrent activity. [Parser entry point](https://github.com/smarr/SOMns/blob/dev/src/tools/replay/TraceParser.java), [buffer implementation](https://github.com/smarr/SOMns/blob/dev/src/tools/replay/actors/UniformExecutionTrace.java).
- **C2 / C3:** A shared event representation and buffered recording layer support multiple concurrency models, rather than recording every machine instruction. The replay harness exercises both sender- and receiver-side actor tracing and several other models. [Replay tests](https://github.com/smarr/SOMns/blob/dev/tests/replay/test.sh).

This is a research runtime, not a general JVM application recorder. The harness contains disabled validation cases attributed to timer-thread incompatibility; its presence is evidence of exercised scenarios, not proof that all models or timing interactions work uniformly.

### 12. [PRUNERS/ReMPI](https://github.com/PRUNERS/ReMPI)

**Language / role:** C/C++, with Fortran interfaces and LLVM-based OpenMP instrumentation; parallel-program replay through the ReMPI and ReOMP subsystems, counted together.

ReMPI captures MPI event outcomes so a failing parallel execution can be replayed under TotalView. ReOMP separately records supported OpenMP synchronization and, when supplied with race-detector reports, identified racy accesses. This repository is especially useful for studying replay at communication and synchronization boundaries. [Supported operations and debugger workflow](https://github.com/PRUNERS/ReMPI#readme).

- **C1:** Replay must reproduce message matching, completion tests/waits, probe outcomes, and request bookkeeping. The recorder maintains validation information and separates recorded events from replay-consumption queues. [Implementation entry point: `rempi_recorder.cpp`](https://github.com/PRUNERS/ReMPI/blob/master/src/rempi/rempi_recorder.cpp).
- **C2 / C3:** PMPI interception, recorder logic, I/O threads, and encoders are distinct components. Optional Clock Delta Compression addresses trace-volume costs; its decoder tracks pending and unmatched events and epoch boundaries. [Compression entry point: `rempi_encoder_cdc.cpp`](https://github.com/PRUNERS/ReMPI/blob/master/src/rempi/rempi_encoder_cdc.cpp).

**Restricted determinism:** The MPI component does not capture arbitrary libc nondeterminism. Persistent-request and nonblocking-collective cases are documented as unsupported, and ReOMP cannot automatically discover all races. The README's broad MPI+OpenMP description must be read together with these component-specific limits.

## Substantial debugger and browser integrations

### 13. [go-delve/delve](https://github.com/go-delve/delve)

**Language / role:** Go; Delve's rr-backed recording/replay and GDB-remote integration, within a full Go debugger.

Delve supplies Go-aware inspection and stepping over rr recordings. It is not a second native recording engine: the recording substrate is rr. It is included because the integration sits inside a substantial debugger with its own target model, goroutine handling, breakpoint semantics, and replay lifecycle.

- **C1:** Replay integration must handle crashed recordings, restarts after process exit, reverse breakpoint counts, and checkpoints without losing Go debugger state. Dedicated tests cover these cases and ensure backward continuation terminates at the start of execution. [Test entry point: `rr_test.go`](https://github.com/go-delve/delve/blob/master/pkg/proc/gdbserial/rr_test.go).
- **C2:** The implementation connects rr's process and trace lifecycle to Delve's reusable `TargetGroup` and remote-process abstractions. It handles redirected I/O, trace discovery, protocol differences, and replay-server startup failures. [Implementation entry point: `rr.go`](https://github.com/go-delve/delve/blob/master/pkg/proc/gdbserial/rr.go).
- **C4:** The changelog records reverse instruction stepping in 2019, rr call injection in 2021, newer rr-version support in 2024, backend race/protocol fixes in 2025, and reverse-breakpoint fixes in 2026. [Dated compatibility history](https://github.com/go-delve/delve/blob/master/CHANGELOG.md).

### 14. [replayio/gecko-dev](https://github.com/replayio/gecko-dev)

**Language / role:** C++ and JavaScript, with other Gecko languages; Replay's modified browser, especially `toolkit/recordreplay` on `webreplay-release`.

This substantial Gecko fork is useful for understanding what a large browser must expose to a replay system: execution progress, ordered synchronization, JavaScript control, graphics, networking, recording completion, and unusable-recording reporting. It is counted for its browser implementation changes, not as an untouched mirror of Mozilla's tree.

- **C1:** Browser initialization itself can introduce nondeterminism. The implementation explicitly initializes lazily created mutexes at reproducible points and controls style-system threading; it also exposes divergence, event-disallowing, and side-effect controls. [Implementation entry point: `ProcessRecordReplay.cpp`](https://github.com/replayio/gecko-dev/blob/webreplay-release/toolkit/recordreplay/ProcessRecordReplay.cpp).
- **C2:** A driver interface separates browser-specific integration from replay machinery, while JavaScript control has explicit notifications for completed, unusable, and unsupported recordings. [JavaScript-control entry point](https://github.com/replayio/gecko-dev/blob/webreplay-release/toolkit/recordreplay/JSControl.h).

**Material limitation:** The source dynamically loads an external record/replay driver; this repository alone is not the complete replay engine. GitHub metadata showed its last push in March 2024, so this report treats it as a historical browser integration and makes no claim that it is Replay's current browser backend. [Repository metadata](https://api.github.com/repos/replayio/gecko-dev).

## Coverage, search process, and limitations

Discovery used more than six distinct live-web search formulations, followed by direct GitHub page/API and source reads. Search angles included native rr alternatives; JVM and Java failure reproduction; PyPy/Python reverse debugging; QEMU/PANDA whole-system replay; checkpoint-based FReD; FreeBSD Castor; MPI/OpenMP replay; browser and Chakra time travel; Rust/Hermit and rd; OCaml replay debugging; and actor/message-passing research. Public GitHub repository search helped locate less-indexed implementations such as JMVX. Additional broad searches increasingly returned the same projects, thin integrations, session viewers, and recent agent-debugging prototypes.

Selection boundaries and exclusions:

- UI-session playback, DOM reconstruction, saved debugger-command playback, and passive execution-trace viewers were not treated as deterministic program reexecution. This excludes many projects marketed as “time travel.” Likewise, deterministic testing alone was insufficient unless a concrete record/replay debugging path was established.
- Closed-source products such as Undo UDB, Pernosco, and WinDbg's recording engine were not represented by documentation/sample repositories. GDB was not assigned an invented official GitHub home: this search did not establish a qualifying official substantive GitHub mirror. These are GitHub-source limitations, not judgments about those tools.
- RevDB is represented by its substantive implementation inside the official PyPy repository, not an unavailable standalone GitHub repository. iReplayer and several historical academic systems were discovered through papers but not retained without a verified qualifying GitHub implementation.
- QEMU's official mirror is identified explicitly. PANDA and rr.soft have substantial distinct implementations; trivial forks are omitted. Only the continued Hermit repository is counted. Delve and Replay's Gecko fork are clearly labeled integrations, and the latter's external-driver dependency is material.
- Historical and research entries remain useful study material, but legacy toolchains, unsupported event classes, and incomplete replay coverage can make adoption expensive. Source inspection and documented tests support the architectural judgments; no candidate was built, executed, or benchmarked, and no numerical performance claims are inferred from stars or marketing.

All 14 repository identities were verified by opening the repository page or reading GitHub's API. Each retained repository has additional primary implementation or architectural evidence beyond its landing-page description. C4 is awarded only where dated compatibility history was actually inspected; recent pushes alone are not used to infer replay-subsystem maturity.
