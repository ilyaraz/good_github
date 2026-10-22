# Graph databases and graph query engines

Research date: **2026-10-09**.

This selection covers 28 substantive GitHub repositories implementing graph storage, graph query execution, or reusable graph database infrastructure. It spans property graphs, RDF/SPARQL, recursive relational queries, embedded engines, distributed services, and graph querying within relational databases. Multi-model systems are included only for their graph subsystems. These are engineering study recommendations, not benchmark rankings or claims that every component is exemplary. Public source availability does not imply identical licensing or production readiness.

Criteria used below:

- **C1 — Correctness:** difficult invariants, concurrency, numerical/query semantics, adversarial inputs, or failure recovery.
- **C2 — Abstractions:** substantial reusable interfaces or representations supporting different applications, backends, or query forms.
- **C3 — Performance and structure:** concrete performance constraints addressed through an intelligible architecture.
- **C4 — Evolution:** years of development accompanied by compatibility management, testing, or explicit migration practices.

Repository identity was checked against the GitHub repository page or public API. Each entry also has an inspected primary document, source file, or test beyond its repository overview. Links within the criteria are the recommended reading entry points. Unless expressly stated, inclusion does not make a claim about current maintenance activity.

## Native property-graph and multi-model engines

### 1. [neo4j/neo4j](https://github.com/neo4j/neo4j)

**Java and Scala — native property-graph database and Cypher engine.** Study the Community Edition storage and query infrastructure; the repository explicitly distinguishes it from additional closed-source Enterprise components.

- **C1:** The concurrency manual explains read-committed anomalies, dependency-sensitive write locking, deadlock detection, and the commit-time requirement that relationships have valid endpoints. This makes the interaction between query semantics and physical locking unusually concrete. [Concurrent data access](https://neo4j.com/docs/operations-manual/current/database-internals/concurrent-data-access/).
- **C3:** Muninn separates page cursors, mapped files, translation tables, and I/O swappers. Its CLOCK eviction discussion explicitly connects replacement-policy choices to irregular graph traversal access patterns. [Page-cache architecture and internals](https://github.com/neo4j/neo4j/blob/2026.09/community/io/src/main/java/org/neo4j/io/pagecache/impl/muninn/page-cache-internals.adoc).

### 2. [memgraph/memgraph](https://github.com/memgraph/memgraph)

**C++ — transactional, primarily in-memory property-graph engine.** A particularly useful codebase for studying how online graph queries coexist with storage maintenance. Its README identifies separate Community and Enterprise licensing.

- **C1:** Concurrent index creation has explicit register, populate, and publish phases. MVCC timestamps govern visibility, and a planner must never use an incompletely populated index.
- **C3:** The same design reduces the interval that blocks writers, supports cancellation, and delays plan-cache invalidation until publication. The document names the storage, planner, and concurrency-test components, connecting the design to implementation. [Accepted concurrent-index-creation ADR](https://github.com/memgraph/memgraph/blob/master/ADRs/004_concurrent_index_creation.md).

### 3. [kuzudb/kuzu](https://github.com/kuzudb/kuzu)

**C++ — embedded analytical property-graph database. Historical: archived on 2025-10-10.** The repository also explains the discontinued official extension server and options for existing installations. It remains valuable for studying analytical execution.

- **C3:** The engine combines columnar storage, CSR adjacency/join indexes, vectorized processing, and factorized intermediates rather than representing every intermediate result as fully expanded rows. These mechanisms are documented in the repository overview.
- **C2:** `FactorizedTable` supplies shared append, scan, lookup, merge, and flattening operations over block collections and schemas. Its interfaces expose memory ownership and nullability propagation, making it a substantive reusable representation for query operators. [Factorized-table interface](https://github.com/kuzudb/kuzu/blob/master/src/include/processor/result/factorized_table.h).

### 4. [FalkorDB/FalkorDB](https://github.com/FalkorDB/FalkorDB)

**Rust with native GraphBLAS dependencies — property-graph engine with sparse-matrix execution.** The inspected default branch is Rust-based; older descriptions of this codebase as exclusively C are insufficient for the present tree.

- **C3:** The repository describes representing adjacency with sparse matrices and evaluating graph queries through linear algebra. This provides a different execution model to compare with iterator-driven adjacency traversal.
- **C1:** The write-authorization design distinguishes inline commands from asynchronous work. It checks graph registration, replication pauses, and replica read-only status under a continuous Redis global-lock hold so role changes cannot race with commit. [Write authorization and role-change invariants](https://github.com/FalkorDB/FalkorDB/blob/main/docs/write-authorization.md).

### 5. [arangodb/arangodb](https://github.com/arangodb/arangodb)

**C++ — multi-model database; focus on AQL graph traversal.** Study how graph operations compose with document queries and how traversal semantics constrain optimization.

- **C1:** Traversal options distinguish path-local from global uniqueness, require breadth-first or weighted traversal for global vertex uniqueness, and reject negative weights. Equal-cost paths and some uniqueness choices deliberately permit nondeterministic results.
- **C3:** Early `PRUNE` evaluation, attribute projections, and vertex-centric index hints address unnecessary expansion and document loading. The manual explains why pruning can retain a partial path even when further expansion stops. [AQL traversal semantics and optimization controls](https://docs.arango.ai/arangodb/3.12/aql/graph-queries/traversals/).

### 6. [ArcadeData/arcadedb](https://github.com/ArcadeData/arcadedb)

**Java — native graph and multi-model database.** Its relationship to OrientDB is explicit: a new storage engine with a substantially modified reused SQL engine and some utilities. It is therefore a separate implementation, not an unchanged fork listed twice.

- **C2:** Native graph records coexist with documents and other models, while SQL, Cypher, and Gremlin provide different query entry points. The repository separates the engine, language integrations, wire protocols, and replication components.
- **C1:** Inspected release notes describe concrete recovery failures: stale log entries applied after snapshot installation, reopening pre-resynchronization files, and schema/page publication ordering on replicas. These are useful cases for tracing tests and fixes rather than relying on the generic ACID label. [Release history and recovery fixes](https://github.com/ArcadeData/arcadedb/releases).

## Distributed graph storage and execution

### 7. [JanusGraph/janusgraph](https://github.com/JanusGraph/janusgraph)

**Java — transactional property-graph layer over interchangeable storage and indexing systems.** Study the boundary between graph-level constraints and backend guarantees.

- **C1:** Its consistency documentation gives a lock–re-read–validate–persist protocol for constrained elements, explains why locking is not enabled everywhere by default, and documents quorum-loss and clock assumptions. It also describes edge forking as an alternative conflict model. [Eventually consistent backends](https://github.com/JanusGraph/janusgraph/blob/master/docs/advanced-topics/eventual-consistency.md).
- **C2 / C4:** Storage, search indexes, and TinkerPop integration evolve independently. Dated releases from 2017 through 2024, backend compatibility matrices, and explicit upgrade instructions make that complexity observable. The development changelog also contains unreleased material; it should not be mistaken for a release announcement. [Compatibility and changelog](https://github.com/JanusGraph/janusgraph/blob/master/docs/changelog.md).

### 8. [vesoft-inc/nebula](https://github.com/vesoft-inc/nebula)

**C++ — distributed property-graph database with separated compute and storage.** The consolidated repository is the selection; older split graph/storage/common repositories are not counted separately.

- **C1:** The repository specifies Raft-based replication, while its test framework starts real metadata, storage, and graph services and checks query results through pytest and Gherkin/TCK scenarios.
- **C3:** Tests can assert an execution plan as well as answers. The documented example verifies that an edge-property predicate reaches `GetNeighbors`, offering a concrete entry into storage-side filtering and the performance consequences of planner transformations. [Test framework and plan assertions](https://github.com/vesoft-inc/nebula/blob/master/tests/README.md).

### 9. [dgraph-io/dgraph](https://github.com/dgraph-io/dgraph)

**Go — distributed graph database with DQL and GraphQL interfaces.** Its graph storage and distributed joins establish category fit independently of its GraphQL API.

- **C1:** Zero and Alpha Raft groups divide coordination from replicated data service. Predicate movement temporarily rejects mutations while reads continue, making retries and rebalancing part of the correctness model.
- **C3:** Predicate-based placement determines where query work executes; an Alpha resolves local predicates and requests remote work before merging results. This is a useful alternative to vertex-based partitioning. [Cluster architecture, movement, and query flow](https://www.dgraph.io/installation/dgraph-architecture/).

### 10. [apache/hugegraph](https://github.com/apache/hugegraph)

**Java — graph server plus distributed storage and placement services.** Focus on `hugegraph-server`, `hugegraph-store`, and `hugegraph-pd` within this single repository.

- **C1:** The storage architecture assigns a Raft group to each partition and describes log application, snapshot creation/loading, failover, and placement coordination. These boundaries give concrete failure-handling responsibilities to inspect.
- **C2 / C3:** A graph-facing client routes through placement metadata to partition engines and RocksDB-backed sessions; filter/aggregation pushdown and parallel partition execution are explicitly located within that structure. [Distributed storage architecture](https://github.com/apache/hugegraph/blob/master/hugegraph-store/docs/distributed-architecture.md).

### 11. [TuGraph-family/tugraph-db](https://github.com/TuGraph-family/tugraph-db)

**C++ — transactional property-graph database with embedded analytics and stored procedures.** Its architecture distinguishes key/value storage, graph storage, and computation layers. [Architecture overview](https://github.com/TuGraph-family/tugraph-db/blob/master/docs/en-US/source/2.introduction/6.architecture.md).

- **C1:** The transaction interface distinguishes read-only and optimistic write transactions, rejects writes through read-only transactions, validates vertex/edge identifiers, and tracks schema references, iterators, index buffers, and count deltas.
- **C2:** Transaction-scoped vertex and directional edge iterators sit above `KvTransaction`, while Cypher and procedure APIs share the graph engine. This is useful for studying how a graph API preserves storage and schema boundaries. [Core transaction interface](https://github.com/TuGraph-family/tugraph-db/blob/master/src/core/transaction.h).

### 12. [alibaba/GraphScope](https://github.com/alibaba/GraphScope)

**C++ and Java in the relevant subsystem — GraphScope Interactive/Flex graph query engine.** Count the monorepo once; its learning and batch-analytics systems are not separate entries here.

- **C2:** The compiler turns Cypher/Gremlin into GAIA intermediate representation and physical plans. The documented module boundaries separate compilation, physical operators, graph-database management, HTTP actors, and storage.
- **C3:** Interactive execution offers immutable and mutable-CSR storage components alongside the physical query engine. This makes representation choice and execution structure inspectable rather than hiding them behind a distributed-platform label. [Interactive source organization and tests](https://graphscope.io/docs/flex/interactive/development/dev_and_test).

## Query frameworks and graph layers over relational systems

### 13. [apache/tinkerpop](https://github.com/apache/tinkerpop)

**Java core, with multiple client languages — Gremlin query framework and graph-provider interfaces.** Study the reusable execution contracts, TinkerGraph reference implementation, and provider test suites.

- **C2:** Graph structure and process APIs allow graph databases and graph processors to plug into shared traversal execution and tooling. The provider guide identifies the implementation obligations and conformance suite. [Provider architecture](https://github.com/apache/tinkerpop/blob/master/docs/src/dev/provider/index.asciidoc).
- **C1:** Formal Gremlin semantics cover numeric promotion, overflow, custom types, provider feature declarations, and step behavior. Dedicated semantic tests reinforce the specification across different implementations. [Gremlin semantics](https://github.com/apache/tinkerpop/blob/master/docs/src/dev/provider/gremlin-semantics.asciidoc).

### 14. [apache/age](https://github.com/apache/age)

**C — PostgreSQL graph extension implementing Cypher.** Study integration with a host database's catalogs, types, transactions, and SQL execution.

- **C2:** AGE exposes graph queries within SQL and supports multiple graphs and graph-property indexes, reusing PostgreSQL infrastructure rather than requiring a separate graph service. The README also explains transaction visibility for graph/catalog creation.
- **C1:** Variable-length expansion regression tests construct self-loops, alternate routes, reverse edges, and nested properties, then check direction-specific path counts and length bounds. This is concrete evidence of the semantic difficulty behind a compact path pattern. [Variable-length traversal regression tests](https://github.com/apache/age/blob/master/regress/sql/cypher_vle.sql).

### 15. [pietermartin/sqlg](https://github.com/pietermartin/sqlg)

**Java — TinkerPop graph implementation over relational databases.** A smaller, substantive system for studying graph-to-SQL translation and graph metadata.

- **C2:** Vertex and edge labels map to relational tables through database dialects; the topology API manages property definitions, identifiers, and multiplicity. The architecture documents adjacency columns and optional foreign keys.
- **C3:** Its stated central challenge is collapsing fine-grained Gremlin steps into fewer database calls; batch modes address the same latency problem on writes. [Architecture, traversal optimization, and batching](https://sqlg.org/docs/3.1.6/).
- **C1:** The changelog records fixes to path/union semantics, multiplicity validation, schema upgrades, and graph-version downgrade prevention. These make compatibility and invariant failures easy to locate. [Changelog](https://github.com/pietermartin/sqlg/blob/master/CHANGELOG.md).

### 16. [cwida/duckpgq-extension](https://github.com/cwida/duckpgq-extension)

**C++ — DuckDB extension for SQL/PGQ graph queries. Research project; explicitly a work in progress.** Its substantial parser and graph-query implementation goes beyond the extension template from which the repository was initialized.

- **C2:** Property graphs are defined over vertex and edge tables, and `GRAPH_TABLE` embeds graph matching in SQL. The documentation explains graph definitions that reflect underlying table changes, direction patterns, and path-result functions. [SQL/PGQ guide](https://duckpgq.org/documentation/sql_pgq/).
- **C1:** Undirected-edge tests compare graph results with a SQL `UNION ALL` formulation, preserve distinct reciprocal edges, and separately verify that a self-loop is not spuriously doubled. [Undirected-pattern SQL logic tests](https://github.com/cwida/duckpgq-extension/blob/main/test/sql/pattern_matching/undirected_edges.test).

## Recursive, typed, and versioned graph systems

### 17. [cozodb/cozo](https://github.com/cozodb/cozo)

**Rust — embeddable transactional relational/graph engine using Datalog.** Maintenance qualification: the public API reported `archived: false` but a last push of 2024-12-04; recent maintenance is not established. The README also disclaims pre-1.0 API/storage compatibility. [Repository metadata](https://api.github.com/repos/cozodb/cozo).

- **C2:** Its documented layers separate language bindings, query execution, and a storage trait. Memory, SQLite, RocksDB, and other backends implement range-scan storage operations; the query layer owns the binary row representation.
- **C1:** Stratification constructs dependency graphs and distinguishes negated rules, fixed rules, and aggregation, then checks strongly connected components for illegal cycles. This is a useful entry into the correctness of recursive graph queries. [Datalog stratification](https://github.com/cozodb/cozo/blob/main/cozo-core/src/query/stratify.rs).

### 18. [cayleygraph/cayley](https://github.com/cayleygraph/cayley)

**Go — quad-based graph database with multiple query frontends and storage backends.** Study the shared iterator layer under graph queries.

- **C2:** The repository exposes Gizmo, MQL, and a GraphQL-inspired query interface over modular stores, providing a reusable query/storage separation.
- **C1 / C3:** Its `And` optimizer explicitly distinguishes semantics-preserving replacement from reordering and materialization. It estimates the cost of choosing one iterator for enumeration and the others for membership checks—a compact, readable implementation of graph-query join planning. [Intersection optimizer](https://github.com/cayleygraph/cayley/blob/master/graph/iterator/and_optimize.go).

### 19. [typedb/typedb](https://github.com/typedb/typedb)

**Rust — strongly typed database for interconnected entities, attributes, and relations.** Study the current TypeDB engine; descriptions of the earlier Java implementation do not describe this tree.

- **C2:** TypeQL supports composable polymorphic patterns and reusable query functions. These abstractions make typed relations and reusable graph queries central to the engine rather than application conventions, as the repository overview demonstrates.
- **C1:** Transaction-isolation tests distinguish independent concurrent insertions from conflicting deletion of the same entity. They assert exactly one failing commit and inspect the resulting isolation-conflict type, connecting graph operations to MVCC/storage behavior. [Transaction-isolation tests](https://github.com/typedb/typedb/blob/master/database/tests/test_transaction_isolation.rs).

### 20. [terminusdb/terminusdb](https://github.com/terminusdb/terminusdb)

**Prolog query/server code with an immutable storage foundation — versioned document and knowledge-graph database.** Study how graph identity, document expansion, and revision history interact. The current repository explicitly identifies new maintainers and its version-12 evolution.

- **C2:** Revision commits, branchable history, document APIs, and WOQL/Datalog querying expose the same linked data through several reusable abstractions.
- **C1:** Internals document copy-on-write/reference-count handling for shared JSON values and path-stack cycle detection for document unfolding. Cyclic references become identifiers instead of recursively expanding forever, and a work limit bounds deep traversal. [TerminusDB internals](https://terminusdb.org/docs/terminusdb-internals/).

## RDF storage, SPARQL, and research query engines

### 21. [apache/jena](https://github.com/apache/jena)

**Java — RDF toolkit, ARQ query engine, TDB2 storage, and Fuseki server.** These are relevant subsystems of one monorepo, not separate repository entries.

- **C2:** The richer `Model` API rests on a smaller `Graph` interface; storage adapters, inference engines, SPARQL execution, and HTTP publication compose across that boundary. [Architecture overview](https://jena.apache.org/about_jena/architecture.html).
- **C1:** Dataset transactions preserve aggregate-query consistency across concurrent changes. The documentation distinguishes general multiple-reader/single-writer locking from storage implementations that permit readers alongside a writer, and specifies thread association and the absence of nested transactions. [Transaction architecture](https://jena.apache.org/documentation/txn/).

### 22. [eclipse-rdf4j/rdf4j](https://github.com/eclipse-rdf4j/rdf4j)

**Java — RDF stores, SPARQL evaluation, inference, and repository APIs.** Study SAIL as an interface between graph query algebra and different persistence implementations.

- **C2:** Stackable SAIL components compose inference, filtering, and full-text functionality over `NativeStore`, `MemoryStore`, or another implementation. Query evaluation accepts algebra objects rather than coupling storage to SPARQL text.
- **C1:** Shared base classes handle connection shutdown, transaction bookkeeping, update flushing, locking, and registration of result iterators for resource management. These are substantive correctness responsibilities delegated away from individual backends. The design document labels itself incomplete, especially its transaction section. [SAIL design](https://rdf4j.org/documentation/reference/sail/).

### 23. [oxigraph/oxigraph](https://github.com/oxigraph/oxigraph)

**Rust — embedded/server RDF database and reusable SPARQL/RDF components.** Study term representation and the boundary between standards-facing crates and storage.

- **C2:** The repository separates reusable RDF data-model, parsing, serialization, and SPARQL components from the database and language bindings.
- **C3:** Architecture notes explain inline versus dictionary-backed terms, multiple quad-index permutations, and selective in-memory iteration. They also openly discuss storage-amplification and string-reclamation tradeoffs. **Version qualification:** this wiki describes a v0.4-oriented design and contains unresolved items; it is an architectural reading aid, not proof of every current implementation detail. [Architecture wiki](https://github.com/oxigraph/oxigraph/wiki/Architecture).

### 24. [ad-freiburg/qlever](https://github.com/ad-freiburg/qlever)

**C++ — RDF/SPARQL query engine with text and spatial query capabilities.** Study the optimizer rather than relying on the repository's headline scale or speed claims.

- **C3:** `QueryPlanner` represents triple graphs and candidate subplans with cardinality/cost estimates, cached results, filter tracking, and connected-component discovery. It also represents spatial-join substitutes for ordinary filters.
- **C1:** Planner state tracks nested named-graph scope, while subplans distinguish basic, optional, and minus semantics. The source documents a concrete invalid substitution case that would prevent a spatial join from receiving its second child. [Query planner interface and invariants](https://github.com/ad-freiburg/qlever/blob/master/src/engine/QueryPlanner.h).

### 25. [openlink/virtuoso-opensource](https://github.com/openlink/virtuoso-opensource)

**C and SQL — multi-model database; focus on the RDF quad store and SPARQL subsystem.** This is the official Open Source Edition repository, distinct from the commercial edition.

- **C3:** The RDF index scheme combines full quad indexes with smaller partial indexes, clustering by predicate to improve locality and the working set. The documentation explains how bound positions determine the access path.
- **C1:** Partial-index entries can survive deletion. Correctness is preserved by consulting a full index before treating a quad as present; accumulated stale partial entries affect performance instead. This is an unusually clear example of an intentionally weaker auxiliary invariant. [RDF index scheme](https://docs.openlinksw.com/virtuoso/rdfperfrdfscheme/).

### 26. [blazegraph/database](https://github.com/blazegraph/database)

**Java — RDF/SPARQL database with a reusable journal/index substrate. Historical: archived on 2026-03-23.** Study its implementation and design comments without treating the old README's deployment claims as current operational evidence.

- **C1:** `AbstractJournal` documents atomic commit and explicitly warns that direct mutable-B-tree access is not thread-safe; callers needing concurrency control must use the task/concurrency-manager API.
- **C2:** Named indexes, append-only versus reusable-allocation persistence modes, and separate journal, concurrency, resource, and transaction interfaces expose a substantial storage substrate below graph execution. [Journal architecture and concurrency boundary](https://github.com/blazegraph/database/blob/master/bigdata-core/bigdata/src/java/com/bigdata/journal/AbstractJournal.java).

### 27. [comunica/comunica](https://github.com/comunica/comunica)

**TypeScript/JavaScript — modular SPARQL engine for local and decentralized RDF.** A strong contrast with engines that assume one local store and stable statistics.

- **C2:** Actors, buses, and mediators separate parsing, source discovery, algebra optimization, query operations, joins, and serialization. Source handling covers RDF streams, SPARQL endpoints, and fragment interfaces. [SPARQL architecture](https://comunica.dev/docs/modify/advanced/architecture_sparql/).
- **C3:** Query planning is partly adaptive because remote-source characteristics may only become known during execution. Join actors implement different physical algorithms for inner, optional, and minus joins, with selection based on available metadata. [Adaptive join planning](https://comunica.dev/docs/modify/advanced/joins/).

### 28. [MillenniumDB/MillenniumDB](https://github.com/MillenniumDB/MillenniumDB)

**C++ — research graph DBMS supporting RDF and property-graph models.** The repository expressly says it is not production ready and identifies incomplete GQL support.

- **C2:** Multiple graph models and query frontends share a persistent engine intended for experimentation with database algorithms. Its domain-graph research explains the abstraction behind representing statements and richer relationships.
- **C3:** The authors combine conventional storage/indexing with worst-case-optimal joins and graph-specific path evaluation, including automaton-guided search. This is a useful bridge between research algorithms and a navigable DBMS implementation. The paper describes its published design; the repository describes the present feature scope. [Authors' systems paper, especially Section 5](https://aidanhogan.com/docs/millenniumdb.pdf).

## Coverage and search notes

Discovery used more than six distinct live-search formulations, including native property-graph storage architecture; distributed graph partitioning and replication; embedded graph engines; Gremlin providers and PostgreSQL graph extensions; RDF/SPARQL storage and optimization; versioned and typed knowledge graphs; worst-case-optimal joins; decentralized SPARQL federation; and SQL/PGQ extensions. Follow-up searches covered the OrientDB/ArcadeDB family and smaller engines. The final expansion added ArcadeDB and DuckPGQ because they contributed distinct implementation and query-integration approaches. A final sweep for C#, Erlang, and Clojure implementations and lesser-known RDF engines surfaced additional candidates and adjacent Datalog systems, but did not establish stronger coverage than the inspected selection; further searching had diminishing returns for this report.

The selection spans Java, C/C++, Rust, Go, Prolog, and TypeScript/JavaScript, and includes Apache, Eclipse, academic, vendor, and smaller independent communities. Apache entries are the projects' official Apache-owned GitHub repositories/mirrors; alternate ASF hosting locations are not additional projects. GraphScope, Jena, HugeGraph, and other monorepos each count once. The old split Nebula repositories, RedisGraph alongside FalkorDB, OrientDB alongside the selected ArcadeDB implementation, and near-identical continuation forks were not added simply to increase coverage.

Excluded from the core list are client drivers, visualization tools, graph-algorithm-only libraries, GraphQL API frameworks without a graph query/storage engine, GraphRAG applications that merely consume databases, tutorials, and repository lists. Proprietary graph products with only SDKs on GitHub do not qualify as engine repositories. Very new engines surfaced in broad searches, but comparable depth of implementation evidence was not established for inclusion here. This is a diverse selection, not an exhaustive inventory of every qualifying graph database.

Limitations: this was read-only source/document research; no candidate was cloned, built, benchmarked, or executed. API rate limiting interrupted part of the metadata pass, so remaining canonical URLs were verified by opening GitHub pages. Some documentation links required following redirects or locating their replacement pages. Architecture documents can lag implementation, explicitly noted for Oxigraph; moving default-branch links can also change after this research date. C1–C4 judgments are grounded engineering inferences from the cited material, not independent correctness proofs. Archived status, research-stage warnings, and Cozo's observed activity limitation are preserved rather than inferred away.
