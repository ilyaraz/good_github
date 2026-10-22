# Business rule engines and decision table evaluators

Research date: **2026-10-09**.

This report selects **24 GitHub repositories** implementing business-rule execution, decision-table evaluation, or reusable inference and expression machinery directly applicable to business decisions. It covers DMN/FEEL, spreadsheet compilation, Rete and related forward chaining, JSON rules, embedded DSLs, and compilation of business predicates into database queries. Workflow monorepos appear only for their decision-engine subsystems. Editors, hosted-service SDKs, authorization-only systems, and examples without an independent evaluator are outside the selection.

Canonical repository names, default branches, fork flags, and archive flags were checked through the live GitHub API. Each selection also received a README review and at least one separate implementation or documentation read. Criteria below identify concrete engineering study opportunities; they do not certify correctness, security, standards compliance, or production suitability across the entire repository. Maintenance observations are a research-date snapshot, not inferred from stars.

**Criteria legend**

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial interfaces and representations that support different applications or execution contexts.
- **C3 — Performance with structure:** identifiable strategies for reducing computation, memory, compilation, or coordination costs.
- **C4 — Sustained evolution:** multi-year changes accompanied by compatibility decisions, testing improvements, or deliberate complexity management.

## Decision tables, DMN, and business-rule platforms

### [apache/incubator-kie](https://github.com/apache/incubator-kie)

**Language/role:** Java; the Drools rule engine and DMN evaluator inside the Apache KIE monorepo. The former `apache/incubator-kie-drools` URL now redirects here; this is one entry, including `drools-core`, `drools-decisiontables`, and `kie-dmn`.

Study how a large inference system separates rule definitions, compiled knowledge, working memory, and scheduling. The repository also shows how spreadsheet rules and DMN decisions coexist with DRL-based inference without being the same representation. [Repository overview](https://github.com/apache/incubator-kie/blob/main/README.md).

- **C1:** Fact insertion order can affect passive queries; the documented lazy, eager, and immediate propagation modes expose that semantic distinction. Phreak's segment/link bookkeeping also prevents incomplete matches from being scheduled as complete ones.
- **C2:** Stateful and stateless sessions separate reusable knowledge from per-execution facts, while DRL and DMN provide distinct authoring paths.
- **C3:** Phreak batches queued changes and uses node, segment, and rule memories with bit masks to schedule relevant work. The tradeoffs are explained with network examples in the [rule-engine guide](https://kie.apache.org/docs/10.0.x/drools/drools/rule-engine/index.html).

**Entry points:** the guide above and the verified [`drools-core` source tree](https://github.com/apache/incubator-kie/tree/main/drools-core).

### [openl-tablets/openl-tablets](https://github.com/openl-tablets/openl-tablets)

**Language/role:** Java; Excel-based business-rule compiler, execution engine, authoring studio, and rule services.

Study a spreadsheet language implemented through parsing, binding, a Java-like type model, runtime execution, and generated interfaces. The engine in `DEV/`, Studio in `STUDIO/`, and service layer in `WSFrontend/` share a common execution foundation. [Architecture](https://github.com/openl-tablets/openl-tablets/blob/main/Docs/ARCHITECTURE.md).

- **C1:** Optimized condition evaluation must preserve empty-cell wildcard behavior, rule order, and type-comparison semantics. The indexing design explicitly discusses equivalence between indexed evaluation and row-by-row evaluation.
- **C2:** Workbook-to-interface compilation, extensible Java function libraries, runtime contexts, and repository-backed deployment support embedded and service-based applications.
- **C3:** Equality, membership, and range indexes progressively narrow candidate rules. Flat rule-number arrays address memory growth, while non-indexable conditions remain selectors. [Condition-indexing design](https://github.com/openl-tablets/openl-tablets/blob/main/Docs/architecture/decision-table-condition-indexing.md).

**Entry points:** the architecture and condition-indexing documents above.

### [flowable/flowable-engine](https://github.com/flowable/flowable-engine)

**Language/role:** Java; the DMN subsystem of a wider workflow platform, especially `modules/flowable-dmn-engine`, with separate API, model, XML-converter, REST, and Spring modules.

Study how decision execution becomes an embeddable service with deployment, database persistence, querying, lifecycle management, and test integration. The relevant subsystem is independently identifiable within the monorepo. [DMN engine source](https://github.com/flowable/flowable-engine/tree/main/modules/flowable-dmn-engine).

- **C1:** The DMN API documents thread-safe engine/service objects, stateless services, explicit engine shutdown, missing-definition errors, illegal arguments, and optimistic-locking failures. Its JUnit extension deploys and cleans up decision resources around tests, making lifecycle behavior examinable.
- **C2:** Repository, rule, and management services separate definition deployment from evaluation and operational inspection; applications can use the same engine through embedded Java or platform integrations. [DMN API and testing guide](https://www.flowable.com/open-source/docs/dmn/ch03-API).

**Entry points:** the DMN source module and API guide above. Claims here concern the DMN subsystem, not every Flowable service.

### [camunda/camunda-bpm-platform](https://github.com/camunda/camunda-bpm-platform)

**Language/role:** Java; Camunda 7's `engine-dmn` subsystem. **Archived historical implementation:** the repository identifies Community Edition as end of life. It remains substantive source material, not a current Community Edition deployment recommendation. [Status](https://github.com/camunda/camunda-bpm-platform/blob/master/README.md).

Study an evaluator with clear stages for typed inputs, local variable contexts, matching rules, output evaluation, hit-policy handling, and evaluation listeners.

- **C1:** `UNIQUE` rejects multiple matches rather than silently choosing one; that invariant lives in a dedicated [hit-policy handler](https://github.com/camunda/camunda-bpm-platform/blob/master/engine-dmn/engine/src/main/java/org/camunda/bpm/dmn/engine/impl/hitpolicy/UniqueHitPolicyHandler.java). The main evaluator separates matching from applying the policy.
- **C2:** The DMN engine can execute standalone or through BPMN business-rule tasks. Its parsed decisions and evaluation-listener interfaces decouple invocation and observation from expression execution. [Subsystem usage](https://github.com/camunda/camunda-bpm-platform/blob/master/engine-dmn/README.md).

**Entry points:** [`DecisionTableEvaluationHandler`](https://github.com/camunda/camunda-bpm-platform/blob/master/engine-dmn/engine/src/main/java/org/camunda/bpm/dmn/engine/impl/evaluation/DecisionTableEvaluationHandler.java) and the subsystem usage guide above.

### [camunda/dmn-scala](https://github.com/camunda/dmn-scala)

**Language/role:** Scala; standalone DMN engine using FEEL-Scala, also integrated into Camunda 8. This is a separate implementation from the archived Camunda 7 Java evaluator. [Project overview](https://github.com/camunda/dmn-scala/blob/main/README.md).

Study explicit value types and failure propagation in a decision evaluator small enough to follow end to end.

- **C1:** Input tests accept true, false, or null and reject other values. Hit-policy code distinguishes `UNIQUE` cardinality, `ANY` output equivalence, priority ordering, and numeric collection. These are explicit `Either[Failure, Val]` paths in the [table evaluator](https://github.com/camunda/dmn-scala/blob/main/src/main/scala/org/camunda/dmn/evaluation/DecisionTableEvaluator.scala).
- **C2:** Parsed decision models, a supplied expression-evaluation function, audit records, custom-function providers, and value-mapper SPIs separate model execution from host-language objects and observability.

**Entry points:** the table evaluator and [engine API](https://github.com/camunda/dmn-scala/blob/main/src/main/scala/org/camunda/dmn/DmnEngine.scala). The README identifies DMN TCK as its conformance measurement mechanism; no independent conformance run was performed here.

### [adamecr/Common.DMN.Engine](https://github.com/adamecr/Common.DMN.Engine)

**Language/role:** C#; DMN decision tables and expression decisions with XML parsing, fluent construction, execution contexts, and a simulator.

Study the separation between model deserialization, reusable definitions, and mutable execution state. The project explains its deliberately limited “virtually immutable” definition model and shares test cases across XML versions, builders, and .NET targets. [Detailed project guide](https://github.com/adamecr/Common.DMN.Engine/blob/master/readme.md).

- **C1:** Table execution rejects conflicting `UNIQUE`/`ANY` results, constrains aggregate outputs, and handles output-priority ordering. Parallel rule and output evaluation make ordering and result collection meaningful correctness concerns.
- **C2:** XML and fluent builders converge on the same definition/execution abstractions; decisions can depend on other decisions, and snapshots support tracing.
- **C3:** Rule matching and output computation have separately selectable parallel paths with concurrent result collection. [Implementation](https://github.com/adamecr/Common.DMN.Engine/blob/master/net.adamec.lib.common.dmn.engine/engine/decisions/table/DmnDecisionTable.cs).

**Entry points:** the guide and table implementation above. The API reported its last push in December 2022; current maintenance is not established.

### [gorules/zen](https://github.com/gorules/zen)

**Language/role:** Rust; embeddable business-decision engine with native language bindings and JSON decision models. Its model is JDM; this entry does not imply complete DMN compatibility.

Study how one runtime supports graphs of tables, expressions, functions, and sub-decisions while sharing execution behavior across language bindings. The current README also describes compilation at load time and the version-2 migration boundary for arbitrary-precision features. [Overview](https://github.com/gorules/zen/blob/master/README.md).

- **C2:** Portable decision content, loader interfaces, node handlers, and bindings separate rules from storage and host applications.
- **C3:** The decision-table handler intersects indexed candidate-row bitsets before evaluating rows, retains first-match order, and uses a separate trace path. It supports whole-table collection and first-hit evaluation with collecting output columns. This is concrete optimization machinery rather than a benchmark slogan. [Table-node implementation](https://github.com/gorules/zen/blob/master/core/engine/src/nodes/decision_table/mod.rs).

**Entry points:** the table-node implementation and [decision-graph source tree](https://github.com/gorules/zen/tree/master/core/engine/src/decision_graph).

### [DTRules/DTRules](https://github.com/DTRules/DTRules)

**Language/role:** Go primary runtime, with historical Java/assembly implementations under `legacy/`; Excel-authored decision tables compiled through an expression language into postfix instructions.

Study a decision-table engine organized as a compiler plus stack VM, with entity schemas, mappings, sessions, and replayable traces. The current implementation differs materially from older descriptions of DTRules as a Java engine. [Current overview](https://github.com/DTRules/DTRules/blob/main/README.md).

- **C1:** Each table execution owns a local-variable frame that must close even on error; nested execution is bounded by a stack limit. The specification also defines change tracking and the invariant that generated XML/postfix stays consistent with the authoring source. [Execution and invariants specification](https://github.com/DTRules/DTRules/blob/main/docs/SPEC.md).
- **C2:** Compiled rule sets can be shared while each request creates a session. The same artifacts support batch execution, embedded applications, and interactive interviews, with external input mapping separated from rule evaluation.

**Entry points:** the current README and specification above. The older architecture document still contains Java terminology, so the current specification was preferred for runtime claims.

### [russellmcdonell/pyDMNrules](https://github.com/russellmcdonell/pyDMNrules)

**Language/role:** Python; spreadsheet-oriented DMN evaluator using a business glossary, FEEL-related expression support, and pandas integration.

Study the practical boundary between irregular spreadsheet structure and executable rule semantics: tables can be oriented by rows or columns, outputs can feed later tables, and returned decisions include executed-rule information. [Authoring guide](https://github.com/russellmcdonell/pyDMNrules/blob/master/README.md).

- **C1:** The implementation validates hit-policy syntax, requires output rankings for priority policies, validates glossary concepts, and bounds recursive table invocation. Failure reports preserve table and spreadsheet context.
- **C2:** A glossary maps business names to expression names; decisions may compose multiple tables, while `decidePandas` applies the same decision interface to rows and returns per-row status/results. [Evaluator and public methods](https://github.com/russellmcdonell/pyDMNrules/blob/master/pyDMNrules/DMNrules.py).

**Entry points:** the authoring guide and evaluator above. The large evaluator module is informative, but its concentration of parsing and execution responsibilities is a tradeoff to examine, not a blanket architectural endorsement.

## Forward-chaining and production-rule engines

### [NRules/NRules](https://github.com/NRules/NRules)

**Language/role:** C#/.NET; Rete production rules authored through a fluent internal DSL.

Study a particularly explicit compiler boundary: fluent rules become a canonical rule model, which is compiled into a Rete network held by a session factory. Multiple sessions share that network while keeping independent fact sets. [Architecture](https://github.com/NRules/NRules/blob/develop/docs/articles/architecture.md).

- **C1:** Linked facts must follow the lifetime of the activation that produced them. `Yield` inserts, updates, and automatically retracts those facts when supporting matches change, whereas standalone facts require explicit retraction. [Forward-chaining semantics](https://github.com/NRules/NRules/blob/develop/docs/articles/forward-chaining.md).
- **C2:** The canonical model admits alternate rule languages and inspection tools, while the compiler/session-factory/session separation supports reusable rule definitions and isolated evaluations.
- **C3:** Sharing a compiled matching network across sessions avoids recompiling the same rules and preserves a clear boundary between reusable structure and working memory.

**Entry points:** the architecture and forward-chaining documents above.

### [evrete/evrete](https://github.com/evrete/evrete)

**Language/role:** Java; embedded Rete engine with fluent builders, annotated Java rule loading, and JSR-94 integration.

Study an engine that exposes a type system and service-provider interfaces for constructing rule languages without requiring a full business-rule management platform. [Project guide](https://github.com/evrete/evrete/blob/master/README.md).

- **C1:** Activation modes deliberately differ in the visibility of working-memory changes. `CONTINUOUS` batches actions until the agenda pass ends; `DEFAULT` uses internal versions so later rule actions exclude deleted or superseded facts. This is an important semantic choice, not merely a scheduling toggle. [Activation-mode contract](https://github.com/evrete/evrete/blob/master/evrete-core/src/main/java/org/evrete/api/ActivationMode.java).
- **C2:** Builders, annotated source/class imports, custom types, and SPIs let applications reuse the inference core with different authoring and data representations.

**Entry points:** the activation-mode contract and [`runtime` implementation tree](https://github.com/evrete/evrete/tree/master/evrete-core/src/main/java/org/evrete/runtime). The README explicitly distinguishes the Java-8-compatible 4.0 line from the planned Java-17 requirement for 4.1.

### [oracle-samples/clara-rules](https://github.com/oracle-samples/clara-rules)

**Language/role:** Clojure/ClojureScript, with Java interoperability; forward-chaining rules and queries. This is the verified canonical repository, despite older links retaining the Cerner owner name.

Study inference with persistent and transient working-memory representations, support tracking, accumulators, and immutable-style session use.

- **C1:** Derived facts are retracted transitively when their support disappears. Unconditional insertions intentionally have different behavior and can make execution order observable. [Truth-maintenance semantics](https://www.clara-rules.org/docs/truthmaint/).
- **C2:** The working-memory protocols distinguish readers, transient updates, accumulated results, activations, and support records. These abstractions make rule compilation, execution, and inspection separable. [Memory implementation](https://github.com/oracle-samples/clara-rules/blob/main/src/main/clojure/clara/rules/memory.cljc).
- **C3:** The same implementation groups tokens/elements by bindings and uses transient mutation before returning persistent state, exposing the performance tradeoff behind the functional API.

**Entry points:** the truth-maintenance guide and memory implementation above. The [changelog](https://github.com/oracle-samples/clara-rules/blob/main/CHANGELOG.md) also documents equality, serialization, node-sharing, and diagnostics fixes.

### [jruizgit/rules](https://github.com/jruizgit/rules)

**Language/role:** C inference core with Python, Ruby, and JavaScript interfaces; Durable Rules combines forward chaining with event correlation, statecharts, flowcharts, and timers.

Study a polyglot engine in which the distinction between persistent facts and consumable events is part of the execution model. Version 2 evaluates the Rete tree in C and does not require Redis. [Architecture overview](https://github.com/jruizgit/rules/blob/master/README.md).

- **C1:** Events are consumed before a consequent runs, unlike facts retained until retraction. The reference also specifies duplicate/unhandled-message errors, asynchronous-action leases, and exception state that rules can inspect. These failure and lifetime semantics are central to correct correlation.
- **C2:** Rules, event sequences, statecharts, and timers share the same engine while language-specific DSLs expose them to multiple host ecosystems. [Python semantic reference](https://github.com/jruizgit/rules/blob/master/docs/py/reference.md).

**Entry points:** the overview and semantic reference above. No numerical speedup or exactly-once distributed-delivery guarantee is inferred from the project's performance wording.

### [nilp0inter/experta](https://github.com/nilp0inter/experta)

**Language/role:** Python; CLIPS-inspired expert-system engine using facts, decorated rules, an agenda, and Rete matching.

**Lineage:** the repository explicitly identifies itself as a PyKnow fork. It is retained as the evolved Experta implementation; PyKnow is not counted separately. Post-rebranding releases document distinct agenda and retracted-fact fixes. [README](https://github.com/nilp0inter/experta/blob/develop/README.rst), [changelog](https://github.com/nilp0inter/experta/blob/develop/CHANGELOG.rst).

- **C1:** Rules must not fire with retracted facts, and activations must be removed without dropping newly queued work. Those concrete bugs, plus fact freezing and incorrect normal-form conversion, are documented in the changelog.
- **C2:** `KnowledgeEngine`, facts, rule preparation, matcher interfaces, and conflict-set nodes separate domain declarations from matching and scheduling.
- **C3:** The matcher ranks repeated checks, reuses matching alpha nodes, then builds beta joins; it emits activation additions/removals after fact changes. [Rete construction](https://github.com/nilp0inter/experta/blob/develop/experta/matchers/rete/__init__.py).

**Entry points:** the Rete implementation and changelog above. Fork lineage is acknowledged rather than presented as an unrelated engine.

### [ulfurinn/wongi-engine](https://github.com/ulfurinn/wongi-engine)

**Language/role:** Ruby; Rete forward-chaining engine with a Ruby rule DSL, queries, and scoped fact overlays.

Study how negation and reversible working-memory scopes interact with cached matches. The project describes its internal interfaces as unstable and warns that pre-1.0 minor versions may break compatibility. [Project status and interface guidance](https://github.com/ulfurinn/wongi-engine/blob/master/README.md).

- **C1:** A negative join invalidates descendants when a blocking fact appears and reactivates them only when its last blocker disappears. The implementation explicitly preserves invalidation order and records negative-join results. [Negation node](https://github.com/ulfurinn/wongi-engine/blob/master/lib/wongi-engine/beta/neg_node.rb).
- **C2:** Nested overlays provide temporary fact scopes over a prepared engine, with explicit restrictions on which scope may be mutated and how long iterators remain valid.
- **C3:** Those scopes allow reuse of an already compiled large ruleset across independent data sets. [Overlay design](https://ulfurinn.github.io/wongi-engine/docs/basics/overlays/).

**Entry points:** the negation node and overlay guide above.

### [noolsjs/nools](https://github.com/noolsjs/nools)

**Language/role:** JavaScript; Rete engine for Node.js and browsers. **Historical/unmaintained:** its README explicitly states that C2FO no longer maintains it; the GitHub API did not mark the repository archived. [Status and programming model](https://github.com/noolsjs/nools/blob/master/readme.md).

Study a fully implemented JavaScript matching engine with separate flows, sessions, working-memory operations, agenda groups, and asynchronous actions.

- **C1:** Retraction and modification must keep per-rule activation indexes and agenda-group indexes consistent. Duplicate activation detection and promise-aware action execution make these invariants visible in the code.
- **C2:** Compiled flows create sessions; rule definitions support alternative constraints, named groups, salience, and custom actions.
- **C3:** The agenda combines AVL trees for ordered scheduling with hashed activation lookup and linked storage for removal. [Agenda implementation](https://github.com/noolsjs/nools/blob/master/lib/agenda.js).

**Entry points:** the programming guide and agenda implementation above. Retained for architecture study, without implying current runtime compatibility.

## Embedded business-rule DSLs and predicate evaluators

### [microsoft/RulesEngine](https://github.com/microsoft/RulesEngine)

**Language/role:** C#/.NET; externally stored workflow/rule definitions evaluated through dynamic expressions and structured result trees.

Study the boundary between configuration, typed rule parameters, expression compilation, and reusable execution results. Custom types and named inputs support rules beyond a single fixed business object. [API guide](https://github.com/microsoft/RulesEngine/blob/main/docs/index.md).

- **C1:** Compiled delegates cannot safely be reused solely by expression text. Cache keys incorporate parameter names/types, return type, and settings fingerprints, exposing a subtle cross-configuration correctness requirement.
- **C2:** Workflows, rule parameters, result trees, scoped expressions, and custom types provide reusable composition points for application business logic.
- **C3:** The parser caches compiled delegates and reuses parsing configuration to avoid repeated assembly scans; configuration is rebuilt when the custom-type array changes. [Expression-parser implementation](https://github.com/microsoft/RulesEngine/blob/main/src/RulesEngine/ExpressionBuilders/RuleExpressionParser.cs).

**Entry points:** the API guide and expression parser above. This evidence supports compilation/caching study, not treating arbitrary host expressions as a sandbox.

### [j-easy/easy-rules](https://github.com/j-easy/easy-rules)

**Language/role:** Java; compact rules abstraction with annotations, fluent construction, composite rules, and expression-language adapters. **Maintenance mode since December 2020**, with the README limiting support to the 4.1 line. [Status](https://github.com/j-easy/easy-rules/blob/master/README.md).

Study an intentionally small condition/action engine whose listener ordering, exception handling, priorities, and stop policies are easy to inspect. [Default execution loop](https://github.com/j-easy/easy-rules/blob/master/easy-rules-core/src/main/java/org/jeasy/rules/core/DefaultRulesEngine.java).

- **C2:** `Rule`, `Facts`, `Rules`, listeners, and composite groups support multiple authoring styles without tying evaluation to a particular application model.
- **C4:** The [2017 v3 release](https://github.com/j-easy/easy-rules/releases/tag/easy-rules-3.0.0) separated facts and rule sets to address concurrency problems; the [2020 v4 release](https://github.com/j-easy/easy-rules/releases/tag/easy-rules-4.0.0) documented breaking changes to fact representation and expression exceptions so failures could be tested and observed. These are explicit multi-year complexity-management decisions.

**Entry points:** the execution loop and release notes above.

### [venmo/business-rules](https://github.com/venmo/business-rules)

**Language/role:** Python; JSON-configured condition/action rules with a developer-defined vocabulary for business users.

Study a modest engine whose useful abstraction is the boundary between permitted business operations and editable rule data. Decorated variable and action definitions export metadata for a rule-authoring interface. [Authoring and execution guide](https://github.com/venmo/business-rules/blob/master/README.md).

- **C1:** Numeric comparisons convert accepted inputs to `Decimal` and use an explicit epsilon for equality and ordering. Boolean validation uses an exact type check, while operator decorators validate arguments. These choices create observable boundary behavior that deserves careful reading rather than assuming ordinary Python comparisons.
- **C2:** Registered types/operators, variable providers, action providers, and metadata export form an extensible vocabulary reusable across pricing, eligibility, and automation scenarios. [Operator/type implementation](https://github.com/venmo/business-rules/blob/master/business_rules/operators.py).

**Entry points:** the guide and operator implementation above. The numerical semantics are described, not endorsed for every financial calculation; a Decimal representation alone does not imply exact equality semantics.

### [zeroSteiner/rule-engine](https://github.com/zeroSteiner/rule-engine)

**Language/role:** Python; custom, optionally typed expression language for matching application objects. It is a predicate evaluator for business decisions, rather than an action-scheduling or DMN engine.

Study parse-time versus evaluation-time typing, host-object resolution, temporal and compound values, and a language that does not simply delegate its syntax to Python evaluation. [Project overview](https://github.com/zeroSteiner/rule-engine/blob/master/README.rst).

- **C1:** Declared object schemas reject unknown attributes at parse time; compound and nullable types require explicit compatibility rules. Numeric semantics also evolved from binary floating point to `Decimal`.
- **C2:** Custom symbol/type resolvers and object accessors let the same expression machinery work over mappings and domain objects. [Type-system guide](https://github.com/zeroSteiner/rule-engine/blob/master/docs/source/types.rst).
- **C4:** The dated changelog spans the 2021 Decimal transition, later typed-function checks, and 2026 operator-precedence and Python-support changes, with breaking behavior called out explicitly. [Change log](https://github.com/zeroSteiner/rule-engine/blob/master/docs/source/change_log.rst).

**Entry points:** the type-system guide and change log above.

### [CacheControl/json-rules-engine](https://github.com/CacheControl/json-rules-engine)

**Language/role:** JavaScript; serializable JSON rules over synchronous or asynchronous facts, producing events and rule results.

Study how declarative boolean conditions can depend on external data without repeating every data fetch. Nested conditions and custom facts/operators make the engine useful beyond its introductory examples. [Project guide](https://github.com/CacheControl/json-rules-engine/blob/master/README.md).

- **C2:** Rules, facts, the per-run almanac, operators, and event handlers separate policy representation from data acquisition and application effects. Runtime facts permit explicitly ordered rule chaining.
- **C3:** Each run gets a fresh almanac that caches fact computations by fact and parameters. Multiple derived facts can share one underlying lookup; cache controls and rule priorities expose the tradeoff between reuse and evaluation order. [Almanac architecture and examples](https://github.com/CacheControl/json-rules-engine/blob/master/docs/almanac.md).

**Entry points:** the project guide and almanac documentation above. The per-run cache boundary is a more useful study point than unsupported throughput comparisons.

### [hyperjumptech/grule-rule-engine](https://github.com/hyperjumptech/grule-rule-engine)

**Language/role:** Go; GRL business-rule DSL with parsed knowledge bases, working memory, salience, and action-driven repeated evaluation.

Study a Drools-inspired engine adapted to Go's application objects and cancellation model. Its grammar, AST, builders, and execution package expose separate compilation and runtime responsibilities. [Project guide](https://github.com/hyperjumptech/grule-rule-engine/blob/master/README.md).

- **C1:** The execution loop checks context cancellation, resets evaluation state, limits repeated firing with `MaxCycle`, and optionally returns condition-evaluation failures. Selecting a highest-salience rule and reevaluating after its action makes nontermination and stale-expression state concrete concerns.
- **C2:** Data contexts, versioned knowledge bases, builders, built-in functions, and listeners separate domain facts, rule text, and execution observation. [Engine implementation](https://github.com/hyperjumptech/grule-rule-engine/blob/master/engine/GruleEngine.go).

**Entry points:** the project guide and engine implementation above. Similarity to Drools does not establish identical Rete architecture or semantics.

### [bilibili/gengine](https://github.com/bilibili/gengine)

**Language/role:** Go; AST-based business-rule execution with sequential, concurrent, mixed, and inverse-mixed execution modes and engine pooling.

Study a service-oriented rule executor from the Chinese Go ecosystem, especially how parsed rule knowledge is shared while data contexts and execution instances are managed separately. [Project description](https://github.com/bilibili/gengine/blob/main/README.md).

- **C1:** Pool acquisition, return, injected-context cleanup, and rule replacement interact with concurrent execution. The pool source exposes several mutexes and shared knowledge references, providing a concrete synchronization design to examine; their presence alone is not proof of race freedom.
- **C2:** Builders, data contexts, injected host APIs, and selectable execution modes allow the same rule machinery to serve different application scheduling needs.
- **C3:** A bounded pool reuses engine wrappers and parsed knowledge to avoid reconstructing every request's execution machinery. [Pool implementation](https://github.com/bilibili/gengine/blob/main/engine/gengine_pool.go).

**Entry points:** the project description and pool implementation above. The API reported its last push in July 2023; the report makes no active-maintenance or numerical-throughput claim.

### [K-Phoen/rulerz](https://github.com/K-Phoen/rulerz)

**Language/role:** PHP; business specifications expressed as a DSL or composable objects, compiled for in-memory and external data targets. **Historical/unmaintained:** the README explicitly says the project is no longer maintained. [Status and scope](https://github.com/K-Phoen/rulerz/blob/master/README.md).

Study a different execution strategy: translate business predicates into the query language of the data source, rather than always loading records into a rule-engine working memory.

- **C2:** Parsed rule ASTs, compilation targets, visitors, and generated executors separate business specifications from the execution backend. Target selection and the `filter`, `applyFilter`, and `satisfies` operations provide reusable interfaces.
- **C3:** A specialized executor is generated per rule/target pair; query-capable integrations push filtering into the data source and avoid fetching all candidates first. [Compilation-target design](https://github.com/K-Phoen/rulerz/blob/master/doc/custom_compilation_targets.md).

**Entry points:** the compilation-target guide and [specification-oriented overview](https://github.com/K-Phoen/rulerz/blob/master/README.md). External adapters are not counted as independent engines, and some historical internal links in the documentation no longer match the split adapter layout.

## Coverage, search process, and limitations

Live discovery used more than six distinct formulations, including broad business-rule/DMN/Rete searches; Java DMN and spreadsheet engines; Clojure and .NET inference; Python expert systems and business-rule DSLs; Go GRL and pooled execution; JavaScript JSON rules and Nools; Ruby Rete and FEEL; PHP specifications; Rust decision engines; and less common language/decision-table combinations. Primary GitHub repository metadata, READMEs, source files, architecture documents, semantic guides, and release notes were then opened. Searches were followed through repository renames and monorepo moves rather than treating old names as additional projects.

The resulting coverage spans Java, Scala, C#, Rust, Go, C, Python, JavaScript, Clojure/ClojureScript, and Ruby/PHP communities. It includes large platforms, embedded libraries, and smaller substantive projects such as Common.DMN.Engine, Evrete, pyDMNrules, and Wongi. Rete engines are included where their reusable fact/rule machinery supports business decisions; general workflow orchestration is not assessed independently.

Later searches yielded diminishing additions: many results were hosted-service wrappers, tutorials, forks of retained engines, or smaller partial evaluators. Exclusions included the DecisionRules API wrapper, DMN demonstration applications, duplicate ZEN forks, the old standalone Camunda DMN repository, and authoring-only tooling. O'Doyle was investigated but omitted to keep the selection centered on business decisions rather than its predominantly UI/game examples. Spot Feel was also opened: its [table implementation](https://github.com/connectedbits/spot-feel/blob/main/lib/spot_feel/dmn/decision_table.rb) returns the first match for both `FIRST` and `UNIQUE`, so it was not retained as an additional strong DMN-semantics example. This is a code-grounded selection decision, not a claim that its advertised FEEL subset has no utility.

Maintenance caveats are explicit for archived or declared-unmaintained projects. A non-archived flag, an old project name, a recent push, or a test directory alone was not treated as C4 evidence. No dependencies were installed, candidate code executed, repositories cloned, benchmark claims reproduced, or maintainers contacted. Standards conformance and race freedom were not independently tested. The engineering judgments are grounded in the cited implementation/documentation slices; other components may have different quality, compatibility, and maintenance characteristics.
