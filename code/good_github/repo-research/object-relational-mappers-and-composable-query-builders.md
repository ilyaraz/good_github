# Object-relational mappers and composable query builders

Research date: **2026-10-09**.

This selection covers **25 GitHub repositories** implementing relational object mapping, composable SQL construction, or both. It includes persistence-context ORMs, framework subsystems, schema-generated clients, typed embedded languages, and data-oriented query formatters. The emphasis is on what an experienced engineer can learn from their abstractions and correctness boundaries, rather than popularity or feature counts. Framework monorepos count once, with the relevant subsystem identified below.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, SQL/type semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial mapping, query, compilation, or extension mechanisms supporting multiple use cases.
- **C3 — Performance with structure:** concrete work on database round trips, compilation, memory, batching, or concurrency through identifiable architectural mechanisms.
- **C4 — Sustained evolution:** years of development accompanied by compatibility work, testing, or deliberate complexity management.

The criteria are evidence-grounded assessments, not certifications. Linked documentation and source files are reading entry points; descriptions of why a design is instructive are editorial judgments. Versioned documentation is identified where used, and no general claim of current maintenance is inferred from repository age or stars.

## Persistence contexts, identity, and units of work

### [sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy)

**Python — ORM and independently usable SQL expression toolkit.** Study the boundary between relational expressions, object instrumentation, and the session's transactional state machine. SQLAlchemy is especially useful for understanding why an identity map is more than a query-result cache.

- **C1:** The session preserves one object per database identity and records attribute changes for flushing. A failed flush requires an explicit session rollback even after the underlying database transaction has rolled back: the in-memory transaction state has its own recovery requirements. The [session guide](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) explains both invariants.
- **C2:** Core provides expressions, schema metadata, dialect integration, and connections separately from the ORM. The [2.0 migration guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) explains how a shared statement-execution model unifies Core and ORM usage, and how the new architecture was exposed in 1.4 before older APIs were removed. This is a useful study of abstraction consolidation and staged compatibility work.

### [hibernate/hibernate-orm](https://github.com/hibernate/hibernate-orm)

**Java — Jakarta Persistence implementation and object-graph persistence engine.** Study the division between expensive shared mapping metadata and short-lived mutable persistence contexts, then follow how flushing turns object changes into SQL work.

- **C1:** Hibernate distinguishes a thread-safe, immutable `SessionFactory` from a single-threaded `Session` and transaction. The persistence context retains entity state while transaction abstractions account for JDBC and JTA integration. The [7.1 architecture chapter](https://docs.hibernate.org/orm/7.1/userguide/html_single/#architecture) makes these lifecycle boundaries explicit.
- **C2:** Mapping types describe conversion, equality, and copying as well as SQL storage. Sessions, factories, transactions, and mapping metadata form reusable contracts across many domain models.
- **C3:** The persistence context queues changes as a transactional write-behind cache; flushing groups DML so batching can be applied. The [flushing chapter](https://docs.hibernate.org/orm/7.1/userguide/html_single/#flushing) connects the object-state architecture directly to database work.

### [dotnet/efcore](https://github.com/dotnet/efcore)

**C# — Entity Framework Core; focus on relational mapping, tracking, and LINQ query support.** This repository also contains Microsoft.Data.Sqlite; the ORM is the subsystem selected here. Study how tracked original values participate in persistence decisions rather than treating change tracking as a convenience layer.

- **C1:** Optimistic concurrency adds the original concurrency-token value to update/delete predicates. Zero affected rows becomes `DbUpdateConcurrencyException`; insertion uniqueness failures are a different, provider-specific failure. The [concurrency guide](https://learn.microsoft.com/en-us/ef/core/saving/concurrency) also distinguishes SQL Server `rowversion` from application-managed tokens needed on other databases.
- **C2:** The repository combines LINQ queries, model mapping, change tracking, updates, and migrations behind a provider plugin API. The same concurrency mechanism accommodates different token strategies and exposes original/current/database values so applications can implement conflict resolution. This makes EF Core instructive for reusable persistence services with backend-specific behavior.

### [doctrine/orm](https://github.com/doctrine/orm)

**PHP — Data Mapper ORM.** Study identity preservation and object-graph hydration without requiring domain objects to manage their own persistence.

- **C1:** The identity map is keyed by root entity name and identifier; composite keys are normalized into a sorted serialized form. Lookup by other criteria can issue another query while still returning the existing object instance. These details distinguish identity correctness from result caching. See [Doctrine internals](https://www.doctrine-project.org/projects/doctrine-orm/en/current/reference/unitofwork.html).
- **C2:** Hydration accepts a result-set mapping and constructs entities, structured arrays, or scalar results, including grouping joined rows by parent. This is a substantial reusable layer between relational results and application representations.
- **C3:** The same internals guide explains snapshot-based change detection, PHP copy-on-write behavior, and the increasing cost of flushing a larger unit of work. Read-only entities and explicit change-tracking policies provide identifiable ways to reduce that work.

### [mikro-orm/mikro-orm](https://github.com/mikro-orm/mikro-orm)

**TypeScript — Data Mapper ORM; focus on its relational drivers and shared entity machinery.** Study how traditional units of work are adapted to concurrent asynchronous requests in Node.js. The repository also supports a document database, which is outside this entry's focus.

- **C1:** Each request needs its own identity map. `RequestContext` uses `AsyncLocalStorage` to select a forked entity manager, and global-context use is guarded by default. The [identity-map guide](https://mikro-orm.io/docs/identity-map) explains how this prevents requests from sharing mutable entity state.
- **C2:** The [unit-of-work guide](https://mikro-orm.io/docs/unit-of-work) describes property/association snapshots, change-set calculation, persistence scheduling, and transaction boundaries at `flush()`. It also covers the distinction between a new entity already known by primary key and one requiring an insert to obtain its key. These mechanisms support ordinary objects while keeping persistence coordination centralized.

## Framework integration, value mapping, and generated APIs

### [django/django](https://github.com/django/django)

**Python — Django ORM, specifically the model/query-expression subsystem.** Study expression resolution and the point where an object-oriented API must preserve database semantics. The rest of the web framework is not a separate selection.

- **C1:** `F()` expressions perform arithmetic in the database, avoiding the lost-update race of reading a counter into Python and saving an incremented value. Mixed-type arithmetic requires an explicit result type, and custom SQL templates have a documented distinction between bound parameters and interpolated context. See the [5.2 query-expression reference](https://docs.djangoproject.com/en/5.2/ref/models/expressions/).
- **C2:** `F`, `Value`, `Func`, `ExpressionWrapper`, `Subquery`, and `OuterRef` compose into filters, annotations, updates, and correlated queries. The same reference explains deferred outer-reference resolution and the `(sql, params)` compilation contract. It is a useful entry into extending a framework ORM without bypassing its expression system.

### [rails/rails](https://github.com/rails/rails)

**Ruby — Active Record and its relational query machinery.** Study the interaction between composable relations, model callbacks, and database transaction lifetimes inside a large framework monorepo.

- **C1:** Transactions are connection-scoped, and rolling back database changes does not restore Ruby objects to their previous state. Nested rollback behavior differs depending on `requires_new`, which uses savepoints on commonly supported databases. The [transaction API](https://api.rubyonrails.org/classes/ActiveRecord/Transactions/ClassMethods.html) also explains why external side effects belong after commit.
- **C2:** `ActiveRecord::Relation` is the reusable query representation returned by collection-producing methods. Lazy evaluation, chaining, and parameterized scopes let application code compose queries before execution. Start with the [query interface guide](https://guides.rubyonrails.org/active_record_querying.html); the selected subsystem is Active Record, not Rails as a whole.

### [jeremyevans/sequel](https://github.com/jeremyevans/sequel)

**Ruby — Database toolkit, composable datasets, and optional model layer.** Study a relational interface whose dataset abstraction is useful independently of model objects, with unusually explicit transaction semantics.

- **C1:** Nested transactions normally reuse the outer transaction; explicit savepoints change rollback behavior. Commit/rollback hooks can be attached to savepoints, with their execution depending on enclosing savepoint outcomes. The [transaction guide](https://sequel.jeremyevans.net/rdoc/files/doc/transactions_rdoc.html) gives concrete control-flow examples rather than hiding these distinctions.
- **C2:** Dataset retrieval and model retrieval share a query foundation but can return different representations. The [querying guide](https://sequel.jeremyevans.net/rdoc/files/doc/querying_rdoc.html) covers predicates, expressions, ordering, and projection. Its explanation of `last` requiring order on a plain dataset is a useful example of surfacing a relational precondition instead of inventing an implicit order.

### [coleifer/peewee](https://github.com/coleifer/peewee)

**Python — Compact ORM with a lower-level SQL AST and query builder.** Study how a comparatively small public object model can sit on top of a much more general relational composition layer.

- **C1:** The [query-builder guide](https://docs.peewee-orm.com/en/latest/peewee/query_builder.html) demonstrates atomic counter updates as database expressions and explicit table/subquery aliases when the same relation appears in multiple roles. Correct qualification and preserving computation in SQL are central correctness concerns.
- **C2:** `Model`/`Field` build on `Table`/`Column`; standalone `Select` objects are not tied to a particular model. The guide shows wrapping an arbitrary query to count it, composing window expressions, and building recursive CTEs. These are reusable query abstractions, rather than merely generated CRUD methods, with selectable dictionary, tuple, or object result representations.

### [elixir-ecto/ecto](https://github.com/elixir-ecto/ecto)

**Elixir — Data mapping, changesets, and language-integrated queries.** Study the representation of a multi-step persistence operation as inspectable data. This entry concerns Ecto itself; its separate SQL-adapter repository is not counted again.

- **C1:** `Ecto.Multi` requires unique operation names and executes operations in order. Changesets supplied directly are checked before starting a transaction, while function-produced changesets are evaluated during execution. An error aborts subsequent operations and identifies the failed operation. See the [Multi API](https://ecto.hexdocs.pm/Ecto.Multi.html).
- **C2:** A Multi can combine inserts, updates, deletes, queries, and functions dependent on earlier results. `to_list/1` exposes a canonical representation for inspection and tests without database execution. This gives engineers a concrete example of separating transaction construction from interpretation while retaining useful failure information.

### [go-gorm/gorm](https://github.com/go-gorm/gorm)

**Go — Reflection-oriented ORM and chainable SQL builder.** Study reusable query transformations alongside the transaction behavior of an API shared by many models and database dialects.

- **C1:** Writes run inside transactions by default. Transaction callbacks commit on success and roll back on error; nested transactions and explicit `SavePoint`/`RollbackTo` permit partial rollback. The [transaction documentation](https://gorm.io/docs/transactions.html) exposes both managed and manual control paths. Its advertised percentage performance improvement is not used as evidence here.
- **C2:** A scope is a function from `*gorm.DB` to `*gorm.DB`. The [scopes guide](https://gorm.io/docs/scopes.html) demonstrates composing predicates, pagination, table selection, and organization filters, including propagating an error through a scope. This small contract provides substantial reuse across query and mutation operations.

### [ent/ent](https://github.com/ent/ent)

**Go — Schema-generated entity and relationship APIs.** Study code generation as an extensible compiler over a graph-shaped schema, rather than viewing generated code as the entire project.

- **C1:** Entities created within a transaction retain a transaction-bound client. Querying their edges after commit requires `Unwrap()` to restore a normal client; misuse can panic. The [transaction guide](https://entgo.io/docs/transactions/) also demonstrates preserving rollback errors and wrapping an existing client-based operation in a transaction.
- **C2:** Schema fields and edges drive generated clients and builders. External templates can extend or override generated assets, and generation hooks can validate the schema graph or emit additional artifacts. The [code-generation guide](https://entgo.io/docs/code-gen/) is a substantive entry into the reusable generator, distinct from downstream generated wrappers.

### [groue/GRDB.swift](https://github.com/groue/GRDB.swift)

**Swift — SQLite record mapping and composable query interface with concurrency infrastructure.** Study how application model persistence is integrated with database queues, readers, and Swift task lifetimes. Its query interface and record protocols establish category fit even though the toolkit also exposes raw SQLite functionality.

- **C1:** The [GRDB 7 migration guide](https://raw.githubusercontent.com/groue/GRDB.swift/master/Documentation/GRDB7MigrationGuide.md) documents a meaningful semantic change: async database access now respects task cancellation, throws `CancellationError`, and rolls back pending transactions. This makes cancellation part of persistence correctness.
- **C2:** Fetchable/persistable record protocols and composable requests let the same model participate in generated queries and direct SQL, as demonstrated in the repository README.
- **C3:** The [DatabasePool implementation](https://raw.githubusercontent.com/groue/GRDB.swift/master/GRDB/Core/DatabasePool.swift) separates a serialized writer from pooled readers, handles WAL busy cases, and establishes snapshot isolation before releasing the writer in concurrent-read coordination. The mechanisms are inspectable, not just a throughput claim.

## Composable SQL languages and query compilers

### [jOOQ/jOOQ](https://github.com/jOOQ/jOOQ)

**Java — Typed SQL DSL, query model, and database-oriented code generation.** Study SQL expressions as reusable objects and the preservation of their meaning across dialects. The repository is the open-source codebase; documentation also describes dialects and capabilities available in other editions.

- **C1:** A null-safe distinctness predicate cannot be rendered identically everywhere. The [DISTINCT-predicate guide](https://www.jooq.org/doc/latest/manual/sql-building/conditional-expressions/distinct-predicate/) shows PostgreSQL `IS DISTINCT FROM`, MySQL's null-safe comparison, and SQLite `IS NOT` translations. This is a concrete cross-dialect semantic obligation.
- **C2:** Tables, fields, conditions, and expression collections are independently constructed and reused. The [dynamic SQL guide](https://www.jooq.org/doc/latest/manual/sql-building/dynamic-sql/) shows predicates assembled separately from their eventual statement and explains the same approach for joins and CTEs. Study the runtime query model beneath the fluent surface syntax.

### [diesel-rs/diesel](https://github.com/diesel-rs/diesel)

**Rust — Typed ORM and SQL query DSL.** Study how Rust traits encode SQL expression types, query structure, and execution metadata, including the obligations imposed on extensions.

- **C1:** SQL function signatures have nullability semantics that do not map trivially to Rust functions: the [extension guide](https://diesel.rs/guides/extending-diesel.html) uses `COALESCE` to explain this. It also requires custom query fragments to declare when generated SQL is unsafe for prepared-statement caching, because unbounded query shapes cannot be treated as one stable cached form.
- **C2:** `QueryFragment`, `AstPass`, `QueryId`, and typed SQL-function declarations support reusable extensions. The guide builds pagination around an arbitrary subquery and adds a windowed total count, showing how to extend the language without replacing its execution machinery.

### [SeaQL/sea-query](https://github.com/SeaQL/sea-query)

**Rust — Dynamic expression, query, and schema ASTs.** Study a runtime-oriented alternative to heavily compile-time-typed query construction. It is independently usable and also underlies SeaORM; SeaORM is not counted as another entry here.

- **C1:** The repository examples preserve operator grouping and renumber bound parameters across composed expressions, including custom fragments with their own local placeholder ordering. The [backend implementation](https://raw.githubusercontent.com/SeaQL/sea-query/master/src/backend/query_builder.rs) exposes precedence/associativity traits and shared statement rendering, making those semantic obligations visible.
- **C2:** A shared query-builder contract renders insert/select/update/delete structures while allowing backend behavior for placeholders, quoting, and other syntax. Expressions and statements are data structures passed through this layer, allowing dynamic composition without requiring an ORM model or execution driver.

### [kysely-org/kysely](https://github.com/kysely-org/kysely)

**TypeScript — Typed composable SQL builder.** Study the separation between result-shape inference and the runtime operation-node tree, particularly how plugins participate without owning the whole query engine.

- **C1:** Plugin execution has an asymmetric lifecycle: `transformQuery` is not guaranteed a matching `transformResult`. The [plugin interface](https://kysely-org.github.io/kysely-apidoc/interfaces/KyselyPlugin.html) therefore recommends a `WeakMap` keyed by query identity to avoid orphaned per-query state and memory leaks.
- **C2:** Plugins transform an `OperationNode` tree and separately transform results. The [plugin guide](https://kysely.dev/docs/plugins) demonstrates reusable policies such as identifier casing, join deduplication, empty-list handling, and null comparison transformation. Combined with the repository's scoped table/column and selected-result typing, this is a substantial extension architecture rather than a string concatenation helper.

### [drizzle-team/drizzle-orm](https://github.com/drizzle-team/drizzle-orm)

**TypeScript — SQL-oriented ORM and typed query builders; focus on the `drizzle-orm` package.** The monorepo also contains migration and schema-integration tools, which are not counted separately. Study how the API's type state changes as clauses and joins are added.

- **C1:** Ordinary builders restrict most methods to one invocation, reflecting SQL's single-clause structure. The [dynamic-query guide](https://orm.drizzle.team/docs/dynamic-query-building) explains that earlier unrestricted repeated `where()` calls caused mistaken expectations about condition merging. The restrictions make that ambiguity visible at compile time.
- **C2:** Explicit `.$dynamic()` mode permits generic functions to enhance queries, including changing result types by adding joins. Dialect-specific builder types support reusable pagination and relationship helpers for both standalone and database-bound builders. Study the intentional boundary between a constrained statement-building API and an extensible transformation API.

### [knex/knex](https://github.com/knex/knex)

**JavaScript with TypeScript definitions — Multi-dialect SQL and schema builder.** Study the combination of a general-purpose query builder with connection-bound asynchronous transaction execution. It is also an instructive foundation for higher-level persistence libraries.

- **C1:** A thrown error or rejected promise from a transaction handler causes rollback. A handler that does not return a promise must explicitly commit or roll back, or its connection can remain occupied. The [transaction guide](https://knexjs.org/guide/transactions.html) describes this promise/resource-lifetime dependency and database-specific savepoint limits.
- **C2:** The transaction object can itself act as a query builder, or be attached to another builder with `transacting`. A transaction provider lazily starts and then reuses the same transaction, letting separately composed operations share execution context. These contracts sit alongside the repository's reusable SQL, schema, streaming, and dialect facilities.

### [JetBrains/Exposed](https://github.com/JetBrains/Exposed)

**Kotlin — SQL DSL and DAO framework.** Study a typed expression vocabulary that works with explicit database execution contexts, including the difference between blocking JDBC and non-blocking R2DBC paths.

- **C1:** Entities remain attached to the transaction/database that loaded them; cross-database references are prohibited. Nested blocks share transaction resources by default, while independent nested transactions use savepoints. The [transaction guide](https://www.jetbrains.com/help/exposed/transactions.html) also distinguishes suspend APIs that still use blocking JDBC from R2DBC operations.
- **C2:** Query conditions are `Op<Boolean>` expressions. The [querying guide](https://www.jetbrains.com/help/exposed/dsl-querying-data.html) demonstrates conditional predicates, tuple membership, aliases, and dynamically adjusted joins and projections. These give engineers useful examples of incrementally constructing typed relational operations.

### [slick/slick](https://github.com/slick/slick)

**Scala — Lifted relational queries and database-action composition.** Study a query compiler with explicit phases, particularly the problems introduced when users reuse and nest query fragments.

- **C1:** `AssignUniqueSymbols` rewrites reused subtrees so symbol definitions are unique; `RelabelUnions` aligns field symbols so projection pruning does not incorrectly remove one side of a union. The [compiler API](https://scala-slick.org/doc/stable/api/slick/compiler/index.html) explains these invariants directly.
- **C2:** `QueryCompiler` is an immutable, stateless sequence of phases, with explicit compiler state and backend profiles. Phases include result mapping, outer-join emulation, aggregation, and comprehension construction.
- **C3:** The same source-backed API documents pruning unused projections, scalar optimization, and flags that let later phases be skipped when the relevant node types are absent. This makes compilation work and generated-query simplification separately understandable.

### [com-lihaoyi/scalasql](https://github.com/com-lihaoyi/scalasql)

**Scala — Collection-style SQL composition and structured result mapping.** Study a deliberately compact architecture centered on runtime SQL generation and JDBC. Despite the repository's ORM label, its design explicitly excludes Active Record-style mutable-object emulation.

- **C1:** `Expr[T]` exposes operations appropriate to the expression's type and imported dialect, rather than all operations available on a normal Scala value. The [design document](https://github.com/com-lihaoyi/scalasql/blob/main/docs/design.md) explicitly acknowledges that database type differences prevent complete type safety; that boundary is part of the learning value.
- **C2:** `Queryable[Q, R]` joins query rendering to result reconstruction, including tuples and parameterized case classes that cannot inherit a common library base. Open `Query`/`Expr` hierarchies and extension methods allow dialect customization. The document explains both the execution pipeline and the maintenance tradeoff of keeping complex compile-time generation out of the core. The README calls the library relatively new, so no maturity criterion is assigned.

### [haskell-beam/beam](https://github.com/haskell-beam/beam)

**Haskell — Typed relational DSL with pluggable database backends.** Study the semantic mismatch between Haskell values and SQL nulls, alongside the compositional structure of relational queries.

- **C1:** The [relationships guide](https://haskell-beam.github.io/beam/user-guide/queries/relationships/) distinguishes equality on `Maybe` values from SQL's three-valued logic. Haskell-style equality may require generated `CASE` expressions; separate operators produce `SqlBool`, with explicit conversion for unknown values. The non-nullability guarantee is conditional on the declared schema matching the database.
- **C2:** The `Q` monad supplies a compositional join primitive, with guards, relationship helpers, outer joins, and subqueries built into the DSL. The repository separates core query functionality from backend extensions and deliberately leaves connection/transaction management to the backend library. Its documentation examples are executed against databases during documentation builds, making the examples useful reading material as well as API explanations.

### [seancorfield/honeysql](https://github.com/seancorfield/honeysql)

**Clojure/ClojureScript — SQL represented as ordinary data structures.** Study composition without generated models: maps and vectors describe statements and expressions, and formatting produces SQL plus parameters.

- **C1:** The [formatter source](https://raw.githubusercontent.com/seancorfield/honeysql/develop/src/honey/sql.cljc) exposes dialect-specific quoting, clause ordering, suspicious-identifier checks, and configurable null-equality transformation. These are concrete examples of the correctness work beneath a small data DSL.
- **C2:** Public statement/expression formatters and registration functions for clauses, operators, and special forms provide reusable extension points. Parameter values remain a separate output alongside SQL text.
- **C4:** The [changelog](https://raw.githubusercontent.com/seancorfield/honeysql/develop/CHANGELOG.md) records development from the 2021 2.0 transition through 2026, including tested documentation, runtime/JDK compatibility, a backward-compatible null-equality option, and identifier/string-escaping security fixes. This is evidence of ongoing semantic and compatibility management, not a claim that every historical version is safe.

### [rbock/sqlpp11](https://github.com/rbock/sqlpp11)

**C++ — Template-based SQL embedded language and database connectors. Maintenance-oriented predecessor:** its README notice dated 2025-06-29 directs users toward sqlpp23 for new development while stating that sqlpp11 will continue to be maintained. This is a separate successor on GitHub, not evidence that sqlpp11 remains the feature-development destination.

Study how SQL scope and statement completeness become compile-time policy checks.

- **C1:** The [statement implementation](https://raw.githubusercontent.com/rbock/sqlpp11/main/include/sqlpp11/statement.h) tracks required/provided tables and CTEs, rejects unresolved requirements, and checks whether a query can serve as a derived table. It also distinguishes prepared parameterized execution from direct execution.
- **C2:** Statement policies assemble the language from reusable clause components, while connectors customize SQL rendering and database capabilities. Static and dynamic query modes trade stronger compile-time knowledge for runtime composition. The [select implementation](https://raw.githubusercontent.com/rbock/sqlpp11/main/include/sqlpp11/select.h) is a smaller companion entry point into that policy-based construction.

## Coverage, search method, and limits

Discovery used more than six distinct live-search formulations, followed by opening all 25 canonical GitHub repository pages and additional primary documentation or implementation files. Search angles included:

- Identity maps, units of work, and ORM architecture across Python, Java, PHP, and .NET.
- TypeScript SQL ASTs, query-builder typing, and ORM request contexts.
- Go reflection-based ORMs, generated entity APIs, and SQL-first alternatives.
- Rust static query typing versus dynamic AST construction.
- Scala/Kotlin compiler phases, runtime query models, and transaction APIs.
- Haskell null semantics and Clojure's data-oriented SQL representation.
- Ruby/Python compact toolkits, framework query systems, and Elixir transaction composition.
- C++ template DSLs, Swift/SQLite concurrency, and a final search of Nim, OCaml, and Perl alternatives.

Later broad architectural queries largely returned the same design families, additional young implementations, or projects whose main purpose was data-platform orchestration rather than an ORM/query library. The selection emphasizes distinct implementation lessons across 15 language communities when JavaScript/TypeScript are grouped together. Smaller-community projects such as Beam, HoneySQL, ScalaSql, SeaQuery, Sequel, and sqlpp11 complement the larger frameworks.

Database engines, bare drivers, migration-only systems, application templates, generated downstream clients, and repository lists were excluded. SQL-oriented adjacent tools and additional capable ORMs were not included merely to increase the count. A separate query-builder implementation can qualify even when it underlies an ORM; here SeaQuery represents that family without adding SeaORM as a closely related extra entry. Rails, Django, Drizzle, and EF Core are each counted once with the relevant subsystem specified.

This is a substantial selection, not an exhaustive ecosystem census. In particular, Nim, OCaml, and Perl candidates surfaced in the tail search but are not evaluated to the same depth as retained entries. Some rendered GitHub source pages and documentation endpoints failed to load; readable official raw files or alternative official documentation were used where available. The same README fetched through a raw URL was not counted as independent additional evidence. GRDB, for example, also has its pool implementation and migration guide inspected.

No candidate code was installed, cloned, or executed, and no throughput comparisons were independently reproduced. C1/C2 assignments describe documented mechanisms and obligations; they do not imply freedom from bugs, complete type safety, automatic SQL-injection protection for every escape hatch, or identical backend behavior. C3 is awarded for explicit architectural responses to performance constraints. C4 is used where the inspected history supplies more than a creation date. The sqlpp11 maintenance/successor distinction is material; other entries are not presented as having a uniform maintenance or support commitment.
