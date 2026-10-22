# Plugin systems and component lifecycle frameworks

Research date: **2026-10-09**

This selection covers reusable machinery for discovering extensions, dispatching hooks, composing services, loading modules, and managing component activation and teardown. It includes both dynamic plugin systems and frameworks that manage the lifecycle of statically assembled application components. The 23 repositories range from compact libraries to OSGi implementations; relevant subsystems are identified for broader repositories. These are engineering study recommendations, not a claim that every component is uniformly exemplary or that every project offers isolation, hot reload, or automatic recovery.

Criteria legend:

- **C1 — Correctness:** demanding invariants, concurrency, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or mechanisms supporting different applications.
- **C3 — Performance and structure:** concrete performance constraints addressed through understandable architectural choices.
- **C4 — Evolution:** documented evolution over years, with compatibility, testing, or complexity management evidence.

## Hook dispatch and Python extension frameworks

### 1. [pytest-dev/pluggy](https://github.com/pytest-dev/pluggy)

**Language/role:** Python; hook specification, registration, and execution framework used by pytest, tox, and devpi.

Study how a small public abstraction supports many independently developed extensions. **C2:** host-defined hook specifications and plugin implementations separate the extension contract from registration and dispatch. **C1:** the execution engine must combine ordinary implementations, first-result short circuiting, and two generations of generator wrappers while preserving exceptions and unwinding wrappers in reverse order. Its handling of missing arguments, missing or extra yields, and `StopIteration` makes the failure semantics particularly instructive. Start with the [execution engine](https://github.com/pytest-dev/pluggy/blob/main/src/pluggy/_execution.py).

**C4:** the [changelog](https://github.com/pytest-dev/pluggy/blob/main/CHANGELOG.rst) records staged deprecations around the 2021 1.0 release, the withdrawal of 1.1 after wrapper compatibility failures, explicit opt-in wrappers in 1.2, compatibility aliases in 1.3, and exception-related fixes in 2025. This is concrete evidence of maintaining a widely extended contract rather than simply an old repository.

### 2. [openstack/stevedore](https://github.com/openstack/stevedore)

**Language/role:** Python; extension discovery and invocation built on Python package entry points. **Official GitHub mirror:** development is maintained on OpenDev, as the repository explicitly states.

Study the separation between discovering a plugin, loading its object, instantiating it, selecting it, and invoking it. **C2:** driver, hook, named, enabled, and dispatch managers express different selection and cardinality patterns without requiring applications to implement their own import mechanism. The [API reference](https://docs.openstack.org/stevedore/latest/reference/index.html) also exposes test-instance constructors that bypass installed-package discovery.

**C1:** name collisions, missing entry points, import or construction failures, and exceptions during extension mapping are separate policy decisions. The [extension implementation](https://github.com/openstack/stevedore/blob/master/stevedore/extension.py) makes conflict resolution configurable and distinguishes load-failure callbacks from propagation during `map`. This is useful for studying partial failure in extensible applications; it should not be mistaken for a sandbox or a complete service lifecycle container.

### 3. [webpack/tapable](https://github.com/webpack/tapable)

**Language/role:** JavaScript; reusable hook execution machinery underlying webpack's plugin model.

Study a plugin API whose execution strategy is compiled from its registrations. **C2:** synchronous, asynchronous series, asynchronous parallel, bail, loop, and waterfall hooks give hosts explicit composition semantics; registration ordering and interceptors add extension points around dispatch itself. The repository's overview explains these distinct contracts.

**C3:** the implementation specializes generated functions for the call convention, arguments, registered tap types, and interception requirements instead of interpreting the whole configuration on every invocation. **C1:** that specialization must still preserve error propagation and completion semantics across callbacks and promises. The [code generator](https://github.com/webpack/tapable/blob/main/lib/HookCodeFactory.js) is the primary reading entry: compare its synchronous, callback, and promise branches. The engineering attraction is the visible connection between dispatch overhead and generated control flow; no numerical speedup is assumed here.

### 4. [tcalmant/ipopo](https://github.com/tcalmant/ipopo)

**Language/role:** Python; Pelix bundle/service framework and iPOPO service-oriented component model, counted together as one repository.

Study how service availability changes the validity of already instantiated components. **C2:** factories, component instances, dependency handlers, service specifications, and validation callbacks provide a reusable model for applications whose providers appear and disappear at runtime. The [component reference](https://ipopo.readthedocs.io/en/latest/refcards/ipopo.html) distinguishes instantiated, validated, killed, and erroneous components, including retry after failed validation.

**C1:** the [instance manager](https://github.com/tcalmant/ipopo/blob/v3/pelix/ipopo/instance.py) coordinates binding and lifecycle checks under a reentrant lock. It invalidates components when handlers become unsatisfied, guards against resurrecting killed instances, and converts failed validation into an explicit erroneous state after cleanup. The ordering of dependency removal, invalidation callbacks, rebinding, and service publication is the substantive material to study.

### 5. [enthought/envisage](https://github.com/enthought/envisage)

**Language/role:** Python; application framework organized around plugins, extension points, and shared services.

Study the distinction between contributing extension data and publishing executable services. **C2:** the [service registry documentation](https://docs.enthought.com/envisage/envisage_core_documentation/services.html) describes lookup by protocol, property queries, and selection through minimization or maximization; services can be ordinary Python objects. This supports reusable collaboration among plugins without requiring every object to inherit a framework base class.

**C4:** the [release history](https://docs.enthought.com/envisage/changelog.html) records concrete lifecycle and compatibility work across years: the 2023 release moved plugin shutdown until after the GUI event loop exited, added extension-point unbinding, and deprecated older plugin managers; the August 2026 release removed reliance on `pkg_resources` to restore compatibility with current packaging tools. Envisage is a useful smaller-community counterpart to the JVM platforms below, particularly for studying maintenance of extensible desktop applications.

## JVM module and service runtimes

### 6. [pf4j/pf4j](https://github.com/pf4j/pf4j)

**Language/role:** Java; plugin manager with extension discovery, dependency metadata, and explicit plugin states.

Study the interaction between lifecycle state and class identity. **C1:** only started plugins should contribute extensions; disabled plugins may still have class loaders, so discovery and eligibility cannot be treated as equivalent. Host-version requirements also prevent loading extensions against incompatible application APIs. These rules are documented in the [plugin lifecycle guide](https://pf4j.org/doc/plugin-lifecycle.html).

**C2:** plugin loaders, descriptor finders, extension factories, and managers can be replaced independently. The [class-loading guide](https://pf4j.org/doc/class-loading.html) explains per-plugin loaders, the default parent-last strategy, special treatment of Java and framework classes, and delegation through plugin dependencies. This offers a bounded codebase for studying extensibility below a full OSGi platform, while retaining the hard problem of which loader owns a shared interface.

### 7. [apache/felix-dev](https://github.com/apache/felix-dev)

**Language/role:** Java; Apache Felix monorepo. Relevant subsystems are `framework`, `scr`, and especially `dependencymanager`; these are one selection, not separate repositories.

Study how dynamic service events can be serialized for each component without forcing the entire application onto one thread. **C1:** the [Dependency Manager thread model](https://felix.apache.org/documentation/subprojects/apache-felix-dependency-manager/reference/thread-model.html) specifies a per-component serial queue for lifecycle callbacks and dependency injection, including events arriving while another thread is processing that queue. **C3:** an executor factory permits independent components to activate concurrently while preserving each component's callback ordering; the documentation also identifies the bootstrap dependency problem when the executor factory itself uses managed components.

**C2:** the [DependencyManager API](https://felix.apache.org/documentation/_attachments/apidocs/dependencymanager/r15/org/apache/felix/dm/DependencyManager.html) separates components from the services and other dependencies controlling them. Follow the documentation into the monorepo when comparing imperative Dependency Manager composition with declarative services and the underlying OSGi runtime.

### 8. [eclipse-equinox/equinox](https://github.com/eclipse-equinox/equinox)

**Language/role:** Java, with native support code; Eclipse's OSGi framework and associated services. Focus on the `org.eclipse.osgi` bundle container.

Study the state machine behind installation, resolution, activation, stopping, and module revisions. **C1:** [Module.java](https://github.com/eclipse-equinox/equinox/blob/master/bundles/org.eclipse.osgi/container/src/org/eclipse/osgi/container/Module.java) explicitly validates nested state transitions, bounds lock acquisition, reports state-change failures, and preserves interruption information. Lazy activation has to account for an activation already in progress on the current thread.

**C2:** [ModuleContainer.java](https://github.com/eclipse-equinox/equinox/blob/master/bundles/org.eclipse.osgi/container/src/org/eclipse/osgi/container/ModuleContainer.java) separates the container adaptor, module database, resolver, framework wiring, and start-level machinery. Those boundaries make this useful beyond reading Eclipse IDE code: the repository implements a reusable OSGi runtime. It is a larger and more specification-driven study than PF4J, with lifecycle transitions integrated into resolution and module identity.

## Native modules and service components

### 9. [apache/celix](https://github.com/apache/celix)

**Language/role:** C/C++; dynamic bundles, an in-process service registry, and a dependency manager inspired by OSGi.

Study how native objects can have their lifetime governed by changing service dependencies. **C1:** the [component guide](https://celix.apache.org/docs/2.3.0/celix/documents/components.html) details waiting, initialization, suspension, resumption, and stopping states. Required-service loss affects activation, and lifecycle callbacks run on the Celix event thread; service changes may require withdrawing a component's own services before rebinding.

**C2:** plain C structs or C++ objects can provide or consume services through separate bundle, registry, and dependency-manager APIs. The [service guide](https://celix.apache.org/docs/2.3.0/celix/documents/services.html) explains registration, tracking, and serialized event processing. The useful engineering contrast with Felix is the explicit coordination of native object destruction and a framework event thread. These linked guides describe release 2.3.0; the repository's current branch can contain later APIs.

### 10. [CppMicroServices/CppMicroServices](https://github.com/CppMicroServices/CppMicroServices)

**Language/role:** C++; OSGi-inspired bundle lifecycle and dynamic service registry, with additional services in `compendium`.

Study reentrant registry behavior and the difference between obtaining a service and tracking its continued availability. **C1:** the [service-hook architecture](https://docs.cppmicroservices.org/en/stable/framework/doc/service_hooks.html) documents synchronous callbacks from arbitrary caller threads, a requirement for reentrancy, and the possibility that listener removal is reported before addition. Its `ListenerInfo::IsRemoved` mechanism makes the ordering problem concrete rather than assuming callbacks form a simple sequence.

**C2:** bundles, service references, listeners, and hooks support reusable providers and consumers as well as proxying and on-demand services. The [robust client walkthrough](https://docs.cppmicroservices.org/en/stable/doc/src/tutorial/Example4.html) follows service arrival and departure through actual C++ code. It explicitly leaves synchronization to the example's integrator, so it is architectural teaching material rather than a complete production concurrency recipe. The linked stable documentation identifies itself as 3.7.4.

### 11. [mosra/corrade](https://github.com/mosra/corrade)

**Language/role:** C++; broader utility library, selected specifically for `Corrade::PluginManager`.

Study native plugin ownership with both static and dynamic linking. **C1:** the [manager reference](https://doc.magnum.graphics/corrade/classCorrade_1_1PluginManager_1_1Manager.html) distinguishes loading from instantiation, prevents ordinary unloading while instances or dependents remain, and explains the special deletion and pointer-release obligations for hot reload. These rules expose why unloading a shared library is an object-lifetime problem, not merely a call to the operating system loader.

**C2:** typed plugin interfaces, metadata, aliases, static-plugin registration, dynamic discovery, and explicitly registered dependencies between managers form reusable machinery. The [plugin-management guide](https://doc.magnum.graphics/corrade/plugin-management.html) connects interface declarations and version checks to build-system registration. Corrade is particularly useful for understanding a plugin subsystem that remains separable from the graphics applications that use it.

### 12. [GNOME/libpeas](https://github.com/GNOME/libpeas)

**Language/role:** C/GObject; plugin engine with language-specific loaders and GObject extension interfaces. **Official read-only GitHub mirror** of GNOME GitLab.

Study the distinction between a user-visible plugin package and the multiple extension objects it can supply. **C2:** the [engine API](https://gnome.pages.gitlab.gnome.org/libpeas/libpeas-2/class.Engine.html) separates plugin discovery, loader enabling, extension construction, and loaded-plugin configuration. Applications define their own extension interfaces rather than sharing one universal plugin class.

**C1:** [peas-engine.c](https://github.com/GNOME/libpeas/blob/main/libpeas/peas-engine.c) marks transitions before recursive dependency traversal to avoid infinite recursion, records missing or failed dependencies, unloads dependent plugins first, and destroys loaders after unloading plugins during disposal. **C3:** language loaders are enabled on demand, avoiding the cost of loading an interpreter when its plugins are unused, as the repository overview explains. This is a substantive mirror with implementation code, not a pointer-only replacement repository.

## Process boundaries, WebAssembly, ABI contracts, and .NET composition

### 13. [hashicorp/go-plugin](https://github.com/hashicorp/go-plugin)

**Language/role:** Go; subprocess plugins communicating through `net/rpc` or gRPC.

Study why process management and RPC-interface management are separate responsibilities. **C1:** [client.go](https://github.com/hashicorp/go-plugin/blob/main/client.go) coordinates plugin processes, management goroutines, pipe draining, startup timeouts, version negotiation, and cleanup. Its wait groups distinguish subprocess-management completion from finishing stdout/stderr reads; configuration also distinguishes launching a process from reattaching to one.

**C2:** plugin interfaces, versioned plugin sets, RPC brokers, and reattachment support multiple hosts and, through gRPC, multiple implementation languages. The [server implementation](https://github.com/hashicorp/go-plugin/blob/main/server.go) is the companion entry for understanding the handshake and protocol boundary. The repository expressly limits this design to local reliable communication. Subprocess separation prevents a plugin panic from directly panicking the host, but this library should not be read as providing an operating-system sandbox or a general distributed RPC platform.

### 14. [extism/extism](https://github.com/extism/extism)

**Language/role:** Rust with a C-facing interface; WebAssembly plugin runtime. This entry covers the central runtime, not each language SDK as another project.

Study the lifecycle of compiled code, runtime stores, plugin instances, and calls across a host/guest boundary. **C1:** [runtime/src/plugin.rs](https://github.com/extism/extism/blob/main/runtime/src/plugin.rs) handles fuel configuration, epoch interruption, cancellation, runtime reset, and rejection of reentrant calls. Its instance accounting explicitly addresses memory retained until a Wasmtime store is released.

**C2:** a common plugin interface and injected [host functions](https://extism.org/docs/concepts/host-functions/) let different hosts offer controlled application capabilities to guest code. The host-function documentation specifies signatures, type translation, and user-data lifetime. **C3:** a separate `CompiledPlugin` representation and compilation-cache configuration expose reusable compiled code independently of execution state. These mechanisms make the repository useful for studying sandboxed extensibility, while the permissions and host functions an application exposes remain part of that application's design.

### 15. [rodrimati1992/abi_stable_crates](https://github.com/rodrimati1992/abi_stable_crates)

**Language/role:** Rust; Rust-to-Rust FFI and runtime-loaded library infrastructure, including `abi_stable` and its derive machinery.

Study compatibility at the binary boundary rather than discovery alone. **C1:** the [root-module loader](https://github.com/rodrimati1992/abi_stable_crates/blob/master/abi_stable/src/library/root_mod_trait.rs) checks the library header and expected layout before initializing a root module. It deliberately retains loaded libraries to prevent references into them from becoming dangling. **Unloading is explicitly unsupported**; this is a meaningful architectural constraint, not an omitted convenience.

**C2:** the repository provides FFI-safe standard-type equivalents, generated trait objects, prefix types for extensible interfaces, and a separation among interface, implementation, and application crates. These allow multiple native plugins to share typed contracts without depending on Rust's unstable default ABI. The useful study is how layout checks and ownership restrictions cooperate; this is not an isolation boundary for executing untrusted native code.

### 16. [microsoft/vs-mef](https://github.com/microsoft/vs-mef)

**Language/role:** C#; Managed Extensibility Framework implementation, especially `Microsoft.VisualStudio.Composition`.

Study the separation among part discovery, immutable catalogs, composition graphs, and mutable export-provider lifetimes. **C1:** the [hosting guide](https://microsoft.github.io/vs-mef/docs/hosting.html) explains cardinality validation, cascading rejection of invalid parts, diagnostic root causes, and disposal concerns. **C2:** discovery adapters bring two MEF attribute families into a common model, and export providers own instantiated parts and scoped lifetimes.

**C3:** the [design rationale](https://microsoft.github.io/vs-mef/docs/why.html) connects Visual Studio's startup and composition costs to precomputed, validated, serializable graphs. Reloading that cache avoids rediscovering and recomposing assemblies on every startup. This is an architectural tradeoff worth studying: VS-MEF emphasizes a complete composition graph, rather than providing the original MEF's dynamic recomposition facility. It is a reusable library that can be hosted independently of Visual Studio.

### 17. [natemcmaster/DotNetCorePlugins](https://github.com/natemcmaster/DotNetCorePlugins)

**Language/role:** C#; dynamic .NET assembly loading with dependency isolation and selective type sharing.

Study the difference between isolating a plugin's implementation dependencies and unifying its public contract types with the host. **C1:** [ManagedLoadContext.cs](https://github.com/natemcmaster/DotNetCorePlugins/blob/main/src/Plugins/Loader/ManagedLoadContext.cs) distinguishes private assemblies, shared/default-context assemblies, resolver results, culture-specific resources, and native-library probing. A shared interface loaded into the wrong context is a correctness failure, not simply a packaging inconvenience.

**C2:** `PluginLoader` supports host-defined contracts instead of imposing a particular plugin interface. The [loader implementation](https://github.com/natemcmaster/DotNetCorePlugins/blob/main/src/Plugins/PluginLoader.cs) ties reload and disposal to collectible contexts and manages file-watcher/debouncer cleanup. As its overview explains, requesting unloading still requires the host to release references to plugin objects. This is a focused assembly-loading foundation; applications supply their own higher-level activation and service contracts.

## Application boot, shutdown, and resource composition

### 18. [fastify/avvio](https://github.com/fastify/avvio)

**Language/role:** JavaScript; asynchronous application boot and shutdown framework, also used by Fastify.

Study nested plugin registration as a dependency tree whose shape can grow during boot. **C1:** children must finish before the relevant parent branch is complete, `after` and `ready` have different barriers, and plugin errors alter subsequent processing. The [plugin execution implementation](https://github.com/fastify/avvio/blob/main/lib/plugin.js) unifies callbacks and promises, suppresses duplicate completion, clears timeouts, and coordinates per-plugin loading queues.

**C2:** the host can attach this machinery to an ordinary application object; plugins, readiness callbacks, context overrides, and shutdown handlers form a reusable lifecycle API. The repository's detailed guide shows how these pieces compose. Avvio is a strong selection for understanding asynchronous boot independently of HTTP routing, so Fastify itself is not counted as an additional repository merely for using it.

### 19. [jupyterlab/lumino](https://github.com/jupyterlab/lumino)

**Language/role:** TypeScript; web-application toolkit, selected for its core plugin registry and application integration.

Study asynchronous service activation and dependency-aware deactivation in an extensible client application. **C1:** [coreutils/src/plugins.ts](https://github.com/jupyterlab/lumino/blob/main/packages/coreutils/src/plugins.ts) checks dependency cycles, shares pending activation promises, clears failed activation promises, and computes downstream deactivation order. Before tearing down a plugin, it checks that the affected plugins expose deactivation callbacks; callbacks are awaited while their dependencies remain available.

**C2:** typed service tokens, required and optional dependencies, singleton service resolution, and startup/deferred activation policies are separated from the UI shell. The [application integration](https://github.com/jupyterlab/lumino/blob/main/packages/application/src/index.ts) composes that registry with commands, menus, and widgets. The repository is counted once; the selection concerns these lifecycle abstractions rather than asserting the same quality criteria for every widget or layout package.

### 20. [uber-go/fx](https://github.com/uber-go/fx)

**Language/role:** Go; dependency-injection application framework with managed startup and shutdown.

Study construction separately from execution and resource ownership. **C2:** the [lifecycle guide](https://uber-go.github.io/fx/lifecycle.html) describes constructor/decorator registration and invocation before execution begins; components then contribute startup and shutdown hooks. This supports reusable components such as servers, clients, and background workers without requiring them to manage the whole process.

**C1:** the [lifecycle implementation](https://github.com/uber-go/fx/blob/master/internal/lifecycle/lifecycle.go) tracks how many startup hooks completed successfully, runs corresponding shutdown hooks in reverse order, checks context cancellation, and accumulates cleanup errors instead of abandoning cleanup after the first failure. Explicit state and hook timing records make partial startup inspectable. The important limitation is that long-running work belongs in background goroutines, with hooks coordinating its start and stop; a hook is not intended to contain the service's lifetime loop.

### 21. [stuartsierra/component](https://github.com/stuartsierra/component)

**Language/role:** Clojure/ClojureScript; managed lifecycle for stateful resources assembled into immutable system maps.

Study how a small abstraction can make ownership and initialization order explicit without turning ordinary functions into framework objects. **C2:** the lifecycle protocol, dependency metadata, system maps, and subsystem extraction support reusable stateful components. **C1:** the [core implementation](https://github.com/stuartsierra/component/blob/master/src/com/stuartsierra/component.cljc) injects updated dependencies before each operation, traverses dependency order for startup and reverse order for shutdown, and attaches the partial system and failing component to exceptions. That diagnostic state should not be confused with automatic rollback.

**C4:** the [change log](https://github.com/stuartsierra/component/blob/master/CHANGES.md) documents compatibility decisions and supported-version testing from 2013 onward, subsystem support in 2022, and `Closeable` integration in 2025 for scoped cleanup, including in tests. Its small size is a study advantage, not a lack of reusable semantics.

### 22. [weavejester/integrant](https://github.com/weavejester/integrant)

**Language/role:** Clojure/ClojureScript; lifecycle framework where configuration data describes the component graph.

Study the transition from a declarative configuration map to initialized resources and back through suspend, resume, and halt operations. **C2:** references and multimethods allow arbitrary values—including functions—to participate, without requiring every component to be a record implementing a lifecycle interface.

**C1:** [core.cljc](https://github.com/weavejester/integrant/blob/master/src/integrant/core.cljc) rejects missing or ambiguous references and unbound variables before building the relevant graph, records partially constructed systems in errors, and orders halt operations by dependencies. Resumption compares the new configuration with the earlier system and supports reusing existing resources. The repository guide also makes idempotent `halt-key!` an explicit obligation. Compared with Component, the distinctive engineering material is preserving the relationship between configuration, resolved references, and runtime instances across lifecycle operations.

### 23. [dry-rb/dry-system](https://github.com/dry-rb/dry-system)

**Language/role:** Ruby; application container, component loading, and provider lifecycle framework.

Study the boundary between registering components and preparing or starting resource providers. **C2:** the [provider implementation](https://github.com/dry-rb/dry-system/blob/main/lib/dry/system/provider.rb) separates provider-local registrations from the target container, supports lifecycle callbacks and namespaces, and preserves registration options when transferring components. It tracks completed steps and guards against recursive resolution restarting the same provider step.

**C4:** the [changelog](https://github.com/dry-rb/dry-system/blob/main/CHANGELOG.md) documents the 2022 transition from bootable components to providers with deprecations, subsequent public registrar APIs, restoration of a compatibility alias in 2024, and lazy-loading, finalization, and reloading fixes in 2025. This is useful evidence of managing complexity at the intersection of dependency injection, Ruby loading behavior, and application resource lifetime. The broader container is relevant here because it includes provider lifecycle management, rather than dependency injection alone.

## Coverage, search method, and limitations

Discovery used more than six distinct live search formulations, including Python hook/entry-point frameworks; Java plugin states and class loading; OSGi dependency-manager thread models; native C/C++ service components and unload behavior; Go subprocess RPC plugins; Rust stable-ABI and WebAssembly plugins; .NET composition and collectible assembly contexts; JavaScript asynchronous boot and application plugins; Clojure system lifecycle alternatives; and Ruby provider boot/shutdown. Later cross-language and native-unloading queries mostly returned already represented designs, closely overlapping Clojure alternatives, or application-specific loaders. Repository pages were opened directly, and every retained entry has an additional opened primary documentation or implementation source. GitHub API verification was rate-limited, so identity verification used repository pages instead.

The selection favors reusable infrastructure. Searches also surfaced Mount, Clip, Donut System, Makina, and Jig; these were not all retained because Component and Integrant already provide two distinct Clojure models. Application-specific plugin implementations, starter templates, plugin marketplaces, package-manager plugin installers, and general UI component renderers were outside the chosen scope. Broad runtimes and frameworks were not included merely because they can load modules. Avvio represents its reusable boot engine without separately counting Fastify; Lumino, Felix, Corrade, Equinox, Extism, and iPOPO each count once despite multiple relevant packages or subsystems.

Stevedore and libpeas are explicitly identified as official substantive mirrors. No archived or historical-only repository is intentionally retained, but this report does not infer maintenance health from a recent push or an unarchived flag. C4 is awarded only where the cited release history demonstrates continuing compatibility or complexity-management work. Linked default branches can advance, and versioned Celix and CppMicroServices guides may lag development branches. The architectural mechanisms are observed facts; judgments about what an engineer can learn and which tradeoffs are instructive are grounded inferences. No candidate code was executed, dependencies installed, performance benchmarked, or security guarantees independently audited.
