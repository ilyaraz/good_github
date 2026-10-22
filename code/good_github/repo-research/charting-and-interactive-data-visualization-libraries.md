# Charting and interactive data visualization libraries

Research date: **2026-10-09**.

This report selects **27 GitHub repositories** for studying the engineering of charts and interactive data views: visualization grammars, browser chart engines, streaming renderers, scientific plotting, and native libraries. It includes static charting foundations where their coordinate systems, statistical semantics, or backend abstractions are particularly instructive. Datashader is included as a visualization pipeline used inside interactive systems; deck.gl is included for its reusable data-layer and interaction architecture. Neither is presented as a conventional chart widget library.

Repository identity and category fit were checked against the linked GitHub pages. Each entry also cites material actually opened from project documentation or implementation sources. Criterion assignments are engineering judgments grounded in that material, not certifications of correctness or recommendations that every subsystem is exemplary. Main-branch code and published documentation can describe different versions. No general claim of active maintenance is made from a recent crawl, push, or star count.

**Criteria legend**

- **C1 — Difficult correctness:** invariants, numerical or statistical semantics, concurrency, adversarial inputs, or consequential failure modes.
- **C2 — Reusable abstractions:** substantial components or interfaces supporting multiple visualization use cases.
- **C3 — Performance architecture:** concrete resource or responsiveness constraints addressed through understandable implementation structure.
- **C4 — Sustained evolution:** evidence spanning years together with compatibility work, testing, or deliberate complexity management.

## Declarative grammars and statistical chart construction

### 1. [vega/vega](https://github.com/vega/vega)

**Language / role:** JavaScript; declarative interactive visualization runtime. Relevant monorepo subsystem: `packages/vega-dataflow`, within the larger parser, transform, scenegraph, and rendering system.

Study how a visualization specification becomes an incrementally maintained computation rather than a sequence of imperative redraws. **C1:** the dataflow engine propagates changes in topological order; pulses distinguish added, removed, and modified tuples, while operator parameters can reference other operators. Maintaining those dependencies and change categories is a meaningful correctness problem. **C2:** the engine separates its scheduler, operators, parameters, and pulses from domain-specific transformations, allowing the same runtime to support filtering, aggregation, layout, and visual encoding. The [dataflow package design and source-tree entry point](https://github.com/vega/vega/tree/main/packages/vega-dataflow) explains these boundaries explicitly.

### 2. [vega/vega-lite](https://github.com/vega/vega-lite)

**Language / role:** TypeScript; a higher-level visualization language that compiles to Vega specifications. It has a substantive compiler and interaction semantics, so it is retained separately from Vega.

Study the relationship between concise chart specifications and explicit interaction queries. **C1:** multi-view selections have global, union, and intersection resolution; emptying a selection differs from resetting a selection bound to scales, and aggregation/binning restricts where selections remain meaningful. **C2:** point and interval selections compose with filters, conditional encodings, scale domains, facets, and repeated views. These are reusable language constructs rather than separate event handlers for each chart. The [selection parameter guide](https://vega.github.io/vega-lite/docs/selection.html) is a particularly useful entry point because it documents both semantics and limitations, including nearest-point selection and unsupported mark combinations.

### 3. [observablehq/plot](https://github.com/observablehq/plot)

**Language / role:** JavaScript; a layered grammar for exploratory graphics, with interaction facilities.

Study its separation between transformations in data space and initializers in screen space. **C2:** transforms compose by returning mark options; grouping, binning, normalization, faceting, and derived channels can be reused across marks. **C1:** custom transforms must preserve the relationship between data and facet indexes and avoid mutating inputs; screen-space initializers run after scales exist and may replace channels. These ordering and indexing contracts explain why apparently simple chart transformations need disciplined interfaces. Start with the [transform and initializer contracts](https://observablehq.github.io/plot/features/transforms). A complementary implementation-oriented example is the [changelog's shared GeoJSON clipping paths](https://raw.githubusercontent.com/observablehq/plot/main/CHANGELOG.md), which links clipping semantics to projection and reuse of SVG resources.

### 4. [antvis/G2](https://github.com/antvis/G2)

**Language / role:** TypeScript; a configurable grammar of graphics with pluggable visualization components and rendering engines.

Study both the extension interface and a concrete transform. **C2:** the [Chart API](https://g2.antv.antgroup.com/en/manual/api) exposes component registration and separates chart specification from Canvas, SVG, or WebGL renderer selection. **C1:** the [stackY implementation](https://raw.githubusercontent.com/antvis/G2/v5/src/transform/stackY.ts) groups and orders series, treats positive and negative values separately, handles zero-valued layers, preserves original channels, and identifies stack boundaries for styling. This is useful code for studying the numerical and visual semantics of a grammar operator. The source link deliberately targets the verified `v5` branch; it should not be assumed to describe every historical G2 API.

### 5. [tidyverse/ggplot2](https://github.com/tidyverse/ggplot2)

**Language / role:** R; statistical chart construction through a grammar of graphics. Primarily a charting foundation rather than a built-in interactive dashboard runtime.

Study how statistical computation, geometry, positional adjustments, scales, and facets cooperate without becoming one chart-specific procedure. **C2:** Geom, Stat, and Position are distinct abstractions, coordinated by the internal Layer class. **C1:** the documented build pipeline establishes when aesthetics are evaluated, scale transformations occur, statistics run, computed variables are mapped, positions are adjusted, and missing values are handled. Changing that order can change the meaning of a chart. The [Layer class reference and data-flow diagram](https://ggplot2.tidyverse.org/reference/Layer-class.html) provide an unusually explicit architectural map and link directly to `R/layer.R`. Layer itself is internal and is not the supported extension surface.

## Browser chart engines and reusable chart components

### 6. [chartjs/Chart.js](https://github.com/chartjs/Chart.js)

**Language / role:** JavaScript with TypeScript declarations; Canvas chart engine.

Study a rendering lifecycle that permits extensions while controlling when work occurs. **C2:** [plugin hooks](https://www.chartjs.org/docs/latest/developers/plugins.html) cover initialization, update, scales, drawing, events, and destruction; cancellation and redraw requests have specific contracts. **C3:** the [performance guide](https://www.chartjs.org/docs/latest/general/performance.html) ties optimizations to lifecycle stages: early decimation reduces rendered data, disabled animations permit Path2D caching, and prepared data avoids parsing. It also explains OffscreenCanvas worker rendering, transfer costs, unavailable DOM interactions, and manual resizing. **C1** is visible in the same guide's sorted/unique index preconditions and the limits of moving function-bearing configuration between threads. These are concrete tradeoffs, not a blanket browser performance ranking.

### 7. [apache/echarts](https://github.com/apache/echarts)

**Language / role:** TypeScript/JavaScript; broad interactive browser chart engine built on zrender.

Study the boundary between shared data, series-specific processing, and scheduled rendering. **C2:** [datasets and encodings](https://echarts.apache.org/handbook/en/concepts/dataset/) let multiple series reuse a source and map its dimensions to axes, labels, tooltips, and visual channels. **C3:** the [scheduler implementation](https://raw.githubusercontent.com/apache/echarts/master/src/core/Scheduler.ts) builds per-series task pipelines and distinguishes progressive rendering from incremental data append; thresholds, step sizes, and blocking stages control execution. **C1:** its comments explain why render mode must be detected at a consistent processing stage to avoid incorrect decisions after filtering. This makes ECharts useful for studying how performance policies depend on pipeline invariants.

### 8. [plotly/plotly.js](https://github.com/plotly/plotly.js)

**Language / role:** JavaScript; the underlying interactive chart engine used by Plotly's language integrations.

Study its separation between user trace data, calculated data, and rendering. **C1:** the [scatter calculation implementation](https://raw.githubusercontent.com/plotly/plotly.js/main/src/traces/scatter/calc.js) retains valid positions with missing stacked values, distinguishes zero filling from interpolation, preserves original period coordinates for hover, and sorts calculated points with original-index tie breaking. Those decisions affect both numerical meaning and interaction behavior. **C2:** trace calculation incorporates axis conversion, colorscale calculation, selection, and stacking through separate modules rather than embedding them all in a scatter renderer. The [contributor guide](https://raw.githubusercontent.com/plotly/plotly.js/main/CONTRIBUTING.md) is a second entry point for understanding schema review, browser interaction tests, and image baselines. The Python and R interfaces are not counted again.

### 9. [recharts/recharts](https://github.com/recharts/recharts)

**Language / role:** TypeScript/React; composable SVG chart components.

Study the interaction between React composition, internal chart state, and observable rendering behavior. **C2:** version 3 supports custom components inside charts and moves consumers away from cloned internal state props toward explicit component/hook interfaces. **C1:** the migration documents concrete semantics for nullish error-bar domains, null values in connected areas, deterministic grid-to-axis association, and SVG paint order. These are correctness concerns that arise when a component tree doubles as chart configuration. The [3.0 migration guide](https://github.com/recharts/recharts/wiki/3.0-migration-guide) also describes splitting state into smaller tested units and the consequences of previously exposing internal state. This is an instructive complexity-management case without assuming that every compatibility issue was eliminated.

### 10. [dc-js/dc.js](https://github.com/dc-js/dc.js)

**Language / role:** JavaScript; coordinated multidimensional charts built around D3 and Crossfilter.

Study how a chart library coordinates filtering across views. **C2:** [BaseMixin](https://dc-js.github.io/dc.js/docs/html/BaseMixin.html) supplies chart groups, dimensions, filter handlers, event hooks, and shared redraw behavior. **C1:** filtering is normally a toggle rather than replacement; exact, ranged, and predicate filters have different application paths, and group redraw can wait for an asynchronous commit handler. Correct linked views depend on preserving those distinctions. The [changelog](https://raw.githubusercontent.com/dc-js/dc.js/develop/Changelog.md) records D3 event-signature compatibility work and isolation of compatibility layers. Treat this as an established design worth studying; the reviewed compatibility history is not evidence that its dependency guidance or release cadence is current for a new deployment.

### 11. [d3fc/d3fc](https://github.com/d3fc/d3fc)

**Language / role:** JavaScript; a monorepo of independently usable components for interactive D3 charts. Relevant subsystems: series rendering and discontinuous scales.

Study how to retain access to low-level visualization composition while sharing chart components. **C2:** the [series package](https://github.com/d3fc/d3fc/blob/master/packages/d3fc-series/README.md) provides common scales and value-accessor conventions across SVG, Canvas, and WebGL series, with multi-series composition. **C1:** [discontinuous scales](https://github.com/d3fc/d3fc/tree/master/packages/d3fc-discontinuous-scale) remove intervals such as weekends from an axis. Their mapping and tick policies have observable edge cases: ticks in removed intervals are clamped to a boundary and can overlap. The package documents that limitation rather than pretending that omitting time ranges is merely formatting. Count the monorepo once, not once per package or rendering backend.

## Streaming, financial, and GPU-oriented browser visualization

### 12. [leeoniya/uPlot](https://github.com/leeoniya/uPlot)

**Language / role:** JavaScript; compact Canvas time-series and related chart renderer.

Study a deliberately constrained engine whose performance choices are easy to inspect. **C3:** the [linear path renderer](https://raw.githubusercontent.com/leeoniya/uPlot/master/src/paths/linear.js) switches to pixel-bucket decimation for dense series, accumulates extrema and endpoints, and avoids computing a pixel coordinate for every x value within a bucket. **C1:** the same implementation must preserve gap information, traverse reversed/oriented scales correctly, close fills, and clip bands. This is a useful example of why downsampling cannot simply discard arbitrary samples. **C2:** the repository also exposes pluggable path renderers and hooks for multiple chart forms. Numerical speed comparisons from the README were not treated as independently established benchmark results.

### 13. [tradingview/lightweight-charts](https://github.com/tradingview/lightweight-charts)

**Language / role:** TypeScript; interactive Canvas financial charting.

Study incremental time-axis maintenance alongside a small extension architecture. **C1:** the [data layer](https://raw.githubusercontent.com/tradingview/lightweight-charts/master/src/model/data-layer.ts) maintains shared objects in time-point and series maps, reconstructs sorted time points when necessary, cleans up unused points, and emits changes only for affected series. **C2:** [series primitives](https://tradingview.github.io/lightweight-charts/docs/plugins/series-primitives) separate extension state, coordinate-producing views, and pixel-producing renderers, with attach/detach and autoscale contracts. **C3:** the documentation explicitly connects that split to repeated redraws without redundant recomputation and advises caching frequently invoked autoscale calculations. This is the open-source Lightweight Charts repository, distinct from TradingView's other chart products.

### 14. [visgl/deck.gl](https://github.com/visgl/deck.gl)

**Language / role:** TypeScript/JavaScript and shaders; layered GPU data visualization. Relevant monorepo subsystems: core layer lifecycle and data layers, rather than the Python wrapper alone.

Study how declarative layer replacement can preserve expensive GPU state. **C2:** the [layer lifecycle](https://deck.gl/docs/developer-guide/custom-layers/layer-lifecycle) matches successive layers by identifier and transfers persistent state, with explicit initialization, update, drawing, picking, and finalization hooks. **C3:** the [performance guide](https://deck.gl/docs/developer-guide/performance) explains that data changes cause buffer regeneration and upload, motivating stable data references and custom comparison logic. **C1:** viewport-dependent layers must override default update decisions when screen-space calculations require it; otherwise a legitimate optimization can leave stale results. This is especially useful for scatterplots, spatial aggregates, and linked data views, even though many examples use maps.

## Python scientific and interactive visualization

### 15. [bokeh/bokeh](https://github.com/bokeh/bokeh)

**Language / role:** Python and TypeScript; browser visualization with Python models, BokehJS, and optional server sessions. These are parts of one repository, counted once.

Study the consistency boundary between visualization models and concurrent application work. **C1:** the [server API guide](https://docs.bokeh.org/en/latest/docs/user_guide/server/library.html) specifies that updates run with each session document locked, that different sessions may update concurrently, and that shared data needs an appropriate immutability or synchronization policy. It also distinguishes process-local updates from deployment across multiple workers. **C2:** documents and session update callbacks provide a reusable model boundary for embedding interactive plots in host applications rather than requiring each plot type to invent synchronization. The guide's lifecycle and embedding examples are useful architectural entry points; its current ASGI facilities should not be projected backward onto older Bokeh versions.

### 16. [holoviz/holoviews](https://github.com/holoviz/holoviews)

**Language / role:** Python; dimensioned data objects, compositional plots, and reactive exploration across plotting backends.

Study why a high-level visualization interface needs its own substantial execution model. **C2:** [streams](https://holoviews.org/user_guide/Responding_to_Events.html) connect named parameters and events to DynamicMap callbacks; dimensions, layouts, and overlays provide reusable composition. **C3:** the [live-data guide](https://holoviews.org/user_guide/Live_Data.html) explains how eager HoloMaps can exhaust Python or browser memory and how DynamicMap computes elements on demand. Its bounded cache trades memory for recomputation and can capture explored states for export. **C1:** the guide explicitly notes that interaction-dependent cache contents are not a controlled sampling of parameter space. This is materially more than a generated wrapper around Bokeh or Matplotlib.

### 17. [holoviz/datashader](https://github.com/holoviz/datashader)

**Language / role:** Python; rasterization and aggregation for large datasets, often embedded in interactive plotting systems.

Study an alternative to drawing one visual object per input record. **C2:** the [pipeline guide](https://datashader.org/getting_started/Pipeline.html) separates projection, aggregation, transformation, colormapping, and embedding, with glyph and reduction choices independent of the final display. **C3:** aggregation compresses the input into a fixed-size grid; subsequent stages operate on that grid rather than on the full dataset. The same architecture accommodates different data containers and CPU/GPU-oriented input ecosystems. The engineering lesson is the separation of data-size-dependent work from image-size-dependent work, not a claim of unlimited throughput. Datashader supplies the data-to-image machinery; interaction and application presentation commonly come from companion libraries.

### 18. [matplotlib/matplotlib](https://github.com/matplotlib/matplotlib)

**Language / role:** Python with C/C++ components; static, animated, and interactive scientific plotting.

Study coordinate transformations as reusable infrastructure rather than ad hoc arithmetic in each plot type. **C2:** the [transformations tutorial](https://matplotlib.org/stable/users/explain/artists/transforms_tutorial.html) distinguishes data, axes, figure, display, and physical coordinates, and shows how artists compose these spaces. **C1:** blended transforms allow one coordinate to follow data while another follows the axes, but require separable transformations; the technique cannot be applied unchanged to polar coordinates. Panning, zooming, resizing, and annotation placement all depend on respecting those distinctions. The tutorial is a useful route into transform composition and inversion, including the difference between a mathematically valid transform and one suitable for a particular interactive display operation.

### 19. [pyqtgraph/pyqtgraph](https://github.com/pyqtgraph/pyqtgraph)

**Language / role:** Python/NumPy/Qt; scientific plots and visualization widgets for interactive applications.

Study performance mechanisms that expose their accuracy and failure tradeoffs. **C3:** [PlotDataItem](https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotdataitem.html) supports clipping to the visible x range and automatic downsampling with subsample, mean, and peak-preserving methods. **C1:** skipping finite-value checks can fail when NaN or infinity occurs; dynamic-range limiting works around incorrect off-screen rejection in Qt under extreme magnification, with hysteresis to avoid constant recalculation. **C2:** PlotDataItem coordinates separate curve and scatter objects behind a shared data interface. The documented tradeoffs make it a strong study target for scientific instruments and rapidly changing plots, without needing to accept comparative speed claims from the README.

### 20. [vispy/vispy](https://github.com/vispy/vispy)

**Language / role:** Python and GLSL; GPU-based interactive scientific visualization, with scene and visual abstractions.

Study how one transformation abstraction serves CPU-side coordinate operations and generated shader code. **C2:** the repository separates application/window integration, the gloo OpenGL interface, visuals, transforms, and scene organization. The [transform API](https://vispy.org/api/vispy.visuals.transforms.html) documents forward/inverse operations and `ChainTransform`, whose GLSL functions are assembled through shader function chains. **C1:** composition order is explicit—the last listed transform is applied first—and nonlinear transforms require corresponding inverse semantics rather than interchangeable matrix multiplication. This is useful for understanding consistency between rendered geometry and interactive coordinate queries. The entry concerns the verified `vispy/vispy` implementation; it does not conflate it with separately described experimental successor architectures.

## Julia, systems languages, and native charting

### 21. [MakieOrg/Makie.jl](https://github.com/MakieOrg/Makie.jl)

**Language / role:** Julia and shaders; interactive scientific plotting with multiple backends. Relevant monorepo subsystems include Makie, ComputePipeline, GLMakie, WGLMakie, and CairoMakie; they count as one repository.

Study coordinated reactive updates across plotting computations. **C1:** the [observable guide](https://docs.makie.org/stable/explanations/observables) demonstrates that independently changing x and y can trigger duplicate computation or temporary shape mismatches. **C2:** the [compute pipeline](https://docs.makie.org/stable/explanations/compute-pipeline) expresses inputs and computations as graph nodes and edges, including graphs connected through parent-owned outputs. **C3:** grouped updates mark dependents dirty and defer calculation until values are requested, skipping redundant work. Bridging outputs back to push-style observables changes that laziness. Together these documents show both the failure motivating an architectural change and the tradeoffs of the replacement.

### 22. [plotters-rs/plotters](https://github.com/plotters-rs/plotters)

**Language / role:** Rust; plotting for native and WASM environments, with bitmap, vector, and GUI-oriented backend integration.

Study typed coordinate and rendering abstractions. **C2:** [`CoordTranslate`](https://docs.rs/plotters/latest/plotters/coord/trait.CoordTranslate.html) associates a logical input type with translation into backend coordinates; Cartesian implementations compose ranged coordinate types. The repository separates drawing areas, elements, chart context, and backend responsibilities. **C1:** the [numeric coordinate implementation](https://raw.githubusercontent.com/plotters-rs/plotters/master/plotters/src/coord/ranged1d/types/numeric.rs) handles degenerate ranges, reversed pixel ranges, finite/infinite mapping behavior, tick granularity, and checked conversion of discrete indexes. These are substantive numerical edge cases to inspect rather than evidence that all possible numeric inputs are supported. Some backend implementations live in separate repositories; they are not counted as additional entries here.

### 23. [epezent/implot](https://github.com/epezent/implot)

**Language / role:** C++; immediate-mode interactive plotting for Dear ImGui applications.

Study efficient plotting inside an application's existing frame loop. **C3:** [`implot_items.cpp`](https://raw.githubusercontent.com/epezent/implot/master/implot_items.cpp) uses templated primitive renderers, bulk draw-list reservation, culling, and reuse of reserved capacity. **C1:** its bulk rendering path limits reservations according to the draw-index type, starts new draw commands when needed, and accounts for culled primitives before releasing unused reservations. This is a compact example of performance code constrained by buffer and indexing invariants. **C2:** data getters and striding support different layouts without forcing all callers into one container representation. The project targets interactive program visualization; its README explicitly distinguishes that role from publication-quality figure export.

### 24. [ScottPlot/ScottPlot](https://github.com/ScottPlot/ScottPlot)

**Language / role:** C#; interactive .NET plotting across several GUI and non-GUI hosts. Relevant subsystem: ScottPlot 5's rendering pipeline.

Study an extensible sequence of rendering operations. **C2:** [`RenderManager`](https://raw.githubusercontent.com/ScottPlot/ScottPlot/main/src/ScottPlot5/ScottPlot5/Rendering/RenderManager.cs) exposes an ordered list of render actions covering autoscaling, layout, ticks, plottables, panels, legends, and overlays. **C1:** it provides a pre-render synchronization contract for concurrent data modification, bounds repeated renders caused by axis changes, and includes a mechanism to suppress axis-change event loops. Canvas state is saved and restored around actions. **C3:** per-action timings make the pipeline's costs inspectable. These mechanisms deserve examination together; they do not amount to an assertion that arbitrary application callbacks are thread-safe. At research time, the repository also stated that anonymous code contributions were restricted.

### 25. [ChartsOrg/Charts](https://github.com/ChartsOrg/Charts)

**Language / role:** Swift; native Apple-platform chart library, distributed under the DGCharts name. This is a substantive Swift implementation originating from MPAndroidChart, not Apple's Swift Charts or a generated binding.

Study the coordinate layer beneath native gestures, animation, and chart geometry. **C1:** [`Transformer.swift`](https://raw.githubusercontent.com/ChartsOrg/Charts/master/Source/Charts/Utils/Transformer.swift) fixes the composition order of value, touch, and offset transforms, supports inverted axes and inverse touch mapping, and handles infinite scale factors from degenerate ranges. **C4:** the [historical changelog](https://raw.githubusercontent.com/ChartsOrg/Charts/master/CHANGELOG.md) spans Swift/Xcode compatibility changes in 2018 through the 2021 migration to a different snapshot-testing framework and bounds-check fixes. The repository page separately explains the later DGCharts rename to avoid a naming conflict. This supports studying sustained compatibility and testing work; the older changelog is not presented as proof of current release cadence.

### 26. [jfree/jfreechart](https://github.com/jfree/jfreechart)

**Language / role:** Java; general charting for desktop and server-side use, with separate JavaFX integration.

Study a traditional object-oriented chart engine with explicit dataset, axis, plot, and renderer boundaries. **C2:** [`XYPlot`](https://raw.githubusercontent.com/jfree/jfreechart/master/src/main/java/org/jfree/chart/plot/XYPlot.java) accepts the `XYDataset` interface, delegates drawing to `XYItemRenderer`, maps datasets to axes, and implements pan/zoom behavior. **C4:** the repository's [migration notes and release history](https://github.com/jfree/jfreechart#migration) document years of fixes and restructuring: integrating JCommon, extracting JavaFX/SWT components, changing Java requirements, and removing the complex, unreliable `SegmentedTimeline`. The explicit explanation for removing troublesome functionality is particularly useful evidence of complexity management. The core repository is counted once; demo projects and platform adapters are not separate selections.

### 27. [gonum/plot](https://github.com/gonum/plot)

**Language / role:** Go; chart construction and portable drawing infrastructure, primarily for generated plots.

Study small interfaces coupled to substantive axis and layout algorithms. **C2:** the repository separates plot layout, standard plotters, convenience helpers, and vector-graphics backends; the [plotter API](https://pkg.go.dev/gonum.org/v1/plot/plotter) shows reusable data-range and drawing interfaces, including invalid-data errors. **C1:** [`labelling.go`](https://raw.githubusercontent.com/gonum/plot/master/labelling.go) implements the Talbot–Lin–Hanrahan tick-label algorithm, balancing coverage, density, simplicity, and legibility while handling range-containment constraints and floating-point tolerances. This offers more numerical depth than a collection of chart examples. Gonum identifies this repository as the official fork/successor of Plotinum; the predecessor is not listed again as an independent project.

## Coverage, search process, and limitations

Discovery used more than six distinct query formulations and continued with targeted source searches. The principal angles were:

1. Visualization grammars, reactive dataflow, compilation, and selection semantics.
2. Canvas/WebGL browser engines, decimation, progressive rendering, and streaming time series.
3. Coordinated charts, Crossfilter, reusable D3 components, and layer lifecycles.
4. Python scientific plotting, Qt widgets, GPU visuals, server sessions, and large-data rasterization.
5. Julia reactive plotting and Rust typed coordinate/backend interfaces.
6. C++ immediate-mode plotting and C# rendering pipelines.
7. R statistical grammars, Go axis algorithms, and Java desktop chart architecture.
8. Swift/Android chart families and a final scan of Flutter/Compose libraries and additional time-series libraries.

Late searches surfaced D3FC, Dygraphs, FL Chart, and Vico, alongside many already-covered engines, wrappers, demos, and comparison lists. D3FC was added because its cross-renderer composition and discontinuous-scale semantics supplied distinct study material. The other late candidates were not fully verified to the same depth and are not silently treated as rejected on quality grounds. Coverage is broad but not exhaustive, with lighter treatment of mobile-first frameworks and no attempt to enumerate every D3 primitive package.

The selection excludes tutorial/demo-only repositories, awesome lists, generated language wrappers without independently examined machinery, hosted dashboard products, general-purpose graphics engines, and standalone network-analysis or GIS applications. Closely related repositories were kept separately only when they implement a distinct substantial layer, such as Vega-Lite's language over Vega's runtime or HoloViews' dynamic composition over plotting backends. Monorepos and backend families were counted once. No retained project is represented as an official GitHub mirror of development hosted elsewhere, and no archived repository is intentionally presented as an active project.

All evidence is read-only repository/documentation research. No candidate was cloned, installed, executed, or benchmarked. Some URLs serve moving branches or development documentation, and older changelogs can lag release pages; historical claims are limited to the periods actually supported. A few attempted documentation or source URLs were inaccessible through the browser tool, so entries use successfully opened alternatives. The final list is a source-reading guide, not a uniform assessment of maintenance health, licensing suitability, API stability, or measured performance.
