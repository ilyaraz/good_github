# Graph algorithm and graph partitioning libraries

Research date: **2026-10-09**.

This report selects 25 substantive GitHub repositories for studying reusable graph algorithms, graph representations, parallel graph computation, and balanced graph or hypergraph partitioning. It includes general application libraries and specialist scientific-computing systems. Community detection appears as a graph-algorithm use case; it should not be confused with partitioning under explicit capacity constraints. Monorepos and their bundled subsystems count once.

The criteria below describe specific evidence-backed strengths, not a judgment that every component is exemplary:

- **C1 — Difficult correctness:** graph invariants, concurrency, numerical semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or representations supporting multiple algorithms and application domains.
- **C3 — Structured performance engineering:** explicit time, memory, communication, or accelerator constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility management, testing, or control of accumulated complexity.

## General graph libraries and representation design

### 1. [networkx/networkx](https://github.com/networkx/networkx)

**Language / role:** Python; general graph modeling and algorithms. A useful pairing is its flexible application-facing graph model with a demanding combinatorial optimization implementation.

- **C1:** Maximum-weight matching implements blossom contraction and a primal-dual method, maintaining nested blossoms, mates, labels, and slack values. Integer weights permit integer arithmetic, while the documentation explicitly warns about floating-point precision affecting optimality. The implementation exposes the invariants and numerical choices rather than hiding them behind an external solver. [Matching implementation](https://networkx.org/documentation/stable/_modules/networkx/algorithms/matching.html).
- **C2:** Directed, undirected, simple, and multigraph classes share arbitrary hashable node identifiers and attribute conventions. Filtered and reversed graph views reuse algorithms without copying topology; the documentation also explains mutation restrictions and the cost of deep view chains. Study the boundary between a convenient common interface and representation-dependent costs. [Graph types and views](https://networkx.org/documentation/stable/reference/classes/index.html).

### 2. [igraph/igraph](https://github.com/igraph/igraph)

**Language / role:** C; graph-analysis engine used directly and through language interfaces. Particularly useful for studying how a native algorithm library remains embeddable when operations allocate intermediate structures and can fail.

- **C1:** The error system combines checked return values with a cleanup stack. Its worked graph-condensation example registers temporary graphs, contracts components, simplifies edges, and transfers ownership only after successful completion. The distinction between recoverable errors and an inconsistent library state is explicit. [Error handling and cleanup architecture](https://igraph.org/c/html/latest/igraph-Error.html).
- **C4:** The changelog documents a multi-year transition toward more consistent APIs, staged renamings and deprecated aliases, alongside fixes for allocation failures, integer overflow, and invalid cached graph properties. The 2022–2024 entries provide concrete evidence of compatibility and correctness management, rather than merely an old repository date. [Changelog](https://raw.githubusercontent.com/igraph/igraph/main/CHANGELOG.md).

### 3. [boostorg/graph](https://github.com/boostorg/graph)

**Language / role:** C++; Boost Graph Library. Study its separation of algorithm requirements from concrete containers, especially when adapting algorithms to application-owned data.

- **C2:** Graph concepts distinguish capabilities such as incidence traversal, edge enumeration, mutation, and property access. Property maps let algorithms obtain colors, distances, or weights independently of how a graph stores them. This is a substantial example of generic programming beyond one universal graph class. [Graph concepts](https://www.boost.org/doc/libs/1_89_0/libs/graph/doc/graph_concepts.html).
- **C1 / C3:** `adjacency_list` makes storage policies visible in its template parameters. Choosing vector or list storage changes removal costs, descriptor validity, and vertex-index behavior; bidirectional storage also has a memory cost. Its invalidation tables are essential to understanding whether exterior property maps remain correct after mutation. [Representation and invalidation guide](https://www.boost.org/doc/libs/1_89_0/libs/graph/doc/adjacency_list.html).

These documentation entry points are deliberately pinned to Boost 1.89.0, not presented as the latest release.

### 4. [jgrapht/jgrapht](https://github.com/jgrapht/jgrapht)

**Language / role:** Java; generic graph structures and a broad algorithm library. Study how wrappers and graph-type contracts keep optional behavior out of every basic operation.

- **C2:** Generic vertex and edge types, graph builders, suppliers, and delegating wrappers support different ownership and application models. A listenable wrapper adds mutation events, while a synchronized wrapper supplies a different concurrency contract. The guide distinguishes concurrent reads from unsafe mixed reads and writes. [User overview and architecture](https://jgrapht.org/guide/UserOverview).
- **C4:** The history records API migrations and deprecated-interface removal over multiple releases, together with fixes for graph equality, hashing, synchronization, exceptional paths, and arithmetic edge cases. The 2020–2023 entries make the cost of maintaining a large algorithm surface visible. Study the history alongside the wrapper design to see how semantic consistency is maintained across graph implementations. [Release history](https://raw.githubusercontent.com/jgrapht/jgrapht/master/HISTORY.md).

### 5. [barakugav/JGAlgo](https://github.com/barakugav/JGAlgo)

**Language / role:** Java; graph algorithms with generic application IDs and specialized indexed execution. A less ubiquitous library with an unusually explicit bridge between ergonomic APIs and primitive storage.

- **C2:** A `Graph<V,E>` exposes an index-graph view and mappings between application identifiers and dense integer identifiers. Algorithms can operate on the indexed representation while callers retain their domain objects. [Graph API and index views](https://barakugav.github.io/JGAlgo/0.5.1/com/jgalgo/graph/Graph.html).
- **C1 / C3:** Dense index ranges enable arrays and bitmaps instead of hash-based algorithm state, but mutation can renumber indices. The API specifies that mappings track these changes and restricts direct modification of the view. The repository further describes primitive collections and allocation reuse as implementation choices. Study this explicit bookkeeping boundary rather than assuming identifiers remain stable. [Repository implementation overview](https://github.com/barakugav/JGAlgo).

The repository warns that its API is not yet stable; the linked API guide is version 0.5.1.

### 6. [petgraph/petgraph](https://github.com/petgraph/petgraph)

**Language / role:** Rust; reusable graph representations and algorithms. Useful for comparing several storage models behind compatible traversal interfaces.

- **C2:** Algorithms work through graph traits, with generic node and edge payloads. The crate offers adjacency-list graphs, stable-index graphs, graphs keyed by application values, matrices, and compressed sparse row storage rather than forcing every workload into one structure. [Crate architecture and modules](https://docs.rs/petgraph/latest/petgraph/).
- **C1 / C3:** The representations deliberately trade memory use, lookup behavior, and index stability. `StableGraph` preserves remaining indices through removals; index-width choices affect storage; `GraphMap` uses node values as keys. These are observable correctness and performance contracts for clients storing external algorithm state. The same documentation is a good starting point for tracing which algorithms require which capabilities.

### 7. [Qiskit/rustworkx](https://github.com/Qiskit/rustworkx)

**Language / role:** Rust and Python; native graph algorithms with Python-facing graph objects. Despite its organizational home, its graph library supports general applications.

- **C1:** `PyDiGraph` can enforce acyclicity during mutations, rejecting an edge that would create a cycle. Its multigraph setting also changes the meaning of inserting an existing edge: a simple graph updates the payload instead of adding a parallel edge. These contracts affect both algorithm validity and user-visible behavior. [Directed graph API](https://www.rustworkx.org/dev/apiref/rustworkx.PyDiGraph.html).
- **C2 / C3:** Arbitrary Python objects can serve as node and edge data while traversal and algorithms use the Rust implementation. Cycle checking is an explicit cost-bearing option; operations that attach a newly created parent or child avoid a general cycle search. Study how specialized mutations preserve a strong invariant more cheaply than a fully general insertion.

### 8. [JuliaGraphs/Graphs.jl](https://github.com/JuliaGraphs/Graphs.jl)

**Language / role:** Julia; graph interfaces, representations, and algorithms. The repository identifies itself as the successor to LightGraphs; the archived predecessor is not counted separately.

- **C2:** The `AbstractGraph` interface lets alternative representations provide vertex, edge, and neighbor operations to common algorithms. The project intentionally keeps application attributes outside its core graph representation, allowing topology and domain data to evolve separately. [Repository design overview](https://github.com/JuliaGraphs/Graphs.jl).
- **C1 / C3:** Neighbor access can return references to internal storage, and mutations can invalidate iterators. The interface documentation explicitly requires callers not to modify these collections and explains when to copy them. Study the consequences of allocation-saving traversal in an extensible graph interface: a mathematically read-only algorithm still needs to respect storage aliasing. [Core interface contracts](https://juliagraphs.org/Graphs.jl/stable/core_functions/interface/).

### 9. [gonum/gonum](https://github.com/gonum/gonum)

**Language / role:** Go; the **`graph` subsystem** of a numerical-computing monorepo. The shortest-path packages offer especially clear examples of algorithm preconditions becoming public API contracts.

- **C1:** The path API distinguishes negative-edge rejection, negative-cycle detection, unreachable distances, and undefined shortest paths. Floyd–Warshall and Johnson document different failure/result semantics; enumeration also explains why zero-weight cycles do not produce an unlimited list of paths. [Path algorithms and result contracts](https://pkg.go.dev/gonum.org/v1/gonum/graph/path).
- **C2:** Small graph and traversal interfaces separate algorithms from concrete storage. Optional weighted interfaces fall back to uniform edge cost, and reusable result types distinguish one shortest path, alternatives, and all-pairs results. Study how interface requirements and result ownership support both explicit graph containers and graphs supplied through traversal behavior.

Only the graph library is in scope here; Gonum's unrelated numerical packages are not additional entries.

### 10. [graphology/graphology](https://github.com/graphology/graphology)

**Language / role:** JavaScript with TypeScript definitions; graph objects and an algorithm standard library in one monorepo. The Louvain subsystem provides a concrete path from application attributes to optimized community detection.

- **C1:** Louvain uses different modularity computations for directed and undirected graphs. It refuses a graph containing genuinely mixed edge directions rather than silently applying an inappropriate objective, while permitting a mixed-capability container whose actual edges are homogeneous. [Louvain API and semantics](https://graphology.github.io/standard-library/communities-louvain.html).
- **C2 / C3:** Algorithms share the Graphology graph and attribute conventions. Louvain exposes a queue-set optimization for local moves, configurable randomness and resolution, and detailed outputs such as move counts and modularity-computation counts. This is useful for studying both reusable graph APIs and observability of heuristic work. [Louvain implementation, tests, and benchmarks](https://github.com/graphology/graphology/tree/master/src/communities-louvain).

### 11. [KeRNeLith/QuikGraph](https://github.com/KeRNeLith/QuikGraph)

**Language / role:** C#; generic graph structures and algorithms for .NET. This is a substantive continuation of QuickGraph, with independent fixes, API changes, and framework-target work; the ancestor is not a separate selection.

- **C2:** Algorithms accept capability-oriented graph interfaces and weight functions. Predecessor recording can be attached as an observer to an algorithm instance, separating computation from the result information a caller wants to retain. Study the shortest-path examples for this compositional execution model. [Shortest-path guide](https://github.com/KeRNeLith/QuikGraph/wiki/Shortest-Path).
- **C1:** Release notes document concrete semantic repairs: A* needed to account for tree-edge costs, undirected graph serialization required corrections, and mutation notifications were made more consistent. The new distance interface and obsolete legacy accessors also show how such fixes coexist with API evolution. [2021–2022 release notes](https://raw.githubusercontent.com/KeRNeLith/QuikGraph/master/RELEASE_NOTES.md).

These historical notes establish substantive separate evolution, not a claim about current release frequency.

### 12. [snowleopard/alga](https://github.com/snowleopard/alga)

**Language / role:** Haskell; algebraic graph construction and algorithms. A useful counterpoint to mutable adjacency containers: graph composition is described through operations and laws.

- **C2:** Empty graphs, vertices, overlay, and connection form a reusable graph-construction algebra. Alternative representations and graph classes support different constraints without reducing the library to one expression-tree implementation. Study the laws to understand when representations can be substituted or expressions simplified. [Algebra and representation overview](https://github.com/snowleopard/alga).
- **C1:** The adjacency-map algorithms make DFS state and cycle evidence explicit. Topological sorting returns either an ordering or a nonempty cycle; the strongly connected component implementation maintains preorder, boundary, and path state and returns a graph of component graphs. This provides concrete material on preserving algorithmic invariants in a functional design. [Adjacency-map algorithm source](https://raw.githubusercontent.com/snowleopard/alga/main/src/Algebra/Graph/AdjacencyMap/Algorithm.hs).

## Large-scale, parallel, and accelerator graph computation

### 13. [networkit/networkit](https://github.com/networkit/networkit)

**Language / role:** C++ with Python interfaces; large-network analysis. Its graph-construction API is a compact example of separating ingestion performance from the final representation.

- **C1:** `GraphBuilder` permits concurrent half-edge insertion only when threads work on different source nodes; node creation has a different thread-safety contract. Completing the graph consumes the builder's accumulated state and resets it. These are precise ownership and concurrency rules rather than a blanket thread-safe label. [GraphBuilder API](https://networkit.github.io/dev-docs/cpp_api/classNetworKit_1_1GraphBuilder.html).
- **C3:** Deferring full graph construction allows insertion of only source-side half-edges before a completion phase builds the required structure. Study this phase boundary together with weighted and undirected-edge semantics to see how bulk graph ingestion avoids paying final-container costs on every insertion.

The broader repository supplies reusable analysis algorithms; the builder is the recommended implementation entry point here.

### 14. [ParAlg/gbbs](https://github.com/ParAlg/gbbs)

**Language / role:** C++; Graph Based Benchmark Suite and reusable shared-memory graph framework. Treat it as a research framework and algorithm collection, rather than assuming a stable application-library API.

- **C2:** Graph traversal is factored into operations over vertex subsets and parameterized edge functions. `edgeMapData` separates the traversal mechanism from the computation and its optional per-vertex output data. [Edge-map implementation](https://github.com/ParAlg/gbbs/blob/master/gbbs/edge_map_data.h).
- **C3:** The implementation chooses sparse or dense processing from frontier size and work estimates, supports direction-related flags, and delegates neighbor processing to graph decoders. The repository also supports compressed graph representations and multiple parallel execution arrangements. Study how frontier representation, work estimation, and traversal scheduling meet in one dispatch layer. [Framework and representation overview](https://github.com/ParAlg/gbbs).

This selection represents the Ligra-derived shared-memory family without separately counting every predecessor.

### 15. [gunrock/gunrock](https://github.com/gunrock/gunrock)

**Language / role:** C++/CUDA; GPU graph algorithms expressed through frontiers and operators. The repository distinguishes its newer `main` implementation from the deprecated older implementation retained on `master`.

- **C2 / C3:** Active vertices or edges form frontiers, and reusable operators transform them. This separates algorithm logic from GPU traversal and load-balancing strategies, while preserving push/pull and synchronization choices that matter for irregular graphs. [Programming model](https://gunrock.github.io/gunrock/gunrock.wiki/Programming-Model.html).
- **C1:** The inspected BFS implementation atomically minimizes a neighbor's distance and admits it to the next frontier only when the update improves that distance. It then invokes configurable advance and filtering operators. Study how the atomic update determines work admission when many edges concurrently discover the same vertex. [BFS source on main](https://github.com/gunrock/gunrock/blob/main/include/gunrock/algorithms/bfs.hxx).

### 16. [rapidsai/cugraph](https://github.com/rapidsai/cugraph)

**Language / role:** C++/CUDA and Python; GPU graph analytics. The relevant monorepo layers are `libcugraph` and its Python interfaces, counted together.

- **C1:** The C++ architecture distinguishes owning RAII containers from nonowning views. It explains allocation, copy/move behavior, uninitialized device storage, and error-checking conventions—contracts that determine whether asynchronous GPU computation observes valid memory. [C++ library architecture](https://docs.nvidia.com/cugraph/latest/graph_support/cugraph_cpp_support/).
- **C2 / C3:** Layered interfaces and configurable memory-resource allocation support reuse in larger GPU pipelines. The architecture discusses device containers that avoid unnecessary initialization and synchronization, making memory management an explicit part of performance design. Study those contracts before the individual graph kernels: faster traversal alone does not address allocation and data-lifetime costs.

The cited architecture guide supports these design observations; no hardware-specific throughput claim is inferred from it.

### 17. [GraphBLAS/LAGraph](https://github.com/GraphBLAS/LAGraph)

**Language / role:** C; graph algorithms built on sparse-matrix GraphBLAS operations. Useful for studying a graph library whose reusable execution primitives come from algebra rather than neighbor iterators.

- **C2 / C3:** A graph contains an adjacency matrix plus cached properties such as transpose, degrees, and symmetry information. Basic algorithm interfaces can compute needed caches; advanced interfaces require the caller to manage them. BFS can use cached information for direction optimization. [Graph object and caches](https://lagraph.readthedocs.io/en/latest/graph.html), [basic and advanced algorithms](https://lagraph.readthedocs.io/en/latest/algorithms.html).
- **C1:** Algorithm contracts spell out structural and numerical assumptions: triangle counting requires appropriate symmetry and no self-loops, shortest-path results use type-dependent infinity conventions, and PageRank variants differ in handling sinks. Study how a common matrix representation still requires algorithm-specific semantic checks.

The repository separates established and experimental algorithms; inclusion does not imply identical API stability across both.

## Graph and hypergraph partitioning

### 18. [KarypisLab/METIS](https://github.com/KarypisLab/METIS)

**Language / role:** C; serial graph partitioning, mesh partitioning, and fill-reducing ordering. A compact entry into the architecture of multilevel optimization libraries.

- **C1:** The k-way entry point validates conditions such as a connected input when contiguous blocks are requested. It handles numbering conversion, restores caller-facing numbering, sets up balance constraints, and manages failure cleanup. These integration details are as important as the cut objective for a callable native library. [K-way partitioning source](https://github.com/KarypisLab/METIS/blob/master/libmetis/kmetis.c).
- **C3:** The same source exposes the coarsen–initial-partition–refine pipeline, workspace management, and selection among repeated candidate partitions subject to objective and imbalance considerations. Study it as a readable control layer over specialized routines, not as evidence that a heuristic always reaches the optimal cut.

### 19. [KarypisLab/ParMETIS](https://github.com/KarypisLab/ParMETIS)

**Language / role:** C/MPI; distributed graph partitioning and adaptive repartitioning. This is a separate distributed implementation, not a language binding for serial METIS.

- **C1:** The adaptive-repartition entry point validates local inputs and combines status across the communicator before proceeding. It coordinates distributed graph ranges, numbering conversion, and restoration, so a local problem does not simply let one process continue into a collective phase with incompatible state. [Adaptive repartitioning source](https://raw.githubusercontent.com/KarypisLab/ParMETIS/main/libparmetis/ametis.c).
- **C3:** Adaptive repartitioning accounts for communication and redistribution costs, using vertex migration size as well as edge information. The control flow connects coarsening, adaptive partitioning, and partition remapping. Study how an already distributed computation changes the objective: a better static cut can still be undesirable if moving the data is too expensive.

### 20. [KaHIP/KaHIP](https://github.com/KaHIP/KaHIP)

**Language / role:** C++ with MPI components; graph partitioning, separators, mapping, and related tools. The bundled **ParHIP** distributed subsystem is included once within this repository.

- **C2 / C3:** A configurable partitioning engine separates coarsening, initial partitioning, and uncoarsening. Its control layer also supports repeated runs, alternative cycles, and a first-level refinement path. Study how quality/time presets reuse this architecture rather than becoming unrelated executables. [Partitioner control flow](https://raw.githubusercontent.com/KaHIP/KaHIP/master/lib/partition/graph_partitioner.cpp).
- **C1:** Recursive partitioning carries block ranges, subgraph-to-original mappings, and weight budgets through each split. For odd target block counts, it assigns unequal target weights and selects a compatible refinement mode. These details make recursive composition a correctness problem beyond merely invoking a bipartitioner repeatedly. The same source contains the relevant mapping and budget logic.

### 21. [KaHIP/KaMinPar](https://github.com/KaHIP/KaMinPar)

**Language / role:** C++; shared-memory and distributed graph partitioning, including **dKaMinPar** in the same repository. Particularly relevant when the required number of blocks is large.

- **C3:** The authors' deep multilevel design combines recursive bipartitioning with direct k-way techniques to address the growth of the coarsest problem as the requested block count increases. This gives an architectural explanation for its target workload rather than relying on a benchmark ranking. [Deep multilevel graph partitioning paper](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ESA.2021.48).
- **C2:** Library interfaces expose partitioning separately from command-line tools, with shared-memory and MPI configurations and relative or absolute block-capacity controls. The repository documents integer-width choices, including the need for weight types to hold aggregate weights. Study how the same algorithm family is packaged for different execution and capacity models. [Library, configuration, and type documentation](https://github.com/KaHIP/KaMinPar).

### 22. [kahypar/kahypar](https://github.com/kahypar/kahypar)

**Language / role:** C++; sequential multilevel hypergraph partitioning with native and language interfaces. Hyperedges connect sets of vertices, so contraction and refinement must preserve more state than ordinary graph adjacency.

- **C1:** The hypergraph structure tracks enabled nodes and nets, partition IDs, connectivity, incident cut information, and contraction mementos. Contraction and undo operations must keep these views consistent as topology and partition assignments change. [Hypergraph data structure](https://raw.githubusercontent.com/kahypar/kahypar/master/kahypar/datastructure/hypergraph.h).
- **C3:** Its n-level scheme contracts one vertex per level, making fine-grained state maintenance central to practical performance. The distinction between cut-net and connectivity objectives, plus fixed-vertex policies, explains why specialized bookkeeping is needed rather than repeated reconstruction of a generic graph. [Algorithm and supported constraints](https://github.com/kahypar/kahypar).

Study the source's reversible topology changes alongside the objective definitions; different objectives do not assign the same gain to every move.

### 23. [kahypar/mt-kahypar](https://github.com/kahypar/mt-kahypar)

**Language / role:** C++; shared-memory graph and hypergraph partitioning. Retained separately from KaHyPar because parallel coarsening, initial partitioning, and refinement constitute a substantive separate implementation.

- **C3:** The design combines community-guided parallel coarsening, recursive initial partitioning with work stealing, label propagation, and parallel direct k-way Fiduccia–Mattheyses refinement. Study where work can be shared and where move interactions require coordination. [Authors' architecture paper](https://arxiv.org/abs/2010.10272).
- **C1 / C2:** The C interface makes integration constraints explicit: initialize the global thread pool appropriately, do not call seed-setting concurrently, and use compatible presets when creating and partitioning a hypergraph. It also defines ownership of copied input arrays and validates the number of individual block weights. These contracts make parallel algorithm infrastructure reusable without concealing its global state. [Public C API](https://raw.githubusercontent.com/kahypar/mt-kahypar/master/include/mtkahypar.h).

### 24. [sandialabs/Zoltan](https://github.com/sandialabs/Zoltan)

**Language / role:** C/C++ with MPI; dynamic load balancing, data migration, and distributed graph/hypergraph partitioning. **Official standalone distribution:** its repository says newer development lives in Trilinos and standalone releases can lag. This substantive GitHub source distribution is retained with that limitation; Trilinos is not counted again.

- **C2 / C3:** PHG uses application callbacks to obtain hypergraph data and supports partitioning, refinement, and repartitioning. Its repartition objective combines cut cost with migration volume, while a two-dimensional processor arrangement distributes hypergraph work. Study how application-owned data and communication costs enter a reusable partitioner. [PHG architecture and parameters](https://sandialabs.github.io/Zoltan/ug_html/ug_alg_phg.html).
- **C1:** The same guide specifies how replicated edge weights are reconciled—addition, maximum, or error—and describes callback units needed for meaningful migration costs.
- **C4:** The release history records years of interface and complexity management, including backward-compatible load-balancing APIs, batched callbacks, and hypergraph bug fixes. [Release and migration history](https://sandialabs.github.io/Zoltan/ug_html/ug_release.html).

### 25. [sandialabs/Jet-Partitioner](https://github.com/sandialabs/Jet-Partitioner)

**Language / role:** C++/Kokkos; GPU-oriented multilevel graph partitioning with portable execution backends. A less familiar specialist library that exposes native entry points and execution-space choices, rather than only an experiment driver.

- **C1:** Jet refinement evaluates interacting candidate moves, filters them using estimated gains under changed neighbor assignments, and follows refinement with rebalancing. Keeping the best balanced state matters because an unconstrained improvement phase can violate capacities. Study the distinction between a locally attractive move and a valid complete partition. [Authors' refinement and rebalancing design](https://arxiv.org/html/2304.13194v2).
- **C2 / C3:** The library uses Kokkos execution spaces and KokkosKernels sparse graph storage, with METIS supplying coarsest-level initialization. This makes the coarsening/refinement pipeline and its CPU/GPU boundaries concrete. The repository documents its CMake library target and the difference between library weight support and command-line input capabilities. [Integration and representation guide](https://github.com/sandialabs/Jet-Partitioner).

## Search coverage, selection boundaries, and limitations

Discovery used live web searches followed by opening every retained GitHub repository and additional primary material. Search formulations covered at least these distinct angles:

1. General graph-algorithm libraries and graph partitioning libraries, including NetworkX, igraph, and NetworKit alternatives.
2. Generic graph APIs in Rust and Java, including petgraph, rustworkx, JGraphT, and JGAlgo.
3. Go, Julia, JavaScript, and C# graph ecosystems, followed by graph-interface and shortest-path documentation.
4. Shared-memory graph frameworks, compressed representations, and frontier-based processing.
5. GPU graph analytics and sparse-matrix graph algorithms, including Gunrock, cuGraph, and LAGraph.
6. Serial and MPI graph partitioning, including METIS, ParMETIS, KaHIP, and Zoltan.
7. Hypergraph partitioning and shared-memory refinement, including sequential and parallel KaHyPar implementations.
8. Large-block-count and GPU partitioning alternatives, using searches for KaMinPar, Jet, PuLP, and mt-metis.
9. Functional/algebraic graph libraries and graph laws, which added Alga.
10. Official-source and mirror status, including searches for Scotch and repositories whose development moved elsewhere.

Later searches increasingly returned the same implementation families, bindings, or narrower artifacts. The final additions, Alga and Jet, supplied distinct representation and execution designs. This is a curated selection, not an exhaustive census or ranking.

Scotch was not represented by an unverified GitHub copy: its [official project page](https://www.labri.fr/perso/pelegrin/scotch/) identifies Inria GitLab as the official source location. Binding-only packages, predecessor/fork duplicates, tutorial repositories, awesome lists, graph databases, and visualization- or GNN-first projects were outside this selection. QuikGraph is an explicitly identified evolved fork; Zoltan is an explicitly identified official standalone distribution. Gonum, Graphology, KaHIP, KaMinPar, and cuGraph are each counted once despite multiple relevant packages or subsystems.

Evidence came from repository pages, actual source files, API contracts, project guides, release histories, and authors' design papers. A raw copy of a repository README was not treated as independent corroboration. The criteria assessments and suggested study paths are engineering interpretations of those sources; no candidate code was executed and no published performance result was independently reproduced. Partitioning quality is workload- and configuration-dependent. C4 is used only where multi-year compatibility or complexity-management evidence was inspected; inclusion elsewhere makes no blanket claim of current maintenance or API stability. Moving branch and documentation links describe the material available during this research and can change later.
