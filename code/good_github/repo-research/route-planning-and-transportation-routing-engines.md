# Route planning and transportation routing engines

Research date: **2026-10-09**.

This report selects **25 GitHub repositories** implementing transportation pathfinding, timetable-based journey planning, geographic network analysis, or vehicle route optimization. It includes server engines, embeddable libraries, database extensions, and research implementations. Fleet optimization is included because deciding vehicle assignments and visit order is a distinct routing layer above road-network shortest paths. Generic graph libraries, routing API clients, map frontends, and network-packet routers are outside the scope.

Criteria are engineering-study judgments grounded in the linked material, not certifications of correctness or production suitability:

- **C1 — Difficult correctness:** meaningful invariants, concurrency, numerical semantics, unusual inputs, or failure modes.
- **C2 — Reusable abstractions:** substantial models and interfaces supporting multiple routing applications or variants.
- **C3 — Performance with structure:** concrete strategies for time, memory, or throughput constraints, with identifiable architectural boundaries.
- **C4 — Sustained evolution:** evidence of changes across years together with compatibility management, testing, or deliberate control of complexity.

Repository identity, default branch, fork status, and archive status were checked through GitHub's repository API. None of the selected repositories was marked archived at inspection time; that does **not** establish active maintenance. Historical and compatibility limitations are called out below. Source links generally track the inspected default branch and may change after this date.

## Road-network engines and embeddable routing cores

### 1. [Project-OSRM/osrm-backend](https://github.com/Project-OSRM/osrm-backend)

**Language / role:** C++ routing engine with Lua transport profiles; HTTP and library interfaces.

Study the boundary between interpreting OpenStreetMap, preparing a graph, and answering routes, matrices, and map-matching requests. The repository describes separate contraction-hierarchy and multi-level Dijkstra preprocessing pipelines. Its profile model also distinguishes the optimization weight from estimated travel time, an important distinction when preferring a road without falsifying its expected speed.

- **C1:** The executable scenarios cover overlapping node and multiple-via-way turn restrictions, including conditional restrictions with explicit timestamps and time zones. These are substantially harder than forbidding an individual edge. [Turn-restriction scenarios](https://github.com/Project-OSRM/osrm-backend/blob/master/features/car/multi_via_restrictions.feature).
- **C2 / C3:** Lua callbacks separately process nodes, ways, turns, and segments; they execute during graph extraction, making the flexibility-versus-preprocessing boundary explicit. Profile API versions and reusable tag handlers keep mode-specific semantics out of the query algorithms. [Profile architecture and weight semantics](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/profiles.md).

### 2. [graphhopper/graphhopper](https://github.com/graphhopper/graphhopper)

**Language / role:** Java road-routing library and standalone server.

An especially useful study is how a route can begin in the middle of a road without modifying the shared base graph. `QueryGraph` adds virtual nodes and edges through a per-request overlay while continuing to implement the graph interface used by routing algorithms.

- **C1 / C2:** The overlay documents its directed virtual-edge representation and isolates query changes for concurrent use. Snapping, graph traversal, turn-cost storage, and edge weighting meet at a concrete reusable abstraction. [QueryGraph implementation](https://github.com/graphhopper/graphhopper/blob/master/core/src/main/java/com/graphhopper/routing/querygraph/QueryGraph.java).
- **C4:** The changelog records dated 2024 and 2025 releases, migration-relevant profile and storage changes, and fixes to overlapping turn restrictions. It explicitly separates unreleased changes, including numerical weight and distance representation changes, from released behavior. [Changelog](https://github.com/graphhopper/graphhopper/blob/master/CHANGELOG.md).

### 3. [valhalla/valhalla](https://github.com/valhalla/valhalla)

**Language / role:** C++ tiled road and multimodal routing engine.

Valhalla is useful for comparing runtime cost customization with engines that bake more policy into preprocessing. Its architecture separates tiled graph access, path search, costing, map matching, and maneuver generation; the path-search documentation explains how Thor and Sif cooperate.

- **C1:** Reverse traversal complicates turn restrictions, transition costs, and the meeting condition of bidirectional A*. The documentation also explains why a heuristic must underestimate the selected costing model and why directed edges, rather than only nodes, receive labels. [Path algorithm design](https://github.com/valhalla/valhalla/blob/master/docs/docs/contributing/architecture/thor/path-algorithm.md).
- **C2 / C3:** Runtime costing uses attributes stored in graph tiles; road hierarchies and shortcuts reduce the explored network. Walking and cycling remain on the local hierarchy, illustrating that performance policy depends on the transport mode. The same [design document](https://github.com/valhalla/valhalla/blob/master/docs/docs/contributing/architecture/thor/path-algorithm.md) is the best starting point; the [repository overview](https://github.com/valhalla/valhalla#organization) maps the surrounding modules.

### 4. [GIScience/openrouteservice](https://github.com/GIScience/openrouteservice)

**Language / role:** Java routing and accessibility service built on GraphHopper, with substantive routing extensions.

This deserves a separate entry from GraphHopper because its repository contains additional graph preparation, restriction handling, isochrone construction, and service orchestration. It is not merely an HTTP wrapper. The README also distinguishes services implemented here from independently hosted tools such as VROOM and Pelias.

- **C1:** Core preparation explicitly excludes restriction-sensitive nodes from contraction, uses direction-aware filtering, and checks graph-size and turn-cost prerequisites. This makes preservation of request-sensitive behavior a visible graph invariant. [PrepareCore](https://github.com/GIScience/openrouteservice/blob/main/ors-engine/src/main/java/org/heigit/ors/routing/graphhopper/extensions/core/PrepareCore.java).
- **C2 / C3:** Its partially contracted core keeps selected graph regions available for flexible routing while accelerating the rest. The same implementation separates restriction filters, adjusted weighting, preparation graph, contractor, and an updateable priority queue. [Service and repository scope](https://github.com/GIScience/openrouteservice/blob/main/README.md) provides the broader context.

### 5. [abrensch/brouter](https://github.com/abrensch/brouter)

**Language / role:** Java offline router, Android integration, and server; particularly relevant to cycling and elevation-aware routing.

Study a routing-specific expression language and compact map format together. The profile language has separate global, way, and node contexts, while encoded tag values are interpreted through a versioned lookup table.

- **C1:** The developer guide states that `costfactor` must be at least one for the search cutoff logic to remain valid. It also explains elevation-noise buffering and the distinction between inaccessible ways and ways retained for instruction generation. [Profile semantics and technical constraints](https://github.com/abrensch/brouter/blob/master/docs/developers/profile_developers_guide.md).
- **C2 / C3:** The same profile system supports different modes and preferences, while binary `rd5` segments and omission of unused tags reduce storage and processing work. Lookup-table compatibility rules explain why append-only tag/value numbering matters. Start with the [profile guide](https://github.com/abrensch/brouter/blob/master/docs/developers/profile_developers_guide.md) and [deployment/data overview](https://github.com/abrensch/brouter/blob/master/README.md).

### 6. [RoutingKit/RoutingKit](https://github.com/RoutingKit/RoutingKit)

**Language / role:** C++ route-planning library, particularly customizable contraction hierarchies (CCH).

This is a focused alternative to reading a complete routing server. Its CCH interface separates topology preprocessing, metric customization, and query state, making the tradeoffs around changing traffic weights unusually explicit.

- **C1:** Metrics and queries retain references to other objects; the documentation specifies their lifetime requirements and prohibits querying changed weights before recustomization. Parallel customization has a documented sharing boundary: one helper may customize separate metrics concurrently. [CCH API and ownership rules](https://github.com/RoutingKit/RoutingKit/blob/master/doc/CustomizableContractionHierarchy.md).
- **C2 / C3:** Weight-independent preprocessing can be reused across different cost metrics. Full, parallel, partial, and perfect customization expose different update/query tradeoffs through distinct objects, rather than one opaque optimization switch. The [same guide](https://github.com/RoutingKit/RoutingKit/blob/master/doc/CustomizableContractionHierarchy.md) includes concrete usage examples and index-ordering considerations.

### 7. [itinero/routing](https://github.com/itinero/routing)

**Language / role:** C#/.NET road-routing core, including routing matrices and lower-resource deployments.

Study the older Itinero core as an embeddable .NET implementation. Its contracted edge-based search combines a generic weight representation with graph-specific path and restriction handling.

- **C1:** Forward and backward searches retain multiple incoming edge paths at a vertex, consult restrictions, and use explicit queue bounds to terminate. Treating every visit to a vertex as equivalent would lose the history needed for edge-based restrictions. [Contracted bidirectional search](https://github.com/itinero/routing/blob/develop/src/Itinero/Algorithms/Contracted/EdgeBased/BidirectionalDykstra.cs).
- **C2:** `WeightHandler<T>`, `EdgePath<T>`, a directed graph, source/target collections, and a restriction callback separate cost algebra from traversal. The [README](https://github.com/itinero/routing/blob/develop/README.md) describes use with OSM or other road networks, point routes, matrices, and instructions.

**Status limitation:** GitHub reported the last repository push as February 2024. This entry is a study of this specific core, not a claim about current Itinero development or support. [Repository metadata](https://api.github.com/repos/itinero/routing).

### 8. [Framstag/libosmscout](https://github.com/Framstag/libosmscout)

**Language / role:** C++ offline mapping library; the relevant subsystem is `libosmscout` routing, not its rendering demos.

Study how an offline application library separates route calculation, storage access, profile policy, route geometry, and route descriptions. The service interface is parameterized by routing state and explicitly identifies databases and offsets, allowing the search layer to work with different storage arrangements.

- **C1:** Routing policy distinguishes forward/backward access, incoming/outgoing path costs, U-turn costs, heuristic estimates, and actual travel time. Speed handling combines surface grade, road maximum speed, and vehicle maximum speed—distinct numerical inputs that must agree with the selected profile. [RoutingProfile](https://github.com/Framstag/libosmscout/blob/master/libosmscout/include/osmscout/routing/RoutingProfile.h).
- **C2:** The service delegates profile and database operations through virtual methods while returning distinct results for routes, points, ways, and descriptions. This is useful for studying an engine embedded in an application rather than deployed exclusively as a server. [AbstractRoutingService](https://github.com/Framstag/libosmscout/blob/master/libosmscout/include/osmscout/routing/AbstractRoutingService.h).

## Database routing, geographic analysis, and traffic assignment

### 9. [pgRouting/pgrouting](https://github.com/pgRouting/pgrouting)

**Language / role:** C/C++ and SQL PostgreSQL extension for spatial routing and network analysis.

Study the contract between relational input and graph algorithms. Callers supply an edge-producing SQL query, then request one-to-one, one-to-many, many-to-many, or selected origin/destination combinations.

- **C1:** The Dijkstra family defines directed and reverse-cost semantics, treats negative costs as absent edges, and distinguishes missing paths from zero aggregate cost for identical endpoints. Duplicated endpoints are eliminated. These conventions are part of the public result contract, not just implementation details. [Dijkstra family semantics](https://github.com/pgRouting/pgrouting/blob/develop/doc/dijkstra/dijkstra-family.rst).
- **C2:** A common SQL-facing graph representation supports path, cost, matrix, catchment, via-route, and nearest-vertex operations. The [Dijkstra API](https://github.com/pgRouting/pgrouting/blob/develop/doc/dijkstra/pgr_dijkstra.rst) also documents how signatures and output columns changed across versions, making it useful for studying extension API evolution.

### 10. [vlarmet/cppRouting](https://github.com/vlarmet/cppRouting)

**Language / role:** R package with C++ algorithms and RcppParallel; road-network routing, accessibility analysis, and traffic assignment.

The distinctive subject here is repeated routing inside transport analysis: distance matrices, reachability, demand assignment, and congestion-dependent user equilibrium. The implementation is substantive C++, not simply an R client for a remote engine.

- **C1:** Cross-implementation regression tests compare ordinary, contracted, customizable-contracted, and simplified graphs. They also compare matrix algorithms and verify the relationship between reconstructed paths and their costs. [Consistency tests](https://github.com/vlarmet/cppRouting/blob/master/tests/testthat/test-consistency.R).
- **C2 / C3:** The documented interfaces share a graph across routing and traffic assignment. Algorithm selection depends on sparse pair queries versus dense matrices; contraction hierarchies, PHAST, simplification, and parallel execution address different workloads. The guide also explains the units and admissibility requirements for A* heuristics. [Architecture and usage guide](https://github.com/vlarmet/cppRouting/blob/master/README.md).

### 11. [connor-makowski/scgraph](https://github.com/connor-makowski/scgraph)

**Language / role:** Python with optional C++ acceleration; geographic and supply-chain routing over road, rail, maritime, and custom networks.

Study the extra modeling layer between arbitrary coordinates and a sparse transport graph. This is particularly useful for logistics distance estimation across multiple network types. It should not be confused with a vessel navigation system or a timetable-aware rail journey planner.

- **C1 / C2:** `GeoGraph` distinguishes the penalty used to select an off-network connection from the factor used to report its length. It exposes connection policies, coordinate formats, units, and pluggable algorithms, and documents restrictions on using cached or hierarchical queries with those policies. [GeoGraph implementation and API](https://github.com/connor-makowski/scgraph/blob/main/scgraph/geograph.py).
- **C3:** The contraction-hierarchy implementation separates persistence, preprocessing, witness searches, shortcut representation, and queries. Its ordering heuristic uses edge difference and contracted neighbors, with cached shortcut calculations. [Contraction hierarchies](https://github.com/connor-makowski/scgraph/blob/main/scgraph/contraction_hierarchies.py). The repository's geographic datasets include maritime and rail networks; their route quality still depends on the underlying graph and connection assumptions.

## Public transport and multimodal journey planning

### 12. [opentripplanner/OpenTripPlanner](https://github.com/opentripplanner/OpenTripPlanner)

**Language / role:** Java multimodal trip planner; focus on the OTP2 RAPTOR subsystem and its adapters.

Study a large application that deliberately isolates its most sensitive routing component. OTP supplies transit data through a service-provider interface and maps requests and results at the boundary rather than coupling RAPTOR directly to the rest of the application.

- **C1:** Multi-criteria range routing retains alternatives across arrival time, transfers, duration, and generalized cost. Its design notes explain both the search-window boundary of optimality and the potential state explosion from additional independent criteria. [RAPTOR design](https://github.com/opentripplanner/OpenTripPlanner/blob/dev-2.x/raptor/router/src/main/java/org/opentripplanner/raptor/package.md).
- **C2 / C3 / C4:** The architecture documents more than fifteen years of development, decision records, isolated routing interfaces, required before/after speed tests, and a copy-on-write transaction framework for consistent read snapshots across repositories. These are concrete complexity-management and concurrency mechanisms, not merely evidence of repository age. [Architecture index](https://github.com/opentripplanner/OpenTripPlanner/blob/dev-2.x/ARCHITECTURE.md).

### 13. [conveyal/r5](https://github.com/conveyal/r5)

**Language / role:** Java multimodal routing and transportation-accessibility analysis engine.

R5 is especially useful for one-to-many analysis over a departure-time window and for hypothetical transit scenarios. Its treatment of frequency-based services makes it different from a conventional single-departure journey planner.

- **C1:** `FastRaptorWorker` combines scheduled searches with randomized frequency schedules. Its comments explain why paths may be shared across scheduled departure iterations but not across Monte Carlo draws, and warn about integer overflow at the unreachable sentinel. [FastRaptorWorker](https://github.com/conveyal/r5/blob/dev/src/main/java/com/conveyal/r5/profile/FastRaptorWorker.java).
- **C3:** Reused range-search state, date/mode-prefiltered patterns, selective path retention, and separate stop-to-destination propagation address repeated analytical queries. The [README](https://github.com/conveyal/r5/blob/dev/README.md) explains the scenario-patching and accessibility workload.

**Compatibility limitation:** The project explicitly does not promise a stable API/SDK for third-party integrations. The source also notes an overtaking-related optimality limitation; the engineering interest here includes understanding those boundaries.

### 14. [hove-io/navitia](https://github.com/hove-io/navitia)

**Language / role:** C++ computation core, Python web layer, and PostgreSQL preprocessing; public-transport journey planning.

**Historical public version:** The repository's [README](https://github.com/hove-io/navitia/blob/dev/readme.rst) announces restricted access for a new Navitia version while retaining the historical open version. A recent push must not be interpreted as evidence that this repository represents all current product development. Its substantive public implementation remains available for study.

- **C1:** Journey-pattern grouping requires compatible stop sequences without overtaking. The routing design handles local travel restrictions and explains why stay-seated behavior and walking objectives can be suboptimal. [Routing algorithm document](https://github.com/hove-io/navitia/blob/dev/documentation/rfc/doc-routing-algorithm.md).
- **C2 / C3:** A first RAPTOR pass minimizes arrival time and transfers; reverse passes improve departure time, using bounds from the first pass and dominance checks to avoid unnecessary work. The README separately identifies Kraken, Jörmungandr, and preprocessing, with protocol-buffer messages over ZMQ between computation and web layers.

### 15. [motis-project/motis](https://github.com/motis-project/motis)

**Language / role:** C++ multimodal platform combining street routing, transit, shared mobility, and real-time information.

Study the integration layer that turns several transport models into an end-to-end journey. MOTIS uses separately developed routing cores; its own contribution includes access/egress construction, mode handling, live mobility data, and API orchestration. The next entry covers Nigiri's internal timetable engine, so these entries represent different layers, not two independent implementations of the same core.

- **C1:** The routing endpoint validates offset durations against their internal representation, expands parent stations to routable child stops, and constructs time-dependent wheelchair access paths using elevator information. [Routing endpoint implementation](https://github.com/motis-project/motis/blob/master/src/endpoints/routing.cc).
- **C2:** Street-mode profiles, fixed and time-dependent offsets, sharing-provider filters, and transit queries are explicit components. The [repository overview](https://github.com/motis-project/motis/blob/master/README.md) documents OSM, timetable, real-time, and GBFS inputs, making it useful for studying cross-format integration rather than only shortest-path search.

### 16. [motis-project/nigiri](https://github.com/motis-project/nigiri)

**Language / role:** C++ public-transport routing core used by MOTIS.

Nigiri is an unusually direct study of timetable representation. It distinguishes externally identified trips from internal transports and groups transports into routes that allow later departures to be pruned safely.

- **C1:** Time-zone conversion may split one trip into multiple transports around daylight-saving changes and midnight. Route grouping must change when adding a new optimization criterion, or discarding later departures may become incorrect. Stay-seated trips are concatenated to avoid counting a spurious transfer. [Data structures and timetable invariants](https://github.com/motis-project/nigiri/blob/master/README.md).
- **C2 / C3:** Strong index types, compact vector structures, serialization-friendly storage, and reusable search state support a data-oriented core. The RAPTOR implementation specializes by direction, real-time mode, vias, and query type; it explicitly disables pruning where time-dependent footpaths invalidate the bound. [RAPTOR implementation](https://github.com/motis-project/nigiri/blob/master/include/nigiri/routing/raptor/raptor.h).

### 17. [transnetlab/transit-routing](https://github.com/transnetlab/transit-routing)

**Language / role:** Python research implementations of public-transit routing algorithms.

Useful for comparing algorithm families with less application scaffolding: RAPTOR, trip-based routing, connection scanning, transfer patterns, and partitioned variants. The repository associates the implementations with research publications and provides a Switzerland case study. It is a research collection, not a claim of a complete production service.

- **C1:** The standard RAPTOR code makes round-indexed arrival labels, best-known bounds, change times, footpath propagation, and itinerary predecessors visible. It explicitly assumes equal arrival/departure times in one boarding decision—a modeling assumption readers should examine. [Standard RAPTOR](https://github.com/transnetlab/transit-routing/blob/main/Algorithms/RAPTOR/std_raptor.py).
- **C2:** Preprocessed route/stop, timetable, footpath, and stop-index dictionaries form reusable inputs across the algorithm suite. The [algorithm catalog](https://github.com/transnetlab/transit-routing/blob/main/README.md) distinguishes implemented variants from those still awaiting an update rather than presenting every listed algorithm as finished.

**Status limitation:** Repository metadata showed no push after May 2024; no current maintenance claim is made. [Metadata](https://api.github.com/repos/transnetlab/transit-routing).

### 18. [planarnetwork/raptor](https://github.com/planarnetwork/raptor)

**Language / role:** TypeScript RAPTOR journey-planning library for Node and browser-worker use.

Study a smaller, accessible timetable engine with a clear separation between timetable representation, trip scanning, route queues, query forms, and result construction. It supports range queries and worker pools; its README explicitly distinguishes result filtering from implementing multi-criteria RAPTOR itself.

- **C1:** The scan respects pickup/drop-off rules, interchange time, and transfer-validity intervals. The public model also checks service calendars and rejects ambiguous station codes or dates outside the timetable's validity period. [Scan implementation](https://github.com/planarnetwork/raptor/blob/master/src/raptor/RaptorAlgorithm.ts) and [API/model documentation](https://github.com/planarnetwork/raptor/blob/master/README.md).
- **C2 / C3:** A reused synchronous route cursor and queued marked routes keep the inner search focused; separate range and pooled-query abstractions address batch latency and throughput. Worker documentation explains what is copied across the boundary and why service methods remain inside the worker.

### 19. [bliksemlabs/rrrr](https://github.com/bliksemlabs/rrrr)

**Language / role:** C RAPTOR engine for the Bliksem journey planner; historical implementation.

This is a useful small-systems counterpoint to JVM transit engines. Workers map a shared read-only timetable file and maintain their own permanent search buffers. The README contains both implemented design and future intentions; in particular, its planned mobile and real-time capabilities should not all be treated as completed features.

- **C1:** Compact schedule-time representation, service-day/DST conventions, sentinel values, and careful reinitialization of transfer state expose correctness costs hidden by higher-level languages. The router explains why initial walking labels must be reset without discarding best times that prevent circuitous journeys. [Router implementation](https://github.com/bliksemlabs/rrrr/blob/master/router.c).
- **C3:** Memory-mapped timetable sharing, per-process scratch state, bitsets of changed stops/routes, and avoiding allocation in inner loops form a coherent memory/throughput architecture. [Design overview](https://github.com/bliksemlabs/rrrr/blob/master/README.md).

**Status limitation:** GitHub did not mark it archived, but reported the last push in December 2020. Treat it as historical source, not a currently supported deployment recommendation. [Metadata](https://api.github.com/repos/bliksemlabs/rrrr).

## Fleet routing and visit-order optimization

### 20. [VROOM-Project/vroom](https://github.com/VROOM-Project/vroom)

**Language / role:** C++ vehicle-routing optimizer using road-engine matrices or custom cost matrices.

Study how local search is made compatible with rich delivery constraints. VROOM distinguishes single jobs from paired shipments, and separates route state from the operators that change routes. It is complementary to OSRM, Valhalla, or openrouteservice, not a replacement for their road graph construction.

- **C1:** `TWRoute` maintains forward earliest times, backward latest times, break positions, action times, and load margins. It explicitly checks removals as well as insertions because removing a job can make a route infeasible. [Time-window route state](https://github.com/VROOM-Project/vroom/blob/master/src/structures/vroom/tw_route.h).
- **C2 / C3:** The local-search engine is parameterized by route type and move operators, reuses solution state, tracks a best solution and deadline, and distinguishes paired pickup/delivery insertion from single-job insertion. [Local search](https://github.com/VROOM-Project/vroom/blob/master/src/algorithms/local_search/local_search.cpp).

### 21. [graphhopper/jsprit](https://github.com/graphhopper/jsprit)

**Language / role:** Java toolkit for rich vehicle-routing problems.

jsprit is useful for studying extensibility in ruin-and-recreate search: problem models, insertion rules, state updates, constraints, objective functions, acceptance rules, and listeners are separate concepts.

- **C1:** The constraint guide explains a subtle vehicle-switching case: checking only the newly inserted job is insufficient if the replacement vehicle cannot serve a job already in the route. Hard constraints operate at route and activity levels, while soft constraints rank insertions. [Constraint walkthrough](https://github.com/graphhopper/jsprit/blob/master/docs/Walkthrough%20%20%20Constraints.md).
- **C2:** Search strategies, ruin/recreate modules, custom objectives, listeners, and termination conditions are composable. The documentation also requires insertion costs to align with a custom objective, illustrating a semantic dependency between extension points. [Algorithm walkthrough](https://github.com/graphhopper/jsprit/blob/master/docs/Walkthrough---Algorithm.md).

**Documentation limitation:** These walkthroughs contain older API examples and incomplete subsections. They are architectural entry points; verify exact current API calls against the source when implementing an integration.

### 22. [google/or-tools](https://github.com/google/or-tools)

**Language / role:** C++ optimization monorepo with language bindings; count only the vehicle-routing subsystem under `ortools/constraint_solver` here.

The relevant study is the routing layer built over constraint programming. It exposes route topology and cumulative dimensions while allowing callers to enrich the model with underlying solver constraints.

- **C1:** The header documents linked invariants among successor, vehicle, and active variables: an inactive node points to itself and has no assigned vehicle, while connected successors belong to the same vehicle route. Time/load dimensions introduce additional propagation relationships. [Routing model header](https://github.com/google/or-tools/blob/stable/ortools/constraint_solver/routing.h).
- **C2 / C3:** Transit callbacks, dimensions, optional nodes, vehicle-specific models, first-solution strategies, local-search neighborhoods, and termination limits share a substantial modeling layer. The same [implementation/API entry point](https://github.com/google/or-tools/blob/stable/ortools/constraint_solver/routing.h) explains the combination of approximate search and selected exact subproblem methods. It does not promise a globally optimal answer for every VRP.

### 23. [PyVRP/PyVRP](https://github.com/PyVRP/PyVRP)

**Language / role:** Python modeling and search orchestration with C++ performance-critical components.

Study a solver whose current default-branch documentation describes **iterated local search (ILS)**. Older papers and descriptions emphasize hybrid genetic search; they should not be used to characterize the current implementation without checking the version.

- **C1 / C2:** `DurationSegment` summarizes and concatenates route fragments while tracking waiting-inclusive duration, time-window violation, start bounds, release times, and cross-trip state. Its front/back finalization operations show why composing route segments requires more than summing travel times. [DurationSegment](https://github.com/PyVRP/PyVRP/blob/main/pyvrp/cpp/DurationSegment.h).
- **C3:** The ILS loop separates perturbation, local improvement, acceptance, best-solution tracking, and stopping. Python controls the algorithm while perturbation and local search run in C++. [Current algorithm guide](https://github.com/PyVRP/PyVRP/blob/main/docs/source/dev/algorithm.rst).

The [public README](https://github.com/PyVRP/PyVRP/blob/main/README.md) labels some capabilities as Enterprise; those capabilities are not evidence for this public repository's implementation.

### 24. [reinterpretcat/vrp](https://github.com/reinterpretcat/vrp)

**Language / role:** Rust vehicle-routing solver with reusable optimization components and practical/scientific problem formats.

The distinguishing study is how a rich constraint model connects to a population-diversity mechanism and adaptive heuristic selection. It offers a different design from both a general CP solver and a narrowly specialized CVRP implementation.

- **C1 / C2:** A `Feature` combines hard constraints, objective contributions, and auxiliary state. This explicitly associates invariants such as capacity/time windows with the cached state and scoring needed during search, rather than letting unrelated callbacks drift apart. [Extension model](https://github.com/reinterpretcat/vrp/blob/master/docs/src/internals/development/extension.md).
- **C3:** ROSOMAXA groups solutions using a growing self-organizing map, retains local populations, periodically compacts the map, and uses a Thompson-sampling bandit to select heuristics. These are identifiable mechanisms for controlling search diversity and effort. [ROSOMAXA design](https://github.com/reinterpretcat/vrp/blob/master/docs/src/internals/algorithms/rosomaxa.md).

### 25. [vidalt/HGS-CVRP](https://github.com/vidalt/HGS-CVRP)

**Language / role:** C++ specialized hybrid genetic search for capacitated vehicle routing, with a C interface.

This is a particularly useful compact algorithm implementation. The scope is deliberately restricted: the project documents canonical CVRP, asymmetric distances, and duration constraints, rather than claiming every rich VRP variant.

- **C1:** Feasible and infeasible individuals are treated separately; search may repair offspring with stronger penalties. Ordered crossover tracks which customers were inserted before Split decodes the giant tour into routes. [Genetic search implementation](https://github.com/vidalt/HGS-CVRP/blob/main/Program/Genetic.cpp).
- **C3:** Separate `Population`, `Genetic`, `LocalSearch`, `Split`, and `CircleSector` components expose diversity management, decoding, and SWAP* neighborhood restriction. The project documents its intended instance scale, numerical distance-rounding conventions, fixed-seed checks, and stronger benchmark requirements for algorithm-changing contributions. [Code structure and validation policy](https://github.com/vidalt/HGS-CVRP/blob/main/README.md).

## Coverage, search process, and limitations

Discovery used **16 distinct live search formulations**, followed by GitHub API checks and direct reading of source, tests, and design documents. Search angles included general OSM engines; bicycle/offline routing; contraction hierarchies and PostgreSQL routing; RAPTOR/CSA/trip-based transit; smaller C, C#, TypeScript, Go, and Rust implementations; rich vehicle-routing solvers; maritime and rail networks; flight/airway planning; and traffic-assignment/large-matrix tools. Later searches repeated many already covered families and also exposed newer niche projects; the final selection favors substantive implementations with inspectable evidence over adding every search result.

Coverage includes preprocessing-heavy road engines, runtime costing, compact offline stores, SQL interfaces, timetable-specific algorithms, departure-window accessibility analysis, multimodal integration, and several distinct optimization architectures. SCGraph adds maritime/rail geographic networks; cppRouting adds traffic assignment. Aviation-specific routing and weather-dependent marine navigation are not deeply covered, and their absence should not be read as a finding that no suitable projects exist.

API wrappers such as pyvroom, routing frontends, profile collections, general graph packages without a transportation-specific core, tutorials, and apparent copies of HGS-CVRP were not counted. openrouteservice was retained because its inspected core preparation is a substantive extension of GraphHopper. MOTIS and Nigiri were retained with their dependency relationship made explicit. Monorepos such as OR-Tools and libosmscout are counted once and scoped to their routing subsystem. No separate mirror or fork was represented as an independent implementation.

Every selected repository has a verified canonical GitHub identity and at least one independently read implementation, design, test, or API source beyond repository metadata; several have multiple such sources. The report does not rely on star counts, repeat unverified benchmark numbers, or equate a recent push with a maintenance guarantee. No candidate code was executed, dependencies installed, or large repositories cloned. Performance mechanisms were inspected, not independently benchmarked, and tests were read rather than run. The criteria identify worthwhile engineering subjects; they do not assert that every component is uniformly exemplary.
