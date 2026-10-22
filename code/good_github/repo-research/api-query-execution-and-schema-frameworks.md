# API query execution and schema frameworks

Research date: **2026-10-09**

This selection covers 25 repositories that implement API query execution, schema construction and validation, query planning, or reusable schema-driven request processing. It spans GraphQL interpreters, language-native schema frameworks, database-to-API compilers, federated routers, EQL, OData, and selected REST/RPC frameworks. General database engines, client caches, generic web routers, and standalone data validators are outside the scope. The emphasis is what an experienced engineer can learn from specific subsystems, not a ranking or a claim that every component is exemplary.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting different applications. **C3** — concrete performance constraints addressed through understandable architecture. **C4** — sustained evolution with evidence of compatibility work, testing, or complexity management. Criteria below are grounded assessments of the cited material; unlisted criteria are not necessarily absent.

## Execution libraries and specification semantics

### 1. [graphql/graphql-js](https://github.com/graphql/graphql-js)

**Language/role:** TypeScript/JavaScript; GraphQL reference implementation, including type construction, validation, and execution.

Study the boundary between validating execution arguments, executing an operation, and producing partial results. The inspected source is the repository's `17.x.x` branch; experimental incremental-delivery APIs should be distinguished from ordinary execution.

- **C1:** Field failures are collected while sibling fields continue; non-null failures can propagate to the response root. Subscription setup distinguishes invalid requests, source-stream failures, and a successful stream of results.
- **C2:** Separate synchronous, asynchronous, subscription, and incremental entry points reuse schema and resolver contracts. `executeSync` checks that execution really remained synchronous, rather than silently returning asynchronous work.

Entry point and implementation evidence: [execution/execute.ts](https://github.com/graphql/graphql-js/blob/17.x.x/src/execution/execute.ts).

### 2. [graphql-java/graphql-java](https://github.com/graphql-java/graphql-java)

**Language/role:** Java; embeddable GraphQL schema and execution engine.

Study how execution strategies compose `CompletionStage` results while keeping the GraphQL response deterministic. This is a useful codebase for separating scheduling policy from application data access.

- **C1:** The query strategy permits fields to finish out of order but assembles results in query order; the mutation strategy waits for each top-level mutation before starting the next. Exception handling supports partial data and field errors.
- **C2:** `DataFetcher`, `DataFetchingEnvironment`, custom exception handlers, and replaceable execution strategies make backend access independent of the engine.
- **C3:** A `PreparsedDocumentProvider` caches parsing and validation work separately from query results, exposing a precise and reusable cache boundary.

Entry point: [execution strategies, errors, and document caching](https://www.graphql-java.com/documentation/execution/).

### 3. [graphql-dotnet/graphql-dotnet](https://github.com/graphql-dotnet/graphql-dotnet)

**Language/role:** C#; GraphQL executor, schema types, and supporting packages.

Study the interaction between the execution strategy and deferred data loading. The important subsystem here is the core executor plus `GraphQL.DataLoader`, rather than a particular HTTP host.

- **C1:** Each request receives its own loader context. Fetch exceptions propagate to all associated fields, and the executor handles nested `IDataLoaderResult` values and asynchronous work preceding a load.
- **C2:** Keyed loaders distinguish single-value relationships from collection relationships, with dependency-injected loaders available when reuse across resolvers is needed.
- **C3:** Pending loads are dispatched after other pending fields resolve, allowing batching and request-local caching to reduce repeated backend calls.

Entry point: [DataLoader architecture and execution integration](https://graphql-dotnet.github.io/docs/guides/dataloader/).

### 4. [webonyx/graphql-php](https://github.com/webonyx/graphql-php)

**Language/role:** PHP; GraphQL implementation derived from the JavaScript reference implementation, with PHP-specific execution facilities.

Study how deferred resolution makes batching possible in ordinary PHP, and how the same executor can accommodate asynchronous runtimes through a promise adapter. This is a substantive language implementation, not a generated binding.

- **C2:** Field resolvers and `PromiseAdapter` provide reusable boundaries between schema execution, application data sources, and different promise implementations.
- **C3:** `GraphQL\Deferred` postpones a field until non-deferred work is exhausted. Resolvers can accumulate identifiers across multiple branches and levels, fetch them together, and then complete the waiting fields.

Entry point: [data fetching, deferred resolution, and asynchronous PHP](https://webonyx.github.io/graphql-php/data-fetching/).

### 5. [graphql-python/graphql-core](https://github.com/graphql-python/graphql-core)

**Language/role:** Python; independently maintained Python port of GraphQL.js with native Python execution APIs.

Study specification parity across languages, particularly Python coroutine behavior and scalar coercion. The port's version numbering is itself an instructive compatibility boundary.

- **C1:** The executor preserves partial results and non-null propagation. Recent release notes also document exactness checks when converting Python integers to GraphQL floats and rejection of input-object cycles that cannot have finite values. See the [execution API](https://graphql-core-3.readthedocs.io/en/latest/modules/execution.html) and [release notes](https://github.com/graphql-python/graphql-core/releases).
- **C2:** Schema types, custom resolvers, synchronous execution, coroutine execution, and subscription streams form a reusable foundation for higher-level Python frameworks.
- **C4:** A [January 2022 compatibility discussion](https://github.com/graphql-python/graphql-core/issues/156) explains why minor versions can break APIs when tracking GraphQL.js major versions. The 2026 release notes continue that policy, retain a compatibility release line, and describe running documentation examples as doctests.

## Language-native schema and server frameworks

### 6. [rmosolgo/graphql-ruby](https://github.com/rmosolgo/graphql-ruby)

**Language/role:** Ruby; GraphQL schema framework and runtime.

Study cooperative scheduling that lets application resolvers read like synchronous Ruby while their data requirements are collected for batching.

- **C2:** `GraphQL::Dataloader::Source` separates fetching logic from fields; the schema installs the loader as a reusable execution facility, and a per-query cache shares results within a request.
- **C3:** The scheduler pauses a Fiber when it requests unavailable data, advances sibling fields, and resumes work when batches are fetched. `AsyncDataloader` additionally uses nonblocking Fiber scheduling for parallel I/O.

Entry point: [Dataloader overview and scheduling sequence](https://graphql-ruby.org/dataloader/overview).

### 7. [async-graphql/async-graphql](https://github.com/async-graphql/async-graphql)

**Language/role:** Rust; asynchronous GraphQL schema and server library using procedural macros.

Study how schema declarations carry both execution behavior and admission-control metadata. Its query-cost model is particularly useful for understanding why depth alone does not bound response work.

- **C1:** Depth and complexity checks reject excessive requests during validation, before partial execution occurs. The documentation demonstrates how nested list fields can amplify work.
- **C2:** Schema-builder limits and field-specific complexity expressions are reusable policy mechanisms. A field can account for its arguments and the cost of its child selection, rather than relying only on a global field count.

Entry point: [query complexity, depth, and custom cost calculation](https://async-graphql.github.io/async-graphql/en/depth_and_complexity.html).

### 8. [99designs/gqlgen](https://github.com/99designs/gqlgen)

**Language/role:** Go; schema-driven GraphQL server generation and runtime.

Study how generated schema code exposes typed hooks for application-specific request policies. The selection concerns the generator and runtime together, not generated application boilerplate.

- **C1:** The handler's complexity extension rejects requests whose estimated work exceeds a limit. Custom functions can multiply child cost by list-size arguments, addressing queries that are shallow but expensive.
- **C2:** The generated `Config.Complexity` functions connect schema fields to application policy; limits can be fixed or computed per request. This makes the admission mechanism reusable across schemas and authorization contexts.

Entry point: [complexity extension and generated field-cost functions](https://gqlgen.com/reference/complexity/).

### 9. [sangria-graphql/sangria](https://github.com/sangria-graphql/sangria)

**Language/role:** Scala; GraphQL implementation with typed schemas and deferred execution.

Study the progression from low-level deferred values to a higher-level entity-fetching abstraction.

- **C1:** `DeferredResolver` requires result cardinality and order to match its requests; otherwise the executor cannot associate values correctly. Optional and required fetch variants deliberately differ when entities are missing.
- **C2:** Resolver `Action` values cover immediate, future, partial, deferred, and context-changing results. `Fetcher` layers entity identity and relationship semantics on the lower-level mechanism.
- **C3:** Deferred work is collected into batches; the higher-level API supports deduplication, caching, and maximum batch sizes. These mechanisms expose the tradeoff between waiting for more work and dispatching independent groups.

Entry point: [Sangria guide, especially deferred resolvers and Fetcher](https://sangria-graphql.github.io/learn/).

### 10. [ghostdogpr/caliban](https://github.com/ghostdogpr/caliban)

**Language/role:** Scala; functional GraphQL framework with compile-time schema derivation.

Study a schema represented by native case classes and effects, then interpreted independently of the HTTP framework. See the [schema/interpreter introduction](https://ghostdogpr.github.io/caliban/docs/).

- **C2:** `Schema`/argument derivation and an independent interpreter separate API description from transport. Resolvers can expose `ZQuery` values whose environment, error, and result types are explicit.
- **C3:** Caliban combines requested `ZQuery` fields into one query so the underlying data-source machinery can batch, deduplicate, and cache requests. Data sources identify themselves and map each request to a success or failure; the documented optimization assumes the backend supports batching.

Implementation-oriented entry point: [query optimization and data-source contracts](https://ghostdogpr.github.io/caliban/docs/optimization.html).

### 11. [walmartlabs/lacinia](https://github.com/walmartlabs/lacinia)

**Language/role:** Clojure; GraphQL schema compiler and query executor.

Study an asynchronous execution contract that is explicit about application responsibilities rather than hiding them behind an HTTP framework.

- **C1:** Parallel query resolution still preserves result-key order; top-level mutations complete serially. A resolver that never delivers its promise can block indefinitely, so the documentation explicitly assigns timeout and exception handling to application code.
- **C2:** `ResolverResultPromise`, `deliver!`, and a configurable executor separate completion notification from the mechanism used to fetch data. Synchronous and asynchronous fields can coexist in one schema.

Entry point: [asynchronous resolvers, mutation ordering, and failure modes](https://lacinia.readthedocs.io/en/latest/resolve/async.html). The timeout behavior is a material design limitation to study, not a claim of built-in protection.

### 12. [absinthe-graphql/absinthe](https://github.com/absinthe-graphql/absinthe)

**Language/role:** Elixir; schema macros, validation, execution, and subscriptions.

Study query processing as an editable sequence of small phases, and how that design accommodates correctness fixes without requiring a new server architecture.

- **C2:** Both schema processing and document processing use phase pipelines. Callers can insert, replace, remove, or run portions of a pipeline through a common API. See [Absinthe.Pipeline](https://absinthe.hexdocs.pm/Absinthe.Pipeline.html).
- **C1:** The [changelog](https://github.com/absinthe-graphql/absinthe/blob/main/CHANGELOG.md) records concrete edge cases: nested variable-type validation, null propagation through lists, invalid wrapped types, and subscription shutdown handling. It explicitly marks fixes that can invalidate previously accepted documents.
- **C3:** The same changelog documents avoiding repeated tree traversal for suspended fields and improving memory use for scalar lists, connecting performance work to identifiable execution structures.

### 13. [ChilliCream/graphql-platform](https://github.com/ChilliCream/graphql-platform)

**Language/role:** Primarily C#; monorepo containing Hot Chocolate, Strawberry Shake, and other GraphQL tooling. **Relevant subsystem: Hot Chocolate server execution and schema framework.**

Study the dependency structure of resolver execution and cancellation propagation in a .NET server framework. The monorepo is counted once; its client and IDE are not additional selections.

- **C1:** Child resolvers wait for their parent value while sibling resolvers can run concurrently. The documentation therefore requires ordinary query resolvers to avoid side effects and describes honoring cancellation when the client abandons a request.
- **C2:** Methods and delegates implement resolvers, with synchronous and asynchronous forms using the same resolver-tree model. This separates application services from execution scheduling.
- **C3:** Parallel sibling evaluation and cancellation reduce waiting and unnecessary backend work without obscuring parent-child dependencies.

Entry point: [Hot Chocolate resolver tree and cancellation](https://chillicream.com/docs/hotchocolate/resolvers).

### 14. [strawberry-graphql/strawberry](https://github.com/strawberry-graphql/strawberry)

**Language/role:** Python; type-annotation-based GraphQL schema framework and execution integration.

Study the schema and extension layer, rather than treating Strawberry as a second independent reference executor. Its value beside GraphQL-core is the reusable application-facing lifecycle.

- **C2:** Schema extensions surround execution stages with generator-style hooks. Extensions can inspect the execution context, supply a cached result, or reject an operation before execution. See [schema-extension lifecycle](https://strawberry.rocks/docs/guides/custom-extensions).
- **C1:** The [alias limiter](https://strawberry.rocks/docs/extensions/max-aliases-limiter) adds a document-validation bound through that extension mechanism. It addresses repeated aliased field requests, illustrating a distinct input-abuse dimension beyond nesting depth.

## Planning, database translation, and distributed graphs

### 15. [graphile/crystal](https://github.com/graphile/crystal)

**Language/role:** TypeScript; monorepo containing Grafast, PostGraphile, schema-building packages, and PostgreSQL planning utilities. **Relevant subsystems: Grafast execution and PostGraphile schema generation.**

Study an executor that builds an explicit dependency graph before fetching data. The [PostGraphile integration guide](https://postgraphile.org/postgraphile/5/usage/) separates schema construction, HTTP handling in Grafserv, and execution in Grafast.

- **C1:** Cached plans carry reuse constraints, including variable-dependent directives. Nulls, errors, and list expansion change batch shape through layer plans, while side-effecting steps are protected from dead-code removal.
- **C2:** Field plan resolvers produce reusable step abstractions instead of immediately fetching each field.
- **C3:** Deduplication, tree shaking, step optimization, and finalization are explicit passes. Finalization can prepare SQL once for subsequent execution.

Entry point: [operation plans and optimization lifecycle](https://grafast.org/grafast/operation-plan/). The monorepo is one entry, not separate Grafast and PostGraphile repositories.

### 16. [hasura/graphql-engine](https://github.com/hasura/graphql-engine)

**Language/role:** Haskell for the V2 server; the monorepo also contains the separate V3 engine. **Evidence focus: the documented V2/PostgreSQL compiler and live-query architecture.**

Study authorization as part of query compilation and the consistency of metadata-derived schemas. The [historical server architecture map](https://github.com/hasura/graphql-engine/wiki/Server-code-architecture) is explicitly a 2020 design document; its paths and details should not be assumed to describe V3.

- **C1:** Role-specific schemas and generated SQL incorporate access rules. Metadata dependencies, locked cache updates, and cross-instance schema synchronization expose difficult consistency concerns.
- **C2:** Database metadata becomes a schema and an annotated query representation before SQL generation, supporting tables, views, functions, and relationships.
- **C3:** The [live-query design](https://github.com/hasura/graphql-engine/blob/master/architecture/live-queries.md) explains compiling GraphQL through a SQL AST to avoid field-by-field database round trips, and the cost of repeatedly executing authorization-sensitive subscriptions. Its historical benchmark figures are not treated here as current performance guarantees.

### 17. [join-monster/join-monster](https://github.com/join-monster/join-monster)

**Language/role:** JavaScript; GraphQL-to-SQL planning and result hydration layered onto GraphQL.js.

Study the relational-to-hierarchical impedance mismatch: a flat SQL result must become the object tree expected by nested resolvers.

- **C1:** Object instances map to rows, and list mappings require a unique key. These are concrete identity invariants needed to hydrate joined data correctly.
- **C2:** Schema metadata expresses column dependencies, computed SQL expressions, joins, and batch relationships while allowing ordinary custom resolvers alongside SQL-backed fields.
- **C3:** The planner selects required data and can choose joins or separate batched queries, reducing repeated database calls without requiring every field to come from SQL.

Entry point: [mapping constraints and execution flow](https://join-monster.readthedocs.io/en/latest/how-it-works/). The inspected repository lists v4.0.0 from July 2024 as its latest release; this selection does not infer a current release cadence.

### 18. [apollographql/router](https://github.com/apollographql/router)

**Language/role:** Rust; federated GraphQL routing and query-planning runtime. **Relevant subsystems: `apollo-router` and the repository's federation planner.**

Study how a composed schema changes the search space for distributed execution, including cases where syntactically valid schema changes alter runtime behavior.

- **C1:** Shared fields imply consistent data and list order across subgraphs; changing `@requires` can break in-flight queries unless schema and service changes are coordinated. Plan determinism depends on schema, configuration, and planner version.
- **C3:** Alternative providers and abstract types expand the planner's search space. The documentation connects directive choices, network fetches, and planning complexity, and explains inspecting actual plans to diagnose behavior.

Entry point: [query-planning behavior, migrations, and performance](https://github.com/apollographql/router/blob/dev/docs/source/routing/query-planning/query-planning-best-practices.mdx). This is the router repository, not the separate JavaScript Apollo Server project.

### 19. [wundergraph/graphql-go-tools](https://github.com/wundergraph/graphql-go-tools)

**Language/role:** Go; reusable parser, AST, normalization, validation, planner, data-source, and resolver packages for GraphQL routers. **Relevant subsystem: the V2 module.**

Study the compiler front end of a federated API runtime. The repository explicitly identifies V1 as deprecated and removed, and V2 as the supported implementation.

- **C1:** Normalization must preserve semantics while retaining meaningful errors. When variable names are normalized, a reverse mapping is needed to report failures using the client's original names; conditional directives further complicate reuse.
- **C2:** AST processing, planning, data sources, and execution are separately reusable packages. Cosmo is a consumer of this library, not a second entry here.
- **C3:** Fragment flattening, argument extraction, and deterministic variable naming reduce variation in plan-cache keys. The project's [normalization design article](https://wundergraph.com/blog/normalization_query_planning_graphql_federation) explains the different representations appropriate for validation, analytics, and caching.

Entry points: the repository's package map and the linked normalization article; no comparative benchmark multiplier is assumed.

### 20. [wilkerlucio/pathom3](https://github.com/wilkerlucio/pathom3)

**Language/role:** Clojure/ClojureScript; attribute-graph query planning and execution for EQL-oriented applications. **Status: the repository explicitly labels Pathom 3 alpha.**

Study API composition where the engine discovers a route to requested attributes from resolver input/output relationships, rather than following only a fixed GraphQL field hierarchy.

- **C1:** Planning distinguishes required dependency groups from alternative ways to obtain an attribute. It also detects impossible paths and discards dead dependency branches.
- **C2:** Resolver indexes and declarative requested attributes decouple application code from the chosen resolution route.
- **C3:** AND nodes identify work that can run in parallel; dependency edges ensure downstream work starts only when prerequisites finish. OR nodes retain alternative resolution paths.

Entry point: [planner graph, AND/OR nodes, and impossible paths](https://pathom3.wsscode.com/docs/planner/). Pathom 2 is not separately counted; Pathom 3 is documented as a redesign with different namespaces.

## Schema-driven REST, OData, and RPC

### 21. [PostgREST/postgrest](https://github.com/PostgREST/postgrest)

**Language/role:** Haskell; REST query API derived from PostgreSQL schema objects.

Study a compact API compiler pipeline: parse the HTTP request, resolve it against cached schema information, form a plan, and produce database queries.

- **C1:** Request parsing rejects invalid methods or media types, and planning rejects invalid resource embeddings. The plan fills in SQL details such as conflict targets using schema information rather than treating the URL as raw SQL.
- **C2:** The database schema supplies reusable resources and relationships; distinct request, plan, query, and schema-cache modules make the translation stages explicit.
- **C3:** SQL is parameterized and prepared, and a pooled connection is needed only at the query stage. The schema cache avoids repeated catalog discovery during planning.

Entry point: [architecture and module map](https://postgrest.org/en/latest/explanations/architecture.html).

### 22. [OData/odata.net](https://github.com/OData/odata.net)

**Language/role:** C#; OData protocol libraries, Entity Data Model construction, URI parsing, and payload processing.

Study the schema-aware front end that a server framework can use before executing an OData request. This is protocol and schema infrastructure; it should not be mistaken for a database query executor by itself.

- **C1:** URI parsing binds paths and expressions to an EDM model. Resource paths distinguish entity-set and key segments, while query clauses preserve semantic information and distinguish an absent option from a supplied value.
- **C2:** Typed ASTs for filtering, ordering, searching, selection, and expansion give backend integrations a shared representation. Combined select/expand clauses and boolean search nodes support substantially more than simple endpoint dispatch.

Entry point: [ODataUriParser and semantic query-option ASTs](https://learn.microsoft.com/en-us/odata/odatalib/use-uri-parser). This guide is specifically for ODataLib V7; it is architectural evidence, not a claim that V7 is the latest release.

### 23. [apache/olingo-odata4](https://github.com/apache/olingo-odata4)

**Language/role:** Java; OData 4 library and server extension interfaces. **Historical project: official Apache GitHub mirror, archived June 2, 2026.** The [official project site](https://olingo.apache.org/) reports retirement.

Study a protocol framework whose parsed query expressions are interpreted or translated by application-supplied processors.

- **C1:** Filter expressions carry type and value semantics; the processor must accept only boolean filter results and distinguish unsupported expressions from execution failures. This reveals the boundary between framework parsing and backend semantic responsibility.
- **C2:** `ExpressionVisitor` and `EntityCollectionProcessor` let applications reuse protocol handling while choosing how to evaluate or translate the query. The documentation explicitly contrasts an in-memory teaching implementation with translating expressions into backend statements.

Entry point: [filter AST, expression visitor, and processor integration](https://olingo.apache.org/doc/odata4/tutorials/sqo_f/tutorial_sqo_f.html). Included for architectural study, with no implication of ongoing maintenance.

### 24. [api-platform/core](https://github.com/api-platform/core)

**Language/role:** PHP; API Platform's server component for resource metadata, hypermedia/GraphQL APIs, and data access integration.

Study how API operations and serialized representations control data retrieval. This entry focuses on state providers and Doctrine query extensions, rather than the surrounding application scaffolding.

- **C2:** `ProviderInterface` receives operation metadata, URI variables, and context. Providers can return items or collections and can decorate existing providers to construct alternate representations. See [state providers](https://api-platform.com/docs/core/state-providers/).
- **C3:** `EagerLoadingExtension` joins readable associations according to serialization context. The [performance guide](https://api-platform.com/docs/core/performance/) explains controls at resource and operation level, and warns that partial fetching can leave ORM entities unsuitable for access to unfetched fields. This makes the performance/representation tradeoff inspectable.

### 25. [trpc/trpc](https://github.com/trpc/trpc)

**Language/role:** TypeScript; typed RPC procedure framework with runtime validation and query/mutation/subscription execution.

This is a boundary selection: it uses typed procedures rather than a graph query language or separately authored schema language. Study the connection between inferred static types and runtime checks at the API boundary.

- **C1:** Input and output validators check values that TypeScript alone cannot validate over a network. Output-validation failure becomes an internal server error, making the contract between resolver results and public responses explicit. See [input/output validation](https://trpc.io/docs/server/validators).
- **C2:** Reusable base procedures combine middleware, context refinement, and input contracts before defining query, mutation, or subscription behavior. The [procedure guide](https://trpc.io/docs/server/procedures) provides the architectural entry point for studying this composition.

## Coverage, search process, and limitations

Discovery used more than six distinct live search formulations, followed by opening canonical GitHub pages and additional primary sources for every retained repository. Search angles included:

- GraphQL execution-engine architecture and schema validation across Java, JavaScript, Rust, Go, and Python.
- Functional and less widely known implementations: Clojure/Lacinia, Elixir/Absinthe, Scala/Sangria and Caliban, plus Haskell alternatives.
- Database-derived APIs and SQL planning: Hasura, PostGraphile/Grafast, PostgREST, and Join Monster.
- Federation query planners and routers in Rust and Go, including normalization and plan caching.
- OData libraries and expression visitors in Java and .NET.
- Schema-driven REST/RPC frameworks and their provider, validator, and procedure abstractions.
- Alternative API graph languages and attribute-resolution engines, particularly EQL/Pathom.
- Follow-up searches for release compatibility, archival status, and architectural alternatives.

Later broad queries increasingly returned already-covered designs, application tutorials, client tooling, or database engines. Juniper, Morpheus, FSharp.Data.GraphQL, newer federation routers, and other credible alternatives were discovered or sampled but are not claimed to be exhaustively evaluated. The list favors distinct study targets over enumerating every implementation of the same specification. GraphQL.js-derived language implementations are included for substantive language/runtime adaptation; Strawberry is identified as a schema/integration layer. Monorepos and predecessor/successor families are not multiplied into duplicate entries.

All technical evidence cited is primary material: official repositories, project documentation, maintainer design articles, and release/compatibility discussions. Some GitHub file views rendered incompletely; where needed, their raw source was read. No README was counted twice as independent evidence. A few guides deliberately describe a historical or version-specific architecture, especially Hasura V2 and ODataLib V7, and those limits are stated locally. No candidate code was executed, dependencies installed, services modified, or benchmarks reproduced. Performance criteria refer to mechanisms and documented constraints, not comparative speed claims. Inclusion alone does not assert active maintenance; Olingo's retirement and Pathom 3's alpha status are explicit.
