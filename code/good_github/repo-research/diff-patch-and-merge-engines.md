# Diff, patch, and merge engines

Research date: **2026-10-09**.

This report selects **27 GitHub repositories** implementing substantive text differencing, patch application, three-way merging, structural differencing, or binary delta machinery. It includes reusable libraries, relevant subsystems of larger version-control projects, and research implementations with instructive internals. Presentation-only diff viewers, thin bindings, patch-management workflows, and generic object-merging utilities are outside the main selection. Each repository was checked at its GitHub URL and against additional primary documentation or source code. The engineering-study recommendations are grounded judgments, not claims that every component is uniformly exemplary or suitable for deployment.

Criteria legend:

- **C1 — Correctness:** difficult invariants, conflicting changes, numerical or encoding semantics, adversarial inputs, or recovery behavior.
- **C2 — Abstractions:** substantial interfaces or intermediate representations reusable across multiple applications.
- **C3 — Performance and structure:** concrete memory, latency, I/O, or computational constraints addressed through understandable architecture.
- **C4 — Evolution:** evidence across years of compatibility work, testing, or deliberate complexity management; repository age alone does not qualify.

## Version-control diff and merge subsystems

### 1. [git/git](https://github.com/git/git)

**Language/role:** C; Git's xdiff and merge-ort machinery. **Official publish-only GitHub mirror**, as identified by the repository. Counted once, rather than treating its algorithms as separate projects.

Study the interaction between content differencing, inferred file identity, directory renames, and repeated three-way merges during rebases.

- **C1:** The [remembering-renames design document](https://github.com/git/git/blob/master/Documentation/technical/remembering-renames.adoc) develops the conditions under which rename information remains valid, including same-destination renames, drastic file shrinkage, directory renames, and cache invalidation when execution stops for user intervention.
- **C3:** The same document explains avoiding repeated rename detection and caching both successful pairings and relevant negative results. This is a particularly clear example of an optimization accompanied by its correctness argument.
- **C2:** The [xdiff interface](https://github.com/git/git/blob/master/xdiff/xdiff.h) separates in-memory inputs, diff parameters, output callbacks, and merge parameters, including algorithm selection and conflict-output styles.

### 2. [libgit2/libgit2](https://github.com/libgit2/libgit2)

**Language/role:** C; embeddable Git implementation, specifically its file/tree/commit merge subsystem.

Study how repository-level conflicts become explicit library results instead of being inseparable from a command-line working-tree operation.

- **C1:** [merge.c](https://github.com/libgit2/libgit2/blob/main/src/libgit2/merge.c) explicitly enumerates rename/delete, rename/add, one-to-two, and two-to-one rename cases, then coalesces entries while preserving conflict classifications.
- **C2:** The [public merge API](https://github.com/libgit2/libgit2/blob/main/include/git2/merge.h) distinguishes repository-independent buffer merging from tree and commit merging, which return indexes that callers must inspect for conflicts. Similarity metrics and merge drivers are configurable.
- **C3:** That API exposes a rename-candidate limit and recursive merge-base limit, making costly ambiguity resolution an explicit application policy.

### 3. [eclipse-jgit/jgit](https://github.com/eclipse-jgit/jgit)

**Language/role:** Java; the diff subsystem of Eclipse's independent Git implementation.

The histogram implementation is an unusually readable place to compare human-oriented matching heuristics with bounded computational work.

- **C2:** [HistogramDiff.java](https://github.com/eclipse-jgit/jgit/blob/master/org.eclipse.jgit/src/org/eclipse/jgit/diff/HistogramDiff.java) operates through generic sequence and comparator abstractions and produces edit lists. Its fallback is another `DiffAlgorithm`, rather than a hardwired text-only routine.
- **C3:** The implementation documents choosing low-occurrence common elements as split points, limiting hash-chain searches, and falling back to Myers—or emitting a replacement if no fallback is configured. It also states the internal sequence-size limitation.

This entry concerns JGit's own implementation, not a Java binding to native Git or libgit2. The repository's [module overview](https://github.com/eclipse-jgit/jgit#modules) supplies the broader embedding context.

## General-purpose text and sequence libraries

### 4. [google/diff-match-patch](https://github.com/google/diff-match-patch)

**Language/role:** Multiple implementations, including Python, JavaScript, Java, C++, and C#; plain-text diff, fuzzy matching, and best-effort patching. **Archived on August 5, 2024**, according to GitHub.

Study the distinction between computing an edit script and applying changes to text that has subsequently drifted.

- **C1:** The [Python implementation](https://github.com/google/diff-match-patch/blob/master/python3/diff_match_patch.py) shows patch-position adjustment, imperfect-match rejection, edge padding, and splitting large patches around matching limits. Application returns success flags, although internal splitting means these need not correspond one-to-one with the original patches.
- **C2:** The repository documents a common diff/match/patch API across language implementations. Myers differencing, cleanup, and Bitap matching form separable stages; its [API guide](https://github.com/google/diff-match-patch/wiki/API) is the natural interface reference.

Treat this as an archived algorithmic reference; the numerous direct ports are not counted as additional independent engines here.

### 5. [kpdecker/jsdiff](https://github.com/kpdecker/jsdiff)

**Language/role:** TypeScript/JavaScript; configurable token differencing plus unified/Git patch processing.

Study an extensible Myers engine whose tokenization, equality, result construction, and execution policy are separated from the search.

- **C2:** [The base diff class](https://github.com/kpdecker/jsdiff/blob/master/src/diff/base.ts) provides generic token/input types and hooks for input conversion, tokenization, equality, and postprocessing. It supports synchronous and callback-based use.
- **C3:** The same implementation bounds work with timeout and maximum-edit-length options and prunes diagonals after reaching the edit graph's edges. Linked change components defer construction of the public result representation.
- **C1:** [Release notes](https://github.com/kpdecker/jsdiff/blob/master/release-notes.md) document concrete interoperability corrections involving quoted filenames, absent final newlines, CRLF conversion, and Git extended headers. These are valuable examples of patch-format correctness extending beyond the core algorithm.

### 6. [java-diff-utils/java-diff-utils](https://github.com/java-diff-utils/java-diff-utils)

**Language/role:** Java; generic sequence differences, patch application/restoration, and unified-diff tooling.

Study how a library turns algorithm output into typed chunks and deltas with explicit application failure behavior.

- **C1:** [Patch.java](https://github.com/java-diff-utils/java-diff-utils/blob/master/java-diff-utils/src/main/java/com/github/difflib/patch/Patch.java) verifies chunks before applying them, processes ordinary deltas in reverse order to avoid shifting later locations, and implements fuzzy placement with bounds and previous-hunk constraints.
- **C2:** Patches operate on generic lists and expose conflict-output customization, restoration, and separate copy-returning versus in-place operations.
- **C4:** The [changelog](https://github.com/java-diff-utils/java-diff-utils/blob/master/CHANGELOG.md) records dated 2017–2019 evolution and subsequent algorithm/API changes, including configurable splitting, a dependency-free core, reader/writer regression compatibility, and keeping a new linear-space algorithm non-default while it matured.

### 7. [mitsuhiko/similar](https://github.com/mitsuhiko/similar)

**Language/role:** Rust; low-level sequence algorithms with higher-level text, unified-diff, and merge interfaces.

Study how algorithm-generic operations can coexist with text-specific conveniences without forcing all input into strings.

- **C2:** The [crate architecture and API documentation](https://github.com/mitsuhiko/similar/blob/main/src/lib.rs) separates low-level algorithms, captured `DiffOp` sequences, text changes, unified output, and three-way merging. Indexable sequences and slices are first-class inputs; cached lookups support derived or computed elements.
- **C1:** That documentation explicitly distinguishes a final line with a newline from one without it and explains how change objects carry missing-newline information. This is essential for faithful textual reconstruction and correct patch display.

The [repository overview](https://github.com/mitsuhiko/similar#readme) also describes benchmark and performance-fuzzing facilities; no comparative speed ranking is inferred here.

### 8. [pascalkuthe/imara-diff](https://github.com/pascalkuthe/imara-diff)

**Language/role:** Rust; histogram and linear-space Myers differencing with explicit behavior/performance tradeoffs.

Study token interning, reusable buffers, configurable hunk positioning, and handling repetitive inputs.

- **C2:** [The public implementation/API](https://github.com/pascalkuthe/imara-diff/blob/master/src/lib.rs) separates `TokenSource`, interned input, computation, postprocessing, hunk iteration, and printing. Callers can bypass interning or supply their own positioning heuristic.
- **C3:** The same source explains histogram fallback for highly repeated tokens, preprocessing that removes impossible matches, and early-abort heuristics in Myers. `MyersMinimal` explicitly disables those heuristics when minimality is required.

The [repository documentation](https://github.com/pascalkuthe/imara-diff#readme) describes fuzz coverage and treats valid diff-output changes as compatibility changes. This supports studying the semantic contract, without assuming all algorithm modes produce identical edits.

### 9. [bmwill/diffy](https://github.com/bmwill/diffy)

**Language/role:** Rust; in-memory diff creation, patch parsing/application, and three-way text merge.

This is useful for studying the complete patch lifecycle rather than only edit-distance computation.

- **C1:** [Crate documentation and examples](https://github.com/bmwill/diffy/blob/master/src/lib.rs) specify context-based relocation when hunk line numbers are wrong, distinguish identical overlapping changes from conflicting changes, and demonstrate returning conflict-marked text on unsuccessful merging.
- **C2:** The API provides parallel UTF-8 and byte-oriented operations, leaving file I/O to callers. It separates patch generation, formatting, application, and merge options; the documented multi-file patch iterator lets consumers process individual file operations.

Its [repository page](https://github.com/bmwill/diffy) identifies the diff/merge/patch scope. Do not confuse it with unrelated research projects also called Diffy or count backend-swapping forks separately.

### 10. [mmanela/diffplex](https://github.com/mmanela/diffplex)

**Language/role:** C#; .NET differencing core and display-model builders. This entry concerns the engine, not its UI packages.

Study a compact implementation connecting customizable chunk boundaries to middle-snake search and modification ranges.

- **C2:** [Differ.cs](https://github.com/mmanela/diffplex/blob/master/DiffPlex/Differ.cs) accepts `IChunker` implementations for lines, characters, delimiters, or application-defined chunks. It keeps original pieces separate from the integer identifiers used during matching.
- **C3:** The same source strips common prefixes/suffixes, compares interned piece identifiers, and allocates forward/reverse diagonal work arrays once for reuse through recursive subdivision.
- **C1:** Its bidirectional search explicitly distinguishes odd/even length differences when detecting overlap. That coordinate logic is worth studying alongside the [public interface description](https://github.com/mmanela/diffplex#idiffer-interface).

### 11. [cubicdaiya/dtl](https://github.com/cubicdaiya/dtl)

**Language/role:** C++; Diff Template Library, including sequence patches and diff3.

DTL adds a different algorithm family to the selection: the repository describes Wu, Manber, and Myers' O(NP) sequence-comparison algorithm.

- **C2:** The [repository's API examples](https://github.com/cubicdaiya/dtl#readme) demonstrate arbitrary random-access sequences, edit distance, common subsequences, edit scripts, patching, and three-sequence merging through templates.
- **C1:** [Diff3.hpp](https://github.com/cubicdaiya/dtl/blob/master/dtl/Diff3.hpp) reconciles two edit streams relative to a common base, handles unchanged-side shortcuts, and explicitly treats incompatible additions/deletions as conflicts.
- **C3:** The documentation describes subdividing highly divergent sequences to control edit-script memory growth. Its alternate modes deserve inspection before assuming a particular minimality or output-quality contract.

### 12. [janestreet/patience_diff](https://github.com/janestreet/patience_diff)

**Language/role:** OCaml; patience-diff engine used through typed sequence and hunk interfaces.

Study a substantive OCaml evolution of the Bazaar-derived patience algorithm, including the boundary between equivalent edits and preferred presentation.

- **C1:** [The interface](https://github.com/janestreet/patience_diff/blob/master/src/patience_diff_intf.ml) states matching-block monotonicity and the terminal zero-length sentinel invariant. It documents semantic cleanup and how equivalent hunk placements are scored.
- **C2:** The `Make` functor accepts hashable element types; transformations, matching blocks, hunks, and multi-sequence segmentation are exposed independently of a terminal renderer.
- **C3:** [The implementation](https://github.com/janestreet/patience_diff/blob/master/src/patience_diff.ml) tracks unique-token occurrences, computes increasing subsequences, and falls back to plain differencing when too little of the input would participate in patience matching.

## Syntax-aware diff and structured merge research

### 13. [Wilfred/difftastic](https://github.com/Wilfred/difftastic)

**Language/role:** Rust; syntax-aware structural diff engine with a command-line renderer.

Study the structural comparison itself: the renderer is downstream of an engine that compares positions in two syntax trees.

- **C1:** The [diffing internals](https://difftastic.wilfred.me.uk/diffing.html) model states as paired tree positions and transitions as matching nodes or consuming novel nodes. The shortest route supplies the edit correspondence; preserving the meaning of these states is the central algorithmic invariant.
- **C3:** Dijkstra search generates neighboring vertices on demand instead of first materializing the whole comparison graph. This makes the relationship between search costs and memory allocation particularly visible.

The [repository overview](https://github.com/Wilfred/difftastic#readme) establishes its multi-language, syntax-aware role. It is selected as a diff engine, not presented as a patch applier or merge engine.

### 14. [GumTreeDiff/gumtree](https://github.com/GumTreeDiff/gumtree)

**Language/role:** Java; extensible AST matching and edit-script generation framework.

Study the separation between parsing, node correspondence, and producing executable tree-edit operations, including moves and updates.

- **C2:** The [GumTree API guide](https://github.com/GumTreeDiff/gumtree/wiki/GumTree-API) exposes tree generators, matchers, mapping stores, and edit-script generators as separate stages. This supports language frontends and research algorithms without making them reimplement the whole pipeline.
- **C1:** [ChawatheScriptGenerator.java](https://github.com/GumTreeDiff/gumtree/blob/main/core/src/main/java/com/github/gumtreediff/actions/ChawatheScriptGenerator.java) maintains original-to-copy mappings, updates a working tree while emitting edits, aligns children through a common subsequence, and determines insertion positions after removing moved nodes. Those ordering details distinguish a valid tree transformation from a plausible-looking list of changes.

### 15. [ASSERT-KTH/spork](https://github.com/ASSERT-KTH/spork)

**Language/role:** Java/Kotlin; structured Java-source merge research implementation using Spoon, GumTree matching, and a 3DM-derived merge representation.

The repository explicitly calls itself a research tool and recommends Mergiraf for production-oriented use. It also reports differing behavior for its experimental native-image build; this is not an unqualified deployment recommendation.

- **C2:** [TdmMerge.kt](https://github.com/ASSERT-KTH/spork/blob/master/src/main/kotlin/se/kth/spork/base3dm/TdmMerge.kt) implements merging over generic list-node and content types. It separates structural inconsistencies from content conflicts and retains unresolved revision contents for later processing, making the merge layer distinct from Spoon's Java AST adapter.
- **C1:** [PcsBuilder.java](https://github.com/ASSERT-KTH/spork/blob/master/src/main/java/se/kth/spork/spoon/PcsBuilder.java) converts Spoon nodes into revision-tagged parent/predecessor/successor triples, including virtual nodes and explicit list boundaries. Its comments explain why empty child lists need representation to detect deletions that remove every child.

### 16. [se-sic/jdime](https://github.com/se-sic/jdime)

**Language/role:** Java; structured and semistructured merge experimentation with strategy composition and auto-tuning.

Study how multiple merge approaches are organized around the same operation/context model and how fallback decisions are instrumented. No current maintenance cadence is inferred from the repository's existence.

- **C2:** [CombinedStrategy.java](https://github.com/se-sic/jdime/blob/develop/src/de/fosd/jdime/strategy/CombinedStrategy.java) accepts a list of merge strategies and executes them through a shared operation and copied merge context. Strategy-specific results feed common scenario statistics.
- **C3:** The loop stops when a strategy yields no reported conflicts and records individual and total runtimes. This makes the cost of escalating to additional merge strategies explicit rather than hiding it inside a monolithic merger.

The [repository overview](https://github.com/se-sic/jdime#readme) identifies its ExtendJ integration and shipped parser modifications; the research value is broader than a wrapper around `git merge`.

## Structured data and ownership-aware merging

### 17. [benjamine/jsondiffpatch](https://github.com/benjamine/jsondiffpatch)

**Language/role:** TypeScript/JavaScript; object/array differences, reversible deltas, and patch application.

Study identity-sensitive array matching and the difference between an object's value, its identity, and its current position.

- **C1:** The [array-diff design](https://github.com/benjamine/jsondiffpatch/blob/master/docs/arrays.md) explains why LCS needs an `objectHash` for independently reconstructed objects, how move detection preserves references, and why original and destination indices belong to different coordinate systems. Removals occur before insertions during patch application.
- **C2:** The [public API](https://github.com/benjamine/jsondiffpatch#readme) supports diff, patch, reverse/unpatch, nested object changes, configurable identity, optional long-text differencing, and alternative output formats. Its own delta representation is a reusable intermediate artifact, not merely colored output.

### 18. [Shoobx/xmldiff](https://github.com/Shoobx/xmldiff)

**Language/role:** Python; XML tree differencing, edit scripts, patching, and formatters.

Study how tree identity and matching quality interact with text content and document presentation.

- **C1:** The [API guide](https://xmldiff.readthedocs.io/en/stable/api.html) defines unique-attribute matching and explicitly distinguishes edit-script validity from stable presentation: scripts may change across versions, but must still transform the source tree into the target.
- **C2:** It accepts files, strings, and lxml trees, and separates edit actions from configurable formatters and whitespace normalization.
- **C3:** The same guide documents similarity thresholds, accurate/fast/faster ratio modes, and a chain-based fast-match pass. It candidly states that faster matching can produce less optimal edit scripts.

The [repository overview](https://github.com/Shoobx/xmldiff#readme) identifies both differencing and patching functionality; this is not just an XML pretty-printer comparison.

### 19. [evanphx/json-patch](https://github.com/evanphx/json-patch)

**Language/role:** Go; RFC 6902 patch application and RFC 7386 merge-patch creation/application.

Study a patch interpreter whose correctness depends on ordered operations, pointer resolution, array mutation, and configurable extensions.

- **C1:** [The v5 patch implementation](https://github.com/evanphx/json-patch/blob/master/v5/patch.go) exposes explicit missing-value, invalid-index, and failed-test errors. Apply options control nonstandard negative indices and accumulated size growth from copy operations; the copy limit is configurable rather than automatically a nonzero protection.
- **C2:** It uses lazy nodes and a common container interface for object/array traversal. The [public documentation](https://github.com/evanphx/json-patch#readme) separates ordered JSON Patch processing from merge-patch generation/application and offers per-call application policies.

This entry does not claim the project generates arbitrary RFC 6902 diffs; its documented generation support concerns merge patches.

### 20. [kubernetes-sigs/structured-merge-diff](https://github.com/kubernetes-sigs/structured-merge-diff)

**Language/role:** Go; schema-aware merge and field-ownership engine behind Kubernetes apply semantics.

Study an alternative to ordinary base/ours/theirs text merging: reconciling overlapping field ownership among independent managers.

- **C1:** The [design overview](https://github.com/kubernetes-sigs/structured-merge-diff#readme) distinguishes update from apply, tracks managed field sets, and explains conflicts when one manager attempts to acquire another's fields. Omitted formerly managed fields carry deletion meaning.
- **C2:** The design splits schema, values, typed comparison, trie-like field paths, and merge logic. [update.go](https://github.com/kubernetes-sigs/structured-merge-diff/blob/master/merge/update.go) exposes conversion across API versions and an updater that computes both object changes and ownership changes.

This is a domain-specific but substantial merge engine, not a claim that the entire Kubernetes repository is in scope or that field ownership alone implements concurrency control.

## Binary deltas, streams, archives, and embedded patching

### 21. [jmacd/xdelta](https://github.com/jmacd/xdelta)

**Language/role:** C; VCDIFF/RFC 3284 binary delta encoder/decoder and CLI. The relevant subsystem is `xdelta3`; historical `xdelta1` is not counted separately.

Study a resumable computation interface that separates delta processing from source-block acquisition and output transport.

- **C2:** The [programming guide](https://jmacd.github.io/xdelta/programming-guide/) distinguishes simple memory-buffer functions from `xd3_stream`, `xd3_source`, and `xd3_config`. Applications can provide a synchronous source callback or handle `XD3_GETSRCBLK` and resume later.
- **C3:** Input/output/window events and independently configurable window/block sizes expose buffering and I/O costs directly. The application drives progress and consumes output without requiring an all-at-once file API.

The [repository documentation](https://github.com/jmacd/xdelta#readme) distinguishes its Apache-licensed development line from the separate historical GPL repository. These are not counted as independent engines.

### 22. [google/open-vcdiff](https://github.com/google/open-vcdiff)

**Language/role:** C++; independent VCDIFF encoder/decoder with streaming interfaces.

Study the contract for incremental decoding of an externally supplied instruction stream. No claim of active maintenance is made here.

- **C1:** [vcdecoder.h](https://github.com/google/open-vcdiff/blob/master/src/google/vcdecoder.h) specifies the permitted start/chunk/finish lifecycle, malformed-input failure behavior, dictionary lifetime, and explicit maximum target-file and window sizes.
- **C2:** Streaming and whole-buffer decoders share an output abstraction, allowing different destination string types without changing the decoding engine.
- **C3:** The same interface documents limiting reallocations per window and optionally forbidding references to earlier target data, allowing previously decoded windows to be released.

The [repository page](https://github.com/google/open-vcdiff#readme) establishes the RFC 3284 scope. Its mere presence under Google's organization is not used as a quality or maintenance argument.

### 23. [sisong/HDiffPatch](https://github.com/sisong/HDiffPatch)

**Language/role:** C/C++; binary file and directory diff/patch library and tools.

Study how patch formats, I/O access patterns, decompression plugins, and caller-owned memory interact for large updates.

- **C2:** [patch.h](https://github.com/sisong/HDiffPatch/blob/master/libHDiffPatch/HPatch/patch.h) separates stream inputs/outputs, decompression callbacks, diff metadata, cache buffers, and patch listeners. This supports embedding rather than requiring the command-line tools.
- **C3:** Its APIs distinguish sequential output from random old-data reads and single-pass patch-stream consumption. The header describes cache tradeoffs, memory requirements, and multithreaded I/O/decompression options for relevant paths.

The [repository documentation](https://github.com/sisong/HDiffPatch#readme) identifies its own format and compatibility paths for bsdiff and VCDIFF. Related sibling products and bundled algorithm implementations are not counted separately.

### 24. [mendsley/bsdiff](https://github.com/mendsley/bsdiff)

**Language/role:** C; Matthew Endsley's embeddable adaptation of Colin Percival's bsdiff/bspatch.

This derivative qualifies separately through substantive interface and format changes: the [maintainer's explanation](https://github.com/mendsley/bsdiff#readme) says it removes required disk I/O, minimizes seeking, and uses a patch format incompatible with the original tool.

- **C2:** Allocation, writing, and patch reading are caller-provided stream callbacks. The core diff and patch routines can be embedded independently of the optional executables and compression adapter.
- **C1:** [bspatch.c](https://github.com/mendsley/bsdiff/blob/master/bspatch.c) exposes signed control triples, source/target position arithmetic, length checks, short-read failures, and byte-difference reconstruction in a small codebase.

The numerical and malformed-input handling is a study target, not a security audit or an assertion that every integer edge case is covered. Do not assume its output is interchangeable with BSDIFF40.

### 25. [librsync/librsync](https://github.com/librsync/librsync)

**Language/role:** C; signature-based remote delta computation and application, with an `rdiff` frontend.

Unlike ordinary two-file diffing, the remote-delta model can compute changes using a signature of the old file instead of the old file's complete contents.

- **C2:** The [streaming API](https://librsync.github.io/api_streaming.html) represents resumable operations as opaque jobs, with caller-provided input/output buffers and distinct blocked, finished, and error outcomes.
- **C3:** Explicit state machines preserve progress while applications wait for I/O. Buffer sizing and progress through successive job iterations are part of the documented integration contract.
- **C4:** [NEWS.md](https://github.com/librsync/librsync/blob/master/NEWS.md) documents 2019–2023 work on backward-compatible signature choices, large-file hangs, malformed zero-length copy commands, Windows testing, and reducing intermediate data copying. This is concrete evolution evidence rather than an inference from age.

### 26. [google/archive-patcher](https://github.com/google/archive-patcher)

**Language/role:** Java; ZIP/archive-aware binary patch generation and application. **Archived GitHub repository.**

Study a transformation pipeline around a binary differencer: compressed data obscures similarity, but simply decompressing and recompressing can fail to reproduce the target bytes.

- **C1:** The [architecture description](https://github.com/google/archive-patcher#how-it-works) explains inferring reproducible deflate settings, recording recompression metadata, and leaving entries compressed when those settings cannot be recovered. The target is an exact binary reconstruction, not merely equivalent extracted contents.
- **C2:** [PreDiffExecutor.java](https://github.com/google/archive-patcher/blob/master/generator/src/main/java/com/google/archivepatcher/generator/PreDiffExecutor.java) separates planning from producing intermediate files and supports recommendation modifiers. Plans carry uncompression and recompression ranges.
- **C3:** Only selected changed compressed entries are expanded before differencing; unchanged compressed content remains intact. The documented v1 limitations include ZIP64 and simultaneous rename-plus-content-change detection.

### 27. [eerimoq/detools](https://github.com/eerimoq/detools)

**Language/role:** Python and C; binary delta generation with sequential, HDiffPatch, and in-place update layouts.

Study the extra machinery needed to turn delta algorithms into embedded update protocols. Although it builds on bsdiff and HDiffPatch, its patch layouts and incremental application behavior provide substantive additional engineering.

- **C1:** The [patch-layout documentation](https://github.com/eerimoq/detools/blob/master/docs/index.rst) walks through moving the old image and erasing/writing segments without prematurely destroying required source data. Its resumability discussion requires persistently storing step state and the patch header and rejecting another patch until completion.
- **C3:** The design exposes memory size, segment size, and shift policy, balancing flash operations against transfer costs. Sequential patches support incremental receipt and application.
- **C2:** The [repository documentation](https://github.com/eerimoq/detools#readme) separates algorithm, patch type, and compression choices, and identifies the C incremental applier's narrower sequential-patch support. In-place resumability should not be assumed to apply to every exposed backend.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations: Myers/patience/histogram libraries; syntax-aware AST diff and three-way merge; VCDIFF and binary compression; Rust reusable diff engines; Java/JGit merge implementations; JavaScript fuzzy patching; JSON/XML and Kubernetes field ownership; streaming rsync-style deltas; embedded resumable updates; C++ template differencing; OCaml patience diff; GNU mirror provenance; and Haskell/diff3 and malformed-patch testing. Follow-up searches increasingly returned the same engines, ports, wrappers, or adjacent patch-management tools. Two late additions—DTL and Jane Street's patience_diff—justify extending the usual range to 27 by adding a distinct sequence algorithm and another language/community.

Primary inspection included repository pages, implementation files, API contracts, architecture descriptions, and changelogs. Raw-source reads and GitHub's read-only tree API were used when rendered pages failed. Additional sources were not just duplicate copies of a README. No candidate code was installed or executed, and no benchmark results were independently reproduced. C1 labels identify real correctness obligations and visible handling, not a proof of safety; C3 labels identify mechanisms rather than endorsing cross-project speed claims.

Important boundaries and exclusions:

- **Hosting:** [Mergiraf's official site](https://mergiraf.org/) links its source to Codeberg. It was not included because an official substantive GitHub mirror was not established in this search. GNU diffutils/patch searches surfaced third-party GitHub mirrors; no qualifying official mirror was established, so those mirrors were omitted despite the projects' clear relevance.
- **Duplicate implementations:** Direct diff-match-patch ports, alternate xdelta licensing/history repositories, trivial bindings, and backend-swapping forks were not multiplied into independent entries. Endsley's bsdiff adaptation is explicitly distinguished because it changes embedding interfaces and the patch format. Detools adds update-layout and application-state machinery beyond its underlying algorithms.
- **Monorepos and presentation:** Git, libgit2, and JGit each count once for the named subsystems. Colorizers, comparison GUIs, and review interfaces were excluded when their main contribution was presentation over another engine. Difftastic remains because it implements structural comparison itself.
- **Breadth limits:** Coverage is strongest in C/C++, Rust, Java, JavaScript/TypeScript, Go, Python, and OCaml. Haskell searches did not receive the same depth of primary-source validation and produced no retained entry. CRDT/OT collaboration systems, database schema migration, semantic API compatibility analyzers, and automated program-repair systems are neighboring categories rather than substitutes for this one.
- **Maintenance:** Archived status is stated where verified. Other entries make no blanket active-maintenance claim. Research projects remain useful study targets with their status and limitations visible; use the linked repository when evaluating present-day adoption. Branch links describe the inspected source layout and may evolve after the research date.
