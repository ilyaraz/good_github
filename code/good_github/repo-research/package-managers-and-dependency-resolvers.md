# Package managers and dependency resolvers

Research date: **2026-10-09**

This guide selects **25 GitHub repositories** covering reusable dependency solvers, language package managers, native binary distribution, scientific environments, and operating-system package transactions. It includes both constraint solving and the machinery that turns a dependency graph into a consistent installation. The emphasis is on code an experienced engineer can study: explicit invariants, reusable models, search strategies, filesystem semantics, and failure handling. Each repository heading links to its verified GitHub location; the nearby primary-source links are reading entry points.

The criteria are selection judgments grounded in the cited material, not a claim that every component is exemplary or that the projects have been independently benchmarked or audited.

- **C1 — Difficult correctness:** dependency invariants, concurrency, adversarial metadata, compatibility semantics, or failure handling.
- **C2 — Reusable abstractions:** substantial models and interfaces supporting different policies, backends, or consumers.
- **C3 — Performance with structure:** concrete search, metadata, storage, or execution costs addressed through understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management. Age alone does not qualify.

## Reusable solver libraries

### 1. [openSUSE/libsolv](https://github.com/openSUSE/libsolv)

**Language / role:** C; package metadata management and SAT-based dependency resolution, with bindings for several languages. Study how a compact repository universe supports solving, diagnostics, and transaction planning across packaging formats.

- **C1:** Correctness extends beyond finding a satisfiable assignment. The project's change history records fixes for transaction ordering, multiversion packages, malformed solv files, overflow checks, and loops in decision introspection. These are useful concrete examples of the failure surface surrounding a solver. [Implementation change history](https://raw.githubusercontent.com/openSUSE/libsolv/master/NEWS).
- **C2:** The bindings manual exposes a coherent model of pools, repositories, solvables, jobs, solvers, problems, and transactions. The same underlying machinery can serve multiple package formats and language frontends rather than encoding one command-line workflow. [Bindings and object-model manual](https://github.com/openSUSE/libsolv/blob/master/doc/libsolv-bindings.txt).

### 2. [prefix-dev/resolvo](https://github.com/prefix-dev/resolvo)

**Language / role:** Rust; an embeddable CDCL package solver. Its repository explicitly describes substantial divergence from its original libsolv port, including a generic ecosystem interface and lazy metadata acquisition; it is included as a separate implementation, not merely a fork with a new name.

- **C1:** Conflict-driven clause learning is paired with types for investigating unsatisfiable problems and reporting their causes. This makes the boundary between internal conflict reasoning and usable diagnostics worth studying. [Crate architecture and public types](https://docs.rs/resolvo/latest/resolvo/).
- **C2 / C3:** `DependencyProvider` separates ecosystem-specific metadata from solving, while serializable dependency snapshots allow problems to be replayed. The solver remains single-threaded, but asynchronous providers can fetch metadata concurrently using a caller-selected runtime; `SolverCache` retains requested or computed information. This addresses metadata latency without conflating parallel I/O with parallel search. [Provider, runtime, snapshot, and cache documentation](https://docs.rs/resolvo/latest/resolvo/).

### 3. [pubgrub-rs/pubgrub](https://github.com/pubgrub-rs/pubgrub)

**Language / role:** Rust; a generic PubGrub implementation. This is a useful comparison with Dart's ecosystem-specific implementation below.

- **C1:** The main resolution loop combines unit propagation, learned incompatibilities, and backtracking. Its provider contract distinguishes unavailable dependency information from an empty dependency set and includes cancellation and provider errors—important distinctions when a mathematical solver meets fallible metadata services. [Solver implementation and provider contract](https://raw.githubusercontent.com/pubgrub-rs/pubgrub/main/src/solver.rs).
- **C2 / C3:** Package identifiers, versions, version sets, priorities, and custom unavailability information are provider-defined. The implementation also uses a compact vector before the first backtrack and switches to deduplicating storage afterward, an unusually accessible example of adapting representation to search behavior. [Generic types and search-state implementation](https://raw.githubusercontent.com/pubgrub-rs/pubgrub/main/src/solver.rs).

### 4. [sarugaku/resolvelib](https://github.com/sarugaku/resolvelib)

**Language / role:** Python; general dependency resolution over opaque requirements and candidates. Study the contract between an ecosystem adapter and a reusable backtracking engine.

- **C2:** The provider defines identity, candidate preference, matching, satisfaction, and dependency expansion. `find_matches` must account for all accumulated requirements and excluded candidates; the resolver need not understand Python distribution metadata or any particular version format. [Provider interfaces](https://raw.githubusercontent.com/sarugaku/resolvelib/main/src/resolvelib/providers.py).
- **C1:** The resolution engine preserves incompatibility information while unwinding states, skips irrelevant states during backjumping, and can restore state after an unsuccessful optimistic backjump. Those mechanisms make it a focused study of maintaining search invariants across failed choices. [Resolution and backjumping implementation](https://raw.githubusercontent.com/sarugaku/resolvelib/main/src/resolvelib/resolvers/resolution.py).

## JavaScript graphs and installation layouts

### 5. [npm/cli](https://github.com/npm/cli)

**Language / role:** JavaScript; npm's CLI monorepo, with **Arborist** as the relevant dependency-graph and installation subsystem. Counted once, including its workspaces.

- **C1:** Arborist distinguishes the logical dependency graph from the physical folder tree. Moving a node updates affected dependency edges; links resolve from their targets; peer dependencies introduce placement validity rules. These are concrete invariants that simple recursive tree models miss. [Arborist graph model](https://github.com/npm/cli/tree/latest/workspaces/arborist).
- **C2:** `Node`, `Link`, and `Edge` expose incoming and outgoing relationships and dependency kinds. Arborist can load actual and lockfile-derived trees, construct an ideal tree, and reify that result on disk. The shared graph model connects inspection, planning, pruning, and installation rather than duplicating them in CLI commands. [Arborist API and tree operations](https://github.com/npm/cli/tree/latest/workspaces/arborist).

### 6. [pnpm/pnpm](https://github.com/pnpm/pnpm)

**Language / role:** Primarily TypeScript, with Rust components; JavaScript package management built around a shared content store and explicit dependency layouts.

- **C1:** A package version may need multiple installed instances when its peer dependency contexts differ, including differences inherited through dependencies. The peer-resolution documentation shows how separate contexts become separate linked occurrences. [Peer dependency resolution](https://pnpm.io/how-peers-are-resolved).
- **C3:** The documented layout hard-links package files from a content-addressable store and uses symlinks to represent dependencies. It supports self-imports, avoids circular symlinks, and keeps filesystem nesting depth independent of dependency-graph depth while respecting Node's resolution behavior. This is a concrete storage-and-path design to study; hoisting configuration still affects dependency visibility. [Symlinked node_modules structure](https://pnpm.io/symlinked-node-modules-structure).

### 7. [yarnpkg/berry](https://github.com/yarnpkg/berry)

**Language / role:** TypeScript; modern Yarn, distinct from Yarn Classic. Study the boundaries between selecting packages, obtaining their contents, and exposing them to a runtime.

- **C2:** The architecture separates `Resolver`, `Fetcher`, and `Linker`/`Installer` responsibilities. Fetchers return filesystem abstractions that can represent archives or directories, while linkers implement installation strategies. Plugins participate through shared project, workspace, configuration, and cache models. [Architecture guide](https://yarnpkg.com/advanced/architecture).
- **C1:** Peer dependencies require a package to be interpreted in the context of its consumers. Yarn represents these distinctions with virtual packages rather than treating a package name and version as a sufficient identity. The architecture guide connects that identity model to the resolution and linking pipeline. [Resolution stages and virtual packages](https://yarnpkg.com/advanced/architecture).

## Python package management

### 8. [pypa/pip](https://github.com/pypa/pip)

**Language / role:** Python; installer and resolver integrating package discovery, compatibility checks, metadata generation, and installation.

- **C1 / C2:** The resolver architecture separates candidate finding, the provider adapter, and the generic resolvelib engine. Backtracking must operate with metadata that may be discovered only after fetching or building a candidate, while respecting Python and distribution compatibility. This is a good study of an apparently simple install request crossing several fallible subsystems. [Dependency resolution internals](https://pip.pypa.io/en/stable/topics/more-dependency-resolution/).
- **C4:** The changelog documents the 2020 resolver transition and follow-up fixes for looping, extras, and yanked releases, alongside later compatibility and deprecation work through 2026. Restoring a removed build-directory option as a no-op for compatibility is a particularly concrete example of migration management. [Dated changelog](https://pip.pypa.io/en/stable/news/).

### 9. [astral-sh/uv](https://github.com/astral-sh/uv)

**Language / role:** Rust; Python package and project management. Focus on its universal resolver and the integration of PubGrub with Python metadata semantics.

- **C1:** Universal resolution forks the marker space when requirements differ by Python version or platform, including regions not covered by explicit alternatives. Equivalent branches can be merged, and persisted resolution markers help stabilize subsequent lockfile resolutions. The documented assumption that distributions for a release have consistent metadata is a meaningful boundary of this model. [Resolver internals](https://docs.astral.sh/uv/reference/internals/resolver/).
- **C3:** The implementation combines background metadata prefetching, preferences for existing locked or installed versions, deterministic package priorities, and heuristics that change decision ordering after repeated conflicts. The documentation explains why these decisions reduce I/O waiting or fruitless search without requiring unsupported benchmark claims. [Search and prefetch strategy](https://docs.astral.sh/uv/reference/internals/resolver/).

## Language-specific resolution models

### 10. [rust-lang/cargo](https://github.com/rust-lang/cargo)

**Language / role:** Rust; Rust's package manager and build orchestrator. The relevant subsystem is dependency and feature resolution; the repository does not promise a stable general-purpose embedding API.

- **C1:** Cargo's resolver tries to unify semver-compatible requirements, can retain incompatible versions separately, and must account for the resulting crate type identities. Lockfile preferences and version constraints interact with backtracking rather than being independent post-processing steps. [Resolver reference and pseudocode](https://doc.rust-lang.org/cargo/reference/resolver.html).
- **C3:** Dependency visitation and version choice affect how much backtracking is required. Reusing a compatible version can also avoid duplicate builds. The reference makes these two cost surfaces—resolution search and the resulting build graph—visible in the algorithm's structure. [Resolution policies and version unification](https://doc.rust-lang.org/cargo/reference/resolver.html).

### 11. [composer/composer](https://github.com/composer/composer)

**Language / role:** PHP; PHP dependency manager with a SAT-oriented resolution engine. Useful for studying solver machinery in an application language rather than only in C or Rust.

- **C1:** Root requirements and fixed packages become assertions. The solver tracks decisions, conflicts, learned rules, and assertion failures, including recovery paths when conflicting assertions must be disabled or reported. These mechanics expose the relationship between user requests and satisfiability diagnostics. [DependencyResolver/Solver.php](https://raw.githubusercontent.com/composer/composer/main/src/Composer/DependencyResolver/Solver.php).
- **C2:** Policy, package pool, rule sets, watched-rule graph, decisions, and problem reporting have separate responsibilities. The solver's constructor and control flow make their collaboration concrete, allowing package-selection policy and repository contents to vary around the core reasoning engine. [Solver collaborators and state](https://raw.githubusercontent.com/composer/composer/main/src/Composer/DependencyResolver/Solver.php).

### 12. [dart-lang/pub](https://github.com/dart-lang/pub)

**Language / role:** Dart; Dart package management and the original PubGrub implementation. Its algorithm document is one of the clearest entry points for learning explainable dependency solving.

- **C1:** The solver specification states the required properties of a solution: one selected version per package, satisfied dependencies, and reachability from the root. Terms, incompatibilities, partial solutions, and derivations make these invariants explicit and provide the material for human-readable failure explanations. [PubGrub solver design](https://raw.githubusercontent.com/dart-lang/pub/master/doc/solver.md).
- **C3:** Conflict analysis learns incompatibilities and backjumps over decisions that cannot repair the conflict. The design explains how avoiding repeated exploration of the same dead ends addresses the combinatorial cost of version search, rather than merely presenting a recursive implementation. [Conflict learning and backtracking design](https://raw.githubusercontent.com/dart-lang/pub/master/doc/solver.md).

### 13. [ocaml/opam](https://github.com/ocaml/opam)

**Language / role:** OCaml; source package manager with compiler switches, conditional dependency formulas, and solver backends.

- **C1:** Dependency filters and version constraints are distinct evaluation stages. Optional dependencies can affect ordering and rebuilds without forcing installation; post dependencies can relax build-order cycles. These semantics make opam useful for studying how build-time and installed-state requirements differ. [Package formulas and dependency semantics](https://opam.ocaml.org/doc/Manual.html).
- **C2:** The API documentation separates core, format, repository, solver, state, and client libraries. The solver layer translates package universes to CUDF and produces action graphs, while state and job machinery handle installed switches and execution. This gives several substantive boundaries for alternative solvers and frontends. [Library and module architecture](https://opam.ocaml.org/doc/api/).

### 14. [haskell/cabal](https://github.com/haskell/cabal)

**Language / role:** Haskell; Cabal libraries and cabal-install, including the **cabal-install-solver** subsystem. Counted once as a monorepo.

- **C1:** The project configuration reference distinguishes hard constraints, package flags, and soft preferences. Its description of local preference optimality is deliberately narrower than global optimality, an instructive example of specifying precisely what a resolver promises. [Constraints and preferences](https://cabal.readthedocs.io/en/latest/cabal-project-description-file.html).
- **C3:** The modular solver exposes backjump limits, goal reordering, conflict counting, fine-grained conflict handling, and optional conflict-set minimization. The documentation describes tradeoffs: a heuristic can improve difficult instances while slowing ordinary ones, and better error minimization may consume additional solving time. [Solver configuration and tradeoffs](https://cabal.readthedocs.io/en/latest/cabal-project-description-file.html).

### 15. [JuliaLang/Pkg.jl](https://github.com/JuliaLang/Pkg.jl)

**Language / role:** Julia; Julia package management. The `Resolve` module provides a contrasting graph-and-max-sum approach to the SAT and PubGrub implementations in this guide.

- **C1:** The implementation represents required and fixed versions, checks hard constraints through `verify_solution`, and distinguishes an unsatisfiable result from a timeout. Its improvement loop maintains lower bounds and includes checks against cycling; these are valuable implementation-level invariants, not a claim of formal verification. [Resolve module](https://raw.githubusercontent.com/JuliaLang/Pkg.jl/master/src/Resolve/Resolve.jl).
- **C3:** A greedy attempt handles straightforward graphs before invoking the max-sum machinery. Graph sanity checking propagates constraints, removes unreachable structure, prunes, and groups equivalent versions. The sequence shows where preprocessing and cheap successful cases can reduce expensive search. [Resolution and graph-simplification orchestration](https://raw.githubusercontent.com/JuliaLang/Pkg.jl/master/src/Resolve/Resolve.jl).

## JVM artifact resolution

### 16. [coursier/coursier](https://github.com/coursier/coursier)

**Language / role:** Scala; Maven/Ivy dependency resolution and artifact retrieval, usable through libraries and command-line tools.

- **C2:** High-level `Resolve` and `Fetch` APIs sit above an immutable low-level resolution model. The core can be driven with different effect types, while artifact fetching and caching are separate concerns. This is a useful study of an effect-independent graph algorithm embedded in an I/O-heavy application. [High-level API](https://get-coursier.io/docs/api) and [low-level architecture](https://get-coursier.io/docs/api-low-level).
- **C3:** The cache layer controls metadata freshness and download execution separately from dependency selection, including configurable thread pools and TTL behavior. The low-level interface makes iteration completion and metadata errors explicit, allowing callers to manage network cost without treating partial graph expansion as successful resolution. [Cache and resolution-process API](https://get-coursier.io/docs/api-low-level).

### 17. [apache/maven-resolver](https://github.com/apache/maven-resolver)

**Language / role:** Java; reusable artifact repository and dependency-resolution infrastructure used by Maven and other consumers. **Official GitHub mirror:** Apache's source index lists this repository alongside its GitBox repository; the GitHub project also accepts pull requests. [Official repository index](https://maven.apache.org/scm.html).

- **C2:** Dependency collection first constructs a graph that may contain conflicts and cycles. Selectors, managers, traversers, version filters, and graph transformers apply separate policies before the resolved graph drives artifact retrieval. The distinction between graph collection and artifact resolution is central to its reusable design. [Transitive dependency-resolution architecture](https://maven.apache.org/resolver/transitive-dependency-resolution.html).
- **C1:** Named locks protect shared repository state across threads, processes, or distributed deployments. Shared/exclusive modes, forbidden lock upgrades, interruption handling, and filesystem-specific caveats make concurrency requirements explicit. The documentation also explains why a cross-process implementation needs a shared name mapping rather than arbitrary in-memory identities. [Named-lock architecture](https://maven.apache.org/resolver/maven-resolver-named-locks/index.html).

## System packages and scientific environments

### 18. [NixOS/nix](https://github.com/NixOS/nix)

**Language / role:** Primarily C++; functional package management centered on store objects and derivations. Included for dependency identity, storage, and realization rather than conventional semver SAT solving.

- **C1:** Store objects are immutable; references obey a closure property, and the reference graph is acyclic apart from permitted self-reference. The manual distinguishes references represented in an object's contents from externally recorded references. Those details are central to reasoning about copying, retaining, and realizing dependency closures. [Store-object model](https://nix.dev/manual/nix/2.35/store/store-object).
- **C2:** Store objects and derivations provide common representations for build inputs, results, and dependencies. The store abstraction supports different backends, including local stores and binary caches, so higher layers need not reduce dependency management to a particular filesystem directory. [Store architecture](https://nix.dev/manual/nix/2.35/store/).

### 19. [spack/spack](https://github.com/spack/spack)

**Language / role:** Python with answer-set-programming integration; package concretization and builds for scientific and HPC environments. Focus here is the engine, not the separately maintained package-recipe catalog.

- **C1:** An abstract package specification can leave versions, compilers, and variants open. Environment concretization must decide whether all roots share one instance of each package, share when possible, or solve independently; those choices change whether conflicting variants are admissible. Existing concrete specifications can remain fixed until explicitly reconcretized. [Environment concretization semantics](https://spack.readthedocs.io/en/latest/environments.html).
- **C3:** The solve command exposes optimization criteria and distinguishes solving together from solving in rounds. Its handling of build versus reuse objectives makes the practical cost of a solution part of the architecture, beyond merely finding a satisfiable assignment. [Solve command implementation](https://spack.readthedocs.io/en/latest/_modules/spack/cmd/solve.html).

### 20. [conda/conda](https://github.com/conda/conda)

**Language / role:** Python; cross-language environment and binary package management. Study the environment-state model and solver integration, without assuming every backend uses the same search algorithm.

- **C1:** A solve is influenced by installed packages, explicit-request history, pins, default packages, and update policy. The deep-dive documentation shows how those constraints are assembled before computing a new environment and its changes. Preserving user intent across updates is therefore part of correctness, not simply a final version comparison. [Solver deep dive](https://raw.githubusercontent.com/conda/conda/main/docs/source/dev-guide/deep-dives/solvers.md).
- **C2:** `MatchSpec` expresses queries; package, cache, and prefix records represent different states of artifacts. The solver interface separates final-state solving, change computation, and transaction construction. These distinctions support multiple backends and connect package selection to an existing installation. [Record models and solver interfaces](https://raw.githubusercontent.com/conda/conda/main/docs/source/dev-guide/deep-dives/solvers.md).

### 21. [mamba-org/mamba](https://github.com/mamba-org/mamba)

**Language / role:** C++ with bindings; Conda-compatible package management, including libmamba and micromamba. Counted once. Its value here is the integration of a solver with transport, archives, and transactions.

- **C1:** The internals connect Conda MatchSpecs to libsolv rules and explain package exclusivity and dependency satisfaction. Transaction ordering matters after solving too: a dependency must be available before scripts or Python noarch handling that rely on it. [Solver and transaction internals](https://mamba.readthedocs.io/en/latest/developer_zone/internals.html).
- **C3:** The architecture combines libsolv's pool identifiers and indexed provider lookup with download and archive components. Parallel downloading is separated from the solver's compact package universe. This is a useful integration study of network throughput, metadata representation, and dependency reasoning without treating them as one optimization problem. [Internal components and data structures](https://mamba.readthedocs.io/en/latest/developer_zone/internals.html).

### 22. [rpm-software-management/dnf5](https://github.com/rpm-software-management/dnf5)

**Language / role:** C++, with language bindings; RPM package management built around **libdnf5** and its command-line consumers.

- **C2:** Callers populate a `Goal`, resolve a `Transaction`, download its packages, and run it. Library callbacks expose progress and mirror failures across these stages. This is a substantial reusable workflow for applications embedding package management. [Transaction tutorial](https://dnf5.readthedocs.io/en/stable/tutorial/transaction.html).
- **C1:** Resolution problems are recorded in the transaction and inspected through problem and log APIs rather than necessarily appearing as thrown exceptions. The migration documentation also specifies callback ownership differences between C++ and bindings. Both details matter when a frontend must stop on a failed plan and keep callback state valid. [Transaction API changes and error handling](https://dnf5.readthedocs.io/en/latest/tutorial/api-changes/transaction.html).

### 23. [void-linux/xbps](https://github.com/void-linux/xbps)

**Language / role:** C; Void Linux's binary package system, with libxbps and several frontends. A comparatively compact entry point for studying operating-system package transactions.

- **C1:** Transaction preparation gathers dependencies, processes replacements, checks reverse dependencies, detects package conflicts, and checks shared-library requirements. The implementation distinguishes missing dependencies, conflicts, and unresolved libraries through different errors; explicit force modes are visible exceptions to normal checks. [Transaction preparation implementation](https://raw.githubusercontent.com/void-linux/xbps/master/lib/transaction_prepare.c).
- **C2:** A structured transaction dictionary carries packages, missing dependencies, conflicts, obsolete files, and size statistics. Preparation produces a dictionary marked immutable, providing a clear boundary between assembling a plan and consuming it through the library's frontends. This is a useful alternative to large object-oriented transaction frameworks. [Transaction representation and finalization](https://raw.githubusercontent.com/void-linux/xbps/master/lib/transaction_prepare.c).

## Native library packages and binary compatibility

### 24. [conan-io/conan](https://github.com/conan-io/conan)

**Language / role:** Python; C and C++ package management with an explicit binary-compatibility model. Study the distinction between resolving a recipe version and identifying a usable binary built from it.

- **C1:** Package identity incorporates settings, options, and dependency information. Whether dependency changes invalidate a consumer depends on how code is used: embedding static or header-only content differs from dynamically linking to a shared library. The dependency-mode documentation specifies these distinctions and their consequences for package IDs. [Dependency effects on binary identity](https://docs.conan.io/2/reference/binary_model/dependencies.html).
- **C2:** The package-ID model is configurable through recipe and configuration policies, allowing different compatibility rules for compilers, architectures, library types, and dependencies. This is a substantial abstraction over binary reuse, rather than one hard-coded checksum of a manifest. [Package-ID model](https://docs.conan.io/2/reference/binary_model/package_id.html).

### 25. [microsoft/vcpkg-tool](https://github.com/microsoft/vcpkg-tool)

**Language / role:** C++; the vcpkg executable and dependency-planning engine. The package catalog in `microsoft/vcpkg` is not counted as a second implementation.

- **C1:** Versioning combines registry baselines, lower bounds, explicit overrides, and version schemes that are not always mutually comparable. Its policy of choosing the lowest satisfying version differs materially from a universal newest-version strategy. [Versioning rules](https://learn.microsoft.com/en-us/vcpkg/users/versioning).
- **C2:** The implementation models package clusters, feature dependencies, installed state, and proposed installation state separately. Feature edges and platform-variable evaluation feed planning, including default-feature and reinstall behavior. This supports the combination of feature selection, existing installations, and target/host distinctions needed by native dependency management. [Dependency graph and planning implementation](https://raw.githubusercontent.com/microsoft/vcpkg-tool/main/src/vcpkg/dependencies.cpp).

## Coverage, search method, and limitations

Discovery used live web searches with multiple independent formulations, followed by opening repository roots and additional primary material. Search angles included:

- General package-solver architecture: SAT, CDCL, PubGrub, lazy metadata, and reusable provider interfaces.
- JavaScript package graphs: npm Arborist, peer dependencies, symlink layouts, content stores, and resolver/fetcher/linker separation.
- Python and compiled-language resolution: backtracking, environment markers, Cargo unification, Composer rules, opam formulas, Cabal solver controls, and Julia graph solving.
- Scientific environments: Spack concretization and Conda/Mamba solver and transaction architecture.
- Functional and operating-system package management: Nix stores, Linux package transactions, XBPS, and DNF libraries.
- Native binary packages: Conan ABI/package identity and vcpkg version, feature, and platform planning.
- JVM artifact ecosystems: Maven/Ivy graphs, Coursier effects and caching, and Maven Resolver concurrency.

These were separate discovery searches, not just searches for a predetermined list of repository names. Later, more specific searches mostly returned implementations already represented or adjacent catalogs and frontends, giving diminishing returns in distinct architectural coverage. Every retained repository had its GitHub root opened, and at least one additional primary document or implementation file was opened and read. Search snippets alone were not used to qualify an entry. Raw source links above identify files that were actually inspected; they are not guessed branch paths.

The selection deliberately includes smaller libraries alongside complete managers. Shared ancestry or algorithms are called out where material: Resolvo has a documented independent evolution from libsolv; the Rust and Dart PubGrub implementations serve different embedding contexts; Conda, Mamba, and libsolv are separate implementations or integration layers. Monorepos and their bundled tools are counted once. Package catalogs, awesome lists, tutorials, thin command wrappers, and generic SAT libraries without a substantive package-resolution focus were excluded.

This is not exhaustive: Ruby, Go, .NET, Lua, and some operating-system communities are underrepresented. Projects primarily hosted elsewhere were not added on the strength of an unverified GitHub mirror; Maven Resolver's verified official mirror is explicitly identified. No retained entry is being recommended merely as a historical archive or unofficial mirror. Repository identity and category fit were checked, but the report does not infer current maintenance quality from stars, recent pushes, or a creation date. **C4 is used sparingly where dated compatibility evidence was actually read.**

Documentation spans published versions and moving development branches; Nix's cited manual is explicitly versioned. Some direct source pages were unavailable through the browser, so the corresponding entries use successfully retrieved official architecture or API documentation instead. No candidate code was executed, installed, or benchmarked. Performance discussions identify mechanisms and tradeoffs; the source-selection judgments remain grounded in inspected material rather than measured comparisons between projects.
