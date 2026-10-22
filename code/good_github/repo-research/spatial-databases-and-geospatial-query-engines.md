# Spatial databases and geospatial query engines

Research date: **2026-10-09**.

This selection covers **22 GitHub repositories** implementing spatial storage, spatial SQL, distributed geospatial query execution, trajectory and point-cloud extensions, and specialized geographic databases. It includes several substantial spatial subsystems within larger databases, identified explicitly, and query libraries that implement partitioning or execution rather than merely forwarding requests. Pure geometry libraries, map renderers, client bindings, and standalone spatial-index packages are outside this report's main scope.

The descriptions identify useful engineering study material, not uniformly exemplary implementations or production recommendations. Criterion assignments are grounded judgments based on the linked documentation and inspected source. Repository pages were opened to verify canonical identities; every selection also has independently inspected implementation, architecture, or technical documentation. Maintenance is not inferred from popularity or a recent commit.

**Criteria legend**

- **C1 — Correctness:** difficult invariants, concurrency, numerical semantics, malformed inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable models or interfaces that support multiple uses.
- **C3 — Performance and structure:** concrete performance constraints addressed through an understandable implementation architecture.
- **C4 — Evolution:** sustained development supported by compatibility work, tests, migrations, or documented complexity management.

## Relational spatial storage and specialized extensions

### 1. [postgis/postgis](https://github.com/postgis/postgis)

**Language / role:** C and SQL; PostgreSQL spatial database extension. **Official GitHub mirror**; the repository identifies OSGeo as its development home.

Study how spatial types, exact predicates, and lossy access paths cooperate inside a relational database. The geometry/geography distinction exposes the difference between planar and geodetic computations, while the index documentation explains why a bounding-box hit is only a candidate for many predicates.

- **C1:** geometry validity, dimensionality, SRIDs, empty objects, and spherical versus planar measurements impose explicit semantic obligations. **C3:** GiST R-trees, BRIN, and SP-GiST offer different storage and query tradeoffs, with exact predicates refining index results. Both are explained in the [data-management and indexing chapter](https://postgis.net/docs/using_postgis_dbmanagement.html).
- **C4:** the [NEWS history](https://github.com/postgis/postgis/blob/master/NEWS) records years of PostgreSQL/GEOS compatibility changes, deprecated signatures, extension separation, and reindex requirements after changes to multidimensional operators. This is evidence of managing evolution beyond simply retaining an old codebase.

**Entry points:** the data-management chapter and `NEWS` above; follow the repository's `postgis` and `liblwgeom` modules when moving from semantics into implementation.

### 2. [MobilityDB/MobilityDB](https://github.com/MobilityDB/MobilityDB)

**Language / role:** C and SQL; temporal and moving-object data management built on PostgreSQL and PostGIS.

Study trajectories as typed functions of time instead of sequences of unrelated position rows. A particularly useful distinction is between observed instants and what the system assumes between observations.

- **C1:** discrete, step, and linear interpolation have different meanings. Inclusive/exclusive endpoints, uniform base types, sequence ordering, and normalization determine whether two representations denote the same temporal value. The [temporal-type specification](https://github.com/MobilityDB/MobilityDB/blob/master/doc/temporal_types_p1.xml) gives examples and normalization rules.
- **C2:** instants, sequences, and sequence sets provide a common abstraction across temporal booleans, numbers, text, and spatial points. The same specification explains how interpolation is constrained by the base type, making this useful for studying a reusable temporal algebra rather than a GPS-specific schema.

**Entry point:** `doc/temporal_types_p1.xml`; its definitions provide a semantic map for the repository's `meos` and `mobilitydb` implementations.

### 3. [pgpointcloud/pointcloud](https://github.com/pgpointcloud/pointcloud)

**Language / role:** C, with C++ compression integration and SQL; PostgreSQL storage and querying of LIDAR-style point clouds.

Study the choice to group points into patches and preserve schema-defined dimensions instead of storing every return as a conventional row. The project complements PostGIS with its own point-cloud representation and operators; it is a separate implementation, not a duplicate PostGIS distribution.

- **C3:** [compression documentation](https://pgpointcloud.github.io/pointcloud/concepts/compressions.html) explains transposing patches into per-dimension arrays and selecting run-length, common-bit, or deflate encodings according to each dimension's distribution.
- **C4:** [NEWS](https://github.com/pgpointcloud/pointcloud/blob/master/NEWS) documents changes from 2015 through 2023 involving scaled-dimension filtering, patch extents, invalid compressed inputs, PostgreSQL compatibility, upgrade paths, and dump/restore behavior. These are concrete examples of representation and compatibility maintenance.

**Entry points:** the compression design and `NEWS`. The repository README additionally exposes a PostgreSQL/PostGIS CI matrix; it should not be confused with a claim that the published documentation describes the newest source revision.

### 4. [orbisgis/h2gis](https://github.com/orbisgis/h2gis)

**Language / role:** Java; spatial SQL functions, metadata, analysis, and format access for the H2 database.

Study how an embedded relational engine gains a spatial function system without becoming a separate server product. This is a useful smaller counterpoint to PostgreSQL's extension architecture.

- **C2:** [H2GISFunctions](https://github.com/orbisgis/h2gis/blob/master/h2gis-functions/src/main/java/org/h2gis/functions/factory/H2GISFunctions.java) registers function implementations and standard spatial metadata views, separating SQL exposure from individual algorithms.
- **C1:** [ST_Intersects](https://github.com/orbisgis/h2gis/blob/master/h2gis-functions/src/main/java/org/h2gis/functions/spatial/predicates/ST_Intersects.java) makes SRID validation, empty geometry, and SQL-null behavior visible. Its argument-specific null branches are worth auditing rather than assuming all predicates have interchangeable semantics.
- **C3:** that implementation rejects disjoint envelopes before invoking JTS and reuses prepared geometries through a cache, showing an explicit progression from inexpensive filtering to expensive geometry work.

**Entry points:** the registration factory and predicate implementation above.

### 5. [mysql/mysql-server](https://github.com/mysql/mysql-server)

**Language / role:** C++; study the **GIS and spatial-index subsystem**, principally `sql/gis`, rather than treating the entire MySQL monorepo as spatial software.

The distinctive study opportunity is the boundary between spatial reference systems, geometric predicates, and storage-engine index operations.

- **C1:** [rtree_support.cc](https://github.com/mysql/mysql-server/blob/trunk/sql/gis/rtree_support.cc) distinguishes Cartesian and geographic boxes, converts geographic coordinates to radians, and separates physical coordinate equality from logical geometric equality. Those distinctions matter when index comparisons must agree with SQL geometry semantics.
- **C3:** the [spatial-analysis manual](https://dev.mysql.com/doc/refman/8.4/en/optimizing-spatial-analysis.html) describes minimum-bounding-rectangle indexes and quadratic R-tree splitting for spatial columns in InnoDB and MyISAM. The implementation provides a concrete interface between those access paths and GIS operations.

**Entry points:** `sql/gis/rtree_support.cc` and the versioned 8.4 manual above. The source link is to `trunk`; the manual is intentionally version-specific, not a statement that both describe identical releases.

### 6. [sqlite/sqlite](https://github.com/sqlite/sqlite)

**Language / role:** C; the **R*Tree virtual-table subsystem** of SQLite. **Official Git mirror** of a Fossil-managed source tree.

This is spatial range-query infrastructure, not a complete geodetic geometry engine. Study how a reusable spatial access method fits into SQL, persistence, and a virtual-table interface.

- **C1:** the [R*Tree manual](https://sqlite.org/rtree.html) explains outward floating-point rounding, the different implications for overlap and containment queries, and why mutating a tree during its scan can produce `SQLITE_LOCKED`.
- **C2:** custom query callbacks expose subtree classification and priority scores, supporting application-defined search regions and traversal orders.
- **C3:** the [implementation](https://github.com/sqlite/sqlite/blob/master/ext/rtree/rtree.c) and manual expose node, parent, and row-ID shadow tables, priority-queue traversal, and structural integrity checks. The compact subsystem makes these mechanisms unusually approachable.

**Entry points:** `ext/rtree/rtree.c` and the R*Tree manual.

## Columnar and hardware-aware spatial analytics

### 7. [duckdb/duckdb-spatial](https://github.com/duckdb/duckdb-spatial)

**Language / role:** C++; spatial extension for embedded analytical SQL.

Study how geometry processing fits into a vectorized engine whose natural unit of work is a column batch. The repository's older prototype wording is not a reliable inventory of present indexing capabilities; use the current documentation alongside the source.

- **C2:** the inspected [internals document](https://github.com/duckdb/duckdb-spatial/blob/v1.5-variegata/docs/internals.md) distinguishes flexible geometry values from specialized types composed of DuckDB lists and structs, and describes integration with GEOS, PROJ, and GDAL.
- **C3:** the same document explains per-thread arena allocation to reduce repeated small allocations. The [current R-tree documentation](https://duckdb.org/docs/current/core_extensions/spatial/r-tree_indexes) explains bounding-box pruning, exact refinement, Sort-Tile-Recursive bulk construction, and the requirement that an index-scan predicate expose a planning-time constant.

**Entry points:** `docs/internals.md` on the verified `v1.5-variegata` branch and the current R-tree documentation. Treat their version differences as part of the reading exercise.

### 8. [apache/sedona-db](https://github.com/apache/sedona-db)

**Language / role:** Rust with Python and other interfaces; single-node geospatial analytical engine built on Arrow and DataFusion.

This is a separate engine from distributed Apache Sedona below. Study a spatial physical operator integrated into an existing execution-plan ecosystem.

- **C1:** [SpatialJoinExec](https://github.com/apache/sedona-db/blob/main/rust/sedona-spatial-join/src/exec.rs) handles join schemas and projections, exact refinement after candidate generation, and one-time asynchronous preparation shared by probing partitions. Its comments also explain disposal of shared state after execution.
- **C2:** the [spatial-join crate interface](https://github.com/apache/sedona-db/blob/main/rust/sedona-spatial-join/src/lib.rs) exposes planners, predicates, and refinement interfaces for extension crates and external consumers.
- **C3:** build, probe, refinement, and output are explicit phases; provider abstractions separate index construction from the physical operator. The implementation also distinguishes ordinary spatial joins from KNN build/probe assignment.

**Entry points:** the two source files above. No C4 claim is made merely because this engine shares Apache Sedona's name and community.

### 9. [heavyai/heavydb](https://github.com/heavyai/heavydb)

**Language / role:** C++ and CUDA, with SQL planning components; study **HeavyDB's geospatial joins** within the broader repository.

Study an alternative to persistent R-tree lookup: constructing and tuning bounding-box hash structures for analytical spatial joins on CPU/GPU hardware.

- **C3:** [BoundingBoxIntersectJoinHashTable.cpp](https://github.com/heavyai/heavydb/blob/master/QueryEngine/JoinHashTable/BoundingBoxIntersectJoinHashTable.cpp) computes spatial bucket sizes on CPU or GPU, tunes against hash-table size and entries-per-bin constraints, distributes fragments to devices, and integrates hash-table reuse.
- **C1:** [GeospatialJoinTest.cpp](https://github.com/heavyai/heavydb/blob/master/Tests/GeospatialJoinTest.cpp) checks geometric join results and cache-control behavior under different execution scenarios. It also contains documented known limitations, which makes it useful for examining the boundary between supported behavior and unresolved correctness cases.

**Entry points:** the hash-join implementation and tests. The repository has expanded beyond the historical database core; this selection is specifically about that core's spatial execution, not every bundled platform component.

## Distributed indexes and geospatial execution frameworks

### 10. [locationtech/geomesa](https://github.com/locationtech/geomesa)

**Language / role:** Scala and Java; geospatial querying over distributed stores and streaming infrastructure.

Study how one feature model is translated into multiple physical index layouts and storage backends. The project offers a useful contrast to a database owning its entire storage engine.

- **C2:** spatial, spatiotemporal, identifier, and attribute indexes are selected from a `SimpleFeatureType` schema; secondary spatial/temporal tiers can be added to attribute indexes. The [index basics](https://www.geomesa.org/documentation/stable/user/datastores/index_basics.html) explain the configuration and query restrictions.
- **C3:** Z2/XZ2 and Z3/XZ3 distinguish spatial from spatiotemporal indexing and point from extended-geometry workloads, while attribute tiers improve compound filtering.
- **Compatibility evidence:** the same document records index-format generations, including corrected Z-curves and yearly epoch handling. Existing schemas retain their on-disk index versions across software upgrades, making compatibility a first-class storage concern. This supports the study value without independently assigning C4 from a version table alone.

**Entry point:** the index-basics and versioning document; its tables explain which physical layouts to look for in the repository's index modules.

### 11. [locationtech/geowave](https://github.com/locationtech/geowave)

**Language / role:** Java; multidimensional indexing and geospatial queries over several key-value stores.

Study independent abstractions for data adaptation, index strategy, and storage backend. The repository warns that its published website was last generated for the 2.0.x line; these entry points are the documentation in the source tree.

- **C2:** the [architecture document](https://github.com/locationtech/geowave/blob/master/docs/content/devguide/030-architecture.adoc) separates adapters, common index dimensions, sort/partition strategies, and backend storage. Persisted metadata allows the store to describe its own adapters and indexes.
- **C1:** the key representation tracks duplicate counts, while field masks and visibility can split a logical entry across rows. Consumers must reconstruct and deduplicate results correctly.
- **C3:** the [query design](https://github.com/locationtech/geowave/blob/master/docs/content/devguide/045-query.adoc) converts constraints into range scans, then applies exact distributable or client-side filters. It explicitly documents backend differences in server-side filtering support.

**Entry points:** source-tree architecture and query documents above.

### 12. [apache/sedona](https://github.com/apache/sedona)

**Language / role:** Java and Scala with Python/R interfaces; distributed spatial execution on systems including Spark and Flink.

Study how spatial predicates become physical joins and how data partitioning interacts with the host SQL optimizer. This is the distributed framework, distinct from the Rust SedonaDB engine.

- **C3:** the [query-optimization guide](https://sedona.apache.org/latest/api/sql/Optimizer/) shows physical range, distance, and broadcast-index joins, predicate pushdown, and the effect of partition count. It also describes spatial filtering for raster joins.
- **C1:** the same guide separates planar and geodesic distance semantics. Its S2 equi-join path explicitly requires geometric refinement to remove false positives and, for some geometry combinations, deduplication of exploded cell matches. This is useful evidence of the correctness work hidden by an apparently simple spatial join.
- **C2:** spatial operations enter the host's relational plans as reusable operators rather than application-specific distributed jobs.

**Entry point:** the optimizer guide, including its physical plans, approximation caveats, and broadcast-versus-partitioned execution examples.

### 13. [locationtech/geotrellis](https://github.com/locationtech/geotrellis)

**Language / role:** Scala; raster/vector processing framework with distributed, indexed raster-layer storage and queries.

The relevant subsystem is layer storage and retrieval, not simply raster arithmetic. Study how tile keys, metadata, and space-filling curves support both spatial window queries and individual tile lookup.

- **C2:** the [module hierarchy](https://github.com/locationtech/geotrellis/blob/master/docs/guide/module-hierarchy.rst) describes reusable layer representations, backend integrations, and spatial/spatiotemporal query APIs.
- **C3:** the [HDFS raster-layer design](https://github.com/locationtech/geotrellis/blob/master/docs/architecture/002-hdfs-raster-layers.rst) explains sorted MapFiles, index ranges encoded in filenames, file pruning without opening payloads, LRU reader caching, and a single-shuffle write strategy.
- **C1:** that design explicitly checks original keys because distinct keys can share a space-filling-curve index, and refines scan results against the original query bounds.

**Entry points:** module hierarchy and the HDFS architecture decision. The latter documents a particular backend, not a promise that all backends use the same file layout.

### 14. [geopandas/dask-geopandas](https://github.com/geopandas/dask-geopandas)

**Language / role:** Python; partitioned geospatial dataframe execution and spatial joins using Dask and GeoPandas. This is a query-execution library, not a standalone database.

Study a relatively compact example of translating geographic locality into a distributed task graph. Its value here is the implementation of query scheduling and spatial partition metadata, not the forwarding of individual geometry calls.

- **C3:** [sjoin.py](https://github.com/geopandas/dask-geopandas/blob/main/dask_geopandas/sjoin.py) joins partition extents first to prune task pairs; when metadata is unavailable, it explicitly constructs all left/right partition combinations. It builds the resulting Dask graph and propagates output partition extents.
- **C2:** spatial partitions are a reusable layer over dataframe operations. The [partitioning guide](https://dask-geopandas.readthedocs.io/en/stable/guide/spatial-partitioning.html) explains Hilbert, Morton, and geohash ordering and the tradeoffs in partition count and overlap.

**Entry points:** `sjoin.py` and the partitioning guide. The inspected join implementation explicitly supports inner joins only; this is not evidence of arbitrary distributed SQL support.

### 15. [aseldawy/spatialhadoop2](https://github.com/aseldawy/spatialhadoop2)

**Language / role:** Java; spatial indexing and MapReduce query processing over Hadoop. **Historical: the README explicitly states that it is no longer maintained** and directs users to Beast.

Study the older architecture of global partition indexes, specialized input formats, and local geometric processing. Its educational value is independent of its suitability for a new deployment.

- **C2:** the repository describes spatial shapes, index-aware record readers, and operations built on those reusable Hadoop abstractions.
- **C3:** [DistributedJoin.java](https://github.com/aseldawy/spatialhadoop2/blob/master/src/main/java/edu/umn/cs/spatialHadoop/operations/DistributedJoin.java) filters pairs of global-index partitions before local joins and exposes repartitioning and batching choices.
- **C1:** the same implementation uses a reference-point duplicate-avoidance rule when replicated partition data would otherwise emit repeated join pairs. That is a concrete distributed spatial correctness invariant.

**Entry point:** `DistributedJoin.java`, alongside the repository README's architecture and maintenance notice. Beast is not counted as a second GitHub project without a verified official substantive GitHub repository.

## In-memory and embedded spatial stores

### 16. [tidwall/tile38](https://github.com/tidwall/tile38)

**Language / role:** Go; spatial datastore and real-time geofencing server with disk persistence and replication.

Study the relationship between continuously changing objects, geographic queries, and event-oriented geofences. The core collection implementation is a useful entry point before the server protocols and notification machinery.

- **C1:** [collection.go](https://github.com/tidwall/tile38/blob/master/internal/collection/collection.go) maintains identifier, spatial, value, and expiry indexes on replacement/deletion. It rounds lower and upper bounds outward when converting to the spatial index's `float32` representation, preserving a conservative search envelope.
- **C3:** the same file uses an R-tree for candidate search, exact GeoJSON predicates for refinement, and a geodetic distance function for nearest-neighbor traversal. Cursor handling and periodic deadline checks expose the interaction between query throughput and server responsiveness.
- **C2:** the repository's common query model supports nearby, within, and intersection searches, which also underpin geofence monitoring.

**Entry point:** `internal/collection/collection.go`; use the repository README to relate collection operations to the external command and geofence model.

### 17. [tidwall/buntdb](https://github.com/tidwall/buntdb)

**Language / role:** Go; embedded in-memory key-value database with persistent logging, transactions, and multidimensional spatial indexes.

Study how an ordinary transactional key-value API accommodates spatial indexing without requiring a network service. It is narrower geometrically than Tile38, but has a distinct storage and transaction implementation.

- **C1:** [buntdb.go](https://github.com/tidwall/buntdb/blob/master/buntdb.go) includes rollback of modified records and indexes, commit buffering, and recovery from a partially written log append by truncating the incomplete portion. The README describes the multiple-reader/single-writer locking model.
- **C2:** a supplied rectangle-extraction function connects arbitrary stored values to spatial indexes; intersection and nearest-neighbor iteration operate through the same transactional interface.
- **C3:** the implementation combines ordered indexes with R-tree lookup and batches persistence writes per transaction. The tradeoff is explicit: indexed data stays in memory, while durability is handled separately.

**Entry point:** `buntdb.go`, especially transaction commit/rollback, spatial-index creation, `Intersects`, and `Nearby`.

## OSM-specific and versioned geographic databases

### 18. [clarisma/geodesk](https://github.com/clarisma/geodesk)

**Language / role:** Java; embedded OpenStreetMap spatial database and query toolkit. This entry covers the Java engine, not its separately named language implementations or bindings.

Study an OSM-native object model in which nodes, ways, relation membership, tags, and geometries remain connected. The README also states a concrete GOL format compatibility boundary between toolkit generations.

- **C2:** the feature API preserves OSM objects and relationships instead of requiring applications to reconstruct them from flattened geometry rows. The verified [feature source tree](https://github.com/clarisma/geodesk/tree/main/src/main/java/com/geodesk/feature) separates views, filters, matchers, storage, and query execution.
- **C3:** [Query.java](https://github.com/clarisma/geodesk/blob/main/src/main/java/com/geodesk/feature/query/Query.java) walks the tile index, limits outstanding tile work, dispatches tasks to an executor, and consumes batches through a blocking queue.
- **C1:** its explicit treatment of pending work, errors, and partial results makes asynchronous query completion and missing-data behavior worth studying; comments acknowledge unresolved design questions rather than establishing blanket correctness.

**Entry points:** the feature module and `query/Query.java`.

### 19. [drolbr/Overpass-API](https://github.com/drolbr/Overpass-API)

**Language / role:** C++; specialized database and query language for selecting OpenStreetMap objects and relationships.

Study a purpose-built geographic database that ingests updates while serving independent query processes. The interesting architecture extends well below its HTTP API.

- **C1:** the [component overview](https://dev.overpass-api.de/overpass-doc/en/more_info/components.html) explains dispatcher coordination, copy-on-write payload blocks, and shadow index files so readers retain a consistent view during updates.
- **C3:** it separates payload files, object-ID-to-geographic-index maps, and geographic-index-to-file-block indexes. Query startup loads index information while payload access remains selective.
- **C2:** [query.cc](https://github.com/drolbr/Overpass-API/blob/master/src/overpass_api/statements/query.cc) combines reusable query constraints and filtering stages for the OSM object model. The database and statement interpreter are distinct from the web-server integration.

**Entry points:** the component overview and the query statement implementation. The overview is operational architecture documentation, not a claim that every installation enables the same metadata/history depth.

### 20. [GIScience/oshdb](https://github.com/GIScience/oshdb)

**Language / role:** Java; spatial and temporal analysis of full OpenStreetMap history.

Study a database organized around historical entities rather than only current geometries. This provides a different solution to time-aware geographic analysis from MobilityDB's interpolated trajectories.

- **C1:** the [data-model document](https://github.com/GIScience/oshdb/blob/main/documentation/manual/data-model.md) explains resolving way/node references at the correct timestamp and preserving erroneous or incomplete source data, including missing referenced objects and invalid coordinates.
- **C3:** versions of an object are grouped into delta-encoded entities; multilevel grid cells provide spatial partitioning, and tag key/value tables reduce repeated strings. Queries must examine intersecting cells across all zoom levels because large or widely moving features occupy different levels.
- **C2:** the repository exposes snapshot and contribution views with region, time, and property filtering and MapReduce-style analysis, serving both extraction and aggregated history research.

**Entry point:** `documentation/manual/data-model.md`; the repository README connects that model to the public analytical API.

### 21. [locationtech/geogig](https://github.com/locationtech/geogig)

**Language / role:** Java; versioned geospatial object storage with spatial indexes over repository snapshots.

Study the interaction between version-control data structures and spatial access paths. **Historical documentation caveat:** the inspected release notes describe the 1.x line, including 2017–2018 releases. They do not establish present maintenance or current deployment readiness.

- **C2:** the [binary-object specification](https://github.com/locationtech/geogig/blob/master/doc/technical/source/geogig-binary.rst) defines commits, trees, features, buckets, envelopes, and typed attributes as reusable storage structures.
- **C3:** the [release/design notes](https://github.com/locationtech/geogig/blob/master/RELEASE_NOTES.md) explain sharing snapshots through a Merkle DAG and constructing corresponding spatial trees with quadtree clustering. Indexes can materialize attributes to reduce subsequent feature lookups.
- **C1:** those notes describe automatic index updates when commits are created and a migration fixing parent ordering during commit-graph traversal. These show that version history and spatial indexes must preserve coupled invariants.

**Entry points:** the binary specification and release/design notes. The implementation is selected for its unusual versioned spatial-storage architecture, not as a generic Git wrapper.

## Semantic geospatial querying

### 22. [apache/jena](https://github.com/apache/jena)

**Language / role:** Java; specifically the **GeoSPARQL subsystem** and its integration with the Jena/Fuseki query engine. The monorepo is counted once.

Study geographic predicates in an RDF query engine where features, geometry objects, and serialized geometry literals are separate entities.

- **C1:** the [GeoSPARQL documentation](https://jena.apache.org/documentation/geosparql/) explains CRS/unit conversion, multiple topological relation families, and query-rewrite behavior that can return both features and their geometries. These semantics differ substantially from a single SQL geometry column.
- **C2:** geometry datatypes and relation APIs support extensible serializations and use through both SPARQL and Java APIs.
- **C3:** the implementation uses spatial indexing and configurable caches for decoded geometries, coordinate transformations, and relation results. The documentation explains per-dataset query-rewrite indexes and the read-only-after-build nature of the described STRtree.

**Entry point:** the GeoSPARQL technical guide, particularly query rewriting, spatial indexing, and cache configuration. The older standalone `galbiston/geosparql-jena` project is not counted again.

## Coverage, search method, and limitations

Live discovery used substantially more than six formulations. Search angles included spatial SQL extensions; distributed geospatial key-value stores; embedded Rust/Go databases; OSM query and history engines; GeoSPARQL/RDF stores; Hadoop/Spark spatial joins; raster-layer storage; versioned geographic databases; GPU spatial SQL; and official GitHub mirrors. Follow-up searches pursued concrete architecture, source, tests, and changelog evidence. Later broad queries mostly returned already represented families, client projects, tutorials, or repositories whose official status was uncertain; HeavyDB was the final distinct architecture added.

The selection spans C, C++, CUDA, Rust, Go, Java, Scala, and Python, from in-process indexes through relational extensions and distributed frameworks. Its strongest coverage is vector/spatiotemporal query processing. Raster persistence and queries are represented through GeoTrellis and Sedona; it is not an exhaustive survey of scientific array databases.

Important boundaries and exclusions:

- **SpatiaLite** is highly relevant, but the inspected [official project repository](https://www.gaia-gis.it/fossil/libspatialite/index) uses Fossil. No authoritative substantive GitHub mirror was verified, so third-party copies and packaging repositories were not substituted.
- **Beast** appeared repeatedly as SpatialHadoop's successor. The project's [research paper](https://www.cs.ucr.edu/~tvu032/publications/21_beast.pdf) points to Bitbucket; no verified official substantive GitHub home was established. Rasdaman was also searched, but a qualifying official GitHub implementation was not verified. These are search limitations, not claims that the systems lack merit.
- Pure geometry/index foundations such as S2, H3, GEOS/JTS, and standalone R-tree libraries were not used to inflate a database/query-engine list. GeoDesk language variants, historical GeoSpark naming, and the pre-Apache GeoSPARQL-Jena repository were not counted as additional projects.
- GitHub pages and specific primary files were read; projects were not cloned, built, benchmarked, or subjected to a full correctness audit. No numerical performance comparisons are asserted. Tests are evidence of intended behavior and complexity management, not proof that all edge cases are handled.
- Source branches and “current” documentation can change. DuckDB's prototype-era prose, GeoWave's published-site lag, and GeoGig's historical documents are flagged where they affect interpretation. PostGIS and SQLite are explicitly identified as official mirrors; SpatialHadoop is explicitly identified as unmaintained. No general active-maintenance claim is made for the remaining selections.

Validation: **22 unique canonical repository URLs**, each with at least two justified criteria and an inspected technical entry point beyond its repository landing material. General-purpose monorepos are scoped to their spatial subsystems, and no fork is presented as an independent implementation.
