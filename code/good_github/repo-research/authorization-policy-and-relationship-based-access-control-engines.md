# Authorization policy and relationship-based access control engines

Research date: **2026-10-09**

This selection covers engines that evaluate authorization policies, traverse permission relationships, compile authorization models, or embed reusable access-control semantics in applications. The 22 repositories span distributed services, local interpreters, database compilation, framework libraries, capability tokens, and standards-based policy decision points. Authentication servers, SDK-only repositories, and policy-distribution systems without their own relevant evaluator are outside the scope. Repository headings link to verified GitHub locations; the additional links identify material actually inspected.

Criteria legend:

- **C1 — Difficult correctness:** nontrivial invariants, concurrency, language semantics, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial models, interfaces, languages, or components usable across applications.
- **C3 — Performance with structure:** concrete techniques for controlling evaluation, storage, latency, or resource costs within an understandable architecture.
- **C4 — Sustained evolution:** multi-year development evidenced by compatibility work, testing, migrations, or complexity management—not age or popularity alone.

The criteria identify worthwhile engineering subjects, not a security certification or a claim that every component is exemplary. Statements about what an engineer can learn are grounded interpretations of the linked implementation and documentation.

## Relationship engines and permission graphs

### [authzed/spicedb](https://github.com/authzed/spicedb)

**Go — distributed relationship-based authorization database.** Study how graph evaluation, datastore revisions, and cached decisions interact when a permission change must become visible to a subsequent request.

- **C1:** The consistency model explicitly addresses stale authorization and the “New Enemy” problem. ZedTokens let callers request a snapshot at least as fresh as a previous operation; exact-snapshot requests have a distinct failure case when the revision is no longer available. These are application-visible correctness choices, not merely database tuning.
- **C3:** Layered caching is paired with per-request consistency modes. The documentation explains the tradeoff between cache reuse and freshness rather than treating cached permission checks as unconditionally safe.

Entry point: the [consistency design and ZedToken guide](https://authzed.com/docs/spicedb/concepts/consistency), including `minimize_latency`, `at_least_as_fresh`, and `at_exact_snapshot`.

### [openfga/openfga](https://github.com/openfga/openfga)

**Go — authorization-model and relationship-tuple service.** A particularly useful implementation to study for recursive checks expressed as direct relations, computed usersets, tuple-to-userset rewrites, and set operations.

- **C1:** The check algorithm tracks visited subproblems to avoid cyclic traversal. Its exclusion operation evaluates both branches concurrently but cancels the other branch only when one result determines the outcome; the design gives concrete execution traces.
- **C2:** Stores isolate authorization models and tuples, while a `CheckResolver` interface separates the graph algorithm from surrounding resolution behavior.
- **C3:** Resolver composition places cached resolution and dispatch throttling around the local checker, including recursive dispatch back through those layers. This makes resource control part of the algorithm's architecture.

Entry points: [check algorithm and resolver composition](https://github.com/openfga/openfga/blob/main/docs/check/README.md) and [service architecture](https://github.com/openfga/openfga/blob/main/docs/architecture/architecture.md). Some concurrency subsections in the former remain unfinished; the claims above use its completed explanations.

### [Permify/permify](https://github.com/Permify/permify)

**Go — authorization service combining relationships and attributes.** The repository now identifies Permify as part of FusionAuth. Its snapshot-token design is a useful comparison with SpiceDB's consistency interface.

- **C1:** Snap tokens connect permission evaluation to a database snapshot after writes. The guide explains how callers can avoid checking permissions against older relationship state and what happens when a token is omitted.
- **C3:** Cached check identities incorporate the transaction identifier along with schema version, context, resource, and subject. This is a concrete approach to keeping cached answers tied to the data and model used to derive them.

Entry point: the [snap-token and cache-key documentation](https://fusionauth.io/permify-docs/operations/snap-tokens). Read this alongside the repository's schema examples to study the interaction of authorization modeling and revision-aware evaluation; do not infer identical consistency guarantees across different Zanzibar-inspired implementations.

### [aserto-dev/topaz](https://github.com/aserto-dev/topaz)

**Go — local authorizer integrating OPA with a typed relationship directory.** Topaz is included for its directory and evaluator integration, not simply because it embeds OPA.

- **C2:** A directory distinguishes typed objects, typed relationships, and permissions computed from relationships or other permissions. Rego policies access that model through directory builtins, giving applications both graph and general policy abstractions.
- **C3:** The architecture keeps a BoltDB-backed directory near the authorizer and loads objects on demand. The documentation explicitly contrasts this with placing the complete authorization dataset in OPA's in-memory data document, making the storage/evaluation boundary worth studying.

Entry points: [component and storage architecture](https://www.topaz.sh/docs/architecture) and [directory model and permission traversal](https://www.topaz.sh/docs/directory). The relevant subsystem is the authorizer/directory combination, including its builtin API boundary.

### [ory/keto](https://github.com/ory/keto)

**Go; TypeScript-like Ory Permission Language — relationship authorization service.** Study the path from a permission model to checks performed within a consistent storage snapshot.

- **C1:** The check engine wraps evaluation in `WithLatestSnapshot`. Failure to acquire that snapshot propagates as an error; an unknown result caused by a limitation can become `FailedPrecondition` in strict mode. The distinction between false, unknown, and execution failure is visible in the implementation.
- **C3:** Batch checking uses an error group with a configured concurrency limit and records results by input position. It is a compact example of controlling parallel authorization work without losing request/result correspondence.
- **C2:** OPL models derived permissions and inherited relationships, separating application permission definitions from the Go execution machinery.

Entry points: [check engine implementation](https://raw.githubusercontent.com/ory/keto/master/internal/check/engine.go) and [permission-model guide](https://www.ory.com/docs/keto/modeling/create-permission-model).

### [warrant-dev/warrant](https://github.com/warrant-dev/warrant)

**Go — centralized ReBAC service with relational storage.** Useful for studying a comparatively approachable service that combines authorization checks, model administration, and application identity integration.

- **C2:** The service supports reusable object/relation models and multiple persistence backends. Its configuration also distinguishes API-key requests from token-based requests, where configured JWT subject and tenant claims scope the authorization endpoint.
- **C3:** Check concurrency, maximum concurrency, and request timeouts are explicit configuration controls. Together with the stateful database deployment model, these expose practical boundaries around parallel graph evaluation.

Entry points: [configuration and identity scoping](https://github.com/warrant-dev/warrant/blob/main/configuration.md) and [database-backed deployment examples](https://github.com/warrant-dev/warrant/blob/main/deployment.md).

**Qualification:** The [repository's limitations section](https://github.com/warrant-dev/warrant#limitations) restricts this open-source implementation to low-to-moderate throughput and development or lower-throughput uses. Do not attribute the hosted WorkOS FGA service's distributed architecture or Warrant-Token behavior to this codebase.

### [pthm/melange](https://github.com/pthm/melange)

**Go generating SQL/PLpgSQL — PostgreSQL-native authorization compiler.** This smaller project offers a distinct architecture: compile an OpenFGA-style model into database functions that query application relationships through a `melange_tuples` view.

- **C1:** The changelog records corrections to recursive tuple-to-userset exclusions and complex intersections. It also records rejecting schemas with unsupported conditions rather than silently dropping those conditions—an especially instructive compiler correctness boundary.
- **C3:** Model analysis selects specialized SQL, precomputes role-hierarchy closure, and uses database query structure instead of an external traversal service. Release notes describe semi-join and common-table-expression improvements, connecting performance work to recognizable relational operations.

Entry points: the [repository's compilation architecture](https://github.com/pthm/melange) and [changelog](https://github.com/pthm/melange/blob/main/CHANGELOG.md).

**Qualification:** The inspected releases are pre-1.0. Treat the supported model subset explicitly; this selection does not imply complete OpenFGA semantic compatibility or long-established operational maturity.

## Policy languages, interpreters, and capability logic

### [open-policy-agent/opa](https://github.com/open-policy-agent/opa)

**Go; Rego — general-purpose policy evaluator used for authorization.** OPA is valuable for studying a policy runtime whose inputs and decisions are independent of any one application's permission vocabulary.

- **C2:** Rego rules operate on structured input and policy data behind a reusable evaluation boundary. The repository provides both service and embedded use, allowing authorization logic to be shared across different enforcement integrations.
- **C3:** The performance documentation explains rule indexing, indexable equality and pattern conditions, partial evaluation, and the different lookup costs of arrays versus keyed objects. It also describes the constraints under which the optimizations apply, which makes the material more useful than a generic throughput claim.

Entry points: [policy performance and indexing](https://www.openpolicyagent.org/docs/policy-performance) and the [repository's runtime and integration overview](https://github.com/open-policy-agent/opa). Focus on the evaluator/compiler boundary and on how policy formulation changes the amount of work performed.

### [cedar-policy/cedar](https://github.com/cedar-policy/cedar)

**Rust — authorization language, validator, and evaluator.** Study a deliberately explicit authorization contract with principals, actions, resources, context, and entity relationships.

- **C1:** Cedar specifies default denial, forbid-overrides-permit behavior, and diagnostics for determining policies and errors. A crucial detail is that a policy that errors is skipped: an error in one policy is not automatically a global denial. This makes error semantics and the caller's handling of diagnostics important engineering subjects.
- **C2:** The repository separates the public authorizer/validator API from core parsing, evaluation, and type checking. Schemas and entity data support many application domains without requiring each integration to implement its own policy language.

Entry points: [authorization and error semantics](https://docs.cedarpolicy.com/auth/authorization.html) and the [repository's crate layout](https://github.com/cedar-policy/cedar). The relevant components are `cedar-policy` and `cedar-policy-core`; the monorepo is counted once.

### [cerbos/cerbos](https://github.com/cerbos/cerbos)

**Go — policy decision point with resource/principal policies and query planning.** Study how the same authorization system supports individual decisions and plans for filtering accessible data.

- **C1:** Historical release engineering notes describe preserving plan semantics when simplifying membership tests, handling nulls, and treating non-boolean condition results as false. These are concrete examples of the correctness burden when translating policy decisions into downstream query conditions.
- **C3:** The same notes describe reducing singleton membership to a comparison, empty membership to false, and coalescing concurrent policy-compilation requests to avoid latency spikes. Performance work appears at both expression and request-coordination levels.

Entry points: the [engine source tree, including loader, tests, and benchmarks](https://github.com/cerbos/cerbos/tree/main/internal/engine), and the [v0.22.0 implementation/release notes](https://docs.cerbos.dev/cerbos/latest/releases/v0.22.0.html). The latter is historical evidence of the engineering work, not a claim that v0.22.0 is the current release.

### [microsoft/regorus](https://github.com/microsoft/regorus)

**Rust — independent Rego interpreter with embedding and FFI support.** Useful for comparing another implementation of Rego semantics with OPA, especially when the runtime must fit constrained host environments.

- **C1:** The changelog documents signed-integer modulo edge cases, complete-rule conflict handling, nested-document merge behavior, and limits on deeply nested input. These reveal concrete numerical, semantic, and adversarial-input problems in a policy interpreter.
- **C2:** Selectable features, `no_std` support, host-provided builtins, and language bindings provide substantial embedding abstractions. The repository also explains its use of OPA's tests and identifies exclusions, so compatibility should be assessed as a tested subset rather than assumed equivalence.

Entry points: [runtime capabilities and compatibility notes](https://github.com/microsoft/regorus) and [semantic fixes and execution-budget changes](https://github.com/microsoft/regorus/blob/main/CHANGELOG.md). Regorus is a separate implementation, not an OPA wrapper or a second listing of the same code.

### [osohq/oso](https://github.com/osohq/oso)

**Rust core with multiple host-language libraries; Polar — deprecated library, retained for historical engineering study.** The repository explicitly marks the open-source library deprecated. This entry concerns that library, not the implementation of today's hosted Oso product.

- **C1:** Oso's engineering account explains the existing VM's hand-written event loop: host callbacks return results to saved VM state, and failed predicates can trigger backtracking. Preserving bindings, control flow, and state across the Rust/host-language boundary is the central correctness challenge.
- **C2:** Polar's rule language and host-object integration reuse one logical engine across application languages. Resource blocks, roles, permissions, and parent relations provide higher-level authorization modeling over that runtime.

Entry points: [the `polar-core` source tree](https://github.com/osohq/oso/tree/main/polar-core) and [the maintainers' VM and query-execution explanation](https://www.osohq.com/post/oso-winter-hackathon). The article's proposed async rewrite was explicitly a proof of concept; it is not presented here as a shipped implementation.

### [eclipse-biscuit/biscuit-rust](https://github.com/eclipse-biscuit/biscuit-rust)

**Rust — Biscuit capability-token verification and Datalog authorization.** Included because the token format carries executable authorization restrictions; the interesting subsystem is the verifier/authorizer and its logic engine.

- **C1:** The Datalog implementation carries fact origins and filters matching facts through trusted-origin sets. Rules also require usable variable bindings and boolean constraints. These mechanisms matter when authority facts, appended token blocks, and verifier-supplied facts must not gain interchangeable trust.
- **C2:** Facts, rules, checks, and scoped trust form reusable authorization primitives, while the C interface exposes the implementation to other host environments. This is a distinct alternative to a central relationship database or application-owned policy objects.

Entry points: [Datalog rule evaluation and origin tracking](https://raw.githubusercontent.com/eclipse-biscuit/biscuit-rust/main/biscuit-auth/src/datalog/mod.rs) and [C API documentation](https://github.com/eclipse-biscuit/biscuit-rust/blob/main/biscuit-capi/README.md). The repository overview explains how these components fit signed, attenuable tokens.

## Embedded application authorization libraries

### [apache/casbin](https://github.com/apache/casbin)

**Go — model-driven access-control library.** The former `casbin/casbin` location redirects to this verified Apache repository. Study the original Go engine rather than counting its language ports as independent selections.

- **C2:** The enforcer separates the model, matcher functions, policy effector, persistence adapter, watchers, and role managers. Its policy/effect/request/matcher model accommodates different access-control semantics without requiring a new engine for each application.
- **C3:** A synchronized cached enforcer adds decision caching, bypasses caching for requests that cannot produce a supported key, clears the cache on policy reload, and exposes expiry and explicit invalidation. This makes cache lifecycle and the relationship between a base evaluator and optional wrappers directly inspectable.

Entry points: [base enforcer and extension boundaries](https://raw.githubusercontent.com/apache/casbin/master/enforcer.go) and [synchronized cached enforcer](https://raw.githubusercontent.com/apache/casbin/master/enforcer_cached_synced.go). These mechanisms are study material, not a claim that arbitrary policy mutations or application contexts are automatically safe to cache.

### [stalniy/casl](https://github.com/stalniy/casl)

**TypeScript — conditional application permissions and related integrations.** The relevant core is `packages/casl-ability`; its adapters and integrations remain part of one monorepo entry.

- **C2:** Rules distinguish actions, subject types, conditions, and fields. Configurable condition and field matchers separate the ability model from one particular application's data representation or query mechanism.
- **C3:** `RuleIndex` indexes candidates by subject type and action. It merges wildcard candidates according to rule priority and caches merged results, reducing the work needed for repeated permission checks while keeping rule selection in one understandable component.

Entry point: [the `RuleIndex` implementation](https://raw.githubusercontent.com/stalniy/casl/master/packages/casl-ability/src/RuleIndex.ts), especially index construction, priority ordering, wildcard merging, and rebuilding on rule updates. Together with the repository examples, it provides a compact study of turning declarative application rules into efficient candidate lookup.

### [palkan/action_policy](https://github.com/palkan/action_policy)

**Ruby — policy objects, authorization contexts, and framework integration.** This is a useful contrast with standalone policy servers because its correctness and performance boundaries follow Ruby object and request lifetimes.

- **C1:** The caching guide explicitly distinguishes short-lived contexts from long-lived objects and explains cleanup obligations for thread-local caching in custom integrations. Cache keys incorporate authorization context and policy/record information; reusing results across the wrong lifetime can therefore change authorization behavior.
- **C3:** Per-rule, per-thread, and external caching address repeated policy construction and repeated checks, including checks that would otherwise cause additional database queries. External caching is selected explicitly for individual rules rather than assumed suitable for all policies.

Entry point: [the detailed caching guide](https://raw.githubusercontent.com/palkan/action_policy/master/docs/caching.md). Read it as a study of cache scope and invalidation contracts, with the repository's policy-object API providing the reusable application boundary.

### [openstack/oslo.policy](https://github.com/openstack/oslo.policy)

**Python — reusable policy enforcement for OpenStack services; official GitHub mirror.** The repository identifies OpenDev as the development home. The GitHub mirror contains substantive source and is retained as such.

- **C2:** Applications register named default rules through a shared enforcer while operators override policy separately. Documented defaults, rule composition, and policy-generation tools give many services a common mechanism without fixing their resource vocabulary.
- **C1:** Release notes describe copying registered rule objects to prevent mutation during parallel processing and rebuilding policy state when a previously populated policy file becomes empty. Both concern subtle shared-state or reload failures.
- **C4:** The [release archive](https://docs.openstack.org/releasenotes/oslo.policy/) spans multiple years and OpenStack series. Deprecation handling, changed-default migration controls, and JSON-to-YAML migration work provide substantive compatibility evidence beyond repository age.

Entry points: [enforcer/default-rule usage](https://docs.openstack.org/oslo.policy/latest/user/usage.html) and [2024.1-series compatibility and correctness notes](https://docs.openstack.org/releasenotes/oslo.policy/2024.1.html).

## Standards, reactive decisions, and enterprise enforcement

### [authzforce/core](https://github.com/authzforce/core)

**Java — extensible XACML 3.0 policy decision point.** Study the boundary between a standardized authorization language and implementation-specific parsing, datatype, and extension decisions.

- **C1:** The repository documents strict versus relaxed parsing choices and defensive input bounds. Its adapted conformance suite distinguishes invalid policies rejected during initialization from invalid requests rejected before evaluation, with explicit issuer and date/time edge cases. This makes standards conformance a concrete engineering subject.
- **C2:** Extension interfaces cover attribute and policy providers, functions, combining algorithms, request preprocessing, result postprocessing, and decision caching. The implementation exposes meaningful evaluator boundaries rather than merely wrapping a fixed service API.

Entry points: [architecture, extension points, and conformance choices](https://github.com/authzforce/core) and [the XACML conformance-suite notes](https://github.com/authzforce/core/blob/develop/pdp-testutils/src/test/resources/conformance/xacml-3.0-from-2.0-ct/README.md). The latter also records unsupported or optional cases; inclusion does not imply every optional XACML feature is implemented.

### [wso2/balana](https://github.com/wso2/balana)

**Java — XACML evaluator descended from Sun's XACML implementation.** Balana is retained as a substantively evolved implementation with XACML 3.0 support, not as a second copy of an unchanged upstream fork.

- **C1:** The PDP handles request parsing, required-attribute validation, and unsupported scope conditions, producing indeterminate outcomes where appropriate. The code makes it possible to study how malformed or incomplete requests are represented without collapsing every failure into an ordinary deny.
- **C2:** `PDPConfig`, policy finders, attribute finders, request contexts, and evaluation contexts divide the evaluator from external policy/data acquisition. The same decision point can be embedded behind different integrations.

Entry point: [the `PDP` implementation](https://github.com/wso2/balana/blob/master/modules/balana-core/src/main/java/org/wso2/balana/PDP.java). Start at request parsing and the evaluation overloads, then follow the configured finder interfaces. No claim about current maintenance cadence is inferred from the project's lineage.

### [heutelbeck/sapl-policy-engine](https://github.com/heutelbeck/sapl-policy-engine)

**Java — reactive attribute-based policy evaluation.** SAPL is distinctive because attributes and authorization decisions can form streams, making subscription behavior part of evaluation semantics.

- **C1:** Its semantics distinguish lazy sequential `&&`/`||` evaluation from eager parallel `&`/`|`, while errors and undefined values participate in three-valued logic. A dominant boolean result can suppress an expensive subscription, but error/undefined results alone do not justify the same shortcut.
- **C3:** Compilation flattens logical chains and organizes operands by cost: constants, pure runtime expressions, and asynchronous streams. This connects short-circuit semantics to both evaluation cost and which external streams get subscribed to.

Entry points: [version 4.1.2 evaluation semantics](https://sapl.io/docs/4.1.2/2_11_EvaluationSemantics/) and the [repository's engine and integration overview](https://github.com/heutelbeck/sapl-policy-engine). This is especially relevant to engineers evaluating continuously updated decisions rather than only request/response authorization.

### [usnistgov/policy-machine-core](https://github.com/usnistgov/policy-machine-core)

**Java — NIST Policy Machine / NGAC authorization core.** A valuable alternative to the dominant Zanzibar and policy-language families, with authorization administration itself modeled as protected operations.

- **C1:** The PDP wraps administrative operations with access checks; event processing executes obligations in response to policy events. The Policy Machine Language specifies operation access requirements and represents prohibitions with inclusion/exclusion conditions, exposing correctness questions beyond a single allow/deny lookup.
- **C2:** Policy administration, decision, and event processing are separated into PAP, PDP, and EPP components. Graph query/mutation interfaces and multiple backing implementations allow the policy model to be reused without tying callers to one graph store.

Entry points: [component architecture and administrative-operation example](https://github.com/usnistgov/policy-machine-core) and [Policy Machine Language reference](https://github.com/usnistgov/policy-machine-core/blob/main/docs/pml.md). The relevant subsystem is the core graph/administration/evaluation model, not merely its gRPC exposure.

### [apache/ranger](https://github.com/apache/ranger)

**Java — enterprise authorization administration and service plugins.** Counted once as a monorepo; the relevant subsystem is the common plugin policy engine under `agents-common`, together with policy distribution from the administration service.

- **C2:** A shared engine and policy representation support service-specific enforcement plugins, including resource/tag authorization and data-oriented decisions such as filtering and masking. This is useful for studying the division between common evaluation and enforcement adapters.
- **C1:** `RangerPolicyEngineImpl` coordinates policy-engine access with read/write locking when in-place updates are enabled. Its delta-update path distinguishes updating an existing engine from producing a replacement, making concurrent evaluation and policy refresh explicit architectural concerns.
- **C3:** Service-local evaluation and policy deltas address repeated remote work and update cost. The implementation also includes performance tracing around engine operations.

Entry points: [system and plugin overview](https://github.com/apache/ranger) and [common policy-engine implementation](https://raw.githubusercontent.com/apache/ranger/master/agents-common/src/main/java/org/apache/ranger/plugin/policyengine/RangerPolicyEngineImpl.java). These observations apply to the inspected common engine, not uniformly to every plugin in the repository.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, followed by primary-source inspection. The principal angles were:

- Zanzibar-style relationship services, graph traversal, consistency tokens, and cached permission checks.
- General policy languages and alternative interpreters: Rego, Cedar, and Polar.
- Embedded Go, TypeScript, Ruby, and Python authorization libraries.
- Java XACML decision points, conformance suites, and extension interfaces.
- Reactive/streaming ABAC, NGAC administration, and enterprise service-plugin enforcement.
- Datalog capability tokens and trust provenance.
- PostgreSQL-native relationship authorization and policy-to-SQL compilation.

Broader and follow-up searches increasingly returned SDKs, alternate-language ports, wrappers, tutorials, and the same established engines. OPAL-style distribution tooling, authentication/OAuth servers, awesome lists, and unrelated projects using “policy engine” terminology were excluded. Casbin ports were not separately counted. Topaz was retained despite its OPA dependency because its typed directory, storage design, and evaluator integration constitute a substantial additional subsystem. Balana's independent XACML evolution distinguishes it from an unchanged fork.

Every retained repository's GitHub page was opened, and at least one additional primary implementation, design, configuration, release, or API source was read. GitHub sometimes failed to render source files; verified raw source URLs were used where available. No candidate code was run, dependencies installed, or repositories cloned. This is documentary and source-level research, not a benchmark or security audit. Numeric performance claims and general claims of active maintenance were deliberately avoided.

The principal qualifications are explicit above: Oso is deprecated and included historically; oslo.policy is an official GitHub mirror; Warrant's open-source throughput scope differs from its hosted successor; Melange has a pre-1.0 supported subset; Regorus documents compatibility exclusions. Historical release notes demonstrate particular engineering decisions without asserting that the cited release is current. The list favors diverse, inspectable mechanisms over exhaustive coverage or a popularity ranking.
