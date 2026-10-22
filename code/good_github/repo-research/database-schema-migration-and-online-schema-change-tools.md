# Database schema migration and online schema change tools

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing online table transformations, declarative schema comparison and planning, migration execution frameworks, and migration safety checks. It includes dedicated tools and clearly identified migration subsystems in larger repositories. Cross-database data transfer, backups, generic ETL, and database engines' internal DDL implementations are outside the scope. The emphasis is on code worth studying, not a ranking or a guarantee of production suitability.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, database semantics, or failure recovery. **C2** — substantial reusable abstractions supporting multiple workflows or backends. **C3** — practical performance constraints addressed through understandable architecture. **C4** — sustained evolution with concrete compatibility, testing, or complexity-management evidence. Criteria below are engineering judgments grounded in the linked primary material; only the explicitly justified criteria are claimed.

## Online schema change and operational safety

### 1. [github/gh-ost](https://github.com/github/gh-ost)

**Go · triggerless online schema changes for MySQL.** Study how an external process coordinates an initial table copy with ongoing writes captured from the binary log.

- **C1:** Copy tasks and change-application tasks converge on the ghost table, but draining the asynchronous backlog makes cutover more difficult than an ordinary rename. The design explains write blocking, atomic swapping, and safety latches that return a failed cutover to its prior stage. [Triggerless design](https://github.com/github/gh-ost/blob/master/doc/triggerless-design.md).
- **C3:** A controlled writer alternates copying and binlog application to limit contention. Unlike synchronous trigger propagation, ghost-table writes can pause when lag or load requires it; the design also acknowledges additional network traffic. The same document is a useful architecture entry point, including its replica-based checksum testing strategy.

### 2. [percona/percona-toolkit](https://github.com/percona/percona-toolkit)

**Primarily Perl for this subsystem · `pt-online-schema-change` within the Percona Toolkit monorepo.** Study the contrasting design in which triggers propagate writes while a replacement table is populated.

- **C1:** The tool must preserve concurrent changes, identify rows reliably, swap tables, and repair foreign-key references. Its manual distinguishes atomic rename from the riskier foreign-key `drop_swap` path, rather than treating all cutovers as equivalent.
- **C3:** Copy chunks adapt toward a target execution time. Replica-lag checks, server-load thresholds, query-plan checks, and lock timeouts constrain the migration's impact on production traffic. These controls are closely connected to the copying algorithm.

Entry point: the substantive [online schema change manual](https://docs.percona.com/percona-toolkit/pt-online-schema-change.html), especially Description, foreign-key methods, chunking, and load controls. This entry concerns that tool, not every utility in the repository.

### 3. [block/spirit](https://github.com/block/spirit)

**Go · online schema change and related data operations for MySQL 8.0+.** This is a substantial reimplementation inspired by gh-ost, with a different concurrency and throughput design, rather than a duplicate fork entry.

- **C1:** Its high-watermark optimization skips certain binlog events only when the later copy will capture the current row. The documented distinctions between memory-comparable primary keys and collation-sensitive keys expose the correctness conditions behind deduplicating changes. Checkpoint recovery also depends on retained binlogs and compatible invocation/binary state.
- **C3:** Parallel copying and change application, chunk sizing by memory budget, and a map that consolidates repeated row changes address large migrations. The shared engine uses MVCC-consistent reads, checksums, and atomic cutover. [Engine and command overview](https://github.com/block/spirit/blob/main/docs/README.md).

The repository's optimization discussion is a second entry point. Its support and replica-lag tradeoffs differ from gh-ost; this is not a universal speed recommendation.

### 4. [vitessio/vitess](https://github.com/vitessio/vitess)

**Go · Online DDL scheduler and VReplication migration machinery within Vitess.** Study schema migration as a recoverable distributed operation across tablets and shards.

- **C1:** VReplication persists transfer progress transactionally with transferred data. A newly promoted primary can resume the stream and take ownership of the migration; the documented stale-stream limit bounds automatic recovery. [Failover recovery mechanics](https://vitess.io/docs/23.0/user-guides/schema-changes/recoverable-migrations/).
- **C3:** Scheduling distinguishes expensive copy phases from potentially lighter tailing phases, constrains overlapping work, and prevents simultaneous migrations of the same table. This connects concurrency policy directly to resource contention. [Concurrent migration scheduling](https://vitess.io/docs/23.0/user-guides/schema-changes/concurrent-migrations/).

The evidence here uses the versioned 23.0 documentation. It does not imply atomic schema deployment across all shards or characterize the rest of the Vitess monorepo.

### 5. [xataio/pgroll](https://github.com/xataio/pgroll)

**Go · PostgreSQL migrations exposing multiple schema versions simultaneously.** Study compatibility between old and new application deployments through an expand/contract lifecycle.

- **C1:** Versioned views map applications onto physical tables. Breaking column changes use replacement columns, backfills, and triggers that propagate writes between old and new representations; cleanup waits until old clients have moved. The repository's “How pgroll works” section explains these invariants.
- **C2:** A common migration-operation model and start/complete/rollback lifecycle encapsulate the mechanics for different changes. Applications select their schema version through `search_path`, making rollout coordination an explicit part of the abstraction.

Entry points: the repository's architecture explanation and [getting-started compatibility notes](https://github.com/xataio/pgroll/blob/main/docs/getting-started.md). The latter specifically warns that PostgreSQL 14 versioned views do not preserve table RLS behavior because `security_invoker` views require PostgreSQL 15; the zero-downtime positioning is not a blanket compatibility guarantee.

### 6. [shayonj/pg-osc](https://github.com/shayonj/pg-osc)

**Ruby · PostgreSQL shadow-table schema changes and backfills.** A smaller, direct implementation worth comparing with binlog-based MySQL tools and view-based pgroll.

- **C1:** Triggers record changes in an audit table while a shadow table is copied. Replay remaps renamed columns, removes dropped columns, and applies operations before the final swap. The original table requires brief `ACCESS EXCLUSIVE` locking during setup and cutover, so “online” does not mean lock-free.
- **C3:** Configurable replay batches and a remaining-delta threshold control catch-up before taking the final lock. The distinction between bulk copy, incremental replay, and the final locked phase makes the throughput/lock-duration tradeoff inspectable.

Entry point: [replay implementation](https://raw.githubusercontent.com/shayonj/pg-osc/main/lib/pg_online_schema_change/replay.rb), alongside the repository's caveats. The documented primary-key requirement and lack of partitioned-table support materially limit its scope.

### 7. [stripe/pg-schema-diff](https://github.com/stripe/pg-schema-diff)

**Go · PostgreSQL schema diff library and SQL migration planner.** Study how a planner obtains online behavior from native PostgreSQL operations without maintaining a shadow-table replication process.

- **C1:** Plans are checked against a temporary database and carry hazards for dangerous operations. Dependencies prevent invalid object ordering; new indexes can be built before old ones disappear, and constraints can be installed separately from validation.
- **C2:** SQL graph vertices represent schema-object operations, dependencies express ordering constraints, and priorities influence a topological sort. This gives different object generators a common planning mechanism. [SQL dependency-graph implementation](https://raw.githubusercontent.com/stripe/pg-schema-diff/main/pkg/diff/sql_graph.go).

The repository's worked index-replacement and `NOT NULL` examples are the other entry point. It explicitly says some migrations still need locks or downtime and that stateful shadow-table techniques are not supported.

### 8. [ankane/strong_migrations](https://github.com/ankane/strong_migrations)

**Ruby · safety layer around Active Record migrations.** Study operational knowledge encoded as checks and execution policy rather than as a separate migration history engine.

- **C1:** Checks distinguish dangerous type changes, blocking index creation, constraint validation, and application column-cache hazards. The checker also tracks transaction state when deciding whether lock-timeout retries remain safe; its comments acknowledge multi-statement retry complications. [Checker implementation](https://raw.githubusercontent.com/ankane/strong_migrations/master/lib/strong_migrations/checker.rb).
- **C2:** Adapter-specific checks, configurable custom checks, timeout policy, and selected safe-by-default transformations reuse one interception layer across migration operations. The [documented extension interface](https://github.com/ankane/strong_migrations#custom-checks) shows how applications add their own rules.

This is an instructive policy engine, not proof that every permitted migration is safe. Explicit escape hatches and configuration remain part of its contract.

## Declarative comparison and schema planning

### 9. [ariga/atlas](https://github.com/ariga/atlas)

**Go · schema inspection, diffing, migration planning, and execution.** Study a common schema model shared by declarative and versioned migration workflows.

- **C1:** Execution tracks revision progress at statement granularity, distinguishes partially applied migrations, validates migration-directory checksums, and makes ordering policy explicit. These are concrete safeguards against histories that diverge from the database's actual execution state.
- **C2:** The migration driver composes inspection, differencing, execution, locking, snapshots, and plan application. Separate state readers, revision storage, planners, and executors make those facilities reusable. [Migration interfaces and executor](https://raw.githubusercontent.com/ariga/atlas/master/sql/migrate/migrate.go).

The [declarative workflow documentation](https://atlasgo.io/declarative/apply) explains development-database normalization and planning. It also identifies Pro-only resources and policies; the public repository should not be assumed to contain every capability advertised by the hosted/commercial product.

### 10. [sqldef/sqldef](https://github.com/sqldef/sqldef)

**Go · idempotent schema management from SQL DDL for several relational databases.** Study a parser-and-schema-model approach to desired-state migration, contrasted with tools that normalize everything through a temporary database.

- **C1:** Dependency keys must respect PostgreSQL quoted identifiers, MySQL `lower_case_table_names`, and other dialect rules. Treating differently quoted names as identical can corrupt the dependency graph; the implementation makes these cases explicit.
- **C2:** A shared schema layer and generic stable topological ordering support multiple database modes and types of dependent objects. Deterministic ordering of otherwise independent operations makes generated plans easier to review and reproduce.

Entry point: [DDL ordering and identifier normalization](https://github.com/sqldef/sqldef/blob/master/schema/ddl_ordering.go). The adjacent [schema source directory](https://github.com/sqldef/sqldef/tree/master/schema) exposes canonicalization, parsing, generation, and targeted normalization/order tests. Idempotent planning does not itself provide online execution.

### 11. [skeema/skeema](https://github.com/skeema/skeema)

**Go · declarative MySQL/MariaDB schema management from `CREATE` statements.** Study empirical verification of generated DDL and integration with external online schema change tools.

- **C1:** Skeema executes definitions in a workspace, introspects server metadata, and checks that generated `ALTER` statements transform an empty old definition into the desired definition. It also reconstructs `SHOW CREATE TABLE` to detect introspection gaps. [Correctness guardrails](https://www.skeema.io/docs/features/safety/).
- **C2:** The same schema workflow supports environments, linting rules, dry-run/diff behavior, and configurable external OSC execution; workspace placement is a separate policy from schema comparison.
- **C4:** The safety documentation describes a long-running implementation history and an explicit compatibility test process: common server versions on commits and all supported MySQL/MariaDB/Percona versions for releases.

The repository is Community Edition. Premium-only object types and capabilities are clearly separated in its README. Structural verification does not validate every property of existing production data.

### 12. [prisma/prisma-engines](https://github.com/prisma/prisma-engines)

**Rust · Schema Engine subsystem behind Prisma Migrate.** Counted once; the query engine and the separate TypeScript CLI repository are not additional entries.

- **C1:** The migration table records immutable checksums and distinct started, finished, and rolled-back states. Unresolved failures stop deployment. Migration generation replays SQL in a shadow database to discover its actual schema effect instead of assuming a parser understands arbitrary scripts.
- **C2:** A thin schema core orchestrates connector-defined functionality through a shared interface. SQL diffing, schema description, migration persistence, and the JSON-RPC boundary separate database behavior from the calling CLI.

Entry points: [Schema Engine architecture](https://raw.githubusercontent.com/prisma/prisma-engines/main/schema-engine/ARCHITECTURE.md) and the [subsystem source tree](https://github.com/prisma/prisma-engines/tree/main/schema-engine). The architecture document distinguishes development-time shadow-database work from deployment; it contains historical design commentary, so future-looking passages are not treated as current commitments.

## Migration history and reusable execution frameworks

### 13. [flyway/flyway](https://github.com/flyway/flyway)

**Java · versioned and repeatable migration execution with database-specific support.** Study a file-oriented migration model coupled to a persistent execution history.

- **C1:** The schema history distinguishes success, failure, missing or changed migrations, and superseded repeatable migrations. Checksums detect modifications to already-applied scripts; validation and repair have separate responsibilities. [Schema history and validation](https://documentation.red-gate.com/flyway/flyway-concepts/migrations/flyway-schema-history-table).
- **C2:** Recursive migration discovery, SQL/Java execution paths, lifecycle callbacks, and database support allow the engine to serve application startup, build tools, and deployment pipelines. Versioned migrations and changed repeatable migrations have defined execution ordering. [Migration lifecycle](https://documentation.red-gate.com/flyway/flyway-concepts/migrations).

The repository distinguishes Flyway OSS from Redgate editions containing additional capabilities. Database transaction semantics still determine what can be rolled back; a history table is not an atomicity guarantee.

### 14. [liquibase/liquibase](https://github.com/liquibase/liquibase)

**Java · changeset-based database change management.** Study the separation between change identity/history, concurrency coordination, and database/integration extensions.

- **C1:** `DATABASECHANGELOGLOCK` coordinates competing processes while change history determines what remains to execute. Its persistent lock can survive an unclean exit, creating a recovery obligation explicitly described by the project. [Lock-table mechanics](https://docs.liquibase.com/community/user-guide-5-0-3/what-is-the-database-changelog-lock-table).
- **C2:** The public Community implementation supports database extensions and integrations with several build and application frameworks. Changelogs and changesets provide a reusable deployment representation rather than one script tied to one application's startup procedure.

Entry points are the lock-table documentation and repository module layout, including the core, integration tests, and extension-testing modules. The inspected README identifies current Community licensing as **Functional Source License**; this report is a GitHub implementation selection, not an assertion that all entries use the same open-source licensing model.

### 15. [sqitchers/sqitch](https://github.com/sqitchers/sqitch)

**Perl · dependency-aware database change management using native database scripts.** Study an alternative to a single monotonically increasing version number.

- **C1:** A plan records named changes and dependencies, including dependencies on other projects. Deployment integrity uses linked change identities; verification checks deployment presence, plan membership, order, and optional verification scripts. [Verification contract](https://sqitch.org/docs/manual/sqitch-verify/).
- **C2:** Deploy/revert/verify scripts, tags, targets, and engine-specific command-line execution form a reusable lifecycle across different databases without requiring an ORM. [Core concepts and plan model](https://sqitch.org/docs/manual/sqitch/).

Verification scripts are optional, and a missing script is a warning rather than a failed verification. That distinction is useful when studying the boundary between framework guarantees and application-authored correctness checks.

### 16. [sqlalchemy/alembic](https://github.com/sqlalchemy/alembic)

**Python · SQLAlchemy migration graph, operations, and dialect integration.** Study both revision topology and backend-specific execution semantics.

- **C1:** Revisions form a DAG traversed topologically. Multiple database heads are represented explicitly, and a merge revision requires both branches before crossing the merge point, permitting databases on either branch to converge. [Branch and merge mechanics](https://alembic.sqlalchemy.org/en/latest/branches.html).
- **C2:** The operations API supports a batch context that reflects a table, creates a changed replacement, copies data, and replaces the original when direct alteration is unsuitable. It also exposes naming conventions and reflection controls for constraints. [Batch migration architecture](https://alembic.sqlalchemy.org/en/latest/batch.html).

The batch documentation carefully distinguishes named and unnamed constraints and self-referencing foreign keys. Its “online mode” means a live connection, not a promise of nonblocking table replacement.

### 17. [django/django](https://github.com/django/django)

**Python · `django.db.migrations` and database schema editors within Django.** Study a migration system that evolves both database structure and a historical application-model state.

- **C1:** Migration dependencies cross application boundaries. Data migrations must use historical models rather than present-day imports, or replaying an old migration can break after the application changes. Serialized references to fields, managers, and functions create explicit compatibility obligations.
- **C2:** Declarative operations support schema editing, state reconstruction, and optimization. Squashing reduces operation sequences, while replacement metadata lets old and squashed histories coexist so installations at different points can continue upgrading.

Entry point: the substantive [migration internals and lifecycle guide](https://docs.djangoproject.com/en/5.2/topics/migrations/), especially Historical models and Squashing migrations. This is a deliberately versioned 5.2 reference and a selection of the migration subsystem, not an evaluation of the entire framework.

### 18. [golang-migrate/migrate](https://github.com/golang-migrate/migrate)

**Go · migration library and CLI with independent source and database drivers.** Study the centralized execution state machine and its recovery boundary.

- **C1:** Execution acquires a driver-provided lock, rejects dirty database state, marks a target version dirty before running its body, and clears it only after success. Graceful stopping is checked between migrations; forcing a version is separate from executing SQL.
- **C2:** `source.Driver` and `database.Driver` keep retrieval and backend behavior separate from ordering and execution logic. Existing driver instances can be supplied programmatically, and bounded prefetching is controlled by the common engine.

Entry point: [migration state machine](https://raw.githubusercontent.com/golang-migrate/migrate/master/migrate.go). This is the evolved project descended from `mattes/migrate`, which is not counted separately. Driver-specific locking and transaction support must be checked rather than inferred from the common API.

### 19. [pressly/goose](https://github.com/pressly/goose)

**Go · SQL and Go-function migrations with a configurable library provider.** Study how a migration library accommodates embedded applications without requiring global configuration.

- **C1:** Missing/out-of-order migrations have explicit policy, and transactional and nontransactional Go functions are mutually exclusive. Optional session lockers coordinate multiple processes, with retry behavior provided by the locking implementation.
- **C2:** A provider composes a dialect, `*sql.DB`, `fs.FS`, migration registrations, and configurable storage. Independent providers can use different configurations, and filesystem migrations can come from disk or embedded assets.

Entry point: [provider architecture and options](https://pressly.github.io/goose/documentation/provider/). Crucially, this API does **not** lock the database by default; callers must configure the locker or ensure serialization. The older `rubenv/goose` lineage is not an additional repository entry.

### 20. [yogthos/migratus](https://github.com/yogthos/migratus)

**Clojure · general migration framework with SQL and Clojure-code migrations.** Study protocol-based execution and connection ownership in a JDBC environment.

- **C1:** The database store reserves a sentinel migration ID to coordinate execution, rechecks completion before applying work, and releases the reservation in cleanup. Its implementation explains why probing for a missing tracking table must occur in a separate transaction: a PostgreSQL error can otherwise poison the transaction needed to create it.
- **C2:** A `Store` protocol separates persistence from migration operations. SQL files and EDN-described Clojure functions share ordering and history, while connection specs, existing connections, and data sources support different host applications.

Entry point: [database store implementation](https://raw.githubusercontent.com/yogthos/migratus/master/src/migratus/database.clj), together with the repository's SQL/code migration documentation. Transactional DDL limitations remain database-dependent; the source is especially useful for examining those boundaries.

### 21. [rust-db/refinery](https://github.com/rust-db/refinery)

**Rust · embeddable SQL migration toolkit and CLI.** Study a typed migration runner with synchronous and asynchronous database integration.

- **C1:** The runner can reject an already-applied version whose name or checksum differs, reject missing history, and select per-migration or grouped transactions. Its documentation explicitly warns that grouping cannot make MySQL schema changes rollback-safe.
- **C2:** `Migrate` and `AsyncMigrate` traits let the same runner operate on different connection types. Embedded migrations, configured connections, target selection, and an iterator execution interface serve different application integration needs.

Entry point: the primary [Runner API documentation](https://docs.rs/refinery/latest/refinery/struct.Runner.html), which links directly to implementation. The repository documents the embedding macro and backend feature selection. This is a migration toolkit, not an ORM or schema-diff engine.

### 22. [DbUp/DbUp](https://github.com/DbUp/DbUp)

**C# · composable database upgrade library driven by SQL scripts.** Study how execution history and transaction policy can be made independent extension points.

- **C1:** Failure semantics differ between no transaction, one transaction per script, and one transaction for the complete upgrade. DbUp exposes these as explicit strategies and documents that DDL rollback depends on the database. The default is no transaction. [Transaction strategies](https://dbup.readthedocs.io/en/latest/more-info/transactions/).
- **C2:** The journal decides which scripts were executed; a custom `IJournal` can replace the default table, while `NullJournal` deliberately reruns suitable idempotent scripts. This separates history policy from script provision and execution. [Journaling abstraction](https://dbup.readthedocs.io/en/latest/more-info/journaling/).

These mechanisms make a useful study of partial-failure and replay contracts. Neither journaling nor a builder method alone should be interpreted as universal exactly-once execution.

### 23. [fluentmigrator/fluentmigrator](https://github.com/fluentmigrator/fluentmigrator)

**C# · migration DSL, database generators/processors, and .NET runners.** Study an extensible migration framework's evolution across both database and runtime ecosystems.

- **C2:** Typed fluent interfaces allow reusable column/table conventions and provider-specific extensions. The runner composes migration discovery, version metadata, processors, and generators through dependency injection. [Custom extensions](https://fluentmigrator.github.io/advanced/custom-extensions.html).
- **C4:** The changelog includes dated 2018 releases, later dependency-injection and provider separation, compatibility changes, and current prerelease handling of connection ownership and Firebird metadata locks. It explains replacements for removed interfaces rather than merely listing release numbers. The README also records adoption of Testcontainers for integration tests. [Evolution and compatibility record](https://raw.githubusercontent.com/fluentmigrator/fluentmigrator/main/CHANGELOG.md).

The changelog's prerelease section is evidence of ongoing design work, not a claim that those behaviors have shipped in a stable release.

### 24. [doctrine/migrations](https://github.com/doctrine/migrations)

**PHP · database migration planning and execution built on Doctrine DBAL.** Study how a migration API accommodates DBAL connections and platform-specific transactional behavior.

- **C1:** The project explains how MySQL/Oracle DDL can implicitly commit an enclosing transaction, why this became more visible with PHP 8 drivers, and why mixing DML and DDL can require splitting a migration or overriding `isTransactional()`. [Implicit-commit failure analysis](https://www.doctrine-project.org/projects/doctrine-migrations/en/3.9/explanation/implicit-commits.html).
- **C2:** `DependencyFactory` accepts existing connections and configuration loaders, then supplies reusable command implementations for generation, execution, status, and history management. It can be embedded in a custom console application without the supplied executable. [Custom integration](https://www.doctrine-project.org/projects/doctrine-migrations/en/3.9/reference/custom-integration.html).

The selected documentation is the maintained 3.9 line as labeled by the project at inspection; upcoming-major-version behavior is kept distinct from the described current behavior.

### 25. [sequelize/umzug](https://github.com/sequelize/umzug)

**TypeScript · framework-independent migration execution for Node.js.** Study the boundary between migration discovery, user callbacks, and execution-history storage.

- **C1:** The executor distinguishes pending/executed work, explicit rerun policies, reverse execution order, and ambiguous file ordering. It wraps callback failures with migration identity and direction, and records completion only after the callback succeeds. The separation between callback execution and history writes also exposes a failure boundary that integrations must handle.
- **C2:** Typed context, custom resolvers, lifecycle events, and interchangeable stores permit SQL files, JavaScript/TypeScript functions, and database-backed histories without tying the runner to Sequelize.

Entry point: [core executor and resolver implementation](https://raw.githubusercontent.com/sequelize/umzug/main/src/umzug.ts). The repository provides concrete storage and v2-to-v3 adaptation examples. The core's ordered callbacks and history writes do not themselves establish cross-process locking or a transaction encompassing both operations.

## Coverage and search notes

Discovery used more than six distinct live search formulations, followed by direct repository and primary-source inspection. Search angles included MySQL binlog versus trigger-based OSC; PostgreSQL shadow tables and versioned views; native PostgreSQL online DDL planning; declarative SQL/HCL schema tools; dependency graphs and verification scripts; Go libraries and transaction/locking behavior; Rust embedding; .NET migration frameworks; Ruby safety layers; PHP/JavaScript integrations; and Clojure/Elixir communities. Later passes also surfaced Reshape, Facebook OSC, and further ecosystem-specific runners. Marginal architectural overlap increased, so this report selects representative implementations rather than enumerating every migration package.

The final list spans Go, Perl, Ruby, Java, Python, Rust, Clojure, C#, PHP, and TypeScript. Smaller implementations such as Spirit, pg-osc, pg-schema-diff, Refinery, and Migratus sit alongside broader frameworks. Percona Toolkit, Vitess, Django, and Prisma Engines are counted once each, with their relevant subsystems identified. Ancestors, thin wrappers, and duplicate forks are not counted independently. Database-transfer tools such as pgloader, general CDC systems, and engine-native DDL internals were excluded by scope; other ORM migration implementations and similar runners remain outside this bounded selection.

Every retained canonical repository URL was opened, and each entry has an additional opened primary implementation/API/design source beyond the repository README. Sources were read, not merely selected from search snippets. Some GitHub pages and raw-file fetches failed; usable repository pages, official documentation, or successfully retrieved source files supplied the cited evidence instead. No candidate was installed, cloned, executed, or benchmarked.

Repository presence and documentation do not establish a maintenance service level. This report makes no blanket “actively maintained” assertion and retains no entry identified as archived or as an unofficial mirror. C4 is claimed only where concrete evolution and compatibility/testing evidence was inspected. Default-branch links can change, and several references deliberately use versioned documentation; the research date and those version boundaries should guide later rechecking. Descriptions of algorithms and limits are sourced facts; judgments that they make rewarding study material are the researcher's inference, not a claim that every component is uniformly exemplary.
