# Map rendering and vector tile engines

Research date: **2026-10-09**.

This selection covers 27 GitHub repositories implementing geographic map rendering, vector tile generation and processing, tile codecs and archives, and substantive tile-serving engines. It includes browser, native, offline, and server architectures. General graphics libraries, routing engines, basemap styles, deployment recipes, and thin framework bindings are outside the selection. Archive and codec projects are included because their implementations directly determine how map engines obtain and process tiles.

Criteria identify reasons to study a particular subsystem, not a certification of the entire repository:

- **C1 — Difficult correctness:** geometry and numerical invariants, concurrency, malformed inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or models supporting different sources, renderers, platforms, or applications.
- **C3 — Performance with structure:** concrete strategies for bounded memory, responsive rendering, throughput, or efficient I/O, with understandable component boundaries.
- **C4 — Sustained evolution:** documented changes across years together with compatibility work, testing, or management of architectural complexity.

## Interactive browser and cross-platform renderers

### 1. [maplibre/maplibre-gl-js](https://github.com/maplibre/maplibre-gl-js)

**Language / role:** TypeScript and GLSL; browser GPU renderer for styled vector maps.

Study the conversion from geographic features into reusable GPU buffers, especially the boundary between style evaluation, tile layout, and drawing. This is a substantially evolved continuation of the former open-source Mapbox GL JS line, rather than an additional copy of that original project.

- **C2:** `Bucket` implementations encapsulate geometry-to-buffer conversion; buckets can serve families of style layers sharing layout properties. `ProgramConfiguration` connects data-driven style properties to shader attributes and uniforms.
- **C3:** Tile fetching, parsing, layout, and feature indexing run in workers; buffer data crosses to the main thread for drawing. Shader compilation and caching are separately managed. The [architecture document](https://github.com/maplibre/maplibre-gl-js/blob/main/ARCHITECTURE.md) explains both the abstractions and the work split.

### 2. [maplibre/maplibre-native](https://github.com/maplibre/maplibre-native)

**Language / role:** C++ core with platform SDKs; native vector map renderer. Counted once for the core and its bindings.

This is particularly useful for studying asynchronous rendering under continuous camera and style changes.

- **C1:** The geometry tile worker has explicit parsing, coalescing, symbol-layout, and idle states. It combines pending updates while waiting for glyphs and images, addressing stale work and starvation under load. See the [worker state-machine explanation](https://github.com/maplibre/maplibre-native/blob/main/docs/mdbook/src/design/geometry-tile-worker.md).
- **C2:** Public mutable style objects are separated from immutable implementation snapshots, allowing renderer and worker threads to share style state. Generated style APIs and platform SDK boundaries make the same core reusable across applications. The [architecture document](https://github.com/maplibre/maplibre-native/blob/main/ARCHITECTURE.md) explains snapshot diffing and ownership; some build-system and naming passages retain historical terminology.

### 3. [openlayers/openlayers](https://github.com/openlayers/openlayers)

**Language / role:** JavaScript; browser mapping library with vector, vector tile, and raster rendering.

An instructive alternative to a single style-spec-driven engine, particularly where projections, source types, and layer composition matter.

- **C2:** `Map`, `View`, `Source`, and `Layer` separate interaction/container ownership, projection and resolution, data acquisition, and visual representation. These boundaries accommodate tiled imagery, arbitrary image extents, and vector data. See [core concepts](https://github.com/openlayers/openlayers/blob/main/site/src/doc/tutorials/concepts.md).
- **C1 / C3:** The vector tile layer documents buffer requirements for symbols crossing tile edges, decluttering priorities across layers, and the ordering consequences of hybrid rendering. It also exposes the cost of rebuilding feature batches during animation versus reusing them. The [VectorTileLayer API](https://openlayers.org/en/latest/apidoc/module-ol_layer_VectorTile-VectorTileLayer.html) makes these correctness/performance tradeoffs explicit.

### 4. [tangrams/tangram](https://github.com/tangrams/tangram)

**Language / role:** JavaScript and GLSL; WebGL cartographic renderer with YAML scene descriptions.

Study a renderer built around configurable scenes and programmable styles, with its own substantial label-placement implementation.

- **C2:** Scene definitions combine data sources, filtering, styles, and shader customization; the renderer accepts several vector data representations rather than one fixed basemap schema.
- **C1:** Collision processing waits for every registered style to contribute labels, orders candidates by priority, and keeps linked labels visible or hidden together. Aborting a tile resolves waiting work before removing its state. These behaviors are directly visible in [collision.js](https://github.com/tangrams/tangram/blob/master/src/labels/collision.js).
- **C3:** The tile manager checks whether collision-relevant tile state has changed before starting another label pass, and coordinates an outstanding collision task with later updates. See [tile_manager.js](https://github.com/tangrams/tangram/blob/master/src/tile/tile_manager.js).

### 5. [protomaps/protomaps-leaflet](https://github.com/protomaps/protomaps-leaflet)

**Language / role:** TypeScript; Canvas vector map renderer and labeler integrated with Leaflet. **Maintenance mode:** the README recommends it for legacy Leaflet systems and directs new general-purpose work toward MapLibre GL JS.

Its smaller implementation is valuable for studying labeling without traversing a complete GPU engine.

- **C1:** Label deduplication depends on a documented anchor-within-bounds invariant. The spatial index also inserts wrapped copies of labels at the antimeridian and tracks ordering for collision decisions. See [labeler.ts](https://github.com/protomaps/protomaps-leaflet/blob/main/src/labeler.ts).
- **C2 / C3:** A common asynchronous `TileSource` interface supports different storage sources. Geometry decoding computes scaled coordinates and bounds together, avoiding a later rescaling pass in the ordinary rendering path. See [tilecache.ts](https://github.com/protomaps/protomaps-leaflet/blob/main/src/tilecache.ts).

### 6. [galileo-map/galileo](https://github.com/galileo-map/galileo)

**Language / role:** Rust; cross-platform geographic renderer using wgpu. This is the canonical destination of the former `Maximkaaa/galileo` URL. The README describes the project as work in progress.

Study how Rust data ownership and backend-neutral rendering models can support both feature layers and vector tile layers.

- **C2:** `RenderBundle` collects images, lines, polygons, labels, and markers, separating world-space content from screen-space content before backend rendering. See the [bundle implementation](https://github.com/galileo-map/galileo/blob/main/galileo/src/render/render_bundle/mod.rs).
- **C1 / C3:** The tile store distinguishes loading, prepared, packed, and error states. Raw MVT data can be shared through `OnceCell` references, while prepared data is cached by tile and style identity with memory weights and eviction bookkeeping. See [tile_store.rs](https://github.com/galileo-map/galileo/blob/main/galileo/src/layer/vector_tile_layer/tile_provider/tile_store.rs). These are concrete mechanisms, not evidence that its performance matches established renderers.

### 7. [Mapsui/Mapsui](https://github.com/Mapsui/Mapsui)

**Language / role:** C#; .NET map rendering components using SkiaSharp across multiple UI frameworks. The vector tile package is explicitly listed as experimental; the broader map renderer is the subsystem selected here.

- **C2:** The renderer dispatches through style and widget renderer registries, supports custom layer rendering, and shares rendering paths between UI output and bitmap export. This makes the map rendering implementation reusable beyond one application framework.
- **C1:** Feature picking renders candidate features into a clipped surface and examines pixel changes, then reverses drawing order to return uppermost features first. Viewport bounds, screen/world conversion, alpha, and canvas state interact in this path. Both criteria can be studied in [MapRenderer.cs](https://github.com/Mapsui/Mapsui/blob/main/Mapsui.Rendering.Skia/MapRenderer.cs).

## Offline maps and cartographic rendering cores

### 8. [mapsforge/mapsforge](https://github.com/mapsforge/mapsforge)

**Language / role:** Java; offline vector map library, renderer, and map writer for Android and desktop.

Study the architectural consequences of caching rasterized geographic tiles while keeping labels correct during panning and rotation.

- **C1 / C3:** The label-layer design separates labels from tiled ways and areas to avoid rotation and cross-tile clipping problems. Label retrieval shares the map-reading pass, stores results in an LRU structure, and moves layout recalculation to a dedicated thread. See the [label-layer design](https://github.com/mapsforge/mapsforge/blob/master/docs/LabelLayer.md), which also explains shortcomings of the preceding approach.
- **C4:** The [changelog](https://github.com/mapsforge/mapsforge/blob/master/docs/Changelog.md) records years of platform compatibility, rendering, and file-format work through 2026. It explicitly documents an architectural rewrite that broke application APIs while preserving older map-file compatibility—useful evidence of deliberate compatibility boundaries.

### 9. [mapsforge/vtm](https://github.com/mapsforge/vtm)

**Language / role:** Java and OpenGL; vector tile renderer for Android, desktop, iOS, and browser backends.

This is a substantive continuation of `opensciencemap/vtm`, with Mapsforge compatibility and subsequent rendering development. The predecessor is not counted separately.

- **C1 / C3:** `TileManager` coordinates tile indexing, loader jobs, current versus next visible tile sets, locking, cache limits, and the backlog of geometry waiting for GPU upload. Zoom thresholds address visual instability when changing levels. See [TileManager.java](https://github.com/mapsforge/vtm/blob/master/vtm/src/org/oscim/layers/tile/TileManager.java).
- **C4:** The [changelog](https://github.com/mapsforge/vtm/blob/master/docs/Changelog.md) documents Mapsforge v5/theme compatibility in 2017, MVT decoder work in 2018, Android compatibility fixes, and later tessellation, hillshading, and label-repetition changes through 2026. This establishes independent evolution beyond a renamed fork.

### 10. [Framstag/libosmscout](https://github.com/Framstag/libosmscout)

**Language / role:** C++; offline OSM library. The selected subsystem is map data access and cartographic rendering, rather than its routing or location-search components.

- **C1:** Indexed geographic queries may return overlapping objects even for disjoint requested boxes, and labels can extend beyond the geometry that selected them. The [render-process documentation](https://libosmscout.sourceforge.net/documentation/renderprocess/) explains why stable rendering requires careful query expansion and clipping order.
- **C2:** A `Database` facade wraps data/index access, while rendering backends have explicit requirements for polygon holes, floating-point coordinates, text measurements, and curved labels. See [backend requirements](https://libosmscout.sourceforge.net/documentation/renderbackend/).

These design pages are historical and partly incomplete; they are useful explanations of the architecture and its invariants, not a complete current API reference.

### 11. [mapnik/mapnik](https://github.com/mapnik/mapnik)

**Language / role:** C++; reusable cartographic rendering toolkit for server and desktop applications.

Study a geographic drawing library whose data access and output environments remain outside the core.

- **C2:** Runtime datasource plugins supply features to a core organized around querying, filtering, styling, and rendering. The [design document](https://github.com/mapnik/mapnik/blob/master/docs/design.md) explicitly explains why Mapnik is a library rather than a complete map server.
- **C3:** The feature/style processor collects only properties needed by active rules, skips inactive styles, and supports replaying buffered features across multiple styles instead of repeating source access. See [feature_style_processor_impl.hpp](https://github.com/mapnik/mapnik/blob/master/include/mapnik/feature_style_processor_impl.hpp). This is a concrete example of pushing selection toward data acquisition while preserving reusable render traversal.

### 12. [MapServer/MapServer](https://github.com/MapServer/MapServer)

**Language / role:** C with supporting C++; map rendering and geospatial service engine. The rendering subsystem is the focus here.

- **C2:** Rendering utilities dispatch through a renderer function table while managing shared symbol and style semantics. Symbol preparation handles vector, text, image, and SVG representations without placing all format-specific behavior in the caller.
- **C1 / C3:** Symbol scaling obeys resolution-dependent minimum and maximum sizes. The image-local symbol cache keys reuse on dimensions, scale, rotation, widths, and colors, including alpha; eviction reuses cache objects while releasing their images. These details expose both visual equivalence requirements and resource management. Start with [maprendering.c](https://github.com/MapServer/MapServer/blob/main/src/maprendering.c).

This entry concerns the actual renderer, rather than treating every OGC service feature as evidence of rendering quality.

## Tile generation and processing pipelines

### 13. [felt/tippecanoe](https://github.com/felt/tippecanoe)

**Language / role:** C++; vector tileset compiler for GeoJSON, FlatGeobuf, and CSV. The README identifies this as the official home; the original Mapbox repository is not counted again.

Study how a tile compiler chooses which detail survives at different zoom levels under tile-size and memory constraints.

- **C1:** Simplification must preserve shared intersection nodes and handle polygon collapse without corrupting the intended representation. The implementation distinguishes already-reduced placeholder geometries from ordinary features. See [tile.cpp](https://github.com/felt/tippecanoe/blob/main/tile.cpp).
- **C3:** The same file separates simplification worker tasks and permits earlier simplification when coalesced geometry consumes too much memory. The [changelog](https://github.com/felt/tippecanoe/blob/main/CHANGELOG.md) adds concrete examples of staged polygon cleaning, reduced attribute-memory use, numerical conversion fixes, and termination fixes for adaptive dropping/coalescing loops.

### 14. [onthegomap/planetiler](https://github.com/onthegomap/planetiler)

**Language / role:** Java; configurable large-scale vector tileset generator.

An unusually accessible case study in external-memory geometry processing and parallel pipeline design.

- **C1:** OSM input requires multiple passes and reconstruction of ways and multipolygons. After projection, simplification, clipping, and rounding, polygon topology is repaired because quantization can introduce self-intersections.
- **C2:** Profiles customize feature generation, relation preprocessing, and per-tile postprocessing independently of the execution pipeline.
- **C3:** Intermediate features are sorted by tile key using external merge sorting; tile batches are sized to distribute expensive work; repeated tile contents can avoid re-encoding; output writing is separated from parallel encoding. The [architecture guide](https://github.com/onthegomap/planetiler/blob/main/ARCHITECTURE.md) traces these stages and links their implementations.

### 15. [systemed/tilemaker](https://github.com/systemed/tilemaker)

**Language / role:** C++ with Lua processing scripts; OSM-to-MVT compiler producing tile files, MBTiles, or PMTiles without requiring a database.

- **C2:** Lua callbacks decide which input objects become layers and attributes; JSON configuration controls zoom ranges, precision, compression, and layer composition. The [configuration reference](https://github.com/systemed/tilemaker/blob/master/docs/CONFIGURATION.md) exposes the boundary between reusable engine mechanics and map-specific policy.
- **C1:** Multipolygons and boundary relations need different treatment from ordinary ways. Relation memberships are accepted before being consumed, and nested relations require a postscan stage because ancestors are unavailable during the initial scan. The [relations guide](https://github.com/systemed/tilemaker/blob/master/docs/RELATIONS.md) documents this ordering and explains that deeply nested ancestry is flattened rather than preserved as a hierarchy.

### 16. [tilezen/tilequeue](https://github.com/tilezen/tilequeue)

**Language / role:** Python; asynchronous tile generation and queue orchestration from the Mapzen/Tilezen ecosystem.

Treat this as a useful legacy architecture reference: the repository is unarchived, but its README still describes Python 2.7 installation assumptions. A recent repository update alone does not establish a modern supported runtime.

- **C1:** Worker completion tracking distinguishes finishing one coordinate from finishing an entire queued group, controls acknowledgement/progress updates, and handles shutdown while workers are blocked on queues. See [worker.py](https://github.com/tilezen/tilequeue/blob/master/tilequeue/worker.py).
- **C2:** Queue reading, processing, storage, and acknowledgement collaborators are injected into workers. In-flight suppression has interchangeable Redis-backed and no-op implementations, illustrating where orchestration policy sits outside tile encoding. See [inflight.py](https://github.com/tilezen/tilequeue/blob/master/tilequeue/queue/inflight.py).

### 17. [versatiles-org/versatiles-rs](https://github.com/versatiles-org/versatiles-rs)

**Language / role:** Rust; tile conversion, processing, validation, and serving toolkit. Counted once across its component crates.

- **C1:** Rectangular bounds cannot faithfully describe disconnected islands or arbitrary coverage. Its coverage model distinguishes rectangles, exact quadtrees, and zoom pyramids; set operations preserve which tiles actually exist. See the [tile-coverage architecture](https://github.com/versatiles-org/versatiles-rs/blob/main/DEVELOPMENT.md#architecture-tile-coverage).
- **C2 / C3:** A composable pipeline language combines tile sources and transformations for either archive output or live serving. Operations include raw vector ingestion, overzooming, feature/property filtering, and repair, executed through parallel streaming. See the [pipeline documentation](https://github.com/versatiles-org/versatiles-rs/blob/main/versatiles_pipeline/README.md).

Study the distinction between coverage metadata and rectangular request geometry, then follow how the same processing pipeline is reused in batch and request-driven execution.

## Tile subdivision, codecs, and archive access

### 18. [mapbox/geojson-vt](https://github.com/mapbox/geojson-vt)

**Language / role:** JavaScript; on-demand GeoJSON subdivision into simplified vector tile data.

This is a compact algorithmic companion to the full renderers: it produces tile geometry rather than drawing maps itself.

- **C1:** Coordinate storage is selected only after checking whether the world span plus wrapping buffer fits the signed-integer representation; otherwise the code uses floating-point storage. Projection, dateline wrapping, clipping, and simplification have separate stages.
- **C3:** An initial index stops at configurable zoom/point thresholds. Later requests descend from retained source geometry only as needed, using an explicit work stack rather than recursive calls. See [index.js](https://github.com/mapbox/geojson-vt/blob/main/src/index.js).
- **C1 evidence beyond the algorithm:** The [edge-case tests](https://github.com/mapbox/geojson-vt/blob/main/test/test-edge-cases.js) provide concrete regression inputs for studying boundary behavior.

### 19. [mapbox/vtzero](https://github.com/mapbox/vtzero)

**Language / role:** C++; MVT decoder and encoder built around lightweight views and builders.

- **C1:** Decoding checks whether declared geometry point counts can fit the encoded byte count, addressing malicious expansion claims. Its documentation also candidly describes limits: duplicate layer names and some unusual protobuf encodings are deliberately not checked or supported.
- **C3:** Decoding normally avoids allocation except for property lookup tables, with explicit discussion of how decoded structures can still exceed input size. These tradeoffs are in [advanced topics](https://github.com/mapbox/vtzero/blob/master/doc/advanced.md).
- **C2:** Layer/feature traversal and geometry handlers let callers choose their own in-memory geometry representation. The [reading guide](https://github.com/mapbox/vtzero/blob/master/doc/reading.md) is the practical entry point.

The documented omissions are part of its educational value; it should not be described as a universal validating decoder.

### 20. [mapbox/mapnik-vector-tile](https://github.com/mapbox/mapnik-vector-tile)

**Language / role:** C++; Mapnik-based vector tile processing library. **Archived** at the time of research; included as a historical implementation reference.

- **C2:** Its processor reuses Mapnik layers and data access while deliberately processing layers independently of rendering styles. Consequently clipping, simplification, fill rules, and polygon-union policy become explicit processor settings. See [vector_tile_processor.hpp](https://github.com/mapbox/mapnik-vector-tile/blob/master/src/vector_tile_processor.hpp).
- **C1:** Encoding and decoding must preserve valid geometry through coordinate transformation and simplification. The [round-trip simplification tests](https://github.com/mapbox/mapnik-vector-tile/blob/master/test/system/round_trip_simplification.cpp) check resulting geometry types and coordinates for points, lines, polygons, and holes.

Study this alongside Mapnik to understand the change from drawing a styled map to exporting reusable tile geometry; it is a separate implementation, not a binding-only repository.

### 21. [maplibre/maplibre-tile-spec](https://github.com/maplibre/maplibre-tile-spec)

**Language / role:** Rust, Java, TypeScript, and C++ implementation areas alongside the MapLibre Tile specification. Counted once as a codec/format project, not merely a standards document.

- **C1:** Versioned frames, column types, null presence, geometry extents, and offsets define interoperability invariants. The [data-model overview](https://github.com/maplibre/maplibre-tile-spec/blob/main/docs/overview.md) distinguishes stable v1 from experimental v2 and explains how unknown frame versions can be skipped.
- **C2 / C3:** Reusable column vectors separate storage encodings from the in-memory model. Contiguous buffers, dictionary and run-based encodings, sampling-based encoding selection, and reduced object materialization address decoder and GPU-upload costs. See the [implementation guide](https://github.com/maplibre/maplibre-tile-spec/blob/main/docs/implementation-guide.md).

Some performance-oriented capabilities are design goals rather than universal implementation guarantees. Experimental v2 should not be represented as having v1's stability.

### 22. [protomaps/PMTiles](https://github.com/protomaps/PMTiles)

**Language / role:** Primarily TypeScript, with Python and integrations; tiled archive format and range-reading implementations.

Study remote random access to tiles when ordinary object storage replaces a tile server.

- **C2 / C3:** The format separates header, root directory, optional leaf directories, metadata, and tile data. The root placement requirement allows an initial request to acquire useful indexing information without downloading the archive. See the [v3 specification](https://github.com/protomaps/PMTiles/blob/main/spec/v3/spec.md).
- **C1:** The JavaScript reader detects inconsistent ETags and unsuitable HTTP range responses, and retries after archive cache invalidation. Its shared-promise cache coordinates concurrent directory/header reads and cancellation. See [js/src/index.ts](https://github.com/protomaps/PMTiles/blob/main/js/src/index.ts).

This entry covers the archive reader and format implementation; the separate Go command-line project is not implicitly counted.

## Tile servers and server-side rasterization

### 23. [maplibre/martin](https://github.com/maplibre/martin)

**Language / role:** Rust; vector tile generation/serving and related archive tooling. The monorepo is counted once.

- **C2:** The HTTP service, reusable `martin-core` source implementations, MBTiles tools, and low-level tile utilities have separate crate responsibilities. Source discovery and resource handling are described in the [architecture guide](https://github.com/maplibre/martin/blob/main/docs/content/architecture.md).
- **C3:** Asynchronous request handling, database connection pools, and tile/resource caching address repeated I/O and request concurrency without making HTTP handlers responsible for every backend detail.
- **C2:** [Composite sources](https://github.com/maplibre/martin/blob/main/docs/content/sources-composite.md) combine multiple datasets through one request, while aliases preserve stable externally used names. This is a useful study of source composition and API continuity.

The guide's throughput language is not an independently verified benchmark; the concrete architecture is the reason for selection.

### 24. [go-spatial/tegola](https://github.com/go-spatial/tegola)

**Language / role:** Go; vector tile server with native geometry processing and database-generated MVT paths.

- **C2 / C3:** Standard providers stream features through cancellable callbacks and allow layers from different data sources to be combined. MVT providers bypass Tegola's geometry processing and encoding, trading that flexibility for database-side generation. See [provider.go](https://github.com/go-spatial/tegola/blob/master/provider/provider.go).
- **C1:** The included [MakeValid design](https://github.com/go-spatial/tegola/blob/master/maths/makevalid/README.md) explains polygon repair through segment splitting, clipping, labeled triangulation, ring stitching, and hole assignment. Winding and shared-edge invariants make it a substantive geometry study.

The repair document describes a particular algorithm in the codebase; provider selection determines which processing path an actual deployment exercises.

### 25. [bbox-services/bbox](https://github.com/bbox-services/bbox)

**Language / role:** Rust; composable spatial-service monorepo. The selected subsystem is `bbox-tile-server`, including connections to the map service.

- **C2:** An asynchronous `TileSource` trait represents vector and raster sources with common tile requests and metadata, backed by database, archive, and WMS implementations. Source-specific errors and datasource pooling stay behind this boundary. See [datasource/mod.rs](https://github.com/bbox-services/bbox/blob/main/bbox-tile-server/src/datasource/mod.rs).
- **C1 / C3:** The tile seeder separates fetching from writing, applies backpressure, and changes concurrency policy for PMTiles output rather than treating every sink identically. A dedicated batch writer handles archive output. See [seed.rs](https://github.com/bbox-services/bbox/blob/main/bbox-tile-server/src/seed.rs).

Useful for comparing a service suite's source/sink composition with a narrowly PostGIS-only server; this selection does not imply uniformly complete support across all BBOX services.

### 26. [CrunchyData/pg_tileserv](https://github.com/CrunchyData/pg_tileserv)

**Language / role:** Go with SQL/PostGIS; deliberately thin dynamic MVT server.

- **C2:** Function layers turn SQL functions into parameterized tile APIs, exposing argument types and defaults through discovery metadata. This supports filtering and custom spatial processing without modifying the Go server. See [function layers](https://github.com/CrunchyData/pg_tileserv/blob/master/hugo/content/usage/function-layers.md).
- **C3:** The same guide explains transforming query bounds into the table's CRS to retain spatial-index use, while transforming selected geometry for MVT output. It also distinguishes `STABLE`, `IMMUTABLE`, and parallel-safe function behavior.
- **C1:** Tile-address validation and XYZ-to-geographic bounds conversion are visible in [tile.go](https://github.com/CrunchyData/pg_tileserv/blob/master/tile.go).

Most geometric encoding work deliberately resides in PostGIS; this repository is valuable for studying that boundary, rather than as an independent geometry kernel.

### 27. [maptiler/tileserver-gl](https://github.com/maptiler/tileserver-gl)

**Language / role:** JavaScript/Node.js; vector tile service and server-side rasterization through MapLibre Native.

Its substantive contribution is renderer orchestration and service behavior rather than another implementation of the underlying GPU engine.

- **C1:** The render path guards against returning a pooled renderer twice, distinguishes releasing a healthy instance from discarding a bad one, and handles acquisition failures. See [serve_rendered.js](https://github.com/maptiler/tileserver-gl/blob/master/src/serve_rendered.js).
- **C3:** Separate renderer pools by scale factor expose the tradeoff between memory and renderer creation latency. Tile margins can prevent clipped labels but require loading additional neighboring data. Both decisions are explained in the [configuration reference](https://github.com/maptiler/tileserver-gl/blob/master/docs/config.rst).

This is a useful study of making a native renderer serve concurrent HTTP requests with bounded resources and explicit failure handling.

## Search coverage and limitations

Discovery used more than six distinct live-web formulations, including browser/WebGL rendering architecture; planet-scale OSM and GeoJSON compilation; Rust/Go PostGIS servers; native/mobile and offline rendering; Mapnik/MapServer labeling; C++ tile codecs; PMTiles and Canvas rendering; newer Rust/wgpu engines; composable tile pipelines; and C#/.NET/Skia mapping. Follow-up searches for streaming, clipping, simplification, and offline label caches increasingly returned already inspected projects, small forks, bindings, and application deployments. The final two additions, Mapsui and libosmscout, broadened the language and offline-rendering coverage enough to justify 27 entries.

Canonical repository identities were checked by opening GitHub pages or reading the public GitHub API. Source-tree indexes were used to verify implementation paths, and every retained project received an additional primary-source read beyond its repository overview. The sources linked beside criteria are practical reading entry points. The GitHub API rate limit was reached during the final additions; their canonical pages and source/documentation pages were verified through web access instead.

The selection avoids counting original Mapbox Tippecanoe alongside its official Felt continuation, or OpenScienceMap VTM alongside the independently evolved Mapsforge fork. The [t-rex repository](https://github.com/t-rex-tileserver/t-rex) explicitly says it is no longer maintained and has been replaced by BBOX; it was therefore excluded in favor of BBOX. Basemap schema/style projects such as OpenMapTiles, general globe/3D visualization engines, GIS applications, and general geometry libraries were not expanded into additional entries. Tangram's native counterpart and other valid renderers are also omitted: this is a diverse selection, not an exhaustive census.

Archived, maintenance-mode, experimental, and legacy-runtime limitations are stated where established. An unarchived repository or recent push is not treated as proof of active support. Historical design documents can lag current code; their limitations are noted where material. No candidate code was executed, dependencies installed, repositories cloned, or performance measurements reproduced. Criterion assignments are grounded engineering judgments from the cited material, and do not claim that every component is uniformly exemplary.
