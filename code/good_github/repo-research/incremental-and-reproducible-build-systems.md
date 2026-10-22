# Incremental and reproducible build systems

Research date: **2026-10-09**.

This report selects 26 GitHub repositories for studying incremental dependency evaluation, reliable artifact reuse, reproducible build environments, and the schedulers and storage mechanisms underneath them. It includes complete build tools, reusable engines, and a few build-graph generators or package managers whose build subsystems are substantial. Incrementality, hermetic execution, and bit-for-bit reproducibility are different properties; inclusion does not imply that every tool provides all three. The criterion assessments below are engineering judgments grounded in the linked implementation and documentation, not endorsements of every component.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting different use cases. **C3** — concrete performance constraints addressed through understandable architecture. **C4** — sustained evolution accompanied by compatibility, testing, or complexity-management evidence. Every selection meets at least two criteria; unlisted criteria have not been independently established here.

## Large build graphs and cross-language execution

### 1. [bazelbuild/bazel](https://github.com/bazelbuild/bazel)

**Language / role:** Java core, C++ client, Starlark extensions; cross-language incremental build and test system.

Study the boundary between dependency evaluation and action execution. The [Skyframe architecture](https://bazel.build/reference/skyframe) explains immutable keys and values, functions that discover dependencies over multiple evaluations, and the mapping from filesystem observations to configured targets and actions.

- **C1:** Reads must become registered dependencies. An untracked filesystem read can produce a stale incremental result; unavailable dependencies cause a function to yield and restart rather than continue with incomplete inputs. Parallel execution relies on these dependency and side-effect constraints.
- **C2:** The same key/function/value machinery represents files, directory listings, packages, configured targets, and actions, giving an unusually broad example of a reusable incremental evaluator.
- **C3:** Bottom-up invalidation and change pruning avoid rebuilding downstream nodes when recomputation produces an unchanged value. The document also explains why mutating partially changed outputs is a harder correctness problem than rebuilding a node.

### 2. [facebook/buck2](https://github.com/facebook/buck2)

**Language / role:** Rust with Starlark rules; large-scale cross-language build system. The relevant subsystem is **DICE**, counted within this repository.

The [Modern DICE engineering walkthrough](https://buck2.build/docs/insights_and_knowledge/modern_dice/) is a useful account of how dependency tracking, equality, versioning, and asynchronous work fit together.

- **C1:** DICE records versions of computed values and their dependencies. Its central state-management thread coordinates invalidation and completed computations, providing a concrete design for reasoning about shared incremental state.
- **C2:** Clients supply keys, computations, and equality checks; the evaluator supplies dependency tracking and shared work. Language rules are separated from the Rust core through Starlark, as described in the [project introduction](https://buck2.build/docs/).
- **C3:** Shared computations, concurrent evaluation, and equality-based early cutoff reduce duplicate and downstream work. The walkthrough shows why merely caching leaf operations can leave directory traversal and aggregation as bottlenecks. Despite its expanded name, the walkthrough explicitly says DICE itself is not distributed.

### 3. [pantsbuild/pants](https://github.com/pantsbuild/pants)

**Language / role:** Python build rules and Rust engine; extensible build, test, and analysis orchestration.

Study the [rule-graph construction design](https://github.com/pantsbuild/pants/blob/main/docs/docs/contributions/development/internal-architecture.mdx), especially its distinction between the statically constructed rule graph and runtime memoized computations.

- **C1:** Rule construction must resolve implicit typed inputs without ambiguity. The documented parameter-consumption constraints, edge pruning, and final validation prevent incompatible rule combinations from becoming executable graphs.
- **C2:** Rules, queries, and parameters form a general typed computation framework rather than a collection of language-specific build commands.
- **C3:** Live-variable analysis and monomorphization minimize the parameters in runtime memoization keys. Large intermediate values need not themselves become hashed identities, reducing excessive invalidation and unnecessary key construction.

### 4. [thought-machine/please](https://github.com/thought-machine/please)

**Language / role:** Go; extensible cross-language build system with a restricted Python-like BUILD language.

The [technical FAQ](https://please.build/faq.html) explains the implementation choices behind its dependency graph, parser, and execution pipeline.

- **C1:** Explicit dependencies and input-content hashing determine whether outputs can be reused. The distinction between public BUILD/configuration compatibility and internal hash-format changes is especially useful when considering cache invalidation after upgrades.
- **C2:** Rules accommodate compilation, code generation, packaging, and tests across language ecosystems; the BUILD language is implemented inside the tool rather than delegated to an unrestricted Python process.
- **C3:** Parsing, building, and testing can overlap instead of waiting at global phase boundaries. The FAQ also describes assembling Java and Python packages from intermediate pieces to avoid repeated archive recompression.

### 5. [microsoft/BuildXL](https://github.com/microsoft/BuildXL)

**Language / role:** C# engine with native components; build acceleration, scheduling, and caching. Focus on the **pip graph and incremental scheduler**, rather than treating the entire monorepo as one uniform design.

The [incremental scheduling design](https://github.com/microsoft/BuildXL/blob/main/Documentation/Wiki/Advanced-Features/Incremental-Scheduling.md) documents both the optimization and cases where it must be restricted.

- **C1:** Dirty nodes imply dirty transitive dependents. Clean state is insufficient when outputs have not been materialized; shared output directories, uncacheable work, and filesystem journal changes require additional handling.
- **C3:** Filesystem change-journal records can prune work before fingerprint computation and cache lookup, saving overhead even when ordinary caching would already avoid execution. The document explains why distributed execution disables this particular optimization: a pruned producer's output may have been evicted from the shared cache.

This is a strong case study in the interaction between separate optimizations, rather than a blanket promise that they compose freely.

## Reproducible environments and content-addressed artifacts

### 6. [NixOS/nix](https://github.com/NixOS/nix)

**Language / role:** C++; functional package manager with a derivation-based build engine. The relevant subsystem is **derivation realization and the store**, not package recipes in other repositories.

The [build lifecycle specification](https://github.com/NixOS/nix/blob/master/doc/manual/source/store/building.md) follows builder setup, completion, and output registration in detail.

- **C1:** The specification addresses concurrent realizations, exclusive build locks, output-path handling, process completion, and what the builder can observe through its filesystem, environment, and network. It explicitly distinguishes sandboxed builds and exceptions such as fixed-output derivations.
- **C2:** Derivations describe executable builders with declared inputs and outputs; store objects and closures let this machinery serve diverse languages, toolchains, and software environments.
- **C3:** Deterministic execution is the foundation for transparent artifact reuse. The discussion of input addressing, content addressing, and output references exposes the costs and correctness constraints behind that abstraction.

Do not read sandboxing as proof that arbitrary builders produce byte-identical outputs; builder behavior still matters.

### 7. [apache/buildstream](https://github.com/apache/buildstream)

**Language / role:** Python; software-stack integration and sandboxed component builds.

Study the [cache-key architecture](https://github.com/apache/buildstream/blob/master/doc/source/arch_cachekeys.rst), alongside the [repository overview](https://github.com/apache/buildstream/blob/master/README.rst) for element-based integration of different underlying build tools.

- **C1:** Strong keys incorporate build dependencies' keys, while weak keys omit their versions. Non-strict reuse therefore sacrifices reproducibility guarantees; recovering a reused artifact's actual strong key requires its recorded build metadata, not recomputation from today's dependency definitions.
- **C2:** Source and element abstractions separate fetching, component construction, and software-stack composition. The same framework integrates application packages, toolchains, sysroots, and system images.
- **C3:** The explicit strict/non-strict distinction exposes a real rebuild-cost tradeoff. Storing artifacts under both key types also avoids unnecessary rebuilding when switching modes.

### 8. [moby/buildkit](https://github.com/moby/buildkit)

**Language / role:** Go; reusable build toolkit underlying container-image builds and other artifact workflows.

The [solver design](https://github.com/moby/buildkit/blob/master/docs/dev/solver.md) is a particularly detailed guide to graph identity, operations, cache lookup, and scheduling.

- **C1:** A vertex digest can deduplicate concurrent work, but is not automatically a valid persistent cache identity: an image named by a mutable tag can change between invocations. Stable source identities and operation-specific cache maps handle this distinction.
- **C2:** The solver separates graph vertices, executable operations, workers, results, and frontends. Its operation interface defines cache behavior independently from execution behavior.
- **C3:** Snapshot-content scans and remote transfers can dominate build time. The solver postpones expensive content hashing, loads only necessary cache records, and shares work across requests through an event-driven scheduler.

This makes it useful beyond Dockerfile syntax: the core subject is choosing how much work to perform before a cache decision is possible.

## Incremental engines and dependency-discovery models

### 9. [ninja-build/ninja](https://github.com/ninja-build/ninja)

**Language / role:** C++; low-level incremental executor, commonly fed generated build descriptions.

The [manual](https://ninja-build.org/manual.html) explains why policy belongs in a generator and documents depfiles, command changes, pools, `restat`, and dynamic dependencies.

- **C1:** The distinction between dependencies discovered for subsequent rebuilds and dependencies needed to order the first build is explicit. `dyndep` augments the graph before affected commands execute; `restat` can remove downstream work when output timestamps remain unchanged.
- **C2:** A small file-and-command graph supports many language frontends without embedding compilation rules in the executor.
- **C3:** Configuration decisions are moved out of the edit/build loop. The intentionally restricted execution format keeps parsing and no-op rebuild overhead central to the architecture.

Ninja's timestamp model and declared dependencies do not provide a hermetic environment by themselves.

### 10. [ndmitchell/shake](https://github.com/ndmitchell/shake)

**Language / role:** Haskell; programmable build-system library with dynamic dependencies.

The [architecture guide](https://github.com/ndmitchell/shake/blob/master/docs/Architecture.md) connects persistent records, key states, continuations, and rule implementations.

- **C1:** Length-prefixed append records allow incomplete trailing writes to be discarded after interruption. In memory, loaded/running/failed/ready states coordinate shared requests; continuations have an explicit exactly-once invocation invariant.
- **C2:** The engine is abstract over keys and values. File rules are an outer layer, allowing other dependency types to participate in the same execution machinery.
- **C3:** Suspended actions release execution capacity while awaiting dependencies, and separate built/changed versions support avoiding downstream work.
- **C4:** The [changelog](https://github.com/ndmitchell/shake/blob/master/CHANGES.txt) records evolution from at least 2018 through 2026: shared-cache atomicity fixes, database-corruption handling, dependency-checking improvements, explicit breaking changes, and tests against successive GHC versions.

### 11. [gittup/tup](https://github.com/gittup/tup)

**Language / role:** C; file-based incremental build system with runtime access tracking.

The [dependency walkthrough](https://github.com/gittup/tup/blob/master/docs/html/ex_dependencies.html) makes its unusual graph semantics concrete. The [historical technical report](https://github.com/gittup/tup/blob/master/docs/tech-report.html) supplies background on organizing updates around changed files; its old measurements are not treated as current benchmarks.

- **C1:** Observed reads discover ordinary file dependencies, but generated files still require declared ordering. Tup reports a missing generated-input dependency even when a command happened to succeed, because another execution order could fail.
- **C2:** File-access tracking applies to arbitrary commands and scripts rather than requiring a custom dependency scanner for every language.
- **C3:** Ordering edges and observed-use edges have distinct jobs. A declared prerequisite that was not actually read can establish safe execution order without forcing unnecessary rebuilding whenever that prerequisite changes.

### 12. [apenwarr/redo](https://github.com/apenwarr/redo)

**Language / role:** Python and shell; implementation of the recursive redo build model.

Study the [parallelism and interoperability discussion](https://github.com/apenwarr/redo/blob/main/docs/FAQParallel.md), especially shared subtargets reached from independently recursive invocations.

- **C1:** Global locks across redo instances prevent two parents from building the same subtarget simultaneously. The documentation also covers accidentally closed jobserver descriptors and a shuffle mode for exposing undeclared ordering assumptions.
- **C3:** Parallelism is coordinated across recursive processes through jobserver state instead of treating each recursive build as an independent pool. This is a compact counterpart to centralized graph engines, with explicit interoperability constraints when invoking Make-based subprojects.

**Status:** A quieter, historically significant implementation: the [repository API](https://api.github.com/repos/apenwarr/redo) reported its latest push as 2023-11-07 and did not mark it archived. No claim of current active maintenance is made.

### 13. [swiftlang/swift-llbuild](https://github.com/swiftlang/swift-llbuild)

**Language / role:** C++ with language bindings; embeddable build-engine libraries. Focus here is the **documented BuildEngine**, not every newer subsystem in the repository.

The [build-engine design](https://github.com/swiftlang/swift-llbuild/blob/main/docs/buildengine.rst) exposes subtle distinctions between scanning dependencies, executing tasks, and waiting for completion.

- **C1:** An old dependency is not necessarily still needed when a task reruns. The design explains why blindly scanning or executing all old inputs concurrently can do incorrect or unnecessary work, and distinguishes order-only barriers from persisted dependencies.
- **C2:** Clients dispatch their own work after an inputs-available callback and report completion through a concurrency-aware API. This keeps the engine separable from a particular scheduler or subprocess mechanism.
- **C3:** Dependency scanning overlaps other work so newly discovered ready tasks can start promptly. The document candidly describes limits on concurrent scanning within an individual task.

### 14. [evmar/n2](https://github.com/evmar/n2)

**Language / role:** Rust; separate implementation of a Ninja-compatible build executor, not a fork counted as another copy of Ninja.

The [design notes](https://github.com/evmar/n2/blob/main/doc/design_notes.md) are valuable for their explicit state machine and compatibility edge cases.

- **C1:** Readiness for dependency checking is distinct from being queued or running. Missing generated outputs, deleted historical inputs, and absent depfiles receive deliberate compatibility treatment. One authoritative state per build is supplemented by queues and counters for particular states.
- **C3:** Per-pool concurrency limits and a parser that reuses buffers and expands variables while parsing address startup and scheduling costs directly.

**Limits:** The notes describe unresolved non-UTF-8/path-safety concerns and call this hobbyist code; treat it as a study target, not evidence of universal production readiness. The [API](https://api.github.com/repos/evmar/n2) showed no archive flag and a latest push of 2025-11-10.

### 15. [metaborg/pie](https://github.com/metaborg/pie)

**Language / role:** Java; API and runtime for embedding incremental build scripts and interactive development pipelines.

Start with [ExecContext](https://github.com/metaborg/pie/blob/develop/core/api/src/main/java/mb/pie/api/ExecContext.java) and [BottomUpRunner](https://github.com/metaborg/pie/blob/develop/core/runtime/src/main/java/mb/pie/runtime/exec/BottomUpRunner.java). These are substantive engine components rather than a tutorial implementation.

- **C2:** Typed tasks, resource reads/writes, output stampers, and resource stampers let clients express dependencies on files or selected portions of returned objects. Hash-based resource stamps can ignore timestamp-only changes.
- **C3:** The bottom-up runner schedules work affected by changed resources, orders tasks using dependency information, and supports deferred work and observability. It demonstrates how an embedded engine can serve interactive requests without reevaluating an entire pipeline.

**Status:** The [repository API](https://api.github.com/repos/metaborg/pie) reported `develop` as the default branch, no archive flag, and a latest push of 2024-08-01. The report does not imply ongoing active development.

## Native-toolchain build models and graph generation

### 16. [build2/build2](https://github.com/build2/build2)

**Language / role:** C++; general-purpose build engine within the build2 C/C++ toolchain. This entry excludes the separately hosted package and project managers.

Study the [scheduler contract](https://github.com/build2/build2/blob/master/libbuild2/scheduler.hxx) with the [build-system manual source](https://github.com/build2/build2/blob/master/doc/manual.cli), which explains dependency extraction, compiler-option changes, and checksums for ignoring irrelevant source changes.

- **C1:** Nested waits, task counters, phase transitions, and lock release have explicit synchronization requirements. The scheduler documents deadlock hazards when a thread processes its own queue while waiting on another thread's counter.
- **C3:** The active-thread limit is distinct from the number of created threads. Suspending a master makes capacity available while preserving its ability to resume promptly; preprocessing and dependency extraction also serve change detection before recompilation.

**Hosting:** This is the project's official GitHub-hosted source copy; [README-GIT](https://github.com/build2/build2/blob/master/README-GIT) also directs developers to `git.build2.org`. Treat it as the official GitHub mirror/copy of that upstream, not a community fork.

### 17. [qbs/qbs](https://github.com/qbs/qbs)

**Language / role:** C++ with a QML/JavaScript project language; integrated graph construction and incremental execution.

The [manual source](https://github.com/qbs/qbs/blob/master/doc/qbs.qdoc) describes property tracking and persistent graphs; the [Rule reference](https://github.com/qbs/qbs/blob/master/doc/reference/items/language/rule.qdoc) shows how tagged artifacts connect generic transformers.

- **C1:** Rules can change their output sets. Qbs tracks used properties and deletes obsolete generated artifacts, addressing stale outputs and needless invalidation after configuration changes.
- **C2:** File tags, products, modules, and per-input or multiplex rules form reusable abstractions for compilers, generators, packaging, and different platforms.
- **C3:** Unchanged project descriptions reuse a serialized binary build graph, and stored output timestamps reduce filesystem calls during incremental builds.

**Official mirror:** The [project community page](https://qbs.io/community/) explicitly identifies GitHub as a mirror of its Qt-hosted main repository and describes community-led development after The Qt Company stopped working on it.

### 18. [mesonbuild/meson](https://github.com/mesonbuild/meson)

**Language / role:** Python; high-level build description and graph generation, commonly paired with Ninja. Its inclusion concerns dependency modeling and backend generation, not a claim that Meson itself executes Ninja's incremental scheduler.

The [generated-source guide](https://github.com/mesonbuild/meson/blob/master/docs/markdown/Generating-sources.md) provides precise examples of the graph that custom commands must create.

- **C1:** Linking a library does not imply that a consuming target depends on all of that library's generated headers. Each consumer must receive the relevant header dependency; multi-output generation must also preserve output identity and order.
- **C2:** `custom_target`, reusable generators, and `declare_dependency` compose generated files, libraries, and tool executables. Target-private generator output directories and shared custom targets express different ownership and reuse policies.

The [original design rationale](https://github.com/mesonbuild/meson/blob/master/docs/markdown/Design-rationale.md) is useful architectural history for the frontend/backend separation, but explicitly contains obsolete syntax and is not used as evidence of current API behavior.

### 19. [SCons/scons](https://github.com/SCons/scons)

**Language / role:** Python; programmable software-construction system.

Read the [Taskmaster implementation](https://github.com/SCons/scons/blob/master/SCons/Taskmaster/__init__.py) for the interface between dependency traversal, build decisions, execution, and user-facing behavior.

- **C1:** Execution runs on multiple threads, while preparation and completion handle state that is unsafe to mutate concurrently. A partial multi-target cache restore is explicitly cleaned up before rebuilding, including the case where restored files are read-only.
- **C2:** `Taskmaster` traverses the graph and creates tasks; customizable `Task` subclasses implement behavior such as normal builds, cleaning, and quiet queries. The code documents which behavior belongs in that extension interface rather than forcing callers to replace the engine.
- **C3:** Cache retrieval is integrated into task execution, and the module exposes graph-processing statistics for understanding repeated work and side effects.

## Language-oriented builds and reusable task APIs

### 20. [ocaml/dune](https://github.com/ocaml/dune)

**Language / role:** OCaml; composable OCaml build system with an independently structured engine and shared artifact cache.

Start with the [engine overview](https://github.com/ocaml/dune/blob/main/doc/explanation/tour/engine.rst) and the [cache design notes](https://github.com/ocaml/dune/blob/main/doc/dev/cache.md).

- **C1:** Concurrent writers use atomic file creation and handle races between lookup and insertion. Conflicting metadata for the same rule hash can identify nondeterministic rules; hardlink deduplication requires exclusive access to build artifacts while replacing them.
- **C2:** The engine is separated from rule generation and is documented as reusable by another frontend. Artifact metadata, content identities, and rule identities are also distinct concepts.
- **C3:** Content-addressed storage and hardlinks share artifacts across builds; trimming uses link counts to avoid deleting entries still referenced by build directories.

The design notes distinguish implemented behavior from unused/proposed value-cache entries and note that on-disk version paths have evolved.

### 21. [rust-lang/cargo](https://github.com/rust-lang/cargo)

**Language / role:** Rust; package manager and build orchestrator. Focus on **compilation-unit freshness and fingerprinting**, not rustc's internal incremental compiler.

The [fingerprint module](https://github.com/rust-lang/cargo/blob/master/src/compiler/fingerprint/mod.rs) contains extensive implementation documentation as well as the actual change-tracking code.

- **C1:** Fingerprints must propagate dependency changes, account for missing outputs, distinguish build scripts from normal compilation, and survive interrupted builds. Rewinding the freshness timestamp to build start conservatively detects edits made while compilation was running; failed compilation does not commit a fresh fingerprint.
- **C3:** Compact hashes support quick checks, diagnostic JSON explains invalidation, and translated dep-info files accelerate input scanning. The code explicitly discusses tradeoffs around filesystem timestamps and the limited environment information captured.

Cargo is included for substantive incremental orchestration. This source itself cautions that fingerprinting is not complete hermeticity or a guarantee of reproducible output.

### 22. [gradle/gradle](https://github.com/gradle/gradle)

**Language / role:** Java/Kotlin core with Groovy/Kotlin build APIs; extensible task automation and build caching.

The [cache concepts documentation](https://github.com/gradle/gradle/blob/master/platforms/documentation/docs/src/docs/userguide/optimizing-builds/build-cache/build_cache_concepts.adoc) explains the semantic information needed for safe reuse, while the [execution model](https://github.com/gradle/gradle/blob/master/architecture/build-execution-model.md) describes daemon request handling.

- **C1:** Cache identity includes task/action implementations and declared inputs. Overlapping output directories disable task-output caching because ownership, stale-file removal, and safe parallel execution become ambiguous.
- **C2:** Input normalization and path sensitivity are declared by consuming tasks, allowing different tasks to interpret the same artifacts differently rather than imposing one universal equivalence relation.
- **C3:** Java compile-classpath normalization can reuse work across ABI-compatible dependency changes; runtime-classpath normalization ignores irrelevant archive metadata. These are concrete examples of using domain semantics to avoid computation.

### 23. [com-lihaoyi/mill](https://github.com/com-lihaoyi/mill)

**Language / role:** Scala; JVM-oriented programmable build tool.

The [design principles](https://github.com/com-lihaoyi/mill/blob/main/website/docs/modules/ROOT/pages/depth/design-principles.adoc) explain how task graphs, persistent values, module hierarchies, and filesystem ownership reinforce each other.

- **C1:** Task dependencies are statically visible through an applicative model. Dedicated task output directories reduce conflicting filesystem effects; correctness of caching still relies on tasks respecting the documented purity discipline.
- **C2:** Typed tasks and modules provide compilation, packaging, cross builds, queries, and custom automation through the same graph abstraction. `PathRef` values connect files to value-based change detection.
- **C3:** Cached task results survive process restarts, and the hierarchy provides stable locations for output metadata. Static graphs permit pre-execution planning and parallelism without first running arbitrary dependency-discovery code.

### 24. [sakerbuild/saker.build](https://github.com/sakerbuild/saker.build)

**Language / role:** Java; language-independent incremental build runtime and extension APIs.

Study [TaskDependencyFuture](https://github.com/sakerbuild/saker.build/blob/master/core/common/saker/build/task/TaskDependencyFuture.java) together with [TaskOutputChangeDetector](https://github.com/sakerbuild/saker.build/blob/master/core/common/saker/build/task/dependencies/TaskOutputChangeDetector.java).

- **C1:** Reading a task result registers a dependency even when the upstream task fails. Dependency handles have explicit thread and lifetime constraints, and detector failures can conservatively be interpreted as changes.
- **C2:** A consumer can depend on a selected part of another task's returned object through a custom change detector, rather than inheriting coarse whole-task invalidation.
- **C3:** If an upstream task reruns but the field used by a consumer remains unchanged, the consumer need not rerun. This is a concrete, extensible early-cutoff mechanism at the task API boundary.

**Status:** The [API](https://api.github.com/repos/sakerbuild/saker.build) reported no archive flag and a latest push of 2025-01-01; current active maintenance is not assumed.

## Monorepo task graphs and process-result caching

### 25. [vercel/turborepo](https://github.com/vercel/turborepo)

**Language / role:** Rust core with TypeScript tooling; JavaScript/TypeScript workspace task orchestration.

The [caching guide](https://github.com/vercel/turborepo/blob/main/apps/docs/content/docs/crafting-your-repository/caching.mdx) documents cache contents, global versus task-specific fingerprints, dependency inputs, and worktree behavior.

- **C1:** Cache correctness must account for root workspace dependencies, lockfile changes, environment inputs, task definitions, and arguments. The guide explicitly assumes deterministic tasks and explains why restored artifacts containing absolute paths can be wrong in a different worktree.
- **C2:** Process-level caching applies to builds, tests, linters, and other workspace scripts. Declared output sets determine which files are restored, while terminal logs are captured separately.
- **C3:** Distinct global and task hashes allow relevant changes to invalidate the necessary scope; local and remote artifact reuse avoid rerunning expensive processes.

This is incremental orchestration over existing tools, with a declared-input contract rather than automatic filesystem isolation.

### 26. [nrwl/nx](https://github.com/nrwl/nx)

**Language / role:** TypeScript with Rust native components; project/task graph orchestration and extensible process-result caching.

Pair the [cache model](https://github.com/nrwl/nx/blob/master/astro-docs/src/content/docs/concepts/how-caching-works.mdoc) with the native hasher's [OnceCache implementation and tests](https://github.com/nrwl/nx/blob/master/packages/nx/src/native/tasks/hashers/once_cache.rs).

- **C1:** Concurrent hash-related computations share an initialization cell per key, compute outside the map lock, and allow retries after failed initialization instead of caching the error. Included tests check shared results and failure recovery.
- **C2:** Plugins infer target inputs and outputs, while project and workspace configuration can refine them. Hash inputs can include dependency files, runtime values, configuration, and command arguments across different underlying tools.
- **C3:** Reusable process results avoid execution, while the native compute-once cache avoids duplicate expensive preparation and deep copying under concurrent requests. This supplies a concrete implementation complement to the high-level cache model.

## Search coverage, verification, and limits

Discovery used more than six distinct live-web formulations, including: incremental/reproducible architecture and dynamic dependencies; hermetic Rust/Go build tools; Shake/Tup/redo dependency tracking; Nix/BuildStream/BuildXL/BuildKit artifact models; OCaml and Swift engines; smaller Ninja-compatible and C++ build tools; JVM and JavaScript monorepo caching; and the Pluto/PIE research lineage. Follow-up searches targeted Skyframe, DICE, Pants rule graphs, Cargo freshness, Ninja dynamic dependencies, and official hosting/mirror status. Later broad searches largely repeated these families or returned wrappers, tutorials, recipe collections, and peripheral projects; PIE was the final substantive addition.

All 26 canonical repository URLs were checked through the GitHub repository API. Each entry also rests on opened primary documentation or source beyond repository metadata; implementation contracts and design material, not search snippets or stars, drive the criteria. Source-tree paths were checked through fetched files or repository trees. The selected repositories were not marked archived when checked. Qbs is explicitly an official mirror; build2's official GitHub source copy and separate upstream are identified above. Quieter repositories have dated status notes rather than unsupported maintenance claims. Default-branch links are convenient reading entry points and may change after this research date.

The selection favors distinct architectures over an exhaustive catalog. It does not separately count Buck1, language-rule repositories, or multiple subsystems of one monorepo. Generic incremental-computation libraries without a concrete build-system focus, compiler-internal incremental algorithms, CI services, standalone remote-cache servers, and reproducibility auditors were outside the central scope. CMake and other substantial generators remain valid further reading; Meson represents that layer here. Guix/Lix searches did not establish an appropriate official substantive GitHub source for inclusion in this pass; third-party mirrors were not substituted. Tutorial-only PIE implementations and full-distribution recipe collections were also excluded in favor of the actual PIE engine and foundational build runtimes.

This was read-only source research: no candidate code was installed or executed, and no benchmark claims were independently reproduced. Historical design documents are labeled where relevant, and detailed implementation review is necessarily selective. The report is a guide to productive study, not proof that each tool's complete correctness or reproducibility claims hold for every platform and build recipe.
