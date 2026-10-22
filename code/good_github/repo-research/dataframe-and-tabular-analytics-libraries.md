# Dataframe and tabular analytics libraries

Research date: **2026-10-09**.

This selection covers 24 GitHub repositories that implement dataframe containers, tabular transformation languages, execution engines with direct dataframe APIs, or substantive interoperability abstractions. It spans local memory, out-of-core processing, distributed execution, and GPUs. Backend adapters are included where they contribute their own substantial semantic or compilation layer. The focus is engineering material worth studying, not a ranking or a claim that every component is exemplary. Linked implementation and documentation pages are suggested reading entry points.

Criteria used:

- **C1 — Difficult correctness:** invariants, concurrency, numerical or missing-value semantics, adversarial inputs, and failure modes.
- **C2 — Reusable abstractions:** substantial interfaces and representations supporting many applications.
- **C3 — Performance with structure:** concrete resource constraints addressed through understandable architectural mechanisms.
- **C4 — Sustained evolution:** changes across years accompanied by compatibility work, testing, or explicit complexity management.

## Local dataframe models and statistical transformations

### [pandas-dev/pandas](https://github.com/pandas-dev/pandas)

**Language/role:** Python, Cython, and native extensions; labeled Series and DataFrame analytics.

An especially useful study in reconciling a large mutable-looking API with predictable ownership semantics. Follow the relationship between user-visible copies, internal blocks, and array sharing rather than treating indexing as a collection of independent convenience methods.

- **C1:** Copy-on-Write requires derived frames and series to behave independently on mutation. Each object owns its own manager and blocks, while a weak-reference-based `BlockValuesRefs` tracker detects shared underlying values. This makes alias tracking an explicit correctness mechanism. See the [developer design](https://pandas.pydata.org/docs/development/copy_on_write.html).
- **C3:** The same mechanism permits shared storage until a write requires copying; it connects the semantic guarantee to allocation costs instead of eagerly copying every selection. The [user guide](https://pandas.pydata.org/docs/user_guide/copy_on_write.html) also explains read-only exported arrays and chained-assignment restrictions.
- **C4:** The migration spans opt-in Copy-on-Write in [1.5.0, September 2022](https://pandas.pydata.org/docs/whatsnew/v1.5.0.html), migration guidance and warning mode, and the changed default in [3.0.0](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html). This is concrete evidence of managing a consequential compatibility transition over several years.

### [pola-rs/polars](https://github.com/pola-rs/polars)

**Language/role:** Rust with language bindings, notably Python; columnar dataframe engine with eager and lazy interfaces.

Study how a dataframe expression language becomes an execution engine. The [architecture overview](https://pola.rs/posts/polars_birds_eye_view/) follows expressions into a logical plan, optimization passes, a physical plan, and specialized compute kernels.

- **C2:** Expressions are reusable representations of column computations, rather than callbacks tied to one operation. The separation between the frontend language, logical operators, physical algorithms, and kernels makes it possible to add capabilities at different abstraction levels.
- **C3:** Predicate and projection pushdown reduce the rows and columns processed; physical planning chooses concrete execution algorithms. Parallel execution is part of the API and engine design. These are inspectable mechanisms, not an unsupported benchmark comparison.
- **C1:** Logical-plan construction checks schemas before execution, and optimizations must preserve the meaning of composed expressions. This makes the planner a useful place to examine the boundary between validation and execution.

### [Rdatatable/data.table](https://github.com/Rdatatable/data.table)

**Language/role:** R and C; dataframe-compatible querying, grouping, joins, and updates.

The distinctive study topic is reference semantics inside R's ordinary data-analysis workflow. The [reference-semantics vignette](https://rdatatable.gitlab.io/data.table/articles/datatable-reference-semantics.html) explains both user behavior and the pointer/copy model behind it.

- **C1:** `:=` and `set` mutate by reference, so aliases can observe changes. The documented distinction between shallow pointer-vector copies, deep copies, and explicit `copy()` is central to safely composing functions that receive tables.
- **C2:** Row selection, column computation/update, and grouping compose through the same table interface. Engineers can study how a compact API expresses grouped transformations without requiring a separate object model for each operation.
- **C3:** Updating columns without duplicating the whole table addresses memory pressure directly. The implementation model is concrete enough to reason about when an operation allocates and when it changes shared data.

### [tidyverse/dplyr](https://github.com/tidyverse/dplyr)

**Language/role:** R with native support; composable tabular transformation grammar.

Join implementation is a particularly productive entry point: it connects declarative operations to explicit failure policies and a lower-level matching engine.

- **C1:** The [join reference](https://dplyr.tidyverse.org/reference/mutate-joins.html) specifies missing-value matching, expected relationships between keys, unmatched-row checks, and warnings for unexpected many-to-many equality joins. These address silent row multiplication and data loss, not merely API ergonomics.
- **C2:** Equality, inequality, rolling, and overlap specifications share a join framework. In [join-rows.R](https://github.com/tidyverse/dplyr/blob/main/R/join-rows.R), dplyr standardizes matching policies, delegates matching to `vctrs::vec_locate_matches`, and translates lower-level conditions into operation-specific diagnostics. This is a useful example of reusing a matching abstraction while retaining a coherent public error model.

The selection concerns dplyr itself; separately maintained database backends are not counted as additional implementations here.

### [fastverse/collapse](https://github.com/fastverse/collapse)

**Language/role:** R, C, and C++; statistical aggregation and transformation over vectors, matrices, and data frames.

collapse is valuable for studying performance below the level of a query optimizer: how grouping metadata, weighted reductions, and in-place transformations can be composed into statistical routines. The canonical repository is under `fastverse`.

- **C2:** A common family of statistical functions accepts grouping and weighting information across several R data structures. Grouped transformations can reuse the same summaries through the `TRA` mechanism. See the [project documentation](https://fastverse.org/collapse/).
- **C3:** The [developer vignette](https://fastverse.org/collapse/articles/developing_with_collapse.html) distinguishes lightweight group identifiers from richer `GRP` objects, explains when to reuse them rather than repeatedly hash keys, and shows weighted sums accumulating products without intermediate vectors. Its worked grouped-regression example combines these mechanisms with mutation by reference.

The useful lesson is the accounting of passes, allocations, and reusable grouping state. The report does not adopt the vignette's numerical benchmark results as general performance guarantees.

### [JuliaData/DataFrames.jl](https://github.com/JuliaData/DataFrames.jl)

**Language/role:** Julia; heterogeneous in-memory tables and grouped transformations.

Study the interaction between a flexible column container and Julia's array/view ecosystem. The [type and ownership documentation](https://dataframes.juliadata.org/stable/lib/types/) is unusually explicit about invariants and the ways users can violate them.

- **C1:** Columns must have compatible lengths and one-based indexing. Resizing an exposed column can corrupt the parent frame; sorting one column independently breaks row correspondence; changing grouping columns can invalidate a grouped view. These are concrete consequences of allowing direct column access.
- **C2:** `DataFrame`, `SubDataFrame`, `DataFrameRow`, and `GroupedDataFrame` represent distinct ownership or selection roles while supporting related transformation workflows.
- **C3:** Copying is controlled through constructors and `copycols`; views retain parent storage. Integration with `Tables.CopiedColumns` and immutable Arrow-backed inputs shows how ownership information can avoid unnecessary copies without assuming every producer has identical storage semantics.

## Larger-than-memory, distributed, and accelerated execution

### [dask/dask](https://github.com/dask/dask)

**Language/role:** Python; the **Dask DataFrame subsystem** of a broader parallel-computing monorepo, counted once.

The [dataframe design documentation](https://docs.dask.org/en/latest/dataframe-design.html) explains how pandas-like operations become partitioned task graphs. The important representation comprises partitions, empty pandas metadata objects, and index-boundary information called divisions.

- **C1:** `_meta` carries column names and dtypes before actual computation. Inference can run user functions against synthetic nonempty data, so explicit metadata is needed when inference is expensive or fails. Known divisions also encode ordering assumptions that operations must respect.
- **C2:** Partitioned collections expose a familiar dataframe interface while expressing work through a general task-graph substrate. This is a useful boundary between collection semantics and scheduling.
- **C3:** Known divisions allow operations such as index selection and some joins to avoid irrelevant partitions. Partition sizing also trades execution parallelism against scheduler overhead. Unknown divisions require different strategies, including repartitioning or sorting where needed.

### [modin-project/modin](https://github.com/modin-project/modin)

**Language/role:** Python; pandas-oriented analytics over partitioned execution backends.

Modin's [architecture guide](https://modin.readthedocs.io/en/stable/development/architecture.html) gives a particularly clear layered decomposition: pandas API, query compiler, core dataframe, partition manager, and execution-specific partitions.

- **C2:** The query compiler translates high-level operations into a smaller dataframe algebra without owning scheduling. The core and partition manager handle layout and task dispatch. This separation is useful for studying how one frontend can target multiple execution arrangements.
- **C3:** Two-dimensional block partitioning supports both row-oriented and column-oriented work. Operations needing a whole axis can form row or column partitions, while managers use partition metadata to target work. The guide also discusses costs and limitations, including metadata held in pandas indexes and conversion overhead when changing execution representations.

The engineering interest lies in preserving a rich dataframe API across these boundaries. Inclusion does not assert complete pandas compatibility or that distributed execution benefits every workload.

### [NVIDIA/cudf](https://github.com/NVIDIA/cudf)

**Language/role:** CUDA/C++, Cython, and Python; GPU dataframe algorithms and APIs. The former `rapidsai/cudf` URL redirects here.

Count the libcudf, pylibcudf, and Python components as one repository. The [libcudf developer guide](https://docs.rapids.ai/api/libcudf/stable/developer_guide) is a strong entry into ownership, nested-column representation, and asynchronous execution.

- **C1:** Owning columns/tables and non-owning views have different lifetime obligations. Null masks, nested children, and equal-length table columns impose structural invariants. CUDA stream ordering adds another correctness dimension: crossing streams can require synchronization even when host calls return successfully.
- **C2:** A common column/table model supports algorithms reused by several public interfaces, separating native computation from language bindings.
- **C3:** Explicit stream parameters and stream-aware memory-resource parameters make allocation and asynchronous execution visible in the API. The guide explains why operations returning device columns should avoid unnecessary synchronization.

This is a useful study of making GPU execution constraints part of library design rather than hiding them entirely behind a dataframe facade.

### [vaexio/vaex](https://github.com/vaexio/vaex)

**Language/role:** Python and native components; lazy, out-of-core dataframe analytics.

Vaex offers a contrasting design to distributed partition schedulers: expressions over memory-mapped data with explicit choices about materialization. Start with its [performance guide](https://vaex.io/docs/guides/performance.html).

- **C2:** Virtual columns represent computations that behave like columns without immediately storing their results. They compose with dataframe filtering and statistical operations, separating a user's analytical model from the physical presence of each column.
- **C3:** Expressions are evaluated in chunks, while memory mapping permits access to datasets without eagerly reading them into process memory. The guide explains sharing mapped data between worker processes, caching through dataframe fingerprints, and the tradeoff between repeated virtual-column evaluation and materializing results.

The codebase is worth studying for its deliberate prioritization of memory use and repeated-query behavior. No claim about current release cadence or universal superiority over in-memory engines is made here.

### [Eventual-Inc/Daft](https://github.com/Eventual-Inc/Daft)

**Language/role:** Rust and Python; dataframe execution for tabular and multimodal workloads, locally and across workers.

The [architecture documentation](https://docs.getdaft.io/en/stable/architecture/) connects lazy expressions and logical plans to the Swordfish execution engine and Flotilla distributed orchestration.

- **C2:** Frontend expressions, logical optimization, physical operators, and distributed orchestration form distinct layers. The same analytical interface can express ordinary relational work alongside user functions and expensive data access.
- **C3:** Swordfish uses asynchronous operator pipelines and channels, with different treatment for streaming and blocking work. Expensive projections such as downloads or decoding remain separate operators so batching and backpressure can be controlled independently; they are delayed where semantics permit. Flotilla adds worker scheduling and locality considerations.

This makes Daft a useful comparison with engines whose costs are dominated by arithmetic and scans: scheduling slow or irregular user computations changes which optimizer transformations are desirable. This comparison is an engineering inference from the documented architecture, not a benchmark result.

### [apache/datafusion](https://github.com/apache/datafusion)

**Language/role:** Rust; embeddable columnar query engine with a direct DataFrame API. The relevant subsystem is the dataframe/expression-to-plan execution stack.

Although also a SQL engine, DataFusion belongs here because dataframe programs directly construct its plans. The [crate architecture documentation](https://docs.rs/datafusion/latest/datafusion/index.html) follows logical expressions, physical planning, data sources, and execution.

- **C2:** `TableProvider`, `OptimizerRule`, and `ExecutionPlan` separate data access, rewriting, and executable operators. Schema-aware expressions and plans can be extended without requiring every application to replace the engine. The [contributor architecture guide](https://datafusion.apache.org/contributor-guide/architecture.html) discusses these extension boundaries.
- **C3:** Physical operators produce partitioned streams of Arrow record batches through a pull-based asynchronous interface. Repartition operators supply parallel exchanges; memory pools and disk managers expose resource control. The documentation also explains the latency consequences of sharing a runtime between CPU-intensive work and network I/O.

The repository is counted once; adjacent bindings and downstream databases are not separate entries.

## Portable expression systems and table interoperability

### [ibis-project/ibis](https://github.com/ibis-project/ibis)

**Language/role:** Python; a dataframe expression system targeting multiple analytical backends.

Ibis is a good study in treating dataframe operations as a compiler frontend. The project's [explanation of SQL compilation](https://ibis-project.org/posts/does-ibis-understand-sql/) distinguishes constructing typed relational expressions from parsing arbitrary SQL.

- **C1:** Expression construction produces a typed, shaped intermediate representation. Validation and schema knowledge therefore enter before backend execution. SQL supplied through escape hatches can be schema-aware while its internal expression structure remains opaque to Ibis, an important boundary when reasoning about transformations.
- **C2:** Backend compilation turns the shared expression representation into backend-specific queries; results are then converted back into supported user-facing representations. The documented move to SQLGlot-based compilation illustrates separation between Ibis's relational model and SQL dialect handling.

The useful material is the frontend/IR/backend boundary and its semantic limits. Ibis is not counted as an independent implementation of every execution engine it can target, and the report makes no assumption that all backend features are interchangeable.

### [narwhals-dev/narwhals](https://github.com/narwhals-dev/narwhals)

**Language/role:** Python; a dataframe compatibility layer for library authors working with several native backends.

Narwhals contributes its own semantic machinery, making it more substantive than a generated wrapper. Its [implementation explanation](https://narwhals-dev.github.io/narwhals/how_it_works/) describes compliant backend protocols, dispatch, and expression metadata.

- **C1:** Expressions track properties such as whether they preserve length, behave like scalars, or require ordering. These support checks around broadcasting and mixed-length expressions. Lazy execution needs explicit ordering for order-sensitive operations because native query engines do not all guarantee row order.
- **C2:** Eager/lazy frame wrappers and expression namespaces let downstream libraries share an API while retaining native storage and execution. The implementation also handles transformations needed to express equivalent operations across different backend capabilities.
- **C3:** Native aggregation paths are distinguished from slower fallback operations such as pandas group application. The [contribution guide](https://github.com/narwhals-dev/narwhals/blob/main/CONTRIBUTING.md) adds backend-parameterized testing and constraints against row iteration or mutating user input; these are stated project policies, not an independent coverage audit.

### [JuliaData/Tables.jl](https://github.com/JuliaData/Tables.jl)

**Language/role:** Julia; interoperability protocols for table producers and consumers, rather than a standalone execution engine.

This small-surface abstraction is worth studying because tables can have very different internal layouts. The [interface implementation guide](https://tables.juliadata.org/stable/implementing-the-interface/) supplies required methods, optional methods, and a worked matrix adapter.

- **C2:** Row-access and column-access interfaces allow storage systems, analytical libraries, and I/O packages to communicate through a common protocol. Structural conformance avoids requiring every producer to inherit from one concrete table representation.
- **C1:** Consumers must account for unknown schemas; retrieved columns must satisfy one-based indexing and known-length contracts. Explicit requirements prevent accidental assumptions about arbitrary iterators or custom arrays.
- **C3:** Providing schema information allows consumers to specialize generated work using known column types. Optional access methods and direct column access let implementations expose their existing representation rather than standardizing everything through a row-by-row conversion.

Its inclusion deliberately covers a reusable tabular abstraction, not another full dataframe container.

## Typed native, JVM, and .NET implementations

### [jtablesaw/tablesaw](https://github.com/jtablesaw/tablesaw)

**Language/role:** Java; the core dataframe and column/selection subsystems of a broader analytics and visualization repository.

Tablesaw is a useful example of a typed column API with a reusable representation of row selections. The [column guide](https://jtablesaw.github.io/tablesaw/userguide/columns.html) explains typed storage, mappings, missing values, and predicate selections.

- **C2:** Columns expose type-specific operations, while `Selection` objects describe row positions that can be composed and applied across columns or tables. This separates deciding which rows qualify from materializing the selected values.
- **C3:** [BitmapBackedSelection.java](https://github.com/jtablesaw/tablesaw/blob/master/core/src/main/java/tech/tablesaw/selection/BitmapBackedSelection.java) implements set operations using Roaring bitmaps and exposes primitive integer iteration. The representation makes predicate combination and selection storage concrete study topics.
- **C1:** The column guide documents the equal-length obligation when mutating table columns and the need for missing-value predicates rather than equality comparisons with `NaN`. These are useful examples of correctness obligations that remain visible to callers.

### [Kotlin/dataframe](https://github.com/Kotlin/dataframe)

**Language/role:** Kotlin/JVM; typed, potentially hierarchical dataframe processing.

Study how dynamic tabular schemas meet a statically typed language. The [column model](https://kotlin.github.io/dataframe/datacolumn.html) distinguishes value columns, nested column groups, and columns whose cells themselves contain dataframes.

- **C2:** These column kinds share a dataframe framework while preserving nested structure and type information. Generated extension properties make schemas usable through ordinary Kotlin access syntax, rather than requiring string-based access everywhere.
- **C1:** [Schema compatibility](https://kotlin.github.io/dataframe/schemas.html) is defined by required column names and types, including nested schemas. `cast(verify=true)` and `convertTo` check compatibility; unchecked assumptions are therefore distinguishable from verified conversions. The documentation also explains that schema inference for externally loaded data and schema propagation through transformations have different capabilities.

This is particularly useful for API and compiler-integration design. Current documentation deprecates the older Gradle/KSP schema plugins, so readers should follow the compiler-plugin and schema-generation guidance rather than assuming older setup instructions remain current.

### [techascent/tech.ml.dataset](https://github.com/techascent/tech.ml.dataset)

**Language/role:** Clojure/JVM; columnar datasets built on typed readers, buffers, and specialized storage.

This project is useful for studying how a dynamic functional language can expose analytical data without representing every cell as an ordinary boxed object. The repository describes primitive backing storage, packed date/time values, and string-table representations.

- **C1:** The [column API documentation](https://techascent.github.io/tech.ml.dataset/tech.v3.dataset.column.html) represents missing positions separately with Roaring bitmaps and exposes explicit missing-set operations. Parsing can preserve unparsed strings and their indexes in metadata, distinguishing failed conversion from successfully parsed data.
- **C2:** Columns, readers, datatype information, and column-mapping operations form a reusable layer beneath dataset transformations. Missingness propagation can be specified independently of the value computation.
- **C3:** Typed backing storage and bitmap missingness avoid requiring a boxed nullable object for every cell. This is an architectural motivation grounded in the documented representations; no numerical speed comparison is implied.

### [fslaborg/Deedle](https://github.com/fslaborg/Deedle)

**Language/role:** F# with C# APIs; indexed series and dataframes, including time-series operations.

The [design notes](https://fslab.org/Deedle/design.html) separate storage (`IVector`) from key-to-location mapping (`IIndex`). Frames then combine row/column indexes with vectors of column vectors.

- **C1:** Index alignment and optional values must remain consistent across every column. Index builders return both a new index and a `VectorConstruction` recipe, allowing the corresponding data transformation to be applied consistently.
- **C2:** Vector and index builders permit alternative storage and deferred construction without changing the series/frame interface. The design is particularly useful for understanding why labeled data needs more than a rectangular array abstraction.
- **C4:** [Release notes](https://github.com/fslaborg/Deedle/blob/master/RELEASE_NOTES.md) document .NET Standard migration and concurrency fixes in 2018, missing-value and statistical fixes in later years, and subsequent framework migrations and test-infrastructure work. They also record breaking changes and compatibility aliases, supplying evidence of sustained complexity management rather than merely repository age.

### [hosseinmoein/DataFrame](https://github.com/hosseinmoein/DataFrame)

**Language/role:** C++; heterogeneous column containers and statistical/financial analytics.

This library offers a distinctly native C++ design: template parameters select index and storage/view types, while analytical algorithms use visitors. The [library documentation](https://hosseinmoein.github.io/DataFrame/docs/HTML/DataFrame.html) describes these representations before presenting the operation catalog.

- **C2:** Container operations and analytical visitors are separate extension mechanisms. Columns can hold built-in or user-defined types; algorithms can be added without turning every new statistic into a special container method.
- **C3:** Owning `HeteroVector` storage, contiguous `HeteroView` slices, and disjoint pointer views expose different access and allocation costs through a related interface. A template alignment parameter controls allocation alignment, and synchronous/asynchronous entry points expose execution choices.
- **C1:** The model explicitly constrains column length relative to the index and requires callers to know column types at compile time. View ownership and these schema obligations are productive correctness topics; this is not a claim that the library automatically guards against every misuse.

### [go-gota/gota](https://github.com/go-gota/gota)

**Language/role:** Go; typed Series and DataFrame operations. **Historical: archived by its owner on November 5, 2025; read-only at research time.**

Gota remains a compact, substantive study of building dataframe behavior within ordinary Go data structures. It supports cleaning, transformations, joins, grouping, and tabular input/output without the architectural size of a distributed engine.

- **C1:** The [DataFrame implementation](https://github.com/go-gota/gota/blob/master/dataframe/dataframe.go) copies input series during construction, checks errors on each series, rejects incompatible column lengths, and carries an error state in the dataframe. These show how type integrity, dimensions, ownership, and failure propagation interact.
- **C2:** A dataframe composes typed Series rather than implementing every scalar operation independently. Selection, mutation, combination, and serialization share that representation. The same [implementation, read through its raw source](https://raw.githubusercontent.com/go-gota/gota/master/dataframe/dataframe.go), exposes the constructor and dimension-checking boundary directly.

Include it for historical implementation study, with its archived status visible; the report does not recommend it on the assumption of ongoing maintenance.

## JavaScript and Elixir analytical languages

### [uwdata/arquero](https://github.com/uwdata/arquero)

**Language/role:** JavaScript; column-oriented table transformations, grouping, and window calculations.

Arquero is useful for studying a table language embedded in JavaScript whose execution is more structured than arbitrary per-row callbacks. Its [expression documentation](https://idl.uw.edu/arquero/api/expressions) describes parsing and compiling expressions, including the limits of escaped JavaScript functions.

- **C2:** Table verbs, expression operators, and custom aggregates are separate extension points. The [extensibility guide](https://idl.uw.edu/arquero/api/extensibility) describes aggregate state and dependencies rather than only showing end-user syntax.
- **C1:** Aggregate implementations distinguish total count from valid-value count, with null, undefined, and `NaN` treated as invalid. Sliding-window aggregates need removal behavior as well as initialization, addition, and final value calculation, making incremental-state correctness explicit.
- **C3:** Compiled expressions can access column storage without constructing a tuple object for each row. Shared aggregate dependencies and streaming state provide further opportunities to avoid repeated work.

### [data-forge/data-forge-ts](https://github.com/data-forge/data-forge-ts)

**Language/role:** TypeScript/JavaScript; indexed dataframe and series transformations inspired by LINQ and pandas.

Use the TypeScript repository: the older `data-forge-js` repository is archived and directs readers to this successor. The [key-concepts document](https://github.com/data-forge/data-forge-ts/blob/master/docs/concepts.md) explains its internal sequence model.

- **C2:** DataFrame, Series, and Index share a sequence-oriented design. Data is modeled through index/value or index/row pairs; selectors, predicates, comparers, and generators supply reusable transformation hooks. This supports analytical pipelines over JavaScript object rows without requiring a fixed columnar buffer layout.
- **C3:** ES6 iterators implement deferred, row-by-row evaluation. Operations such as serialization consume the pipeline, while `bake()` explicitly realizes it in memory. Engineers can study the distinction between reusable lazy computation and materialized results, including where repeated enumeration may cost additional work.

This is a contrasting execution model to Arquero's expression compilation, not a duplicate fork entry. The report does not infer a particular maintenance cadence from the successor repository's existence.

### [elixir-explorer/explorer](https://github.com/elixir-explorer/explorer)

**Language/role:** Elixir with a Rust/Polars backend; dataframe and series analytics integrated with Elixir's functional and macro facilities.

Explorer contributes a language-level query system of its own. The [query documentation's implementation section](https://hexdocs.pm/explorer/Explorer.Query.html) explains how syntax becomes executable expressions.

- **C2:** Query macros translate into ordinary `_with` callback APIs. Callbacks receive a special `QueryFrame`; accessing columns yields lazy Series that support the regular Series functions. Programmatically generated queries can therefore reuse the same abstraction without reproducing the surface syntax.
- **C1:** A query-backed frame permits series access but cannot be manipulated like a materialized frame. The documentation also separates comprehensions over column metadata from expressions over column values; mixing these levels is a compilation error. This boundary helps make staged evaluation understandable.
- **C3:** Query operations build lazy expression structures for backend execution instead of requiring Elixir to enumerate and transform individual values. The performance engine is Polars; Explorer is retained for its distinct interface and query-compilation design, not counted as a second independent Polars engine.

## Search coverage, exclusions, and limitations

Discovery used more than six distinct live-search formulations, followed by opening primary repository pages and implementation documentation. Search angles included Python/Rust dataframe optimizers; R and Julia table semantics; distributed pandas-compatible execution; GPU and out-of-core analytics; JVM/Kotlin/C++/Go implementations; JavaScript expression and iterator engines; Clojure, F#, and Elixir designs; and cross-backend/table-interchange protocols. Additional Ruby/Haskell and bitmap-selection searches mostly surfaced adjacent ecosystems, known candidates, or material outside this selection's focus. These follow-up searches produced diminishing returns for the architectural coverage sought here, rather than proving that no other qualifying libraries exist.

Every retained canonical GitHub repository was opened, and an additional primary implementation, design, or API source was read. GitHub source pages that exposed only navigation or line numbers were followed to readable source or supplemented with implementation documentation. Repository stars were not used as qualifying evidence. Criteria are judgments grounded in the cited mechanisms; statements about what an engineer can learn are selection judgments, not independently measured quality scores.

Broad numerical-array libraries, standalone file formats, table viewers, validators, tutorials, and generic database servers were excluded. Arrow's underlying format and compute ecosystem are important dependencies but are not separately counted here. Spark and other broad processing platforms were not added merely because they expose a dataframe API; DataFusion is included specifically as an embeddable library with an inspectable direct dataframe-to-plan stack. Backend reuse is called out for Explorer, Narwhals, and Ibis. Each monorepo is counted once.

Repository moves were resolved to `NVIDIA/cudf` and `fastverse/collapse`. The archived JavaScript predecessor of Data-Forge was excluded in favor of its TypeScript successor; [the predecessor's own notice](https://github.com/data-forge/data-forge-js) documents that relationship. Gota is the deliberately retained archived project and is labeled accordingly. No retained entry is presented as an unofficial mirror.

This was read-only research: no candidate code was installed, cloned, executed, or benchmarked. Release histories were inspected where C4 is asserted, especially pandas and Deedle; a uniform release-cadence or test-coverage audit was not performed for all projects. Documentation and default branches can change, and some older documentation URLs failed before current official pages were found. The report therefore supports choosing codebases and entry points for deeper study, not certifying current production suitability or comparative performance.
