# Automated test case reduction tools

Research date: **2026-10-09**.

This report selects 25 GitHub repositories implementing automated reduction of a failure-inducing input, program, or generated counterexample. It includes standalone reducers and substantial reduction subsystems inside compiler and property-testing projects. It excludes test-suite selection, ordinary source minification, Git history bisection, and corpus deduplication without individual-input reduction. Each monorepo appears once; the relevant subsystem is identified explicitly.

Reduction generally preserves an **oracle's observation**, not all program semantics and not necessarily the underlying bug's identity. “Minimal” below means the result of the implemented search and its transformations, rather than a universal guarantee of the globally smallest reproducer. The study recommendations and criterion assessments are grounded engineering judgments, not claims that every component is exemplary.

## Criteria legend

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or subtle failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or representations supporting multiple reduction tasks.
- **C3 — Performance with structure:** concrete mechanisms addressing expensive tests, search cost, memory, or parallel execution.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or complexity management; age alone does not qualify.

Canonical repository locations and archival status were checked through GitHub repository pages or the GitHub API. Status remarks are snapshots; inclusion without an archival warning does not imply a particular maintenance commitment.

## General-purpose engines and transformation pipelines

### 1. [csmith-project/creduce](https://github.com/csmith-project/creduce)

**Language / role:** Perl orchestration and C++ transformation tooling; standalone C/C++ program reducer, also usable for other textual languages.

Study how a domain-independent search driver combines language-aware transformations with an external interestingness test. The [driver](https://github.com/csmith-project/creduce/blob/master/creduce/creduce.in) schedules initial passes, iterates the main passes to a size-based fixed point, and then performs cleanup.

- **C1:** Parallel oracle execution introduces cancellation, resource contention, and timeout problems. The driver documents deterministic-oracle expectations and reduction-induced infinite loops; the [README](https://github.com/csmith-project/creduce/blob/master/README.md) explains isolated temporary directories and why killing compiler workers can leave temporary files behind.
- **C2:** Transformation operators are separate Perl modules, and pass priorities and inclusion can be configured independently of the oracle. This separation is useful for studying an extensible reducer whose core need not understand C syntax.

The inspected GitHub metadata reported its last push in June 2024; no claim of current active maintenance is made.

### 2. [marxin/cvise](https://github.com/marxin/cvise)

**Language / role:** Python orchestration with C++/LLVM and additional parsing components; a separately evolved C-Reduce port.

C-Vise merits a separate entry because it replaces the orchestration implementation and adds substantive scheduling and multi-file reduction machinery. Its repository README currently says it is **looking for maintainers**.

- **C2:** The [pass manager](https://github.com/marxin/cvise/blob/master/cvise/cvise.py) loads configurable pass groups, distinguishes initial, interleaved, main, and cleanup stages, and registers transformations for includes, Makefiles, files, syntax trees, and ordinary text. These are useful abstractions for reducing whole build reproducers.
- **C3:** The [testing scheduler](https://github.com/marxin/cvise/blob/master/cvise/utils/testing.py) separates pass initialization, candidate transformation, oracle execution, and advancement after success into worker operations. Futures, pass contexts, temporary environments, timeouts, and process notifications make the parallel implementation inspectable beyond a simple worker-count switch.

Shared ancestry with C-Reduce is explicit; this is not an unmodified fork counted twice.

### 3. [CyberShadow/DustMite](https://github.com/CyberShadow/DustMite)

**Language / role:** D; general-purpose file-set reducer originating in D compiler debugging.

Study a comparatively concentrated implementation that represents inputs as trees and supports removal, unwrapping, concatenation, word replacement, and swapping.

- **C2:** The [splitter implementation](https://github.com/CyberShadow/DustMite/blob/master/splitter.d) provides a common entity representation for entire files, lines, words, NUL-separated records, D syntax, unified diffs, indentation, and Lisp-like inputs. This makes it useful beyond a single compiler language.
- **C3:** The [reduction driver](https://github.com/CyberShadow/DustMite/blob/master/dustmite.d) implements parallel look-ahead slots, test-result caches in memory and on disk, and a chronological cache for applying reductions to input trees. Timing categories distinguish candidate construction, saving, testing, and look-ahead waits.

This is a useful entry point for studying how representation choices, speculative testing, and filesystem costs interact in a standalone tool.

### 4. [MozillaSecurity/lithium](https://github.com/MozillaSecurity/lithium)

**Language / role:** Python; line/character reduction and additional strategies used in browser test reduction.

Lithium exposes reduction as a conversation between a candidate iterator and an external test, rather than burying all behavior inside one loop.

- **C2:** [Strategies and reduction iterators](https://github.com/MozillaSecurity/lithium/blob/master/src/lithium/strategies.py) separate candidate generation, feedback, best-known input, and strategy-specific options. This supports chunk deletion and more specialized transformations under the same interface.
- **C1:** The [testcase representation](https://github.com/MozillaSecurity/lithium/blob/master/src/lithium/testcases.py) distinguishes reducible parts from protected content and translates reduction-relative slice indices into physical positions. It also detects mismatched reduction-region markers. These details matter when shrinking a test body while retaining its harness.
- **C3:** The iterator records hashes of tried inputs, avoiding repeated oracle work, while the default algorithm proceeds from large chunks toward single units and repeats successful fine-grained rounds.

### 5. [renatahodovan/picire](https://github.com/renatahodovan/picire)

**Language / role:** Python; reusable delta-debugging library and CLI.

Picire is a strong place to study the algorithmic core independently of parsing or compiler-specific transformations.

- **C2:** The [base algorithm](https://github.com/renatahodovan/picire/blob/master/src/picire/dd.py) accepts testing, splitting, configuration ordering, content construction, caching, and stopping behavior as separate collaborators. It supports reduction of abstract configurations as well as text.
- **C3:** [ParallelDD](https://github.com/renatahodovan/picire/blob/master/src/picire/parallel_dd.py) mixes subset and complement checks, bounds submitted work using a thread pool, and wraps the outcome cache with a lock. The distinction between configuration indices, reconstructed test content, and oracle outcomes is especially instructive.

The implementation is reusable infrastructure rather than a grammar reducer: applications decide how a selected configuration becomes a runnable test.

### 6. [googleprojectzero/halfempty](https://github.com/googleprojectzero/halfempty)

**Language / role:** C; byte-oriented parallel test-case minimizer. **Archived repository.**

Halfempty is worth studying for its speculative execution model even though it is a historical project.

- **C3:** The [design explanation](https://github.com/googleprojectzero/halfempty/blob/master/README.md) describes pessimistic speculation: idle workers explore likely future bisection steps instead of waiting for every preceding test. This directly addresses a dependency bottleneck in expensive oracle runs.
- **C1:** The [bisection implementation](https://github.com/googleprojectzero/halfempty/blob/master/bisect.c) distinguishes a task's immediate parent from its most recent successful source ancestor. Candidate bytes must come from the latter, because unsuccessful speculative deletions must not contaminate later inputs. Offset and chunk-size transitions depend on whether the parent succeeded.

The architectural value is in managing speculative search state; the report does not adopt the README's workload-specific speedup figures as general performance guarantees.

### 7. [DRMacIver/shrinkray](https://github.com/DRMacIver/shrinkray)

**Language / role:** Python; multi-format, parallel standalone reducer.

Shrink Ray combines generic and format-specific passes. Its [README](https://github.com/DRMacIver/shrinkray/blob/main/README.md) explicitly makes limited compatibility promises, making it a design study rather than an assumption of a stable embedding API.

- **C1:** The [parallelism design](https://github.com/DRMacIver/shrinkray/blob/main/notes/parallelism-model.md) describes serializing accepted-result commits, rechecking candidates when nondeterminism handling changes, associating verification evidence with the correct incumbent, and protecting persistence from cancellation.
- **C3:** The same design uses Trio structured concurrency, bounded channels and semaphores, controlled speculative prefetch, and a global oracle limiter. It explicitly accounts for stale successful tests and bounded result buffering behind slow earlier work.

This is particularly useful for engineers building reducers that must remain responsive while managing subprocesses, progress reporting, restarts, and accepted-result persistence.

## Syntax-guided and research search engines

### 8. [uw-pluverse/perses](https://github.com/uw-pluverse/perses)

**Language / role:** Kotlin/JVM reduction core with grammar infrastructure; multi-language syntax-directed program reducer.

The [project documentation](https://github.com/uw-pluverse/perses/blob/master/README.md) explains how ANTLR grammar information constrains candidate generation and supports languages ranging from C and Rust to SQL, SMT-LIB, and XML. The alternative `perses-project/perses` location redirected to the canonical repository above when checked.

- **C2:** Grammar-based language support separates syntactic structure from the external property being preserved, allowing a common reduction framework to serve many languages and compiler tools.
- **C3:** The [test-script executor](https://github.com/uw-pluverse/perses/blob/master/src/org/perses/reduction/TestScriptExecutorService.kt) separates candidate-output construction from script execution, supports prechecks and postchecks, reuses a global execution cache, and tracks submissions, actual executions, and cache hits. Futures, cancellation, and temporary working directories are explicit parts of the execution model.

Study the relationship between syntax-aware search and the cost of materializing and validating each candidate.

### 9. [renatahodovan/picireny](https://github.com/renatahodovan/picireny)

**Language / role:** Python with ANTLR integration; hierarchical delta-debugging framework built on Picire.

Picireny is a separate tree-reduction layer, not a duplicate implementation of Picire's flat configuration search.

- **C2:** The [HDD driver](https://github.com/renatahodovan/picireny/blob/master/src/picireny/hdd.py) accepts reducer and tester classes, configuration filters, caches, unparsing policy, and a sequence of transformations. It traverses tree levels and optionally repeats to a fixed point.
- **C1:** [Hoisting](https://github.com/renatahodovan/picireny/blob/master/src/picireny/hoist.py) searches descendants with matching node names, tests replacement mappings before adopting them, and rebuilds the tree after accepted changes. This is a useful example of preserving structural compatibility while simplifying nested inputs.

The HDD driver's stated 1-tree-minimal result is conditional on its fixed-point mode and lack of a configuration filter; it should not be read as a universal global-minimum promise.

### 10. [langston-barrett/treereduce](https://github.com/langston-barrett/treereduce)

**Language / role:** Rust reduction core; tree-sitter-based reducers for several languages.

The [overview](https://langston-barrett.github.io/treereduce/overview.html) highlights support for malformed input through tree-sitter's error-tolerant parsing. Syntax awareness here does not mean every candidate is guaranteed syntactically valid.

- **C1:** The [reduction engine](https://github.com/langston-barrett/treereduce/blob/main/crates/treereduce/src/reduce.rs) represents accepted edits with versions, identifies stale work, and retries when another worker has changed the shared incumbent. This is a concrete concurrency problem in parallel minimization.
- **C3:** The same engine uses a prioritized task heap, scoped worker threads, locks, and condition variables. Candidate exploration and deletion/replacement work share a structured scheduling system rather than independent subprocess launches alone.

Study it alongside Perses to compare tolerant parse trees with grammar-constrained candidate generation, without relying on cross-project benchmark claims.

### 11. [Amocy-Wang/ProbDD](https://github.com/Amocy-Wang/ProbDD)

**Language / role:** Python and C++; historical ESEC/FSE 2021 research artifact for probabilistic delta debugging.

This repository bundles modified Chisel and Picire/Picireny implementations. It is retained for its separately implemented search algorithm, not as another entry for those upstream frameworks.

- **C2:** The [change documentation](https://github.com/Amocy-Wang/ProbDD/blob/main/CHANGES.md) identifies how ProbDD replaces the search core in both a C/C++ reduction pipeline and a hierarchical reducer. It distinguishes algorithm changes from token counting and experiment logging.
- **C3:** The [probabilistic engine](https://github.com/Amocy-Wang/ProbDD/blob/main/hdd_ProbDD/picire/picire/abstract_probdd.py) maintains per-element probabilities, chooses deletion sets using a probability-based objective, updates beliefs after observations, and reuses test history. It exposes the tradeoff between oracle cost and adaptive search decisions.

The inspected Python implementation uses Python 2 syntax. Treat it as an algorithm and reproducibility study, not a current drop-in library; no universal minimality or speedup claim is inferred from its comments.

## Domain-specific reducers

### 12. [ucla-pls/jreduce](https://github.com/ucla-pls/jreduce)

**Language / role:** Haskell; Java class-file and JAR reduction. **Historical implementation:** GitHub metadata reported the last push in October 2021.

JReduce is valuable for studying dependency-aware reduction below source level. Its [usage documentation](https://github.com/ucla-pls/jreduce/blob/master/README.md) covers isolated predicate workspaces, preserved output/exit behavior, classpaths, protected core classes, and alternative reduction strategies.

- **C1:** The [logical reduction implementation](https://github.com/ucla-pls/jreduce/blob/master/src/JReduce/Logic.hs) models facts about classes, inheritance, fields, and methods, then calculates logical or graph closures. Removing bytecode elements therefore becomes a dependency problem rather than arbitrary byte deletion.
- **C2:** The same implementation refines generic reduction problems through mappings between program items, logical variables, graphs, and reconstructed targets. Engineers can study how several search representations share a common predicate-driven reduction interface.

It is particularly relevant when a reproducer is available as compiled classes rather than source.

### 13. [wala/jsdelta](https://github.com/wala/jsdelta)

**Language / role:** JavaScript/Node.js; JavaScript and JSON reducer. **Historical implementation:** GitHub metadata reported the last push in May 2022.

JS Delta reduces AST structures and supports programmable predicates suitable for crashes, output checks, and static-analysis timeouts.

- **C2:** The [single-input engine](https://github.com/wala/jsdelta/blob/master/src/delta_single.js) separates parsing, tree minimization, predicate evaluation, accepted candidates, and transformation passes. It iterates AST reduction and external transformations when fixed-point reduction is requested.
- **C1:** The engine adds a syntax-validity guard for JSON, whose valid roots differ from JavaScript's. The [transformation layer](https://github.com/wala/jsdelta/blob/master/src/transformations.js) compares consistently pretty-printed sizes before accepting a transformed candidate, explicitly enforcing progress to prevent transformation fixed-point loops.

Study how a tool can reuse JavaScript parsing infrastructure without assuming JavaScript and JSON have identical validity rules.

### 14. [ddsmt/ddSMT](https://github.com/ddsmt/ddSMT)

**Language / role:** Python; SMT-LIB and related solver-input reduction.

ddSMT provides theory-aware simplification without confusing “preserve the observed solver failure” with “preserve satisfiability.”

- **C1:** The [mutator guide](https://github.com/ddsmt/ddSMT/blob/master/docs/guide-mutators.rst) explains when transformations need sorts, declared symbols, indexed operators, or coordinated changes across an entire input. It explicitly states that mutators need not preserve equivalence or satisfiability.
- **C2:** That guide defines a reusable interface for applicability filters, local mutations, and global mutations, with families for bit-vectors, arithmetic, floating point, strings, datatypes, and generic syntax.
- **C3:** The [strategy design](https://github.com/ddsmt/ddSMT/blob/master/docs/guide-strategies.rst) distinguishes batched ddmin, hierarchical traversal, and a hybrid sequence. It stages aggressive top-level changes before more expensive fine-grained mutations.

This is an especially useful codebase for understanding how semantic information can improve reduction without turning the reducer into an equivalence prover.

### 15. [credativ/sqlreduce](https://github.com/credativ/sqlreduce)

**Language / role:** Python; PostgreSQL query reduction using PostgreSQL-derived parsing.

SQLreduce is focused on shrinking a query that produces an error; it is not a general optimizer preserving query results.

- **C1:** The [algorithm walkthrough](https://github.com/credativ/sqlreduce/blob/master/docs/howitworks.md) describes parsing with pglast/libpg_query, modifying parse trees, rendering SQL, and rejecting candidates that yield a different error. Its worked example shows why “the query still fails” is too weak an acceptance condition.
- **C4:** The [dated package changelog](https://github.com/credativ/sqlreduce/blob/master/debian/changelog) records work from 2022 through 2026 adapting to pglast versions, updating tests, and handling an AST-field change from `returningList` to `returningClause`. This is direct evidence of compatibility management across parser evolution.

Study the boundary between a database-specific failure oracle and a structured query simplifier, including its dependency on the database environment.

### 16. [scipopt/MIP-DD](https://github.com/scipopt/MIP-DD)

**Language / role:** C++; delta debugging of mixed-integer programming problems and solver settings.

MIP-DD extends this category beyond source programs. Its [design and usage documentation](https://github.com/scipopt/MIP-DD/blob/main/README.md) describes reducing constraints, variables, coefficients, objectives, bounds, and settings while preserving a reference solution's feasibility, though not necessarily its optimality.

- **C1:** The [solver interface](https://github.com/scipopt/MIP-DD/blob/main/src/bugger/interfaces/SolverInterface.hpp) distinguishes primal, dual, objective, completion, and certification failures. It parameterizes arithmetic and implements tolerance-aware comparisons against reference values, making numerical correctness central to reduction.
- **C2:** Solver adapters separate setup, solving, instance I/O, settings, and effort measurement from the generic reduction process; SCIP and SoPlex are documented integrations.
- **C3:** The documented batch-count adaptation uses measured solving effort to control the expense of repeated oracle calls. Solver limits can also be restricted with a variability margin.

## Reducers embedded in compiler and fuzzing infrastructure

### 17. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**Language / role:** C++; specifically the **llvm-reduce** subsystem for LLVM IR and MIR. The monorepo is counted once.

The [command guide](https://github.com/llvm/llvm-project/blob/main/llvm/docs/CommandGuide/llvm-reduce.md) documents external interestingness scripts, configurable delta passes, repeated pass iterations, parallel jobs, and validity diagnostics.

- **C1:** The [delta engine](https://github.com/llvm/llvm-project/blob/main/llvm/tools/llvm-reduce/deltas/Delta.cpp) verifies candidate work items before testing them and can abort on invalid reductions. It also checks whether counting candidate chunks unexpectedly changed interestingness, exposing either a flaky oracle or a reducer bug.
- **C2:** A reduction pass uses an oracle to select which chunks to retain, separating structural extraction from the general reduction search.
- **C3:** Parallel work can reconstruct candidates from serialized bitcode in separate LLVM contexts. This provides a concrete architecture for avoiding unsafe sharing of mutable compiler IR during concurrent tests.

### 18. [WebAssembly/binaryen](https://github.com/WebAssembly/binaryen)

**Language / role:** C++; specifically **wasm-reduce** inside the Binaryen toolchain.

The [project documentation](https://github.com/WebAssembly/binaryen/blob/main/README.md) identifies the reducer separately from the optimizer. The [implementation](https://github.com/WebAssembly/binaryen/blob/main/src/tools/wasm-reduce/wasm-reduce.cpp) preserves the observed result of a command while simplifying WebAssembly test inputs.

- **C1:** Reduction must respect typed module structure and changing function indices; the implementation keeps a mapping from original indices as functions disappear, validates transformed modules, and checks risky timeout proximity.
- **C2:** `TestCaseHandler` separates candidate reading, writing, and testing from the reduction logic. Implementations handle standalone Wasm/WAT and WebAssembly modules embedded in JavaScript test cases.
- **C3:** The reducer uses optimization passes to obtain large inexpensive simplifications before more destructive fine-grained reduction.

This is a useful example of reusing a compiler's transformation infrastructure without equating ordinary optimization with failure-preserving reduction.

### 19. [KhronosGroup/SPIRV-Tools](https://github.com/KhronosGroup/SPIRV-Tools)

**Language / role:** C++; specifically the **spirv-reduce** library and command-line subsystem.

Study a reducer for a binary shader IR with strict structural and validation rules.

- **C1:** The [reducer coordinator](https://github.com/KhronosGroup/SPIRV-Tools/blob/main/source/reduce/reducer.cpp) checks initial validity and interestingness, applies validation during reduction, and distinguishes invalid input, uninteresting input, completion, and limits. Its transformations address control flow, dominating IDs, functions, blocks, and structure members.
- **C2:** Reduction opportunity finders are independent from pass scheduling and from the supplied interestingness function; cleanup passes are represented separately.
- **C3:** The [pass implementation](https://github.com/KhronosGroup/SPIRV-Tools/blob/main/source/reduce/reduction_pass.cpp) batches available opportunities and decreases granularity. It reparses the saved binary into a fresh IR context for each attempt, an explicit simplicity-versus-cost choice that makes rollback reliable.

### 20. [google/graphicsfuzz](https://github.com/google/graphicsfuzz)

**Language / role:** Java reduction core and supporting Python tooling; specifically **glsl-reduce**. **Archived repository.**

The GLSL reducer is distinct from `spirv-reduce`, whose implementation belongs to SPIRV-Tools and is covered above.

- **C1:** The [reduction manual](https://github.com/google/graphicsfuzz/blob/master/docs/glsl-fuzz-reduce.md) distinguishes wrong-image reduction, which generally requires preserving semantics, from compilation or rendering crashes. It explains why skipping rendering is valid only for appropriate oracles and why unrestricted reductions can introduce nontermination.
- **C2:** The [driver](https://github.com/google/graphicsfuzz/blob/master/reducer/src/main/java/com/graphicsfuzz/reducer/ReductionDriver.java) separates file judging, shader-job operations, reduction opportunities, and pass management. Shader jobs can include multiple stages and associated metadata.
- **C3:** The driver organizes initial, core, and cleanup passes and caches outcomes using shader-job hashes, reducing repeated expensive compiler or rendering checks.

### 21. [AFLplusplus/AFLplusplus](https://github.com/AFLplusplus/AFLplusplus)

**Language / role:** C; specifically the standalone **afl-tmin** input minimizer within AFL++.

The [fuzzing guide](https://github.com/AFLplusplus/AFLplusplus/blob/stable/docs/fuzzing_in_depth.md) distinguishes minimization of an individual input from corpus minimization and describes crashing and non-crashing operation.

- **C1:** The [minimizer](https://github.com/AFLplusplus/AFLplusplus/blob/stable/src/afl-tmin.c) treats crashes, hangs, normal execution, instrumentation checksums, and optional exact-path matching differently. In particular, default crash mode can accept another crash; it should not be mistaken for a guarantee of the same root cause.
- **C3:** It reuses forkserver and shared-memory infrastructure to amortize repeated target execution, then applies staged normalization, deletion, and simplification. The acceptance logic remains separate from the mutation stages.

Study this when target execution overhead and instrumentation-defined behavior matter more than source-language syntax. The original AFL is not counted separately.

## Integrated counterexample shrinking

These projects qualify through their automatic shrinking implementations. They are testing frameworks, not interchangeable command-line reducers for arbitrary existing files.

### 22. [HypothesisWorks/hypothesis](https://github.com/HypothesisWorks/hypothesis)

**Language / role:** Python; the Conjecture shrinking subsystem of Hypothesis.

Study reduction of the decisions used to generate a value, rather than requiring a separately maintained shrink function for every output type.

- **C1:** The [shrinker](https://github.com/HypothesisWorks/hypothesis/blob/master/hypothesis/src/hypothesis/internal/conjecture/shrinker.py) orders choice sequences by length and choice complexity, retains a predicate-satisfying incumbent, and documents progress requirements for shrink passes. Its normal interestingness condition includes a fixed failure origin, reducing the risk of drifting between failures.
- **C2:** The [strategy design guide](https://github.com/HypothesisWorks/hypothesis/blob/master/guides/strategies-that-shrink.rst) explains how composed generators affect shrinking, with examples involving dependent bounds, complex numbers, and datetime behavior. This supports reusable domain-specific generation while sharing one reduction engine.

The engine's choice ordering is an operational definition of simplicity; it need not match every application's preferred presentation of a minimal example.

### 23. [proptest-rs/proptest](https://github.com/proptest-rs/proptest)

**Language / role:** Rust; strategy-associated shrinking in the `proptest` crate.

The repository's crate README describes its current posture as **passive maintenance**. It remains a useful design study for stateful shrinking and compositional invariants.

- **C1:** The [strategy and ValueTree contracts](https://github.com/proptest-rs/proptest/blob/main/proptest/src/strategy/traits.rs) specify the relationship between `current`, `simplify`, and `complicate`, including how to recover a known failing value. They also explain why dependent `flat_map` preserves relationships that independent variants can break.
- **C2:** `Strategy` constructs per-value `ValueTree` state; mappings, dependent strategies, boxed strategies, and sanity checking build on those interfaces. This is a substantial alternative to stateless, type-wide shrink functions.

The [changelog](https://github.com/proptest-rs/proptest/blob/main/proptest/CHANGELOG.md) is an additional useful entry into compatibility and regression work, including floating-point edge cases, platform support, random-generator integration, and minimum Rust versions.

### 24. [silentbicycle/theft](https://github.com/silentbicycle/theft)

**Language / role:** C; property-testing library with custom shrinking and experimental automatic shrinking.

Treat theft as a historical systems-library design: the inspected release changelog ends with version 0.4.5 in 2019, not evidence of current release activity.

- **C2:** The [shrinking design](https://github.com/silentbicycle/theft/blob/master/doc/shrinking.md) supports tactic-indexed user callbacks and automatic reduction of recorded random-bit requests. Request boundaries supply structure without requiring the reducer to understand the generated C type.
- **C1:** The same guide states determinism and generator-shape assumptions needed for repeatable shrinking; automatic shrinking expects smaller random choices to produce simpler generated values.
- **C4:** The [2017–2019 release history](https://github.com/silentbicycle/theft/blob/master/CHANGELOG.md) records fixes to autoshrinking, worker reaping, timeout cleanup, optional callbacks, and out-of-bounds diagnostic printing. These are concrete examples of managing failure modes and API behavior over multiple years.

### 25. [leepike/SmartCheck](https://github.com/leepike/SmartCheck)

**Language / role:** Haskell; historical research tool for reducing and generalizing QuickCheck counterexamples over algebraic data types.

SmartCheck explores a different design point from choice-stream shrinking. Its [project explanation](https://github.com/leepike/SmartCheck/blob/master/README.md) describes generic traversal and reduction without handwritten shrink instances, followed by optional generalization of counterexamples.

- **C1:** The [reduction implementation](https://github.com/leepike/SmartCheck/blob/master/src/Test/SmartCheck/Reduce.hs) tries replacing a value with a subterm only when its type matches, tests the resulting property, and distinguishes failed preconditions from successful reductions. Replacement generation is constrained to structurally smaller values.
- **C2:** The `SubTypes` abstraction and generic substructure traversal let one search procedure reduce many algebraic data types. Search depth, generated-value size, and trial limits are explicit parameters rather than datatype-specific control flow.

Its documented toolchain requirements are historical. Generalization is based on sampled tests and is not a proof that every replacement fails.

## Coverage, search process, and limitations

Discovery used more than six distinct live-web query formulations, including general delta debugging; C/C++ reducers and C-Reduce ports; hierarchical and grammar-based reduction; SMT and solver inputs; Java bytecode; SQL query reduction; WebAssembly and shader IR; property-based automatic shrinking; probabilistic delta debugging; browser/HTML/CSS reduction; D/DustMite; and newer Rust/Go reduction tools. Follow-up searches uncovered numerical optimization and algebraic-data reducers. Later broad queries mostly returned already-inspected reducers, thin scripts, ordinary minifiers, or unrelated uses of “delta” and “reduction.”

For every retained repository, its canonical GitHub location was opened or checked through the GitHub API, and additional primary documentation or source was read. Implementation files, algorithm descriptions, and compatibility histories support the criterion assessments above; search snippets and star counts were not used as quality evidence. Some GitHub tree requests hit API rate limits, so source verification continued through public GitHub pages and raw files. No candidate code was executed, dependencies installed, or repositories cloned.

The selection spans Perl/C++, Python, Rust, D, JavaScript, Java, and Haskell; raw bytes, text chunks, ASTs, grammar trees, typed IR, bytecode dependencies, solver models, and generator decisions; and standalone tools, reusable libraries, research artifacts, and large monorepo subsystems. C-Vise is counted separately because of its substantive orchestration port and evolution. ProbDD is counted for its new search implementation, with its bundled upstream ancestry disclosed. Picireny is a separate hierarchical layer over Picire. Journal snapshots and other mirrors were not added as independent projects.

Important boundaries remain. This is not an exhaustive catalog of proof-assistant minimizers, distributed execution-trace reducers, or every property-testing library with shrinking. Small demonstrations, wrappers around existing reducers, and unverified new projects were not added to fill the list. Performance mechanisms were inspected, but comparative benchmarks were not rerun. Archived and historical implementations can be excellent sources of ideas while requiring significant toolchain work before practical reuse. A reducer's output is only as informative as its oracle: different crashes, unstable timing, changed database state, or invalid generated programs can all change what is actually being preserved.
