# Parser generators and parsing libraries

Research date: **2026-10-09**

This report selects 25 GitHub repositories for studying reusable parsing infrastructure: grammar compilers, generalized and incremental parsers, PEG systems, and parser combinators for text, token streams, and binary data. It includes both established projects and smaller implementations with distinctive engineering decisions. Format-specific parsers and collections of grammars are outside this selection. Repository headings link to canonical GitHub locations checked through repository pages and GitHub metadata; each entry also draws on a separately inspected implementation file or substantive technical document.

The criteria describe reasons to study a codebase, not a certification of every component:

- **C1 — Difficult correctness:** invariants, ambiguity, backtracking, malformed or partial inputs, concurrency, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or intermediate representations supporting multiple grammars and applications.
- **C3 — Performance with structure:** concrete handling of execution cost, memory, incremental work, or compilation cost through understandable architecture.
- **C4 — Sustained evolution:** evidence across years combined with compatibility, testing, or deliberate management of complexity.

## Grammar compilers, LR families, and incremental parsing

### [antlr/antlr4](https://github.com/antlr/antlr4)

**Language/role:** Java grammar tool with runtimes for multiple target languages; adaptive LL parsing. Study how a reusable prediction engine balances context sensitivity, caching, and concurrent parser instances.

- **C1:** The Java prediction engine distinguishes SLL conflicts from genuine ambiguity by retrying with full outer context. Its implementation documentation also explains synchronization when separate parser instances populate shared DFA states; a shared cache does not make an individual parser instance safe to share.
- **C2:** Grammars generate lexers, parsers, and tree traversal interfaces across target runtimes, separating language descriptions from applications that consume parse trees.
- **C3:** ATN simulation constructs DFA paths that later predictions reuse. The design explicitly explains why full-context predictions are not generally cached, including predicate and memory complications.

**Technical entry point:** [ParserATNSimulator architecture and thread-safety discussion](https://www.antlr.org/api/Java/org/antlr/v4/runtime/atn/ParserATNSimulator.html), supporting the prediction and caching claims above.

### [akimd/bison](https://github.com/akimd/bison)

**Language/role:** C and M4-based GNU Bison generator, with multiple target-language skeletons. **Status:** maintainer-operated GitHub mirror/CI repository for GNU Bison, not a separate parser implementation. Akim Demaille's [2018 announcement](https://lists.gnu.org/r/bison-patches/2018-09/msg00005.html) explains this GitHub repository's relationship to Bison and compiler testing.

- **C1:** The GLR skeleton represents unresolved semantic alternatives separately from resolved values. Deferred action resolution must preserve states that can still be destroyed safely after an error; precedence and merge functions decide which alternatives survive. This is a useful study of correctness when parsing can follow multiple stacks.
- **C2:** The same grammar-tool infrastructure supports LALR, IELR, canonical LR, and GLR approaches, with target-specific skeletons separating runtime mechanics from grammar analysis.

**Technical entry point:** [C GLR skeleton](https://github.com/akimd/bison/blob/master/data/skeletons/glr.c), especially `yyGLRState`, `yySemanticOption`, `yypreference`, and `yyresolveStates`.

### [lalrpop/lalrpop](https://github.com/lalrpop/lalrpop)

**Language/role:** Rust parser generator; despite its name, its documented default is LR(1). Study typed grammar compilation and recovery that fits Rust's value and ownership model.

- **C1:** Recovery rules introduce the special `!` symbol and carry both the parse error and discarded tokens. The documentation distinguishes parser recovery from lexer failures: an invalid token must be represented appropriately by the lexer if the grammar is to recover from it. Recovery results must also fit the surrounding rule's output type.
- **C2:** Parameterized grammar macros describe recurring structures such as comma-separated lists and restricted expression subsets. Type inference and Rust semantic actions make these reusable grammar components rather than a library of generated wrappers.

**Technical entry point:** [Error recovery tutorial](https://lalrpop.github.io/lalrpop/tutorial/008_error_recovery.html), including error-bearing AST variants and the lexer boundary.

### [tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter)

**Language/role:** Rust generator/tooling and C parsing runtime; incremental syntax trees for editor and analysis workloads. The generator and runtime are counted as one repository.

- **C1:** Incremental updates require correct old/new byte offsets and point coordinates. Existing node handles may need their own edits or replacement. For concurrency, the documentation requires separate tree copies for simultaneous use rather than treating an individual tree as thread-safe.
- **C2:** Included ranges support parsing embedded languages inside larger documents through the same runtime API.
- **C3:** Reparsing an edited tree reuses unchanged structure. Tree copies use reference counting to make shared immutable structure economical, directly addressing repeated parsing and cross-thread analysis costs.

**Technical entry point:** [Advanced parsing: editing, included ranges, and concurrency](https://tree-sitter.github.io/tree-sitter/using-parsers/3-advanced-parsing.html).

### [haskell/happy](https://github.com/haskell/happy)

**Language/role:** Haskell parser generator with conventional LR and a GLR backend. Particularly useful for studying how generalized parsing can reuse a table-generation foundation.

- **C1:** The GLR backend represents alternatives in a shared and-or graph indexed by input extents and grammar symbols. Producing ordinary trees from that representation can expose exponentially many alternatives; ambiguity is a representation and evaluation problem, not merely a parser switch.
- **C3:** The GLR implementation reuses LALR tables and separates generated driver code from tables so large data structures do not overwhelm compiler optimization. Shared subanalyses avoid duplicating complete trees during recognition.

**Technical entry point:** [GLR backend design and limitations](https://haskell-happy.readthedocs.io/en/latest/glr.html). Its documented limitations matter: familiar Happy facilities, including error-token recovery, do not all carry over to this backend. The [developer notes](https://github.com/haskell/happy/blob/master/DEVELOPER.md) additionally show release sanity checks derived from earlier release failures.

### [softdevteam/grmtools](https://github.com/softdevteam/grmtools)

**Language/role:** Rust grammar-tool monorepo; relevant subsystems are `cfgrammar`, `lrtable`, `lrlex`, and `lrpar`. Study the interface between syntax repair and typed semantic actions.

- **C1:** `lrpar`'s CPCT+ recovery can report alternative minimal repair sequences involving inserted or deleted tokens. An inserted integer token has no legitimate source integer value: the documented action interface distinguishes inserted lexemes, and examples propagate semantic failure through `Result` rather than inventing a value. Syntactic recovery therefore remains separate from successful evaluation.
- **C2:** Grammar representation, LR tables, lexing, and parsing are separated into reusable libraries. Both build-time Yacc integration and runtime parsing fit the suite, with typed actions and an error collection returned alongside a possible result.

**Technical entry point:** [Error recovery and semantic-action handling](https://softdevteam.github.io/grmtools/master/book/errorrecovery.html), including `%avoid_insert` and repair alternatives.

## Generalized parsing and grammar interpretation

### [lark-parser/lark](https://github.com/lark-parser/lark)

**Language/role:** Python parsing toolkit offering Earley and LALR parsing, grammar composition, and tree processing. Study how lexer policy changes the language a generalized parser can actually recognize.

- **C1:** Earley support does not automatically resolve every lexical ambiguity. The documentation distinguishes dynamic lexing's longest matches from `dynamic_complete`, which explores alternatives within token matches. The contextual LALR lexer instead uses parser expectations to restrict candidate terminals.
- **C2:** A common grammar and tree-processing framework supports different parser/lexer combinations, letting applications select ambiguity handling and execution characteristics without replacing all surrounding tooling.
- **C3:** Shared packed parse forests avoid duplicating every ambiguous derivation. The documentation explains the cost of exhaustive lexical exploration, particularly for open-ended regular expressions.

**Technical entry point:** [Parser and lexer architecture](https://lark-parser.readthedocs.io/en/latest/parsers.html). These are documented tradeoffs, not an independently measured speed ranking.

### [jeffreykegler/Marpa--R2](https://github.com/jeffreykegler/Marpa--R2)

**Language/role:** Perl interface and distribution for Marpa's generalized parsing machinery. Useful for studying recognition where ambiguity, nullable rules, and lexer/parser interaction are fundamental design concerns.

- **C1:** The documented grammar model permits left and right recursion, empty productions, and ambiguous grammars. Its scanless interface constrains token selection using what the structural grammar can accept, making lexical ambiguity part of the parsing contract.
- **C2:** The scanless DSL separates structural rules (`::=`) from lexical rules (`~`) and configures semantic actions independently. This gives applications reusable layers for tokenization, recognition, and evaluation rather than embedding all three in one handwritten loop.

**Technical entry point:** [Marpa::R2 manual and scanless-interface explanation](https://metacpan.org/pod/Marpa::R2), including the G1/L0 distinction and longest-acceptable-token matching. Broad performance statements in the manual are not used here as benchmark evidence.

### [Engelberg/instaparse](https://github.com/Engelberg/instaparse)

**Language/role:** Clojure/ClojureScript general context-free grammar parsing. Study how persistent data structures and result representation affect a parser that supports ambiguity and recursion.

- **C2:** EBNF, ABNF, and combinator-based grammar construction feed a common system with alternative tree representations and access to multiple parses. The reusable abstraction is a grammar-to-parser and tree-transformation pipeline.
- **C3:** The performance document traces concrete costs: hashing cached intermediate results, concatenating partial result sequences, and changed JVM substring behavior. It explains custom constant-time concatenation and the memory consequences of retaining input and intermediate parses. These details connect algorithmic promises to host-runtime behavior.

**Technical entry point:** [Performance implementation notes](https://github.com/Engelberg/instaparse/blob/master/docs/Performance.md). The document acknowledges resource limits; support for arbitrary grammars should not be read as uniformly cheap parsing.

## PEG systems and language toolkits

### [neogeny/TatSu](https://github.com/neogeny/TatSu)

**Language/role:** Python PEG/packrat parser generation and runtime grammar interpretation. Study how left recursion is incorporated into a prioritized grammar formalism.

- **C1:** The left-recursion documentation describes support for direct and indirect recursion using the Laurent–Mens approach. It also explains consequences for associativity and warns that ordered choice still affects results. Accepting a recursive grammar is not sufficient to guarantee the author's intended tree shape.
- **C2:** Grammars can generate Python parser code or be used through runtime grammar objects. AST construction and semantic processing make the grammar reusable across recognition and interpretation tasks.

**Technical entry point:** [Left-recursion semantics and implementation basis](https://tatsu.readthedocs.io/en/stable/left_recursion.html). This is a particularly useful comparison with PEG systems that reject left-recursive rules during grammar validation.

### [pest-parser/pest](https://github.com/pest-parser/pest)

**Language/role:** Rust PEG parser framework with grammar tooling and derive-based integration. The parser, derive machinery, and grammar-analysis subsystems count once.

- **C1:** The grammar validator checks repetitions that cannot fail or cannot make progress, unreachable alternatives, and left recursion. Nullable prefixes complicate recursion detection; the inspected implementation includes targeted tests for optional, repeated, and indirect cases. This is substantial static correctness work before user input is parsed.
- **C2:** Declarative grammar rules integrate with Rust through generated parser interfaces. Nested `Pair` values and source spans provide a reusable result model for AST builders and diagnostics.

**Technical entry points:** [Grammar validator and its tests](https://github.com/pest-parser/pest/blob/master/meta/src/validator.rs) and [PEG execution semantics](https://pest.rs/book/grammars/peg.html). Study the validator alongside ordered-choice and repetition behavior rather than assuming CFG semantics.

### [Chevrotain/chevrotain](https://github.com/Chevrotain/chevrotain)

**Language/role:** TypeScript parsing toolkit whose JavaScript grammar DSL does not require an external code-generation step. Study recovery as part of the parser's result contract.

- **C1:** Recovery tries mechanisms including single-token insertion/deletion and resynchronization. The documentation distinguishes a recovered CST node from a complete successful node: child entries may be absent. Embedded-action grammars similarly need meaningful recovery return values instead of blindly assuming every rule completed.
- **C2:** Lexer definitions, grammar rules, CST processing, and embedded actions provide separable application interfaces. Recovery decisions and returned values can be customized rather than being fixed inside a generated parser.

**Technical entry point:** [Fault-tolerance algorithms and output consequences](https://chevrotain.io/docs/tutorial/step4_fault_tolerance.html). This is useful for engineers building editor or diagnostic pipelines that must continue after malformed input.

### [ohmjs/ohm](https://github.com/ohmjs/ohm)

**Language/role:** JavaScript grammar system with separate semantics and incremental matching. Study grammar reuse without coupling recognition to a single AST or interpreter.

- **C2:** Grammar inheritance and separate semantic operations/attributes let multiple interpretations share a grammar. Semantics can themselves be extended for derived grammars, providing explicit reuse mechanisms on both sides of recognition.
- **C3:** A matcher can replace an input range and reuse partial matching results on subsequent matches. The API exposes the persistent matcher separately from one-shot matching, making incremental work an understandable application-level choice.

**Technical entry point:** [API reference: grammars, matchers, and semantics](https://ohmjs.org/docs/api-reference). The combination is especially instructive for interactive language tools that repeatedly interpret changing input.

### [peggyjs/peggy](https://github.com/peggyjs/peggy)

**Language/role:** JavaScript PEG parser generator; successor to PEG.js, which is not counted as another selection. Study extensible compiler passes and explicit memoization policy.

- **C1:** Compiler plugins operate in named stages such as preparation, checking, transformation, and generation. The documentation identifies assumptions that are unsafe before checking finishes, and its session mechanism collects errors before advancing stages. Plugin ordering is therefore part of compiler correctness.
- **C2:** Plugins can inspect or transform the grammar AST, while generated parsers can be distributed without the generator runtime.
- **C3:** Optional caching addresses pathological repeated work, with documented overhead on ordinary inputs. It is an explicit time/memory policy rather than an unconditional claim that memoization is faster.

**Technical entry point:** [Generator documentation, caching options, and plugins API](https://peggyjs.org/documentation.html).

## Rust and C++ parsing libraries

### [rust-bakery/nom](https://github.com/rust-bakery/nom)

**Language/role:** Rust parser combinators for textual and binary formats, including streaming input. Study how a small result algebra controls composition.

- **C1:** The error model distinguishes a recoverable alternative failure, a committed failure, and insufficient input. Streaming parsers must preserve the difference between an incomplete buffer and a definitively malformed value; collapsing them changes protocol behavior.
- **C2:** Parsers combine through functions and combinators, returning the remaining input with their output. Byte, string, numeric, and bit-oriented operations share this model and allow application-specific error types.
- **C3:** Returning slices borrowed from the input permits zero-copy parsing where the format and desired output allow it. This optimization is visible in the types rather than hidden behind an opaque parser service.

**Technical entry points:** [Error variants and their control-flow contracts](https://docs.rs/nom/latest/nom/enum.Err.html) and [API guide to composition and streaming](https://docs.rs/nom/latest/nom/).

### [winnow-rs/winnow](https://github.com/winnow-rs/winnow)

**Language/role:** Rust parsing library, explicitly a substantive fork of nom. It is retained separately because its stream interfaces, result handling, and design priorities have diverged, as documented in the [project rationale](https://docs.rs/winnow/latest/winnow/_topic/why/index.html).

- **C1:** Mutable streams use explicit checkpoints and resets to support speculative parsing. Partial-input handling is represented through the input model, making complete-versus-streaming behavior a deliberate choice.
- **C2:** The `Stream` abstraction distinguishes input state from the slice returned by a parser; this permits more than a plain immutable byte-slice representation.
- **C3:** `Accumulate` allows repeated parsing to produce a collection, count, or no retained values. The design discussion connects allocation choices and simpler function-based execution with tradeoffs against more elaborate parse-mode specialization.

**Technical entry point:** [Detailed differences from nom](https://docs.rs/winnow/latest/winnow/_topic/nom/index.html), complementing the rationale above.

### [taocpp/PEGTL](https://github.com/taocpp/PEGTL)

**Language/role:** C++ template-based PEG library. Study how grammar metadata supports analysis and debugging while actions remain separate from recognition.

- **C1:** Grammar analysis examines rule structure for cycles that can recur without progress, including left recursion. The debugging document also explains why internal implementation rules can be hidden from user actions: reusing a rule internally must not accidentally trigger an application's action for a different syntactic construct.
- **C2:** Grammars are composed from C++ rule types; actions and control behavior can be attached independently. Rule metadata supports inspection and tracing without requiring an entirely different grammar representation.

**Technical entry point:** [Grammar analysis, rule metadata, and tracing](https://github.com/taocpp/PEGTL/blob/main/doc/Debug-Facilities.md). The documentation describes analysis limits, so this should not be mistaken for a proof of every user-defined rule's behavior.

### [foonathan/lexy](https://github.com/foonathan/lexy)

**Language/role:** C++ parsing DSL intended to express the decisions of a handwritten recursive-descent parser. Study explicit commitment and value construction.

- **C1:** A branch separates a condition from its body. Once the condition succeeds, body failure is an error rather than permission to silently try another branch. Choice requires suitable branch rules, making ambiguous control flow and accidental backtracking visible in the grammar's construction.
- **C2:** Recognition rules and value callbacks are distinct, allowing the same DSL to build user-defined values from text or binary inputs.
- **C3:** Explicit branching controls speculative work and avoids rescanning after a decision has been made. The branching guide explains when alternatives inspect input and when they commit, giving engineers a local way to reason about cost.

**Technical entry point:** [Branch rules and choice semantics](https://lexy.foonathan.net/learn/branching/).

### [boostorg/spirit](https://github.com/boostorg/spirit)

**Language/role:** C++ embedded grammar libraries; this entry focuses on Spirit X3 parsing and its relationship to older Spirit generations. **Status:** the current repository notice says it is no longer actively maintained and that pre-X4 components are feature-frozen. Treat this as a substantial legacy study resource.

- **C2:** Typed rules, synthesized attributes, iterator types, and parsing contexts connect grammar expressions to application ASTs while keeping interfaces distinct from implementations.
- **C3:** The X3 program-structure guide separates declaration, definition, and explicit instantiation across translation units. This directly addresses repeated template compilation and generated-code size.
- **C4:** The repository records Boost integration in 2003, V2 in 2008, and X3 in 2014. Its present patch policy requires preserving existing semantics, providing concrete evidence of long evolution followed by deliberate compatibility management, beyond mere repository age.

**Technical entry point:** [X3 program structure and separate compilation](https://www.boost.org/doc/libs/develop/libs/spirit/doc/x3/html/spirit_x3/tutorials/minimal.html). The repository's opening notice takes precedence over older promotional or support wording further down its README.

## Host-language combinators and compiled DSLs

### [mrkkrp/megaparsec](https://github.com/mrkkrp/megaparsec)

**Language/role:** Haskell monadic parser combinators. Study the interaction between parser effects, custom token streams, and structured diagnostics.

- **C1:** The API represents parser state and structured parse errors explicitly and provides mechanisms such as `observing` and `withRecovery` for inspecting or recovering from failures. Applications must handle input consumption and recovery results coherently rather than treating every failed branch identically.
- **C2:** `MonadParsec` and `ParsecT` allow parsing capabilities to compose with monad stacks; custom stream and error types support more than character-only parsers.
- **C3:** Chunk-oriented primitives can return contiguous token chunks without rebuilding them through repeated single-token parsing. The optimization follows the stream abstraction rather than bypassing it.

**Technical entry point:** [Text.Megaparsec API and state/error types](https://hackage.haskell.org/package/megaparsec-9.7.0/docs/Text-Megaparsec.html), read alongside the repository's explanation of chunk primitives.

### [stephan-tolksdorf/fparsec](https://github.com/stephan-tolksdorf/fparsec)

**Language/role:** F# parser combinators with C# infrastructure. Particularly useful for studying precise backtracking scope and useful error preservation.

- **C1:** `attempt` restores state after a failing speculative parser, while narrower sequencing operators only permit rollback under specified failure/state conditions. The guide shows why wrapping a large expression parser can erase a useful deep error and cause unintended alternative parsing.
- **C2:** Parsers carry both result types and user-state types; combinators, lookahead, and operator-precedence facilities reuse that model across language and data-format grammars.
- **C3:** Restricting backtracking to the intended boundary avoids redoing arbitrarily large parses. The documentation also demonstrates separator arrangements that avoid parsing the same separator twice.

**Technical entry point:** [Looking ahead and backtracking](https://www.quanttec.com/fparsec/users-guide/looking-ahead-and-backtracking.html), including the distinction between broad `attempt` and local rollback operators.

### [com-lihaoyi/fastparse](https://github.com/com-lihaoyi/fastparse)

**Language/role:** Scala parser combinators for JVM and Scala.js. Study execution architecture that keeps grammars embedded in ordinary host-language code.

- **C2:** Scala functions and combinators form reusable grammars, with shared core code and separate example language parsers and test/benchmark projects visible in the repository.
- **C3:** The author's FastParse 2 design account explains a move away from interpreting parser-object graphs toward direct calls between parser methods. The instructive issue is dispatch and representation overhead: keeping declarative grammar composition while exposing a simpler execution path to optimization.

**Technical entry point:** [Author's FastParse 2 design explanation](https://www.lihaoyi.com/post/Fastparse2EvenFasterScalaParserCombinators.html). This is a dated architectural explanation, not a claim that the article's historical benchmark results describe every current release or workload.

### [dashbitco/nimble_parsec](https://github.com/dashbitco/nimble_parsec)

**Language/role:** Elixir parser-combinator DSL compiled into functions using binary matching. Study a compiler that fuses declarative parser fragments into host-runtime primitives.

- **C2:** Combinator descriptions are assembled before code emission; named parser references allow reuse across larger grammars. Generated functions explicitly carry input, accumulated values, context, and source-position state.
- **C3:** The compiler groups suitable bound combinators into shared binary patterns and guards, while other combinators require calls and state transitions. Inlining therefore trades execution overhead against compilation cost and code size; named references provide a structural way to limit expansion.
- **C1:** The inspected compiler handles lookahead by preserving and restoring parser state when it cannot reduce the operation to a bound match, exposing the rollback machinery behind the DSL.

**Technical entry point:** [Compiler implementation](https://github.com/dashbitco/nimble_parsec/blob/master/lib/nimble_parsec/compiler.ex), particularly bound/unbound choices and lookahead generation.

### [alecthomas/participle](https://github.com/alecthomas/participle)

**Language/role:** Go parser construction from struct-based grammar declarations. Study how speculative parsing is reconciled with mutation of application AST objects.

- **C1:** Parsing contexts queue field assignments rather than immediately applying every speculative mutation. Branching copies context, acceptance commits the chosen branch, and error tracking retains information about the deepest failure. This makes rollback more than a lexer-cursor operation.
- **C2:** Go types and grammar tags describe the resulting AST; custom lexers and parsing/capture interfaces extend the model. The repository also distinguishes shareable compiled parsers and lexer definitions from individual lexer instances, making reuse boundaries explicit.

**Technical entry point:** [Parse context, deferred assignments, and branch acceptance](https://github.com/alecthomas/participle/blob/master/context.go). The implementation is especially useful for comparing direct-to-AST parsing with libraries that first construct a separate generic tree.

### [benjamin-hodgson/Pidgin](https://github.com/benjamin-hodgson/Pidgin)

**Language/role:** C# parser combinators over generic token streams. Study explicit backtracking with a concrete buffer-lifetime mechanism.

- **C1:** Alternatives do not automatically recover from a parser that already consumed input. `Try` creates a bookmark, rewinds on failure, and discards the bookmark on success. The distinction prevents a seemingly harmless alternative from silently changing committed parsing behavior.
- **C2:** `Parser<TToken, T>` separates token and result types, supporting characters, bytes, and tokenized input. Mapping, dependent composition, and operator-precedence tools support typed grammar construction within C#.
- **C3:** The explicit `Try` boundary also controls buffering required for rollback on streaming input. Its implementation makes the lifetime of that retained input visible and reviewable.

**Technical entry point:** [Try parser implementation](https://github.com/benjamin-hodgson/Pidgin/blob/main/Pidgin/Parser.Try.cs), including bookmark creation, rewind, and discard.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, followed by opening repositories and primary technical sources. The searches covered:

- Adaptive LL, LR/LALR/IELR, GLR, and incremental parsing, including GNU mirror provenance.
- Rust streaming/binary combinators, PEG validation, grammar generation, and error repair.
- Python Earley/LALR toolkits and PEG/packrat systems with left recursion.
- JavaScript/TypeScript generators, incremental matchers, compiler plugins, and recovery.
- C++ template grammars, explicit branching DSLs, and separate-compilation strategies.
- Haskell, F#, and Scala combinators and generator backends.
- Go and C# typed AST/token interfaces, plus Elixir and Clojure approaches.
- Less prominent generalized parsing projects, Marpa's scanless model, and additional D/Kotlin and GLL/GLR candidates.

Later searches increasingly returned alternative implementations of already represented families. The final selection balances distinct architectures and communities rather than trying to exhaust every library in each language. Monorepos count once. Winnow's documented implementation divergence justifies including it alongside its ancestor nom; PEG.js is not duplicated alongside Peggy. Stars were not used as quality evidence.

The inspected [Lezer LR repository](https://github.com/lezer-parser/lr) announces a move away from GitHub. [Chumsky's GitHub repository](https://github.com/zesterer/chumsky) likewise announces its move to Codeberg and is archived. They were excluded because a continuing substantive official GitHub mirror was not established. Bison is retained with its maintainer-mirror provenance explicitly identified. Spirit remains useful as a substantive historical implementation, with its maintenance limitation stated above. A repository's unarchived metadata alone was not treated as evidence of active maintenance.

All 25 retained repository URLs were checked, and every entry has at least two evidence-based criteria and an additional inspected primary technical source. Some documentation links follow moving branches or `latest` versions, so their contents can evolve after the research date. This was read-only source and documentation research: no candidate code was installed or executed, and benchmark claims were not independently reproduced. Judgments about what engineers can learn are grounded interpretations of the linked mechanisms, not proof that every component is exemplary or a recommendation to adopt a library without workload-specific evaluation.
