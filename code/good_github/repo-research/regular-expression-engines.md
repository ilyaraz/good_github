# Regular expression engines

Research date: **2026-10-09**.

This report selects **25 GitHub repositories** containing substantive regular-expression implementations: reusable libraries, streaming matchers, compile-time engines, and five clearly identified language-runtime subsystems. Each selection has at least two evidence-supported criteria. Ports and forks are included only where they provide a separate implementation or substantial architectural evolution. This is a source-study guide, not a ranking, security certification, or claim that every component is exemplary.

**Criteria legend:** **C1** — difficult correctness, including matching semantics, resource limits, concurrency, Unicode, and adversarial inputs. **C2** — substantial reusable abstractions supporting different applications. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — sustained evolution supported by compatibility work, testing, or complexity management across years. Criterion assignments and suggested study value are engineering judgments grounded in the linked primary material. Complexity guarantees must be read with their pattern-size, operation, and feature restrictions.

## Automata, captures, and streaming

### 1. [google/re2](https://github.com/google/re2)

**C++ — general-purpose automata engine for untrusted patterns.** Study how a production matcher preserves familiar match-selection semantics while imposing memory budgets and avoiding recursive execution. The repository explains its linear-in-input matching objective and deliberate exclusion of backreferences and lookaround.

- **C1:** DFA state identity includes ordered instructions and assertion flags, because preserving leftmost-first or leftmost-longest results requires more than recognizing the same language. Shared state-cache eviction also has explicit locking and pointer-validity invariants.
- **C3:** Lazy DFA construction, byte equivalence classes, specialized search loops, and a bailout when DFA execution becomes unattractive connect algorithm choice to memory and throughput constraints. These mechanisms are explained directly in the unusually instructive [DFA implementation](https://github.com/google/re2/blob/main/re2/dfa.cc).

### 2. [rust-lang/regex](https://github.com/rust-lang/regex)

**Rust — `regex`, `regex-syntax`, and `regex-automata`, counted together.** A particularly useful study of exposing advanced engine machinery beneath a simpler public API.

- **C1/C3:** A meta-engine coordinates full and lazy DFAs, a one-pass capture engine, a bounded backtracker, and a Pike VM. Failure and fallback behavior are explicit; for example, visited-state capacity can limit the bounded backtracker, while Unicode word boundaries restrict certain DFA searches.
- **C2:** Lower-level APIs expose multi-pattern capture searches, direct automaton traversal, caller-owned scratch space, and serialized DFAs. Start with the substantive [engine and API guide](https://docs.rs/regex-automata/latest/regex_automata/).
- **C4:** The [changelog](https://github.com/rust-lang/regex/blob/master/CHANGELOG.md) documents the 2023 internal rewrite, subsequent memory regressions, and 2026 fixes to match-offset optimizations. It makes compatibility and optimization maintenance visible rather than merely asserting maturity.

### 3. [google/re2j](https://github.com/google/re2j)

**Java — independent Java implementation of the RE2/Go NFA lineage.** This is a port with its own matcher, not a JNI wrapper. It provides a useful comparison with both C++ RE2 and Java's standard engine; its README explicitly lists API and syntax incompatibilities with `java.util.regex`.

- **C1:** Logical NFA threads carry their own captures, and sparse queues track whether a program counter has already been considered. Correct queue ordering and capture propagation are central to preserving results without unrestricted backtracking.
- **C2/C3:** Compiled programs are separated from reusable execution machines and the public Pattern/Matcher interface. Two working queues and a thread pool reduce repeated allocation. Read [Machine.java](https://github.com/google/re2j/blob/master/java/com/google/re2j/Machine.java), then [RE2.java](https://github.com/google/re2j/blob/master/java/com/google/re2j/RE2.java) for the boundary between compiled representation and public API.

### 4. [laurikari/tre](https://github.com/laurikari/tre)

**C — POSIX matching with approximate, edit-cost matching.** TRE adds a distinct problem to the selection: choosing captures and matches while allowing constrained insertions, deletions, and substitutions.

- **C1:** The approximate matcher propagates tag values, edit counters, and costs through tagged-NFA states, including nested parameter scopes. This makes match preference and cost bookkeeping directly inspectable.
- **C2:** The library extends regular-expression matching with caller-configurable error limits and nonuniform costs, useful beyond a simple yes/no recognizer.
- **C3:** Current and next reach tables hold per-state information, and working storage is allocated per match for thread separation. The [approximate engine](https://github.com/laurikari/tre/blob/master/lib/tre-match-approx.c) also candidly documents an input-length cap associated with internal integer limits. That is a study limitation, not evidence that all size handling is solved.

### 5. [haskell-hvr/regex-tdfa](https://github.com/haskell-hvr/regex-tdfa)

**Haskell — tagged-DFA backend for POSIX extended regular expressions.** Study how a functional API is implemented with mutable scratch arrays while retaining POSIX subexpression results.

- **C1/C3:** The [main engine](https://github.com/haskell-hvr/regex-tdfa/blob/master/lib/Text/Regex/TDFA/NewDFA/Engine.hs) tracks winning states and tags, and dispatches to specialized variants depending on captures and front anchoring. It specializes a common input abstraction for strings, sequences, ByteString, and Text.
- **C2:** The `regex-base` interface supports different result types; asking only for a Boolean can avoid constructing captured strings.
- **C4:** The [changelog](https://github.com/haskell-hvr/regex-tdfa/blob/master/CHANGELOG.md) records compiler/library compatibility work from 2020 through 2026, doctest integration, character-class fixes, removal of partial functions, and Text specialization. The older ChrisKuklewicz repository is not counted separately.

### 6. [ocaml/ocaml-re](https://github.com/ocaml/ocaml-re)

**OCaml — pure OCaml lazy-DFA engine and compositional regex API.** It combines programmatically constructed expressions with Perl, POSIX, Emacs, and glob syntax frontends; its README identifies unsupported backreferences and lookaround.

- **C2:** The [core implementation](https://github.com/ocaml/ocaml-re/blob/master/lib/core.ml) exposes captures, marks, iterators, splitting, and full/partial/mismatch results over shared compiled machinery.
- **C1/C3:** The [compiler and execution code](https://github.com/ocaml/ocaml-re/blob/master/lib/compile.ml) uses lazily populated transition tables and character equivalence classes. Comments explain manually unboxed state representation, locking, and the publication assumptions needed when other domains observe initialized table rows. This is valuable material on the interaction between representation optimization and concurrency correctness; the documented runtime assumptions deserve scrutiny.

### 7. [intel/hyperscan](https://github.com/intel/hyperscan)

**C/C++ — multi-pattern hybrid-automata matching for block and streaming workloads.** Study a database-oriented engine whose result model is match events rather than the usual single Pattern/Matcher operation. This entry concerns the public GitHub code and its documented interface, not a claim about later commercial releases.

- **C1:** Stream boundaries, delayed zero-width assertions, callback-requested termination, and mandatory stream cleanup create concrete lifecycle invariants.
- **C2/C3:** Compiled databases are separated from stream state and caller-provided scratch memory. Block, vectored, and streaming modes serve different input layouts, while preallocated scratch avoids allocation in scan paths. Scratch is not reentrant and must be separate for concurrent or nested scans. The [runtime architecture and API guide](https://intel.github.io/hyperscan/dev-reference/runtime.html) explains these tradeoffs in detail.

### 8. [VectorCamp/vectorscan](https://github.com/VectorCamp/vectorscan)

**C/C++ — independently evolved portable Hyperscan fork.** Its Arm and Power implementations, SIMD abstraction, and separate release history justify a distinct entry. The stated compatibility target is the open Hyperscan 5.4 interface; do not assume compatibility with every later Intel release.

- **C2/C3:** The [SIMD abstraction entry point](https://github.com/VectorCamp/vectorscan/blob/develop/src/util/simd_utils.h) selects x86, Arm, Power, or SIMDe paths while sharing common operations. This is a concrete case study in preserving a complex matching architecture across instruction sets.
- **C1/C4:** The [Vectorscan changelog](https://github.com/VectorCamp/vectorscan/blob/develop/CHANGELOG-vectorscan.md), spanning 2023–2026 entries inspected here, records expanded CI, SIMD-tail and chunk-boundary correctness fixes, accelerator unit tests, and build-system refactoring. It also documents changing platform support and compatibility goals, which should be checked before adoption.

### 9. [openresty/sregex](https://github.com/openresty/sregex)

**C — streaming Thompson and Pike VMs, with a Thompson JIT path. Historical/quiet project.** The newest commit in the inspected [master history](https://github.com/openresty/sregex/commits/master/) was dated December 2016; the README's “heavy development” wording should not be treated as a current maintenance assessment.

- **C1:** The [Pike VM](https://github.com/openresty/sregex/blob/master/src/sregex/sre_vm_pike.c) retains processed-byte offsets, pending captures, EOF state, and boundary context across calls. This makes chunked matching and provisional capture results a useful focused study.
- **C2/C3:** Compiled programs, memory pools, and execution contexts are separate abstractions. Current/next thread lists and free lists support incremental execution and reuse. The Boolean Thompson engine versus capturing Pike engine also exposes the cost of requesting richer results.

## Backtracking, rich syntax, and compatibility

### 10. [PCRE2Project/pcre2](https://github.com/PCRE2Project/pcre2)

**C — Perl-compatible interpreter and JIT, plus an alternative DFA matching API.** Study the engineering cost of rich syntax and multiple execution strategies sharing a compiler and library surface.

- **C1:** The [matching-algorithm guide](https://github.com/PCRE2Project/pcre2/blob/main/doc/pcre2matching.adoc) explains why the usual depth-first matcher and alternative breadth-first matcher can return different results. Captures, backreferences, atomic groups, and partial matching do not have interchangeable behavior across these paths.
- **C3:** JIT accelerates the standard matching semantics, while the alternative matcher has different capability and optimization tradeoffs. A familiar function name is not enough to infer equivalent performance or results.
- **C4:** The [ChangeLog](https://github.com/PCRE2Project/pcre2/blob/main/ChangeLog) records 2024–2026 work on fuzzing, compiled-size and heap controls, Unicode correctness, JIT stack handling, and interpreter/JIT feature parity. This is unusually concrete evidence of ongoing complexity management.

### 11. [kkos/oniguruma](https://github.com/kkos/oniguruma)

**C — multi-encoding, multi-syntax backtracking engine. Archived; project ended April 24, 2025.** Both the archive banner and project-ending statement are present on the repository page. Retain it as a substantial historical implementation, not an active-maintenance recommendation.

- **C2:** Encoding can be selected per compiled expression, and syntax definitions are separated from encoding and execution machinery. This is useful for studying reuse across languages and legacy text representations.
- **C1:** The [execution engine](https://github.com/kkos/oniguruma/blob/master/src/regexec.c) combines capture-stack management with configurable match-stack and retry limits. Some controls depend on build configuration and return explicit unsupported-configuration errors. The limits illustrate failure handling around a feature-rich backtracker; they do not establish RE2-like complexity guarantees.

### 12. [k-takata/Onigmo](https://github.com/k-takata/Onigmo)

**C — separately evolved Oniguruma fork associated with Ruby integration.** The README documents additional Perl-style constructs and backports from Ruby. This is a meaningful compatibility branch, not a second listing of unchanged Oniguruma. Inspected public metadata showed the most recent push in June 2024, so current rapid development is not assumed.

- **C1:** The [matcher](https://github.com/k-takata/Onigmo/blob/master/regexec.c) uses distinct stack records for alternatives, assertions, repeats, capture restoration, and state-check marks. Those records expose the interactions between extensions and rollback semantics.
- **C2:** The reusable engine separates syntax definitions, character encoding, compilation, and execution; its repository documents multiple embedding interfaces and encoding-specific tests. The concrete reason to compare it with Oniguruma is how language-runtime compatibility pressures alter a common engine lineage.

### 13. [jruby/joni](https://github.com/jruby/joni)

**Java — Java implementation of the Oniguruma engine lineage.** A useful source study for moving byte-oriented, encoding-sensitive matching into a managed runtime without merely forwarding to native code.

- **C1:** The [bytecode machine](https://github.com/jruby/joni/blob/master/src/org/joni/ByteCodeMachine.java) implements capture-history trees, encoding-aware case folding, and interruption handling. Restoring capture state and advancing through variable-width encoded bytes are observable correctness concerns.
- **C2/C3:** Compiled Regex objects, Region results, stack-machine execution, and encoding services have distinct responsibilities. Case-fold buffers are allocated lazily, capture trees can be reused, and interruption checks are controlled separately from instruction dispatch. These details connect the abstraction boundaries to allocation and execution overhead.

### 14. [mrabarnett/mrab-regex](https://github.com/mrabarnett/mrab-regex)

**C/Python — the Python `regex` package's own engine.** Especially useful for studying fuzzy matching, repeated capture information, reverse search, and compatibility modes beyond Python's standard `re` behavior.

- **C1:** The [C implementation](https://github.com/mrabarnett/mrab-regex/blob/hg/src/_regex.c) maintains separate structure, backtracking, and pruning stacks, plus best-match and fuzzy-error state. The repository also documents GIL release during matching and the requirement that the subject remain unchanged.
- **C2:** One compiled-pattern interface supports exact and approximate matching, configurable insertion/deletion/substitution constraints, and selectable old/new semantics. The difficult reusable boundary is preserving those semantics across Python string representations and result objects, rather than merely adding syntax sugar.

### 15. [dlclark/regexp2](https://github.com/dlclark/regexp2)

**Go — a .NET-derived backtracking engine implemented in Go.** This is the useful counterpoint to Go's standard `regexp`: it deliberately supports constructs that require a different execution model, and documents rune-based indexing and compatibility options.

- **C1:** The [runner](https://github.com/dlclark/regexp2/blob/master/runner.go) explains separate backtracking, position, and capture-undo stacks. It also handles timeouts, right-to-left scans, and advancing after empty matches while preserving the original anchor position.
- **C2/C3:** Execution state is pooled independently of compiled syntax, and hooks distinguish candidate-position search from execution, including generated implementations. This makes both runtime reuse and code-generation integration inspectable. Compatibility flags do not turn the underlying backtracker into a linear-time engine.

### 16. [fancy-regex/fancy-regex](https://github.com/fancy-regex/fancy-regex)

**Rust — a hybrid engine combining a backtracking VM with automata delegation.** It is substantive engine work even though regular subexpressions are delegated to Rust's regex machinery.

- **C1:** Subexpression analysis distinguishes constructs that need backtracking from those that can be delegated without changing results. Context matters: delegating an apparently simple expression can still alter how alternatives and captures interact.
- **C3:** The [compiler](https://github.com/fancy-regex/fancy-regex/blob/main/src/compile.rs) chooses delegation versus explicit VM instructions and memoizes delegated engines. It also supports an optional emitted-program-size cap because inlined recursive subroutines can grow excessively despite a recursion-depth cap. Study this as selective optimization under semantic constraints; the repository explicitly disclaims a general linear-time guarantee for its richer patterns.

### 17. [ridiculousfish/regress](https://github.com/ridiculousfish/regress)

**Rust — an ECMAScript-oriented backtracking engine.** This adds a different compatibility target from the other Rust selections: JavaScript regex behavior, including the distinction between Unicode characters and UTF-16 code units.

- **C1:** The repository explains surrogate-pair behavior and separate UTF-8, ASCII, UTF-16, and UCS-2 input APIs. Encoding selection is therefore part of matching semantics, not just input conversion.
- **C2/C3:** The [architecture documentation in `lib.rs`](https://github.com/ridiculousfish/regress/blob/master/src/lib.rs) describes parser, intermediate representation, optimizer, bytecode emission, and execution backends. The [IR](https://github.com/ridiculousfish/regress/blob/master/src/ir.rs) distinguishes byte sequences, code-point sets, capture groups, lookaround direction, and loops. This provides readable boundaries for studying optimized rich-syntax matching. The main backtracker does not offer the Rust `regex` crate's worst-case guarantee.

### 18. [boostorg/regex](https://github.com/boostorg/regex)

**C++ — Boost.Regex, an independently implemented generic library.** Study the interaction between a reusable iterator/traits interface and a low-level engine that must support multiple toolchains and matching conventions.

- **C2:** Matcher templates parameterize iterators, allocators, and character traits, allowing the same machinery to work with different input and character environments.
- **C1/C3:** The [non-recursive matcher](https://github.com/boostorg/regex/blob/develop/include/boost/regex/v5/perl_matcher_non_recursive.hpp) models saved captures, assertions, repetitions, and recursion as explicit state records. Alignment, placement construction, and cached memory blocks make correctness and allocation tradeoffs tangible.

The [version history](https://github.com/boostorg/regex/blob/develop/doc/html/boost_regex/background/history.html) is a useful second reading: it records the move to header-only operation, compiler-support changes, fuzzing fixes, and intentional matching-semantic changes. Inclusion is based on the concrete C1–C3 evidence above, rather than age alone.

## Compile-time and scanner-oriented engines

### 19. [hanickadot/compile-time-regular-expressions](https://github.com/hanickadot/compile-time-regular-expressions)

**C++ — CTRE, a compile-time pattern compiler with compile-time or runtime matching.** This changes the compilation boundary: a pattern becomes template-level structure that the C++ compiler can specialize.

- **C2:** The public interface supports matching, searching, captures, splitting, and tokenization over ranges and iterator pairs. Results retain typed access to captures.
- **C1/C3:** The [evaluator](https://github.com/hanickadot/compile-time-regular-expressions/blob/main/include/ctre/evaluation.hpp) dispatches on type lists representing regex operations. It explicitly handles capture marks, alternatives, consumed-input state, and empty-match cycles through `constexpr` functions. Study how compile-time specialization removes runtime interpretation work while preserving backtracking semantics; compile-time construction does not itself imply bounded runtime matching.

### 20. [Genivia/RE-flex](https://github.com/Genivia/RE-flex)

**C++ — regex library with its own DFA engine, also a lexical-analyzer generator.** Included for the substantial matcher implementation, not solely for generating lexers or wrapping optional PCRE2/Boost backends.

- **C2:** A common matcher interface provides scan, find, split, and whole-input matching, with stream-oriented position and boundary handling. The repository distinguishes its own engine from optional external engines.
- **C1/C3:** The [matcher implementation](https://github.com/Genivia/RE-flex/blob/master/lib/matcher.cpp) separates finding plausible starting positions from executing a pattern, supports generated FSM functions and opcode execution, and handles lookback, anchors, and buffer positions. These are concrete entry points for understanding why searching and tokenization need different optimization paths. Its native capture model is more limited than a general Perl-style submatch engine, as the README explains; performance comparisons should account for that difference.

## Regex subsystems inside language runtimes

Each monorepo below is counted once. The recommendation concerns the named subsystem, not an assessment of the entire runtime.

### 21. [golang/go](https://github.com/golang/go)

**Go — `src/regexp` and `src/regexp/syntax`. Official GitHub mirror.** The repository README identifies `go.googlesource.com/go` as canonical and this GitHub repository as its mirror. Study how a standard-library API chooses among several implementations without exposing that choice to callers.

- **C1:** The [bounded backtracker](https://github.com/golang/go/blob/master/src/regexp/backtrack.go) records visited instruction/input-position pairs to prevent repeated exploration. This is an important distinction from unrestricted backtracking despite the filename.
- **C2/C3:** The [execution implementation](https://github.com/golang/go/blob/master/src/regexp/exec.go) selects one-pass execution, bounded bit-state search for small cases, or NFA simulation. Shared input abstractions handle strings, bytes, and rune readers, while pools recycle working state. The thresholds and fallback structure are directly readable.

### 22. [dotnet/runtime](https://github.com/dotnet/runtime)

**C# — `System.Text.RegularExpressions`, especially its symbolic matcher.** The [subsystem README](https://github.com/dotnet/runtime/blob/main/src/libraries/System.Text.RegularExpressions/README.md) identifies the library boundary and its immutable Regex API. The symbolic implementation offers a derivative-based architecture distinct from the Thompson-family engines above.

- **C1:** The [symbolic matcher](https://github.com/dotnet/runtime/blob/main/src/libraries/System.Text.RegularExpressions/src/System/Text/RegularExpressions/Symbolic/SymbolicRegexMatcher.cs) documents why finding a possible end, walking backward to locate the start, and matching forward again are separate steps. Anchors, special end-of-input character classes, and capture handling complicate these passes.
- **C2/C3:** Character-set solvers and minterm partitions support reusable symbolic nodes; lazy DFA/NFA state construction and candidate-position optimizations address state growth and search cost. The comments explain both data representation and execution strategy, making this subsystem approachable without reading the entire runtime.

### 23. [v8/v8](https://github.com/v8/v8)

**C++ — `src/regexp`, particularly Irregexp. Official GitHub mirror.** The repository explicitly identifies itself as the V8 Git mirror. Study a regex compiler embedded in a JavaScript runtime, with both bytecode and native-code output.

- **C1:** The [compiler's architecture commentary](https://github.com/v8/v8/blob/main/src/regexp/regexp-compiler.cc) explains the AST-to-node-network-to-code pipeline and how choice nodes, action nodes, capture registers, and the backtracking stack preserve execution state.
- **C3:** Fixed-length greedy loops can store less backtracking information, and a virtualized execution trace postpones register updates until needed. Specialization is capped to control generated-code growth. The same file carefully distinguishes the conceptual matcher from its optimized realization, making it especially useful for compiler-oriented engineers.

### 24. [openjdk/jdk](https://github.com/openjdk/jdk)

**Java — `java.util.regex` in `java.base`.** This is the JDK's actual engine, a useful comparison with RE2/J's intentionally restricted model.

- **C2:** Compiled immutable Pattern objects are separated from mutable Matcher state and operate over CharSequence inputs. The implementation's node hierarchy represents regex constructs through a common matching protocol.
- **C1/C3:** [Pattern.java](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/regex/Pattern.java) includes different handling for supplementary characters and case folding, capture/loop nodes, and Boyer–Moore-style literal-prefix search. The prefix optimizer explains compact shift tables and why very short patterns do not justify the setup cost. This provides a concrete study of compatibility-rich semantics and local accelerations rather than a blanket linear-time guarantee.

### 25. [python/cpython](https://github.com/python/cpython)

**C/Python — `Lib/re` compiler and `Modules/_sre` execution engine.** Study a cross-language implementation boundary: Python code lowers patterns to instructions consumed by a C matcher.

- **C1:** The [matching core](https://github.com/python/cpython/blob/main/Modules/_sre/sre_lib.h) explains precisely when capture markers must be saved and restored after a failed nested match. Its explicit data-stack machinery and repeat handling expose failure paths that are easy to overlook in small teaching engines.
- **C2/C3:** The [compiler](https://github.com/python/cpython/blob/main/Lib/re/_compiler.py) separates parsing/optimization from instruction emission and selects different operations for case handling, character sets, and repeat forms. It checks the instruction-format version against `_sre`, making the compiler/runtime compatibility invariant explicit. This is the standard engine itself, separate from the independently implemented `mrab-regex` entry.

## Coverage, searches, and limitations

Discovery used **18 live web queries**, followed by repository-page opens and direct primary-source reading. Search formulations covered bounded DFA/NFA engines; SIMD and streaming engines; PCRE/JIT and Oniguruma-family backtracking; JVM ports and Go compatibility engines; OCaml and Haskell implementations; compile-time C++ and scanner engines; approximate/fuzzy matching; runtime symbolic and bytecode engines; embedded C; and ECMAScript/derivative/automata alternatives. Representative queries included:

- `GitHub regular expression engine DFA NFA linear time RE2 regex automata design`
- `GitHub regex engine SIMD streaming Hyperscan Vectorscan architecture`
- `GitHub regular expression engine backtracking JIT PCRE2 Oniguruma design`
- `site:github.com regex engine OCaml re Haskell regex-tdfa`
- `site:github.com regex engine approximate matching TRE fuzzy Python mrab regex`
- `site:github.com regular expressions C++ compile time CTRE Boost regex RE-flex`
- `site:github.com regular expression engine runtime symbolic dotnet V8 regexp interpreter`
- `site:github.com regex engine derivatives ECMAScript Rust regress`

Later searches increasingly returned already-covered engine families, bindings, benchmark collections, and small restricted implementations; they nevertheless added regress for its distinct encoding/compatibility problem. Pure wrappers, regex visualizers, benchmark-only repositories, tutorial engines, and broad automata toolkits were not promoted into the selection. Lexer generators such as re2c were treated as an adjacent category; RE/flex was retained because it also contains a substantial reusable regex matcher. The former standalone `BurntSushi/regex-automata` and original `ChrisKuklewicz/regex-tdfa` locations were excluded as duplicate/moved homes. Onigmo and Vectorscan were retained for the separate evolution described above.

All 25 canonical GitHub repository pages were opened. Every retained repository also had at least one distinct primary implementation or design source read; repeated copies of a README were not counted as independent evidence. GitHub metadata checks supplemented archive and branch verification, although unauthenticated API rate limits prevented a uniform metadata snapshot of all runtime monorepos. Their repository pages and directly retrieved source files provided the verification instead. Some browser fetches failed; direct read-only retrieval of public source files filled those gaps.

This is a broad, selective survey rather than an exhaustive inventory of every language's engine. No candidate code was executed, dependencies installed, or benchmark claims independently reproduced. Source links generally follow moving branches, and inspected passages do not constitute a complete audit. Archive/quiet-project status is stated where material; repository age or a recent push alone was not used to award C4. Differences in capture support, matching order, Unicode representation, and streaming semantics make unqualified speed rankings inappropriate.
