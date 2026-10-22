# Command shells and process pipeline engines

Research date: **2026-10-09**.

This selection covers **26 GitHub repositories** that implement command languages, execute and supervise process pipelines, or provide substantial reusable machinery for those tasks. It spans conventional Unix shells, structured-data shells, embedded languages, formal semantics, parallelizing engines, and process-composition libraries. Terminal emulators, prompt themes, completion collections, generic workflow schedulers, and shell-programming tutorials are outside scope. A monorepo appears once, with its relevant subsystem identified.

Repository identities and archive status were checked through the GitHub API; the linked implementation and documentation files were opened and read. Links refer to the inspected branches and may change. The criteria below are evidence-based selection judgments, not claims that every component is exemplary or that the projects were independently tested during this research.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, language semantics, adversarial input, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or representations that serve multiple use cases.
- **C3 — Performance:** concrete resource or throughput constraints addressed through an understandable design.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or deliberate complexity management.

## Conventional shells and compatibility-oriented implementations

### [zsh-users/zsh](https://github.com/zsh-users/zsh)

**Language/role:** C and Zsh; Z shell source mirror. This is the shell implementation, not a configuration or plugin collection.

Study the relationship between a pipeline, its operating-system processes, and interactive job control. The implementation explains why suspending a command inside a function can require a separate shell process and linked “superjob” and “subjob” records.

- **C1:** The job-control code tracks process groups, terminal ownership, stopped/running states, and PID reuse. Its process lookup explicitly guards against confusing a terminated PID with a reused live PID, which could otherwise lead to an indefinite wait. Start with [`Src/jobs.c`](https://github.com/zsh-users/zsh/blob/master/Src/jobs.c).
- **C4:** The repository documents compatibility changes across many releases, including error-exit behavior, signal inheritance, and sh-emulation pipeline semantics. Its test organization separates parsing, substitutions, options, modules, editing, and completion, making long-term behavioral complexity visible. See the [compatibility notes in `README`](https://github.com/zsh-users/zsh/blob/master/README) and [test-suite guide](https://github.com/zsh-users/zsh/blob/master/Test/README).

### [ksh93/ksh](https://github.com/ksh93/ksh)

**Language/role:** C; the independently evolved ksh 93u+m continuation of AT&T KornShell. GitHub marks it as a fork, but its documented backports, new fixes, release policies, and compatibility work justify treating it as a substantive continuation. The abandoned ksh2020 line is not counted separately.

Study how a feature-rich shell can expose public extension interfaces while keeping parsing, variables, execution, and job control separate.

- **C2:** Public `nval.h` and `shell.h` interfaces support runtime builtins; name-value disciplines, compound variables, parse-tree serialization, and event callbacks are distinct subsystems. The [`DESIGN` document](https://github.com/ksh93/ksh/blob/dev/src/cmd/ksh93/DESIGN) maps these interfaces to their implementations.
- **C3:** The same design explains environment save/restore for subshells that avoid creating a process and shared read-only builtin metadata. These are concrete allocation/process-cost decisions, rather than an unsupported speed claim.
- **C4:** The [project policy and continuation history](https://github.com/ksh93/ksh/blob/dev/README.md) distinguish stable maintenance from development, preserve documented behavior, isolate some POSIX changes behind a mode, and require relevant regression tests. The [dated `NEWS`](https://github.com/ksh93/ksh/blob/dev/NEWS) records ongoing semantic, crash, and pattern-engine fixes.

### [magicant/yash](https://github.com/magicant/yash)

**Language/role:** C99; POSIX-oriented interactive and scripting shell. This entry covers the C implementation, not a separately counted rewrite.

Yash is useful for studying the boundary between standardized shell behavior and optional interactive extensions. Its [project overview](https://github.com/magicant/yash/blob/trunk/README.md) explicitly identifies the intended POSIX version and links the remaining conformance limitations.

- **C1:** The job table reserves a special active-job slot, asserts its lifecycle constraints, and separately manages current/previous jobs, continuation, waiting, and status calculation. [`job.c`](https://github.com/magicant/yash/blob/trunk/job.c) is a focused route into these invariants.
- **C4:** The [test guide](https://github.com/magicant/yash/blob/trunk/tests/README.md) distinguishes portable POSIX cases from Yash-specific cases and explains privilege-dependent skips, terminal-dependent serialization, and Valgrind testing. The [release history](https://github.com/magicant/yash/blob/trunk/NEWS) includes years of explicit compatibility changes, such as recategorizing builtins for POSIX-mode behavior in 2023, followed by later portability and correctness fixes.

### [tcsh-org/tcsh](https://github.com/tcsh-org/tcsh)

**Language/role:** C; official read-only source mirror of the C-shell-family interpreter. Its README identifies the upstream bug tracker and mailing list.

This provides a useful alternative to Bourne-family execution semantics and a compact case study in maintaining Unix process-control code across platforms.

- **C1:** `pjwait` blocks signals while inspecting job state, waits with `sigsuspend`, restores the terminal process group, and computes pipeline status while considering stopped, interrupted, and backquoted jobs. Read [`sh.proc.c`](https://github.com/tcsh-org/tcsh/blob/master/sh.proc.c).
- **C4:** [`Fixes`](https://github.com/tcsh-org/tcsh/blob/master/Fixes) records multi-year portability and compatibility work rather than merely version increments: terminal-dependent tests, history-merge regression testing, multibyte character handling, redirection behavior, and Cygwin resource limits. The platform branches in the process implementation show the corresponding maintenance burden.

### [fish-shell/fish-shell](https://github.com/fish-shell/fish-shell)

**Language/role:** Rust core and Fish scripts; interactive shell with its own language. The historical C++ core was ported to Rust for fish 4.0.

Study how typed process representations and a major implementation-language migration interact with user-visible shell behavior.

- **C1:** [`src/proc.rs`](https://github.com/fish-shell/fish-shell/blob/master/src/proc.rs) separates job/process bookkeeping from process launching and represents external commands, builtins, functions, and blocks explicitly. Its `ProcStatus` distinguishes absent, stopped, signaled, continued, and ordinary exit statuses, with platform-specific handling and assertions around synthesized statuses.
- **C4:** The [changelog](https://github.com/fish-shell/fish-shell/blob/master/CHANGELOG.rst) covers releases from well before the Rust migration through later fixes. The 4.0 notes explain which bindings and behaviors remain compatible, which change, and how to recover older behavior. Later pipeline fixes address function definitions changing while a pipeline is being started. This is unusually concrete material for studying migration without assuming behavioral equivalence comes automatically.

### [oils-for-unix/oils](https://github.com/oils-for-unix/oils)

**Language/role:** Python implementation source translated to C++, with C/C++ runtime support; OSH compatibility shell and YSH language in one repository.

The relevant subsystem is the shared shell frontend/runtime, including OSH word evaluation and YSH's alternative language semantics. Study the effort to make shell syntax amenable to conventional compiler tooling.

- **C1:** The [parser architecture](https://github.com/oils-for-unix/oils/blob/master/doc/parser-architecture.md) defines a lossless-token invariant and its test: concatenating all parsed token text must reconstruct the input. It then explains why here-documents, backticks, array assignment targets, and aliases complicate that invariant.
- **C2:** The [architecture notes](https://github.com/oils-for-unix/oils/blob/master/doc/architecture-notes.md) describe shared definitions and generated Python/C++ code, reusable lexer rules for related sublanguages, and explicit state machines for field splitting. These representations support execution and the planned source-transformation tools.
- **C3:** Regex-based lexers are compiled into C using re2c. The parser document connects this implementation choice to both execution efficiency and avoiding fragile character-by-character handling. Some architecture notes are explicitly unfinished; treat them as a map into the implementation rather than a complete current specification.

## Structured values and host-language integration

### [PowerShell/PowerShell](https://github.com/PowerShell/PowerShell)

**Language/role:** C# and PowerShell; cross-platform shell, language, and cmdlet runtime. This repository covers PowerShell 7+, not the maintained-in-place source of Windows PowerShell 5.1.

Focus on `System.Management.Automation/engine`, where object-producing cmdlets meet external programs and their byte streams.

- **C2:** [`Pipe.cs`](https://github.com/PowerShell/PowerShell/blob/master/src/System.Management.Automation/engine/Pipe.cs) unifies downstream command invocation, queued objects, enumerated inputs, external readers/writers, and output-variable collection. It documents configurable buffering and which connections must remain fixed once execution begins.
- **C1:** The pipe itself is explicitly not thread-safe; external reader/writer facilities provide the buffering boundary. [`NativeCommandProcessor.cs`](https://github.com/PowerShell/PowerShell/blob/master/src/System.Management.Automation/engine/NativeCommandProcessor.cs) adds synchronization between stopping and pipeline threads, process-initialization coordination, I/O-redirection decisions, and raw-byte pipe integration. These are useful examples of lifecycle correctness at the object/process boundary.

### [nushell/nushell](https://github.com/nushell/nushell)

**Language/role:** Rust; structured-data shell. Counted once, including its engine, command, protocol, and plugin crates.

The central study opportunity is the distinction between an immutable-looking value and a consumable stream.

- **C1:** [`PipelineData`](https://github.com/nushell/nushell/blob/main/crates/nu-protocol/src/pipeline/pipeline_data.rs) documents rejected designs in which cloning a value containing a stream would allow consumption through one alias to alter another. The current separation avoids that nonlocal observation effect and the locking it would otherwise require.
- **C2:** The same implementation gives commands a common input/output representation with separate empty, value, list-stream, and byte-stream variants, plus metadata and conversion operations. This supports both structured commands and native-process data without making all input a list or all input a byte string.
- **C3:** Streams preserve incremental and potentially unbounded processing, while concrete values remain independently usable. The source also distinguishes borrowed/moved metadata access from allocation-producing deep clones. The [crate map](https://github.com/nushell/nushell/blob/main/crates/README.md) provides a second entry point into the surrounding architecture.

### [elves/elvish](https://github.com/elves/elvish)

**Language/role:** Go; scripting language and interactive shell with value and byte pipelines.

Study an intentionally straightforward AST-to-operation-tree interpreter, alongside a more subtle pipeline execution model. The [architecture guide](https://github.com/elves/elvish/blob/main/docs/architecture/doc.go) explicitly says this interpreter design favors simplicity; it does not claim maximal performance.

- **C2:** Parsing, operation-tree evaluation, persistent collection values, builtin modules, the interactive editor, and history storage have identified package boundaries. The guide explains how these pieces are assembled rather than merely enumerating features.
- **C1:** In [`compile_effect.go`](https://github.com/elves/elvish/blob/main/pkg/eval/compile_effect.go), each inter-command connection has both an OS byte pipe and a value channel. Execution tracks ownership of each side, detects a departed reader, closes owned resources, joins concurrent forms, and aggregates exceptions. Background execution adds a separate completion/notification path.

### [xonsh/xonsh](https://github.com/xonsh/xonsh)

**Language/role:** Python; Python-based shell with subprocess syntax and callable aliases.

Focus on how a single execution object supports interactive commands, captured text, live pipeline objects, and Python-facing iteration.

- **C2:** The [subprocess guide](https://github.com/xonsh/xonsh/blob/main/docs/subprocess.rst) explains the different capture/blocking operators and their common `CommandPipeline` representation. A captured object can remain live until an output or status operation forces completion.
- **C1:** [`procs/pipelines.py`](https://github.com/xonsh/xonsh/blob/main/xonsh/procs/pipelines.py) handles partial launch failure, closing descriptors for stages that never started, restoring terminal ownership, and grouping real subprocesses for interrupt delivery. Callable aliases can run as Python threads, so the implementation treats them differently from process-group members. This makes host-language integration a concrete resource-management problem.

### [lmorg/murex](https://github.com/lmorg/murex)

**Language/role:** Go; shell and scripting language that carries type information alongside Unix-style pipelines.

Study how command implementations can operate across data formats without each builtin knowing every serialization format.

- **C2:** The [pipeline guide](https://github.com/lmorg/murex/blob/master/docs/user-guide/pipeline.md) describes typed connections compatible with ordinary Unix commands. The [`ReadArray` extension API](https://github.com/lmorg/murex/blob/master/docs/apis/ReadArray.md) supplies a shared, callback-based interface through which builtins consume individual elements from registered data types.
- **C3:** `ReadArray` explicitly distinguishes incremental readers from an `ArrayTemplate` fallback that unmarshals the entire input. It explains the latter's large-input cost and loss of streaming behavior, and shows a context-aware scanner implementation. This is valuable architectural guidance about where a typed shell preserves pipeline resource properties and where it cannot.

### [sammy-ette/Hilbish](https://github.com/sammy-ette/Hilbish)

**Language/role:** Go and Lua; extensible interactive shell using Lua for configuration and extension. The inspected README warns that Windows functionality is incomplete.

The distinctive subsystem is its shared job model for operating-system processes and Lua-driven work.

- **C2:** [`job.go`](https://github.com/sammy-ette/Hilbish/blob/master/job.go) exposes a Lua-facing job API while distinguishing process jobs from Lua jobs. Lua jobs supply run, suspend, and resume callbacks, allowing the shell's job interface to support more than external executables.
- **C1:** The implementation coordinates background reaping, foreground waits, completion channels, mutex-protected state, and job-table membership before emitting lifecycle hooks. Following these paths is useful for studying the race and state-transition obligations created by extensible job control.

The [changelog](https://github.com/sammy-ette/Hilbish/blob/master/CHANGELOG.md) is a second entry point for understanding API changes. This is an implementation study recommendation, not a claim that arbitrary Lua callbacks satisfy the same guarantees as OS process control.

## Scheme and Racket process languages

### [scheme/scsh](https://github.com/scheme/scsh)

**Language/role:** Scheme and C; long-standing Unix shell embedded in Scheme 48. Treat it as an architectural and historical study choice: GitHub's [metadata snapshot](https://api.github.com/repos/scheme/scsh) reported a last push in March 2024, and ongoing maintenance was not established.

- **C2:** The [process-notation reference](https://github.com/scheme/scsh/blob/master/doc/process-notation.scribble) specifies process forms, extended process forms, redirections, and multi-descriptor connections. Arbitrary Scheme computation and external commands can participate in a common process composition language.
- **C1:** The same reference carefully distinguishes Scheme ports from Unix descriptors: rebinding a Scheme output port does not automatically redirect descriptor 1. [`process-high-level.scm`](https://github.com/scheme/scsh/blob/master/scheme/process-high-level.scm) makes another tradeoff explicit: multi-stream collection uses temporary files to avoid pipe deadlocks, closes the write ports, and returns readable ports after the process completes.

These are especially useful sources for studying what can go wrong when a language runtime's I/O model is mapped onto Unix processes.

### [cosmos72/schemesh](https://github.com/cosmos72/schemesh)

**Language/role:** Chez Scheme and C; interactive Unix shell, Scheme REPL, and embeddable process-control library.

Study first-class jobs and compositional shell operations in a Scheme environment. Its structured-pipeline design also serializes individual Scheme values over ordinary connections, with format selection based on the destination.

- **C2:** [`shell/job.ss`](https://github.com/cosmos72/schemesh/blob/main/shell/job.ss) collects the job, command, expression, multi-job, environment, redirection, and pipeline interfaces. It supports both the interactive shell and programmatic creation/control of process compositions.
- **C1:** The [job-control reference](https://github.com/cosmos72/schemesh/blob/main/doc/shell/job-control.md) distinguishes waiting until a job exits from returning when it stops, allows an ostensibly asynchronous start to report that a very fast job already finished, and restricts certain attribute changes while jobs are running. These distinctions expose real lifecycle edge cases.

Documentation for some job-creation and status details is incomplete; the source is therefore an essential companion to the API reference.

### [willghatch/racket-rash](https://github.com/willghatch/racket-rash)

**Language/role:** Racket; Rash language/REPL, `shell-pipeline`, and the Linea reader in one repository. This is an older study candidate: the [API snapshot](https://api.github.com/repos/willghatch/racket-rash) reported a January 2024 last push, so current maintenance is not assumed.

- **C2:** The [mixed-pipeline specification](https://github.com/willghatch/racket-rash/blob/master/shell-pipeline/scribblings/mixed-pipeline.scrbl) separates Unix, object, and composite pipeline members. Composite members can expand into multiple execution stages, providing a reusable runtime beneath the language's pipeline macros.
- **C1:** The driver runs object stages serially but adjacent Unix stages concurrently, and passes a live output port into the next object stage. The specification makes exception propagation, synchronization, background execution, strictness, and the output transformer's responsibility to close the port explicit. [`subprocess-pipeline.rkt`](https://github.com/willghatch/racket-rash/blob/master/shell-pipeline/private/subprocess-pipeline.rkt) is the execution entry point.

Background semantics are marked unstable in the documentation; the attraction here is the mixed execution model and its visible contracts.

## Embeddable interpreters and executable semantics

### [mvdan/sh](https://github.com/mvdan/sh)

**Language/role:** Go; shell parser, formatter, expansion machinery, and interpreter. The relevant subsystem here is `interp`, not only the popular `shfmt` command. Parser dialect support is broader than the interpreter's documented Bash/POSIX execution target.

- **C2:** [`interp/api.go`](https://github.com/mvdan/sh/blob/master/interp/api.go) exposes a reusable runner with configurable command execution, filesystem access, and process-substitution handlers. [`handler.go`](https://github.com/mvdan/sh/blob/master/interp/handler.go) carries environment, working directory, source position, streams, and previous exit status through a common handler context.
- **C1:** The API documents that a runner is not safe for concurrent reuse, while background commands can concurrently write output. It also tracks process-substitution users and active substitutions, and differentiates command failures from fatal handler errors. The documentation explicitly says these hooks do not by themselves provide OS-level isolation, an important boundary when embedding the interpreter.

### [denoland/deno_task_shell](https://github.com/denoland/deno_task_shell)

**Language/role:** Rust; reusable cross-platform shell engine for Deno tasks. It implements a shell subset rather than promising full Bash compatibility.

- **C2:** [`execute.rs`](https://github.com/denoland/deno_task_shell/blob/main/src/shell/execute.rs) accepts parsed command lists, a shell state, custom `ShellCommand` implementations, and explicit input/output pipes. This separates the task-runner integration from the interpreter and allows embedding with captured or custom I/O.
- **C1:** The same executor joins pipeline stages, applies `pipefail` by selecting the rightmost failing stage, isolates subshell environment changes, and carries background handles to the appropriate parent. [`types.rs`](https://github.com/denoland/deno_task_shell/blob/main/src/shell/types.rs) implements hierarchical kill signals and drop guards, with tests for propagation to children and grandchildren.

An instructive limitation found during inspection: the short README's call example lagged the current function signature. Use the actual public executor and types as the implementation entry points.

### [mgree/smoosh](https://github.com/mgree/smoosh)

**Language/role:** Lem and OCaml, using libdash for parsing; executable formalization of POSIX shell semantics. This is a historical research implementation, not presented as a current daily-use shell. The [API snapshot](https://api.github.com/repos/mgree/smoosh) reported its last push in February 2023.

- **C1:** [`semantics.lem`](https://github.com/mgree/smoosh/blob/master/src/semantics.lem) exposes separate stepping relations for expansion, redirection, traps, and evaluation. Quoting/splitting modes and partially expanded states are explicit rather than buried in an execution loop. The repository also records unspecified POSIX cases and provides parser, semantic-unit, and shell-system tests.
- **C2:** The [`OS` abstraction](https://github.com/mgree/smoosh/blob/master/src/os.lem) parameterizes system calls, signals, process groups, file operations, and waiting over an OS state. The same semantics can consequently support actual execution and symbolic stepping, including the repository's visualization tool.

The study value is an inspectable semantic model and differential-testing apparatus; formalization should not be confused with a proof that every implementation dependency is correct.

## Parallel and graph-shaped process engines

### [binpash/pash](https://github.com/binpash/pash)

**Language/role:** Python compiler with shell/native runtime helpers; PaSh parallelizes shell-script dataflow regions.

- **C1:** The [compiler design](https://github.com/binpash/pash/blob/main/src/pash/compiler/README.md) explains the move from ahead-of-time processing to compilation interleaved with execution so that expansion sees the actual environment. It describes using command annotations to constrain transformations and falling back to the original region when compilation fails.
- **C2:** Its AST-to-dataflow-graph-to-AST structure separates discovering a parallelizable region from optimizing it and emitting executable shell. Runtime aggregators combine partial command results through reusable binary combiners.
- **C3:** The [runtime design](https://github.com/binpash/pash/blob/main/src/pash/runtime/README.md) identifies stream splitters, eager polling, aggregation, and dangling-FIFO cleanup as concrete machinery needed to make parallel pipelines useful. This is stronger evidence than reporting a headline speedup.

Some compiler-document links retain historical paths; the two linked documents themselves exist in the current package layout. The inspected [cleanup helper](https://github.com/binpash/pash/blob/main/src/pash/runtime/wait_for_output_and_sigpipe_rest.sh) also documents a single-output-node assumption, so this entry does not imply arbitrary shell graphs are safely parallelizable.

### [dspinellis/dgsh](https://github.com/dspinellis/dgsh)

**Language/role:** C and shell; the Directed Graph Shell suite, with Bash adaptations and a substantive negotiation/runtime library. Counted once for its separate graph-execution design, not as another copy of Bash. This is a research-oriented study choice; the [API snapshot](https://api.github.com/repos/dspinellis/dgsh) reported a May 2024 last push.

- **C2:** The [`dgsh_negotiate` API](https://github.com/dspinellis/dgsh/blob/master/core-tools/src/dgsh_negotiate.3) lets a component declare fixed or variable input/output descriptor requirements. Peers circulate these requirements, solve the connection constraints, allocate pipes, and return descriptors to individual tools. This extends linear pipelines to reusable scatter/gather components.
- **C1:** The API specifies protocol errors, early process failure, negotiation-time failure, and timeout behavior. [`negotiate.c`](https://github.com/dspinellis/dgsh/blob/master/core-tools/src/negotiate.c) makes graph edges, channel multiplicities, per-node connection solutions, and descriptor assignments explicit.

The engineering interest is the distributed setup protocol needed before data can flow, including why an apparently local command failure can strand the rest of a graph.

## Reusable process and pipeline libraries

### [oconnor663/duct.rs](https://github.com/oconnor663/duct.rs)

**Language/role:** Rust; composable child-process expressions and pipelines. The related Python implementation is not counted as another entry.

- **C2:** [`src/lib.rs`](https://github.com/oconnor663/duct.rs/blob/master/src/lib.rs) represents a command/pipeline as a clonable expression over shared internal structure. Piping, redirections, captured output, incremental reading, and deferred start compose over that representation rather than requiring hand-written process plumbing at every call site.
- **C1:** The implementation documents pipeline status precedence, checked versus unchecked failures, cleanup when the left process starts but the right fails to spawn, and the distinction between incremental reading and concurrent output capture. It explicitly warns that reading only one of several active children can deadlock the others.

Use the [API reference](https://docs.rs/duct/latest/duct/) alongside the source. The useful lesson is that a small-looking command API hides launch, waiting, and descriptor-lifetime semantics that must be defined precisely.

### [sindresorhus/execa](https://github.com/sindresorhus/execa)

**Language/role:** JavaScript with TypeScript-facing definitions; Node.js process execution and pipeline composition.

- **C2:** The [pipeline API](https://github.com/sindresorhus/execa/blob/main/docs/pipe.md) supports multiple sources and destinations, selected descriptors, progressive iteration, and intermediate results through `pipedFrom`. It also defines “unpipe” separately from terminating either process.
- **C1:** [`lib/pipe/streaming.js`](https://github.com/sindresorhus/execa/blob/main/lib/pipe/streaming.js) deliberately closes streams when a peer exits instead of automatically signaling the other process. It handles merged sources, listener accounting, and cleanup of destination associations. The distinction matters for programs that react to EOF/EPIPE versus programs that keep running without using the pipe.

This is a useful study in integrating Unix-like pipeline behavior with asynchronous stream and promise lifecycles, without assuming all failures should trigger identical cancellation behavior.

### [tomerfiliba/plumbum](https://github.com/tomerfiliba/plumbum)

**Language/role:** Python; shell combinators and local/remote command objects. Focus on the command subsystem rather than its separate CLI-application helpers.

- **C2:** [`commands/base.py`](https://github.com/tomerfiliba/plumbum/blob/master/plumbum/commands/base.py) builds pipelines and redirections from `BaseCommand` objects, preserving argument binding and the associated machine. The [project overview](https://github.com/tomerfiliba/plumbum/blob/master/README.rst) demonstrates how the same style applies to local and SSH-backed command execution.
- **C1:** The pipeline implementation closes the parent's unused upstream stdout so an early downstream exit can produce SIGPIPE, waits for both sides, closes residual streams after reaping, and distinguishes timeouts from command failures. Its source also admits a limit: distinct expected exit-code sets cannot currently be specified for individual pipeline stages.

Study this for the interaction between a convenient operator-based interface and the less convenient rules around EOF, return-code validation, and resource ownership.

### [byllyfish/shellous](https://github.com/byllyfish/shellous)

**Language/role:** Python; asyncio commands, pipelines, process substitution, and pseudo-terminal interaction.

- **C2:** [`pipeline.py`](https://github.com/byllyfish/shellous/blob/main/shellous/pipeline.py) uses an immutable pipeline value whose redirection operations replace the relevant first or last command. The same composition can be awaited, iterated, or entered as an asynchronous interaction context.
- **C1:** [`runner.py`](https://github.com/byllyfish/shellous/blob/main/shellous/runner.py) separates low-level redirection setup/cleanup from execution. Cancellation sends a configured signal, waits for process/task completion, escalates if necessary, and includes handling for cancellation during cleanup and platform-specific exit behavior. The documented contract considers cancellation complete only when the process exits.

This is particularly useful for studying why cancelling an asyncio task is not itself sufficient to finish supervising the operating-system process it launched.

### [babashka/process](https://github.com/babashka/process)

**Language/role:** Clojure; process and pipeline library for Clojure/JVM and Babashka.

- **C2:** [`process.cljc`](https://github.com/babashka/process/blob/master/src/babashka/process.cljc) provides dereferenceable process records containing streams, exit information, and predecessor links. Builders support creating a whole pipeline, inspecting all its stages, and checking their individual results.
- **C3:** The [pipeline guide](https://github.com/babashka/process/blob/master/README.md) distinguishes forwarding streams through successive `process` calls from `ProcessBuilder.startPipeline`, including a concrete buffering problem with a continuously running producer. This makes the data-transfer architecture and its latency consequences visible.
- **C4:** The [2022–2025 changelog](https://github.com/babashka/process/blob/master/CHANGELOG.md) records argument-parsing compatibility, relative program resolution on Windows, environment/path conversions, and shutdown-hook leak fixes. The source also contains explicit older-JDK fallbacks rather than assuming one process API is universally available.

### [amoffat/sh](https://github.com/amoffat/sh)

**Language/role:** Python; callable external commands with a substantial Unix process-launch and I/O implementation. The README explicitly excludes native Windows support.

- **C1:** The [architecture description](https://github.com/amoffat/sh/blob/develop/docs/source/sections/architecture.rst) separates the child/parent launch paths and uses dedicated pipes for pre-exec exceptions and synchronization after session/process-group setup. It also explains why output must continue draining after the child exits before stream supervision is complete.
- **C3:** Separate input and output/error threads handle simultaneous I/O; the output side uses readiness selection, while internal buffering controls delivery to queues, files, or callback handlers. The document makes the relationship between OS-level buffering and library-level buffering explicit.

Study this for the implementation beneath the [simple callable-command interface](https://github.com/amoffat/sh/blob/develop/README.rst): terminal behavior, stream handlers, child error reporting, and thread shutdown are distinct concerns. Buffer-size and platform details in older architecture prose should be checked against the target operating system rather than treated as universal guarantees.

## Search coverage, exclusions, and limits

Discovery used **24 live search formulations** across conventional POSIX shells and official mirrors; structured shells; Go/Lua/Python integrations; Scheme, Racket, and functional shell libraries; Rust and asyncio process composition; executable POSIX semantics; automatic parallelization; directed process graphs; and embedded task shells. Representative queries included `GitHub zsh official mirror ksh93 yash POSIX shell`, `GitHub shell Scheme scsh es rc rash shell`, `GitHub process pipeline Rust duct execa shellous plumbum`, `GitHub PaSh shell`, `GitHub Smoosh shell`, and `github directed graph shell dgsh pipeline negotiation`. Follow-up searches added dgsh and Deno's task-shell interpreter; later broad pipeline-engine searches mostly returned repeated candidates or general workflow/agent orchestration outside this scope.

Every retained canonical URL was checked through `api.github.com/repos/{owner}/{repo}`. Recursive source-tree indexes established the actual branch/path combinations, and selected raw source or documentation files were fetched and read. No candidate was cloned, installed, built, or executed. No selected repository was marked archived by the API at inspection time; that is not evidence of active maintenance. Scsh, Rash, Smoosh, and dgsh carry explicit recency qualifications, and the Zsh/tcsh mirror roles and ksh93 continuation are identified above.

Bash, dash, and mksh are important omissions: this search did not establish an official substantive GitHub mirror for each to the same evidentiary standard, so unrelated or unofficial repositories with familiar names were not substituted. The similarly named `danishprakash/dash` tutorial implementation was excluded. Other exclusions included shell themes and completion frameworks, thin command wrappers, demonstration-only shells, broad DAG/workflow schedulers, and duplicate implementations or upstream snapshots already represented by a substantive continuation. Functional libraries such as Turtle/Shelly and further rc/es-family implementations remain possible additions; this is a diverse selection, not a census.

Correctness and reuse claims describe visible contracts and implementation mechanisms. Performance criteria concern documented streaming, buffering, process creation, and parallelization choices; no numerical speedup is claimed. Maintenance judgments do not follow from stars, repository age, or a recent push alone. Some research documents retain historical paths or incomplete sections, and those limitations are called out where they affect the recommended reading route.
