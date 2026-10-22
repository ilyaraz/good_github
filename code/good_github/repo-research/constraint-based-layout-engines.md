# Constraint-based layout engines

Research date: **2026-10-09**

This report selects **21 GitHub repositories** implementing constraint-driven placement for widgets, diagrams, graphs, or scientific figures, together with layout-oriented solver kernels. The scope includes incremental linear optimization, geometric constraint propagation, constrained force-directed layout, nonlinear optimization, disjunctive layouts, and compilation of restricted constraint graphs. Ordinary Flexbox/Grid implementations, general optimization packages without a substantive layout subsystem, and convenience wrappers around an unavailable platform solver are outside the selection.

The criteria describe what an experienced engineer can study, not a guarantee that every component is exemplary. Historical implementations remain useful architectural references; they are identified below. “Historical” is a research assessment based on the inspected repository and activity metadata, not necessarily a maintainer's abandonment announcement. A recent push alone is not treated as maintenance or C4 evidence.

## Criteria legend

- **C1 — Difficult correctness:** numerical semantics, feasibility, invariants, conflicting constraints, incremental state, or other substantial failure modes.
- **C2 — Reusable abstractions:** substantial solver, layout, or composition interfaces supporting multiple applications.
- **C3 — Performance with structure:** concrete techniques addressing interactive or repeated-layout costs within an understandable architecture.
- **C4 — Sustained evolution:** release/history evidence spanning years, accompanied by compatibility work, testing, or complexity management.

## Incremental solver kernels for layout

### 1. [gjbadros/cassowary](https://github.com/gjbadros/cassowary)

**Languages/role:** C++, Java, and Smalltalk; original Cassowary toolkit. **Historical reference**; GitHub metadata records its last push in 2017. This is useful for understanding the solver model that later layout systems simplify or adapt, including stays, edit sessions, constraint strengths, and tableau maintenance.

- **C1:** Adding a constraint is more than inserting an equation: the C++ implementation validates supported constraint kinds, distinguishes required-constraint failure, introduces auxiliary variables, and maintains solver state through edits and removals. It explicitly rejects strict inequalities and unsupported read-only-variable constraints. Read the implementation in [ClSimplexSolver.cc](https://github.com/gjbadros/cassowary/blob/master/c++/ClSimplexSolver.cc).
- **C2:** The toolkit separates variables, expressions, constraints, strengths, and solving, with multiple language implementations and interactive examples. The [repository documentation](https://github.com/gjbadros/cassowary#readme) explains these implementations and the UI/window-management applications. Study the C++ solver as the main entry point rather than treating the included language copies as separate repositories.

### 2. [nucleic/kiwi](https://github.com/nucleic/kiwi)

**Languages/role:** C++ solver with Python bindings; a separate implementation of Cassowary. Particularly valuable for studying explicit tradeoffs between an algorithm's ideal semantics and the needs of repeated widget layout.

- **C1:** The [solver internals guide](https://github.com/nucleic/kiwi/blob/main/docs/source/basis/solver_internals.rst) documents floating-point strengths: sufficiently many weak constraints can outweigh a stronger preference. It also explains the omission of native stay constraints and why removed constraints can leave retained variables, requiring occasional solver resets.
- **C3:** The same guide connects performance to compact symbol representations and iteration-friendly associative vectors, rather than merely describing the solver as fast. These are concrete data-layout decisions in the tableau's hot operations.
- **C4:** [Release notes](https://github.com/nucleic/kiwi/blob/main/releasenotes.rst) span 2013–2026 and document zero-size-constraint fixes, comprehensive tests, C++11/C++20 compatibility, benchmarks in CI, Python version support, and free-threaded Python builds. No benchmark multiplier is assumed to apply universally.

### 3. [ratatui/kasuari](https://github.com/ratatui/kasuari)

**Language/role:** Rust; layout-oriented Cassowary kernel descended from `cassowary-rs` and influenced by Kiwi. Only this continuation is counted, avoiding a second entry for the predecessor.

- **C1:** [solver.rs](https://github.com/ratatui/kasuari/blob/main/src/solver.rs) distinguishes duplicate, unsatisfiable, unknown-constraint, and internal solver errors. Its removal path explicitly removes error contributions before pivoting, because reversing that order produces incorrect results. Dummy-only rows and artificial-variable insertion make the feasibility logic approachable.
- **C2:** The solver has no built-in rectangle or coordinate-system model; higher layers compose expressions and relationships, edit variables, and consume changed values. The change-tracking structures in the solver expose a useful boundary between numerical solving and redraw work.
- **Separate evolution:** The [changelog](https://github.com/ratatui/kasuari/blob/main/CHANGELOG.md) substantiates the continuation with a strength newtype, reorganized modules, richer errors, additional tests, `no_std` support, and portable-atomic work. These are substantive changes, although the newer Kasuari name alone does not establish years of independent maintenance.

### 4. [lithdew/casso](https://github.com/lithdew/casso)

**Language/role:** Go; compact incremental solver for UI relationships. **Historical implementation**; last recorded push in 2020. It offers a useful contrast to object-heavy solver APIs.

- **C1:** [solver.go](https://github.com/lithdew/casso/blob/master/solver.go) reduces constraints into augmented simplex form, checks invalid variable symbols, introduces slack/error/dummy symbols, and uses returned markers to remove constraints while updating the objective. This exposes the bookkeeping behind changing a live layout.
- **C3:** The [README's representation notes](https://github.com/lithdew/casso#readme) describe packing symbol type and identity into one unsigned integer to reduce memory and operation costs. The solver separates tableau rows, edit state, markers, and infeasible rows. Its reported microbenchmark is illustrative, not an independently reproduced performance result.
- **C2:** Required and preferential relationships, editable parameters, and a coordinate-independent variable model support different layout policies; the documented two-child resize example demonstrates this without tying the solver to a particular GUI toolkit.

### 5. [inamiy/Cassowary](https://github.com/inamiy/Cassowary)

**Language/role:** Swift; independent simplex/Cassowary implementation with a UI integration layer. **Historical implementation**; last recorded push in 2017. This is an actual solver, not just a Swift syntax wrapper around Apple's Auto Layout.

- **C2:** The repository separates `Simplex`, `Cassowary`, and `CassowaryUI`. The [Cassowary solver](https://github.com/inamiy/Cassowary/blob/master/Sources/Cassowary/Solver/Solver.swift) wraps a reusable simplex tableau with stays, edit state, cached solutions, and typed error translation; the UI layer applies resulting geometry.
- **C1:** [Degeneracy tests](https://github.com/inamiy/Cassowary/blob/master/Tests/SimplexTests/DegeneracyTests.swift) use examples intended to catch pivot cycling. The solver also distinguishes unbounded and failed dual-optimization cases. Its source explicitly documents a workaround for nested `beginEdit()` behavior, so it should be studied with that limitation in view.

### 6. [slightlyoff/cassowary.js](https://github.com/slightlyoff/cassowary.js)

**Language/role:** JavaScript; substantial evolution of the original JavaScript Cassowary port. **Historical implementation**; last recorded push in 2017. Useful for understanding incremental solving in browser-era JavaScript runtimes.

- **C1:** [SimplexSolver.js](https://github.com/slightlyoff/cassowary.js/blob/master/src/SimplexSolver.js) tracks external-variable changes, marker/error variables, nested edit scopes, and infeasible rows. The nested-edit removal logic deliberately retains variables owned by an outer edit session: a concrete lifetime invariant, not merely a numerical calculation.
- **C2:** Stays, editable variables, equations, inequalities, and a toolkit-independent solver support direct-manipulation interfaces and other layout front ends. The [README](https://github.com/slightlyoff/cassowary.js#readme) explains its removal of external dependencies and use in workers, command-line programs, and browsers. It also warns that the published API was unstable; this is not presented as a currently supported browser-layout standard.

### 7. [brodderickrodriguez/cassowary](https://github.com/brodderickrodriguez/cassowary)

**Language/role:** Python; pure-Python solver formerly associated with BeeWare, transferred to its current owner in 2020. **Historical implementation**; last recorded push in 2020. A readable option for tracing solver behavior without a native-language boundary.

- **C1:** [simplex_solver.py](https://github.com/brodderickrodriguez/cassowary/blob/master/cassowary/simplex_solver.py) exposes the complete bookkeeping: required failures, slack/dummy/error variables, edit stacks, automatic versus deferred solving, and dual optimization followed by resetting stay constants.
- **C2:** The [constraint-system guide](https://github.com/brodderickrodriguez/cassowary/blob/master/docs/topics/theory.rst) explains overloaded expression construction, strengths and weights, removable constraints, and scoped edits. The `SolverEditContext` implementation connects the mathematical model to Python's context-manager protocol. The value lies in reusable numerical and interaction abstractions, not an assumption of current Python-version compatibility.

## Widget layout systems and constraint compilation

### 8. [androidx/androidx](https://github.com/androidx/androidx)

**Languages/role:** Java/Kotlin; **ConstraintLayout subsystem** of the AndroidX monorepo. This is the official GitHub repository synchronized with AOSP. The archived standalone `androidx/constraintlayout` repository is not counted separately.

- **C1:** The core [LinearSystem.java](https://github.com/androidx/androidx/blob/androidx-main/constraintlayout/constraintlayout-core/src/main/java/androidx/constraintlayout/core/LinearSystem.java) restores basic feasibility before optimizing a priority goal. It separates row storage, variable pools, pivot candidates, and goal handling, making numerical and state invariants visible beneath the widget API.
- **C3:** That solver skips optimization for already resolved cases and maintains pooled objects and metrics. The complementary [DependencyGraph.java](https://github.com/androidx/androidx/blob/androidx-main/constraintlayout/constraintlayout-core/src/main/java/androidx/constraintlayout/core/widgets/analyzer/DependencyGraph.java) attempts direct graph measurement, tracks graph/measurement invalidation, and groups runs for wrap-content calculations. Studying both explains how a layout engine avoids sending every case through its most general numerical path.
- **C2:** The relevant boundary is the reusable core engine plus widget/Compose adapters, not all of AndroidX. Anchors, guidelines, barriers, chains, size ratios, and measurement behavior provide substantially different compositions over the shared machinery.

### 9. [GNOME/gtk](https://github.com/GNOME/gtk)

**Language/role:** C/GObject; **GTK 4 `GtkConstraintLayout` and its internal solver**. **Official read-only GitHub mirror** of GNOME's GitLab repository; count the monorepo once.

- **C1:** [gtkconstraintlayout.c](https://github.com/GNOME/gtk/blob/main/gtk/gtkconstraintlayout.c) documents the effects of underconstrained systems, conflicting constraints, and removing children without repairing relationships. Widget measurement and allocation must preserve the relationship between solver variables, live children, and layout guides.
- **C2:** The same subsystem accepts constraints through object APIs, GtkBuilder descriptions, and Visual Format Language, including reusable guides with minimum/natural/maximum dimensions. The internal [gtkconstraintsolver.c](https://github.com/GNOME/gtk/blob/main/gtk/gtkconstraintsolver.c) explains the incremental tableau representation, strengths, stays, and expression builder. It is a particularly useful study of fitting a numerical engine into a larger object and widget lifecycle.

### 10. [nucleic/enaml](https://github.com/nucleic/enaml)

**Languages/role:** Python/Enaml; declarative UI framework with a **Kiwi-backed layout subsystem**. Count Enaml separately from Kiwi because it implements substantial policy and toolkit integration above the solver.

- **C2:** [layout_manager.py](https://github.com/nucleic/enaml/blob/main/enaml/layout/layout_manager.py) defines a backend-facing `LayoutItem` abstraction and converts margins, size hints, minimum/maximum dimensions, and user constraints into one solver model. Hugging, resistance, and limiting policies are independently represented.
- **C1:** The same implementation uses different edit strengths to compute preferred and minimum sizes, imposes nonnegative geometry, caches generated constraints, and updates widget geometry after resizing. Correctness involves preserving these policies while individual size hints and constraints change.
- **C4:** [Release notes](https://github.com/nucleic/enaml/blob/main/releasenotes.rst) document years of Python compatibility work, Qt6/PySide6 migration, integer-geometry fixes, parser changes, and regression repairs. This supports evolution and complexity-management claims rather than relying on repository age.

### 11. [gss/engine](https://github.com/gss/engine)

**Languages/role:** CoffeeScript/JavaScript; Grid Style Sheets constraint layout for the DOM. **Historical browser engine**; last recorded push in 2019. Its strongest study value is the orchestration around the solver.

- **C2:** [Engine.coffee](https://github.com/gss/engine/blob/master/src/Engine.coffee) separates commands, queries, update processing, worker engines, and domains. Domains can represent independent constraint graphs or sources of values such as DOM measurements, providing a reusable architecture for combining relationships with measured content.
- **C3:** [Linear.coffee](https://github.com/gss/engine/blob/master/src/engine/domains/Linear.coffee) disables immediate auto-solving, distinguishes structural constraint changes from value suggestions, and selects solve versus resolve accordingly. It also caches operations by expression and scope. The architecture addresses repeated browser layout and worker execution without requiring a fresh global solve for every mutation.

### 12. [lume/autolayout](https://github.com/lume/autolayout)

**Language/role:** TypeScript; Auto Layout geometry and Visual Format Language implementation. A continuation of `IjzerenHein/autolayout.js`, whose README points to this project. Only the continuation is counted. Metadata's last recorded push is in 2024; no stronger maintenance claim is made.

- **C2:** [View.ts](https://github.com/lume/autolayout/blob/main/src/View.ts) implements parent/subview geometry, configurable spacing, intrinsic versus fitting size, and constraint construction over Kiwi. It is a rendering-independent geometry engine with both parsed and programmatic inputs, not simply an Apple API binding.
- **C1:** [SubView.ts](https://github.com/lume/autolayout/blob/main/src/SubView.ts) lazily creates attributes while adding identities such as right = left + width and center = origin + half-size. Intrinsic dimensions become edit variables with distinct parent/child strengths. These identities and priority mappings must remain consistent regardless of attribute access order and resizing.
- **Lineage evidence:** The inspected implementation is TypeScript and directly imports `@lume/kiwi`, substantiating continued implementation changes beyond an unchanged mirror of the older JavaScript repository.

### 13. [czeidler/alm](https://github.com/czeidler/alm)

**Language/role:** Java; Auckland Layout Model, layout algebra, and platform integrations. **Historical research implementation**; last recorded push in 2016. It broadens the selection beyond the Cassowary family by exposing tabstops and areas as the central layout model.

- **C2:** [LayoutSpec.java](https://github.com/czeidler/alm/blob/master/alm/src/main/java/nz/ac/auckland/alm/LayoutSpec.java) composes areas bounded by shared horizontal/vertical tabstops, custom constraints, spacing, insets, and interchangeable `LinearSolver` implementations. Cloning preserves shared tab identities through explicit maps.
- **C1:** The same class must invalidate cached layout sizes as the specification changes and uses a GUI-specific numerical tolerance. [ALMTest.java](https://github.com/czeidler/alm/blob/master/alm/src/test/java/nz/ac/auckland/alm/ALMTest.java) exercises minimum/preferred sizes and ordered button boundaries. It explicitly comments out maximum-size assertions because that calculation is not working; this is a material limitation, not evidence of complete correctness.

### 14. [YueJiang-nj/ORCSolver-CHI2020](https://github.com/YueJiang-nj/ORCSolver-CHI2020)

**Language/role:** Python with CVXPY and optional Z3 comparison code; **research implementation for disjunctive adaptive GUI layouts**. The repository contains the proposed method and separate baseline methods, counted together.

- **C2:** [orclayout_classes.py](https://github.com/YueJiang-nj/ORCSolver-CHI2020/blob/master/Code/ORCSolver%20%28Ours%29/orclayout_classes.py) models widgets, rows, columns, pivots, horizontal/vertical flows, and flow around fixed regions under a common layout hierarchy. Boundary variables, constraints, and soft objectives are accumulated through that hierarchy.
- **C1:** The code snapshots best solution values because optimization variables are shared across alternative nodes and later solves mutate them. It also excludes infinite-loss solutions. This makes state ownership across alternative layouts a concrete correctness problem.
- **C3:** [flow_solver.py](https://github.com/YueJiang-nj/ORCSolver-CHI2020/blob/master/Code/ORCSolver%20%28Ours%29/flow_solver.py) searches candidate row configurations and cuts off candidates using accumulated loss. The inspected class implementation disables an additional legacy refinement that deep-copies CVXPY expression graphs because it can crash current CVXPY. Study it as a research engine with that explicit capability limitation; published timing claims were not reproduced.

### 15. [nalu-development/nalu](https://github.com/nalu-development/nalu)

**Language/role:** C#; **Magnet constraint layout subsystem** in the MAUI library monorepo. Magnet 2.0 supplies a distinct compiled approach to anchors, chains, barriers, and guidelines; it is not a general Cassowary solver.

- **C1:** [MagnetCompiler.cs](https://github.com/nalu-development/nalu/blob/main/Source/Nalu.Maui.Layouts/Layouts/MagnetLayout/Engine/MagnetCompiler.cs) validates identities and targets, constructs axis dependencies, detects cycles, and validates emitted operand slots because execution uses accesses without bounds checks. Compile-time restrictions are therefore part of the runtime correctness argument.
- **C3:** The compiler creates a reusable instruction tape without references to layout instances and consults a structural cache. [MagnetEngine.cs](https://github.com/nalu-development/nalu/blob/main/Source/Nalu.Maui.Layouts/Layouts/MagnetLayout/Engine/MagnetEngine.cs) separates that tape from per-layout arrays and implements guarded delta-arrange reuse, including cross-axis dependency and visibility checks. This connects caching and reduced repeated work to explicit invalidation rules. No universal allocation or speed ratio is inferred from the project's benchmarks.

## Diagrams, graphs, and scientific figures

### 16. [mjwybrow/adaptagrams](https://github.com/mjwybrow/adaptagrams)

**Language/role:** C++; related diagramming libraries. The relevant subsystems are **libvpsc, libcola, and libtopology**; libavoid routing and libdialect are neighboring components, not separate repository entries.

- **C1:** [solve_VPSC.cpp](https://github.com/mjwybrow/adaptagrams/blob/master/cola/libvpsc/solve_VPSC.cpp) maintains separation constraints while merging and splitting variable blocks. Its comments state the incoming-constraint invariant, and its implementation uses numerical tolerances, infeasibility exceptions, and bounded refinement. This is a concrete constrained-placement algorithm distinct from a generic simplex port.
- **C2:** [cola.h](https://github.com/mjwybrow/adaptagrams/blob/master/cola/libcola/cola.h) exposes compound constraints, cluster hierarchies, convergence callbacks, and topology-preserving extension points. `ConstrainedFDLayout` combines nonlinear gradient projection with constraint satisfaction and can run with no graph edges for constraint-only placement.
- **Version distinction:** That header marks the older `ConstrainedMajorizationLayout` deprecated and recommends `ConstrainedFDLayout`. The distinction matters because descriptions of the repository's original stress-majorization method do not describe every current code path.

### 17. [tgdwyer/WebCola](https://github.com/tgdwyer/WebCola)

**Language/role:** TypeScript with JavaScript distribution; browser graph-layout engine, separately implemented from native libcola. Study the composition of graph-distance objectives, geometric projection, and an interactive layout lifecycle.

- **C1:** [vpsc.ts](https://github.com/tgdwyer/WebCola/blob/master/src/vpsc.ts) handles active/inactive separation constraints, block merging/splitting, directed cycles, and unsatisfiable relationships. Its overlap-removal API also states what happens when spans cannot physically fit inside requested bounds.
- **C3:** [layout.ts](https://github.com/tgdwyer/WebCola/blob/master/src/layout.ts) stages unconstrained initialization, user-constraint projection, and non-overlap projection rather than applying every restriction from the first iteration. It also manages fixed nodes and disconnected components. The stages are explicit controls for convergence and interactive work, not a blanket guarantee of scalability.
- **C2:** Groups, alignment/separation constraints, fixed positions, and interchangeable browser adapters expose substantially different graph-layout use cases over the same engine.

### 18. [iVis-at-Bilkent/cytoscape.js-fcose](https://github.com/iVis-at-Bilkent/cytoscape.js-fcose)

**Language/role:** JavaScript; compound-graph layout extension with its own spectral initialization and integration with `cose-base` refinement. This is more substantial than a registration-only Cytoscape wrapper.

- **C2:** The [repository documentation](https://github.com/iVis-at-Bilkent/cytoscape.js-fcose#readme) specifies fixed-node, alignment, and relative-placement constraints, together with compound graphs and incremental use. Placement constraints apply to simple nodes, and overlapping alignment groups must be supplied in the documented compact form.
- **C3:** [spectral.js](https://github.com/iVis-at-Bilkent/cytoscape.js-fcose/blob/master/src/fcose/spectral.js) implements sampled distance construction and spectral placement rather than leaving initialization entirely to an external library. [cose.js](https://github.com/iVis-at-Bilkent/cytoscape.js-fcose/blob/master/src/fcose/cose.js) then passes constraints into refinement and disables incremental tree reduction when placement constraints are present. This is a concrete interaction between an optimization and constraint preservation; the core refinement machinery is a dependency, not all authored in this repository.

### 19. [gaphor/gaphas](https://github.com/gaphor/gaphas)

**Language/role:** Python; diagramming library with its own **constraint propagation solver** for item geometry and inter-item connections. It contributes a different solving model from linear optimization.

- **C1:** [solver.py](https://github.com/gaphor/gaphas/blob/main/gaphas/solver/solver.py) states variable-strength and modification-order invariants, schedules dirty constraints, and limits repeated resolution to prevent indefinite propagation. Its handling of nested constraints and notifications is part of the model, not incidental UI plumbing.
- **C2:** The [solver guide](https://github.com/gaphor/gaphas/blob/main/docs/solver.rst) connects these abstractions to rectangle handle alignment, centering, and keeping lines attached to shapes. Constraint subclasses implement individual relations while the solver manages propagation during canvas updates.
- **Important semantic limit:** The resolution cap bounds repeated propagation; it does not prove that an arbitrary conflicting system is satisfiable. That distinction follows from the inspected solve loop and is part of the architectural assessment.

### 20. [penrose/penrose](https://github.com/penrose/penrose)

**Language/role:** Primarily TypeScript; mathematical diagram language and **nonlinear layout compiler/optimizer**. Count the monorepo once, with `packages/core` as the relevant engine. Domain, Substance, and Style programs separate concepts, instances, and visual rules.

- **C1:** [Optimizer.ts](https://github.com/penrose/penrose/blob/main/packages/core/src/engine/Optimizer.ts) forms a squared exterior-penalty objective for inequality violations, uses L-BFGS state, and tracks inner versus exterior-penalty convergence and errors. Its comments discuss sensitivity to convergence thresholds and scaling. This is numerical constrained layout; a declared constraint does not imply an exact global-feasibility guarantee.
- **C2:** The language-level `ensure` and `encourage` distinction allows the same engine to generate diagrams from many mathematical domains, while the optimizer accepts a function/gradient interface rather than embedding one diagram vocabulary.
- **C4:** The [core changelog](https://github.com/penrose/penrose/blob/main/packages/core/CHANGELOG.md) records changes across multiple years, including constraint coverage, layout stages, compiler/optimizer workers, non-finite-value fixes in line search, and memory-leak fixes. It provides concrete evidence of managing numerical, language, and runtime complexity.

### 21. [matplotlib/matplotlib](https://github.com/matplotlib/matplotlib)

**Language/role:** Primarily Python; **constrained figure-layout subsystem**, not the whole plotting library. A useful real application of Kiwi in a domain where text measurement, axes ratios, colorbars, and nested figures interact.

- **C2:** [_layoutgrid.py](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/_layoutgrid.py) represents nested grids with per-row/per-column boundaries, editable decoration and colorbar margins, relative interior-size constraints, and a solver shared with parent grids. The abstraction supports different subplot compositions without prescribing individual coordinates.
- **C1:** [_constrained_layout.py](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/_constrained_layout.py) explains and implements the measurement/solve/reposition cycle. It runs the procedure twice because tick-label sizes can change after repositioning, checks for axes collapsing to zero, and resets margins after each pass. Manually placed `add_axes()` axes do not participate, and deliberately overlapping GridSpecs can still overlap: these are documented scope limits of the algorithm.

## Coverage, verification, and limitations

Discovery used more than six distinct live-search formulations, including:

1. Cassowary/Kiwi implementations and layout-oriented solver internals.
2. Rust, Go, Swift, Python, C++, Dart, and C# implementations and continuations.
3. GTK/Emeus, Enaml, Android ConstraintLayout, and declarative widget frameworks.
4. GSS, Auto Layout/VFL, and browser constraint layout.
5. VPSC, Adaptagrams, WebCola, compound graphs, and fCoSE.
6. Auckland Layout Model and tabstop-based layout algebra.
7. Penrose, nonlinear diagram optimization, and constrained scientific figures.
8. OR-constraints, adaptive flow layouts, and branch-and-bound research engines.
9. Propagation-based diagram constraints and compiled dependency-graph engines.
10. Follow-up searches excluding the familiar solver names, plus Haskell/Clojure/Lua and C# searches to probe less visible communities.

The final search rounds increasingly returned already covered families, convenience APIs, demonstration projects, downstream editors, or broad layout libraries outside this scope. They did yield the substantive ORCSolver, Gaphas, and Magnet additions, which were inspected before selection closed. The report is not an exhaustive catalog of every language port.

**Verification:** Each retained canonical GitHub URL was opened as a repository page or verified through the public GitHub repository API. Source paths were checked against repository trees where practical and the linked implementation/documentation files were opened and read; a README fetched twice was not counted as independent evidence. Current branch names are used in entry links, so the cited files may evolve after this research date. For the largest monorepos, inspection was confined to the named subsystem. No candidate repository was cloned, installed, built, benchmarked, or executed.

**Deduplication and exclusions:** The original `cassowary-rs` is represented by Kasuari, and the unmaintained `IjzerenHein/autolayout.js` by its Lume continuation. The [standalone Android ConstraintLayout repository](https://github.com/androidx/constraintlayout) is explicitly archived; the selected AndroidX mirror contains the substantive subsystem. GTK's GitHub repository is explicitly marked as a mirror. Emeus and Rhea were investigated but omitted to avoid additional overlapping historical implementations. SetCoLa was inspected as a high-level compiler, but omitted to keep the graph selections focused on solving and placement. Yoga, Stretch/Taffy-style Flexbox engines, SnapKit-like platform wrappers, generic SMT/LP packages, and experimental Houdini demonstrations were not used to pad the list.

**Limits of the evidence:** C1–C3 judgments are architectural inferences grounded in the cited code and documented behavior, not results of an independent correctness audit. C4 is claimed only where inspected release history supports sustained evolution and concrete compatibility or complexity-management work. Historical code, research artifacts, and production-framework subsystems are deliberately distinguished; neither GitHub popularity nor a non-archived flag establishes current support. Selection favors readable, inspectable implementations and therefore does not represent proprietary platform layout engines or non-GitHub-only projects.
