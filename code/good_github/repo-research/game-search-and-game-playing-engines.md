# Game search and game-playing engines

Research date: **2026-10-09**.

This selection covers 23 GitHub codebases that choose moves, solve game positions, or provide substantial reusable infrastructure for game search. It spans competitive engines, research frameworks, exact endgame solvers, imperfect-information strategy computation, and real-time planning. Rendering engines, game launchers, thin engine wrappers, and introductory exercises are outside scope. The engineering study recommendations are inferences from the cited implementations, not claims that every component is exemplary or that an engine's playing strength establishes software quality.

**Criteria legend:** **C1** — difficult correctness involving state invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting multiple games, algorithms, integrations, or use cases. **C3** — concrete performance constraints addressed through an understandable architecture. **C4** — sustained evolution with evidence of compatibility work, testing, or complexity management. Each entry justifies at least two criteria; criteria are not scores or rankings.

## Chess and shogi

### 1. [official-stockfish/Stockfish](https://github.com/official-stockfish/Stockfish)

**C++ — UCI chess engine with neural evaluation and classical search.** A useful study of how numerous search heuristics coexist with carefully defined score and bound semantics. Read the numbered search stages rather than treating the entire engine as one optimization recipe.

- **C1:** Mate-distance pruning, draw handling, and conversion of cached scores using search ply and the fifty-move counter illustrate why a transposition-table value is not simply an evaluation attached to a board. **C3:** The same search pipeline combines table probes, move ordering, selective search, and pruning to control the branching factor. Entry point: [src/search.cpp](https://github.com/official-stockfish/Stockfish/blob/master/src/search.cpp).
- The [contribution guide](https://github.com/official-stockfish/Stockfish/blob/master/CONTRIBUTING.md) adds useful process context: functional changes require Fishtest results and a new benchmark signature; refactorings that might affect performance also require testing. This is evidence of disciplined performance management, without assuming every heuristic has a standalone correctness proof.

### 2. [LeelaChessZero/lc0](https://github.com/LeelaChessZero/lc0)

**C++ — neural chess search with multiple hardware backends.** Study the boundary between irregular tree exploration and batched inference, especially how workers keep expensive accelerators occupied while respecting search and protocol state.

- **C1/C3:** The classic search worker is explicitly split into stages; it manages target minibatches, out-of-order evaluations, shared collisions, atomic stopping, and which thread may emit the final move. These are concrete concurrency and throughput concerns. Entry point: [classic/search.h](https://github.com/LeelaChessZero/lc0/blob/master/src/search/classic/search.h).
- **C2:** `NetworkComputation` exposes batch input, execution, and policy/value outputs behind a backend interface, allowing search to share a contract across implementations. Entry point: [neural/network.h](https://github.com/LeelaChessZero/lc0/blob/master/src/neural/network.h). The repository also contains newer DAG search; this entry's worker discussion specifically concerns the classic subsystem.

### 3. [fairy-stockfish/Fairy-Stockfish](https://github.com/fairy-stockfish/Fairy-Stockfish)

**C++ — configurable engine for chess variants and regional chess-family games.** This is a substantive Stockfish derivative: its distinctive engineering problem is representing different rule systems within a common search engine, rather than merely retuning orthodox chess.

- **C2:** The `Variant` model represents board geometry, custom pieces, promotion regions, drops, capture obligations, castling, and alternative winning conditions. It supports built-in and user-defined games through a shared rules representation. Entry point: [variant.h](https://github.com/fairy-stockfish/Fairy-Stockfish/blob/master/src/variant.h).
- **C1/C3:** Variant construction must reconcile interacting rules. `Variant::conclude()` explicitly enforces consistency and precomputes derived properties for runtime optimizations, providing a concrete example of paying for generality during configuration rather than at every search node. Entry point: [variant.cpp](https://github.com/fairy-stockfish/Fairy-Stockfish/blob/master/src/variant.cpp).

### 4. [cosmobobak/viridithas](https://github.com/cosmobobak/viridithas)

**Rust — UCI chess engine.** A valuable complement to the C++ engines for examining deliberate low-level layout and concurrency choices in Rust. The interesting boundary is between Rust's guarantees and the explicit unsafe representation work needed by the search cache.

- **C1:** Transposition-table storage uses relaxed atomic words; probing rejects a cluster whose checksum does not match its coherence field. The implementation also normalizes mate and tablebase scores when storing them. These mechanisms address torn observations and position-dependent score interpretation; the checksum should not be read as a mathematical guarantee against every collision. Entry point: [transpositiontable.rs](https://github.com/cosmobobak/viridithas/blob/master/src/transpositiontable.rs).
- **C3:** Packed cache entries, clustered storage, replacement decisions, and shared-table access serve the hot search path. Follow their consumers in [search.rs](https://github.com/cosmobobak/viridithas/blob/master/src/search.rs) to study the trade between cache density, synchronization cost, and useful retained work.

### 5. [yaneurao/YaneuraOu](https://github.com/yaneurao/YaneuraOu)

**C++ — USI shogi engine and related search infrastructure.** Particularly useful for comparing chess-derived search machinery with shogi-specific adjudication, and for studying a separate mate-search implementation. Much of the detailed commentary is Japanese.

- **C1:** The main search distinguishes repetition outcomes, maps their scores through ply-sensitive conversions, and handles shogi terminal conditions rather than assuming chess draw rules. Entry point: [yaneuraou-search.cpp](https://github.com/yaneurao/YaneuraOu/blob/master/source/engine/yaneuraou-engine/yaneuraou-search.cpp).
- **C3:** The mate subsystem documents an explicit design tradeoff: proof/disproof-number-guided tree search avoids merging transpositions, retains generated children, and uses compact node storage. The file explains the memory cost and why its algorithm differs from conventional hash-based df-pn. Entry point: [mate_dfpn.hpp](https://github.com/yaneurao/YaneuraOu/blob/master/source/mate/mate_dfpn.hpp). This is a specific subsystem, not a description of every YaneuraOu search mode.

### 6. [TadaoYamaoka/DeepLearningShogi](https://github.com/TadaoYamaoka/DeepLearningShogi)

**C++ and Python — neural shogi engine, MCTS self-play, and training.** The repository separates the shogi library, Python learning code, self-play generation, and USI engine. It acknowledges reused components from other engines; its distinct contribution is the integrated neural shogi search and learning system.

- **C1:** Search updates virtual losses through atomic counters and handles repetition outcomes separately from neural values. The repetition path can override a network estimate, making rule adjudication an explicit part of value propagation.
- **C3:** Searcher groups queue nodes for batched inference and allocate GPU host buffers by the configured batch capacity. Study how per-searcher exploration feeds shared inference resources. Both criteria are visible in [usi/UctSearch.cpp](https://github.com/TadaoYamaoka/DeepLearningShogi/blob/master/usi/UctSearch.cpp); [UctSearch.h](https://github.com/TadaoYamaoka/DeepLearningShogi/blob/master/usi/UctSearch.h) provides the engine-facing declarations.

## Go: neural graph search and classical playouts

### 7. [lightvector/KataGo](https://github.com/lightvector/KataGo)

**C++ and Python — Go engine, analysis service, and self-play learning system.** One of the strongest choices for studying how algorithm explanation, game rules, and inference orchestration fit together.

- **C1:** The graph-search document derives why sharing transposed states requires different accounting from simply treating a tree as a graph. It also clearly separates the core derivation from game-specific cycle handling. Entry point: [GraphSearch.md](https://github.com/lightvector/KataGo/blob/master/docs/GraphSearch.md).
- **C2/C3:** The source map separates raw boards from history-sensitive rules, graph hashing, backend interfaces, thread-safe inference batching, asynchronous search, and batched analysis/match commands. This supports interactive play, analysis services, and training without making each implement its own search stack. Entry point: [C++ architecture overview](https://github.com/lightvector/KataGo/blob/master/cpp/README.md).

### 8. [leela-zero/leela-zero](https://github.com/leela-zero/leela-zero)

**C++ with training tooling — AlphaGo Zero-style Go engine.** A useful earlier neural-MCTS implementation to compare with KataGo. The inspected default branch is `next`; GitHub reported its latest push in May 2024, so this report makes no claim of current active development.

- **C1:** `play_simulation()` installs scope-exit cleanup for virtual loss even if neural evaluation throws, and invalidates moves that violate superko. These are concrete examples of search bookkeeping surviving exceptions and game-history constraints.
- **C3:** Root reuse preserves previous work, while expansion thresholds respond to the tree's memory budget. The architecture makes memory pressure part of search policy rather than allowing unchecked growth. Entry point for both: [src/UCTSearch.cpp](https://github.com/leela-zero/leela-zero/blob/next/src/UCTSearch.cpp). The repository overview also documents that network weights are separate from the engine source.

### 9. [pasky/pachi](https://github.com/pasky/pachi)

**C — modular Go engine using MCTS, tactical playouts, and optional neural priors.** A particularly informative contrast to neural-value engines because substantial work remains in explicit tactical policies and board operations.

- **C2:** The documented design separates the engine interface, node-selection policy, prior hints, playout policy, tactical routines, and distributed orchestration. These interfaces support experiments with different policies and engines within one framework.
- **C3:** Its engineering notes discuss where CPU time goes and explain board-representation choices, including tracking real liberties to support heavier playouts. Entry point for both: [HACKING](https://github.com/pasky/pachi/blob/master/HACKING).
- Scope caveat: the project's own documentation warns that its GTP parser is unsuitable for direct exposure to untrusted users. Inclusion recognizes search architecture, not parser hardening.

## Other board-game engines

### 10. [dhbloo/rapfi](https://github.com/dhbloo/rapfi)

**C++ — Gomoku and Renju engine with classical and neural evaluation.** Study how a general alpha-beta structure incorporates tactical line threats and asymmetric Renju rule details.

- **C1:** The search classifies Renju false-forbidden patterns as important moves, incorporates dedicated continuous-four attack/defense search, and restricts when results may be written to its persistent database, including excluding null-move and certain restricted searches.
- **C3:** Rule- and node-type-specialized search shares a pipeline with transposition tables, move histories, late-move reductions, and multiple search threads. The root selects among workers using search results and completed depth. Entry point: [alpha-beta search implementation](https://github.com/dhbloo/rapfi/blob/master/Rapfi/search/ab/search.cpp). These are implemented mechanisms; no numerical playing-strength or speed claim is needed to justify the selection.

### 11. [abulmo/edax-reversi](https://github.com/abulmo/edax-reversi)

**C — Othello/Reversi engine with bitboards and exact endgame search.** An excellent focused study of endgame specialization: the rules are compact, but correct pass handling and terminal score conventions remain essential.

- **C1:** Small-empty-square solvers explicitly switch players on a pass, distinguish terminal positions, and propagate the final disc-difference score through null-window bounds.
- **C3:** Dedicated small-endgame routines use parity-based move ordering, stability cutoffs, bit operations, and specialized flip computation rather than running every position through a uniform generic search. Entry point: [src/endgame.c](https://github.com/abulmo/edax-reversi/blob/master/src/endgame.c). The repository's description identifies the broader engine as multithreaded, but the small-endgame implementation is the main recommendation here.

### 12. [Nyanyan/Egaroucid](https://github.com/Nyanyan/Egaroucid)

**C++ — Othello engine used by desktop, console, web, and library interfaces.** Its distinctive study angle is explicit parallel principal-variation/null-window search and the handling of incomplete work.

- **C1:** Search records whether the preceding player passed and only treats the next pass as terminal. Parallel tasks translate cancellation into `SCORE_UNDEFINED`, preventing an interrupted task from being treated as a normal score. Entry points: [midsearch.hpp](https://github.com/Nyanyan/Egaroucid/blob/main/src/engine/midsearch.hpp) and [ybwc.hpp](https://github.com/Nyanyan/Egaroucid/blob/main/src/engine/ybwc.hpp).
- **C3:** The Young Brothers Wait Concept implementation applies separate depth thresholds for midgame and endgame splitting, wraps independent search state in tasks, and uses null-window results to stop unnecessary sibling work. This exposes the interaction between pruning and parallel scheduling rather than merely adding threads around a serial function.

### 13. [rhalbersma/mobydam](https://github.com/rhalbersma/mobydam)

**C — international draughts engine; author-endorsed GitHub mirror.** Harm Jetten's [official project page](https://hjetten.home.xs4all.nl/mobydam/mobydam.html) explicitly links this mirror. It is retained as a substantive source distribution, not presented as an independently developed fork.

- **C1:** Move generation retains only capture sequences with the maximum number of captured pieces and updates king/promotion state when constructing resulting bitboards. Entry point: [core/move.c](https://github.com/rhalbersma/mobydam/blob/main/core/move.c).
- **C3/C4:** The documented 2015–2026 releases show progression from single-threaded search to Lazy SMP, pattern-based evaluation, compiler-specific move-generation improvements, a killer-move representation fix, and additional protocol support. This is concrete sustained evolution and compatibility work, not an inference from repository creation time. Entry point: [history.txt](https://github.com/rhalbersma/mobydam/blob/main/history.txt). The mirror's small commit count should not be mistaken for the project's full development history.

### 14. [enz/pentobi](https://github.com/enz/pentobi)

**C++ — Blokus-family engine with reusable board-game MCTS.** The maintainer describes it as primarily in maintenance mode. It is unusually useful for studying the boundary between generic search and specialized multi-player board representation.

- **C2:** The source organization separates reusable board-game utilities, GTP, tests, and abstract MCTS from Blokus-specific state, move generation, and priors. Entry point: [CONTRIBUTING.md source overview](https://github.com/enz/pentobi/blob/main/CONTRIBUTING.md).
- **C1/C3:** `SearchBase` specifies per-thread game-state requirements, positive initial child counts, memory budgets, and abort-check tradeoffs. Its RAVE variant deliberately combines statistics to reduce tree memory and selection work, with the algorithmic tradeoff documented. Entry point: [libboardgame_mcts/SearchBase.h](https://github.com/enz/pentobi/blob/main/libboardgame_mcts/SearchBase.h).

## Card-game solving

### 15. [dds-bridge/dds](https://github.com/dds-bridge/dds)

**C++ with language bindings — bridge double-dummy solver.** This solves card play with all hands known; it is not by itself a complete imperfect-information bridge player. The inspected branch is `develop`, including its 3.1 release-note document.

- **C1:** The notes describe a concrete correctness failure in play analysis: repeatedly starting from a cold transposition table caused a hint-bounded search to return the wrong bound. Reusing the caller's context fixes that path. They also describe memory-lifetime fixes and reporting worker exceptions through error results.
- **C2/C3:** Instance-scoped solver contexts support reusable per-worker state; a persistent worker pool and work-stealing dispatcher process board batches, with difficult boards scheduled first. These architecture details and regression-workload checks are documented in the [3.1 notes](https://github.com/dds-bridge/dds/blob/develop/docs/release_notes/release_v3_1_0.md).
- **C4:** The project overview traces the earlier solver and modernization history, while the [ChangeLog](https://github.com/dds-bridge/dds/blob/develop/ChangeLog) records compiler, threading, memory-management, and interface fixes. The newer notes explicitly preserve existing 3.0 APIs while documenting behavioral corrections and deprecations.

### 16. [bupticybee/TexasSolver](https://github.com/bupticybee/TexasSolver)

**C++ — Texas Hold'em and short-deck strategy solver.** A useful move beyond perfect-information minimax into counterfactual-regret computation over private-hand ranges. The README points to a newer GPU product; this entry evaluates the still-available C++ source, not that separate product or its advertised performance.

- **C1:** The solver filters private ranges against public cards and propagates reach probabilities through action, chance, showdown, and terminal nodes. Correct utilities depend on card compatibility and whose strategy contributes to each reach probability.
- **C3:** The parallel solver distributes chance-card work with OpenMP, supports suit-isomorphism handling, and flattens action-by-hand regret data to control processing cost. Entry point: [src/solver/PCfrSolver.cpp](https://github.com/bupticybee/TexasSolver/blob/master/src/solver/PCfrSolver.cpp). Its explicit node-type dispatch makes the optimization choices traceable to the extensive-form game structure.

## Reusable search and general game playing

### 17. [google-deepmind/open_spiel](https://github.com/google-deepmind/open_spiel)

**C++ and Python — game representations, search algorithms, and strategic-learning research framework.** Counted once as a monorepo; the relevant subsystem is its common game API and search/solver algorithms. It is especially useful for studying which assumptions an algorithm makes about a game's information and transition model.

- **C1/C2:** `Game`/`State` distinguish player actions, chance outcomes, simultaneous play, observations, and information states. The API explicitly distinguishes enumerated stochastic outcomes from sampled stochastic transitions, which affects what algorithms can legitimately infer. Entry point: [open_spiel/spiel.h](https://github.com/google-deepmind/open_spiel/blob/master/open_spiel/spiel.h).
- **C3:** Its MCTS implementation combines evaluator interfaces, explicit chance sampling, proven outcomes, and memory limits with garbage collection. Entry point: [algorithms/mcts.cc](https://github.com/google-deepmind/open_spiel/blob/master/open_spiel/algorithms/mcts.cc). The existence of imperfect-information games in the framework does not make ordinary MCTS appropriate for every such game; algorithms must be selected according to their assumptions.

### 18. [Ludeme/Ludii](https://github.com/Ludeme/Ludii)

**Java — declarative general game system with built-in search agents.** Counted once, focusing on the `AI` subsystem. Study how one game representation supports multiple search strategies and how MCTS components are made replaceable without hiding their interactions.

- **C2:** MCTS composes separate selection, playout, backpropagation, final-move selection, and node implementations. The tree includes deterministic, open-loop, and score-bound node alternatives rather than forcing every game into one state-handling strategy.
- **C1/C3:** Parallel iterations use a thread pool, virtual visits, per-node locking, and tracking of busy workers. The main loop exposes exactly where traversal and expansion synchronize. Entry point: [AI/src/search/mcts/MCTS.java](https://github.com/Ludeme/Ludii/blob/master/AI/src/search/mcts/MCTS.java). This provides an implementation-level route from the project's broad general-game description into its actual search machinery.

### 19. [ggp-org/ggp-base](https://github.com/ggp-org/ggp-base)

**Java — General Game Playing infrastructure for Game Description Language rules.** A historical framework rather than a claim of active development: the inspected repository metadata showed its latest push in January 2021. Its value is the semantic and compilation infrastructure beneath reusable players, not the strength of sample agents.

- **C2/C3:** Players use a common state-machine view of initial states, roles, legal moves, transitions, and goals. The optimizing proposition-network factory transforms GDL, infers constants, removes useless propositions, and normalizes output for existing state-machine implementations. Entry point: [OptimizingPropNetFactory.java](https://github.com/ggp-org/ggp-base/blob/master/src/main/java/org/ggp/base/util/propnet/factory/OptimizingPropNetFactory.java). Its comments explicitly note a restriction on recursive sentence dependencies; this is not an unrestricted compiler for every legal rulesheet.
- **C1:** A consistency checker follows common randomized joint moves through reference and subject state machines and checks legal-move counts, terminal behavior, and goal values. Entry point: [StateMachineVerifier.java](https://github.com/ggp-org/ggp-base/blob/master/src/main/java/org/ggp/base/util/statemachine/verifier/StateMachineVerifier.java). This is useful differential-checking infrastructure, not an exhaustive equivalence proof.

### 20. [jonathan-laurent/AlphaZero.jl](https://github.com/jonathan-laurent/AlphaZero.jl)

**Julia — generic AlphaZero learning system and standalone MCTS.** A valuable higher-level-language counterpart to the specialized C++ engines, with a compact search implementation that exposes mathematical conventions directly.

- **C2:** MCTS accepts a game interface and an external policy/value oracle; the supplied rollout oracle also supports conventional simulation-based MCTS. Entry point: [src/mcts.jl](https://github.com/jonathan-laurent/AlphaZero.jl/blob/master/src/mcts.jl).
- **C1:** Value backup checks whether the player actually changed before reversing the continuation value, rather than assuming every action alternates turns. The code also separates root exploration noise from subsequent selection. The [custom-game guide](https://github.com/jonathan-laurent/AlphaZero.jl/blob/master/docs/src/tutorial/own_game.md) documents game-interface sanity checks, dummy training runs, and gradient-update checks before expensive training. These are specific semantic and failure-detection mechanisms, not a claim that arbitrary game interfaces will work automatically.

## Real-time strategy and planning

### 21. [Farama-Foundation/MicroRTS](https://github.com/Farama-Foundation/MicroRTS)

**Java — small RTS environment with built-in game-tree-search agents.** The old `santiontanon/microrts` URL redirects here. The official README explicitly deprecated the project on August 11, 2025 and says further updates/support are not planned. Retained as a substantive historical research implementation, focusing on `src/ai` rather than its renderer.

- **C1:** Simultaneous, durative unit actions must remain compatible with resources already committed to ongoing actions. Naive MCTS builds a base resource usage and rejects sampled unit actions that conflict with the partially constructed joint action.
- **C3:** Per-unit action tables and epsilon-greedy sampling build joint actions without exhaustively enumerating the full combination space. Entry point: [NaiveMCTSNode.java](https://github.com/Farama-Foundation/MicroRTS/blob/master/src/ai/mcts/naivemcts/NaiveMCTSNode.java). This is a useful study of combinatorial action selection under legality constraints; simplifications relative to a full commercial RTS are part of the research design.

### 22. [davechurchill/ualbertabot](https://github.com/davechurchill/ualbertabot)

**C++ — StarCraft bot monorepo containing BOSS planning and SparCraft combat search.** The maintainer explicitly states that UAlbertaBot has not been actively maintained since early 2021. Counted once; the recommendation concerns its search subsystems and their integration problems.

- **C2/C3:** BOSS separates build-order goals, prerequisite/resource constraints, action relevance, and search parameters. Its smart-search wrapper can resume a timed-out stack search and configures supply bounding and action repetitions. Entry point: [DFBB_BuildOrderSmartSearch.cpp](https://github.com/davechurchill/ualbertabot/blob/master/BOSS/source/DFBB_BuildOrderSmartSearch.cpp).
- **C1/C3:** SparCraft's alpha-beta search handles vectors of simultaneous unit actions, modeled responses, transposition-table move ordering, and periodic time-budget checks. Entry point: [SparCraft/AlphaBetaSearch.cpp](https://github.com/davechurchill/ualbertabot/blob/master/SparCraft/source/AlphaBetaSearch.cpp). The combination is useful for studying two different search problems inside one agent rather than assuming a single planner handles the whole game.

## Falling-block game search

### 23. [MinusKelvin/cold-clear](https://github.com/MinusKelvin/cold-clear)

**Rust with a C API — modern versus-Tetris bot.** The owner archived this repository on January 22, 2024. It remains a substantial historical implementation, particularly valuable for its documented DAG and asynchronous integration semantics.

- **C1:** Search generations distinguish known from speculated future pieces. Converting a generation to known preserves node keys, hold state participates in state identity, and updates for expired generations are rejected. Entry point: [bot/src/dag.rs](https://github.com/MinusKelvin/cold-clear/blob/master/bot/src/dag.rs).
- **C3:** The same file explains state deduplication, generation reclamation, and arena allocation to reduce allocator overhead. It distinguishes implemented layouts from hypothetical compression alternatives.
- **C2:** The [C API](https://github.com/MinusKelvin/cold-clear/blob/master/c-api/coldclear.h) supports asynchronous move requests, supplying newly revealed pieces, starting from a midgame state, and resetting after actual placement diverges from the predicted one. Those explicit contracts make it more reusable than a bot coupled to one client.

## Coverage, search process, and limitations

Discovery used more than six distinct live search formulations, including chess alpha-beta/transposition-table engines; neural Go and graph search; shogi and USI engines; Othello endgame solvers; draughts engines and mirror provenance; Hex/Benzene; bridge double-dummy and poker CFR solvers; Rust/Tetris search; GDL/general game playing; Julia AlphaZero; and RTS build-order/combat search. Follow-up queries explored expectimax and backgammon. Later searches predominantly returned already represented architectures, wrappers, tutorials, or mirrors whose official status was unclear; the author-endorsed Moby Dam mirror was the final substantive addition.

Every retained canonical repository URL was opened or verified through the public GitHub API. Repository material was checked for category fit, and additional primary implementation or architecture material was retrieved and inspected for every entry. API metadata was also checked for archived status and canonical transfers. Source links use the branches inspected during research (`master`, `main`, Leela Zero's `next`, and DDS's `develop`), so their contents can change. This is a source-reading selection, not a build, runtime audit, benchmark reproduction, or promise of current support. No candidate code was executed and no dependencies were installed.

The search deliberately avoided multiplying similar Stockfish forks, counting language bindings as separate engines, or treating popular engine GUIs as search implementations. Fairy-Stockfish is retained because its rule-generalization layer is substantial; related shogi projects are distinguished by their actual search/training subsystems. Moby Dam is explicitly an author-endorsed mirror. Benzene/MoHex and Fuego appeared in discovery, but the inspected Benzene project page pointed to SourceForge and did not establish an official GitHub distribution; unverified GitHub repackagings were not promoted to canonical entries. Backgammon coverage remains limited because a suitable substantive official GitHub source was not established in this search.

The resulting selection is strongest in board-game search. C and C++ predominate for substantive architectural reasons in this ecosystem; Rust, Java, Julia, and Python-backed systems add contrasting ownership, abstraction, and research-workflow approaches. Historical status, specialized rules, incomplete documentation, and algorithm assumptions matter when choosing a codebase to study. Stars and unverified strength/speed claims were not used as quality evidence.
