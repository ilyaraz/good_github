# Client resilience and rate limiting libraries

Research date: **2026-10-09**.

This report selects 27 GitHub repositories implementing reusable retries, circuit breakers, bulkheads, hedging, adaptive concurrency control, and rate limiting. It includes outbound-client libraries and general admission-control libraries usable by clients or servers. Standalone gateways, application-specific wrappers, tutorials, and generic job systems are outside the selection. Tower and Sentinel are included for their relevant library subsystems, each counted once. Hystrix is explicitly historical; `golang/time` is an official mirror.

The criteria assess opportunities for engineering study, not blanket correctness or production-readiness. Implementation descriptions below come from opened primary sources; statements about what an engineer can learn are grounded judgments. Default-branch code can be newer than published packages.

## Criteria legend

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or failure modes.
- **C2 — Reusable abstractions:** substantial interfaces or mechanisms supporting varied applications.
- **C3 — Performance and architecture:** concrete resource or throughput constraints addressed through understandable structure.
- **C4 — Sustained evolution:** multi-year development accompanied by evidence of compatibility management, testing, or complexity control. Age alone does not qualify.

## Composable resilience libraries

### 1. [resilience4j/resilience4j](https://github.com/resilience4j/resilience4j)

**Java — decorators for circuit breaking, retries, bulkheads, rate limits, and time limits.** Study how independent policies surround ordinary functions and reactive operations without requiring an entire client framework.

- **C1:** The circuit breaker combines normal and administrative states, minimum sample counts, failure/slow-call thresholds, and bounded half-open probes. State changes use atomic operations; window recording is synchronized while protected calls execute outside that critical section. The documentation explicitly distinguishes a sampling window from a concurrency limit. [Circuit breaker design](https://resilience4j.readme.io/docs/circuitbreaker).
- **C2:** Separate policy modules, configurable registries, decorators, and event publishers support reuse across functions and framework integrations, as documented in the repository.
- **C3:** Count and time windows maintain aggregates and subtract evicted measurements, allowing constant-time snapshots without retaining every call in a time window. This is a concrete study of monitoring cost on a request path. [Window implementation explanation](https://resilience4j.readme.io/docs/circuitbreaker).

### 2. [failsafe-lib/failsafe](https://github.com/failsafe-lib/failsafe)

**Java — function-oriented failure-handling policies.** Particularly useful for studying the semantics of nesting retries, breakers, timeouts, and fallback handling.

- **C1:** The retry executor guards races between timeout cancellation, sleeping, and creation of the next attempt. It preserves externally generated thread interruption and separately implements asynchronous scheduling. [RetryPolicyExecutor source](https://raw.githubusercontent.com/failsafe-lib/failsafe/master/core/src/main/java/dev/failsafe/internal/RetryPolicyExecutor.java).
- **C2:** Policies independently classify exceptions and returned results. Composition has an explicit outside-in execution order and inside-out result handling; the guide explains how an outer policy must account for exceptions produced by inner policies. These are reusable execution semantics, not HTTP-specific retry rules. [Policy composition guide](https://failsafe.dev/policies/).

### 3. [App-vNext/Polly](https://github.com/App-vNext/Polly)

**C#/.NET — resilience pipelines, including hedging and rate-limiter integration.** Study cancellation ownership and the evolution from separate synchronous/asynchronous policy interfaces to a common pipeline model.

- **C1:** Hedged actions receive separate contexts and cancellation tokens; the accepted action's context is merged back, and outstanding actions are cancelled before returning. The guide explains why callbacks that ignore cancellation can delay completion. [Hedging architecture](https://www.pollydocs.org/strategies/hedging.html).
- **C2:** Typed and untyped pipelines unify synchronous and asynchronous execution and compose configurable strategies. The migration preserves access to the v7 API through the `Polly` package while supporting gradual migration to `Polly.Core`. [v7-to-v8 migration guide](https://www.pollydocs.org/migration-v8.html).

### 4. [failsafe-go/failsafe-go](https://github.com/failsafe-go/failsafe-go)

**Go — composable resilience policies with adaptive limiting, throttling, and hedging.** A useful comparison with the Java Failsafe project: the Go implementation also makes adaptive load control a first-class policy family.

- **C1:** The adaptive limiter must distinguish growing queues from changes in request mix. It compares recent execution-time quantiles with a longer baseline and also observes the relationship between inflight work and throughput. The documentation describes lowering the limit experimentally to distinguish overload from a shifted baseline. [Adaptive limiter design](https://failsafe-go.dev/adaptive-limiter/).
- **C2:** Policies wrap generic functions; the limiter can also operate independently through permits and context-aware acquisition, with completion reported separately.
- **C3:** Queue bounds and gradual rejection scale with the current concurrency limit. This connects the controller's capacity estimate to bounded waiting and burst handling rather than merely adjusting a number. [Configuration and standalone permit API](https://failsafe-go.dev/adaptive-limiter/).

### 5. [connor4312/cockatiel](https://github.com/connor4312/cockatiel)

**TypeScript — retries, circuit breakers, timeouts, bulkheads, and fallback policies.** Study explicit policy composition and asynchronous state transitions. **Version caveat:** the inspected branch includes changes under `4.0.0 (TBA)`; half-open sampling should not be assumed available in a released version.

- **C1:** The inspected breaker tracks inflight half-open calls, successful/failed samples, and a shared decision promise. Waiting calls recheck state, and cancellation participates in that path. These details expose correctness problems hidden by a simple three-state diagram. [CircuitBreakerPolicy source](https://raw.githubusercontent.com/connor4312/cockatiel/master/src/CircuitBreakerPolicy.ts).
- **C2:** Reusable policy configuration, breaker implementations, backoff factories, and `wrap` separate failure classification from execution behavior.
- **C3:** The changelog explains replacing methods on one policy class with standalone constructors so bundlers can remove unused policy mechanisms. It also records queue-starvation, cancellation, and timeout-listener fixes. [Architecture changes and release boundary](https://github.com/connor4312/cockatiel/blob/master/changelog.md).

### 6. [tower-rs/tower](https://github.com/tower-rs/tower)

**Rust — protocol-independent service middleware; relevant subsystems are retry, timeout, limits, and load shedding.** Counted as one repository. Study how resilience mechanisms become composable layers around asynchronous request/response services.

- **C1:** `poll_ready` can reserve resources that must be released if a service or response future is dropped. Readiness belongs to a particular service instance; cloning a ready service does not establish that the clone is ready. [Service contract and backpressure rules](https://docs.rs/tower/latest/tower/trait.Service.html).
- **C2:** The `Service`/layer model supports both clients and servers without binding the policies to HTTP.
- **C3:** Retry budgets constrain aggregate retry traffic over time, addressing multiplicative retry storms across dependencies. The budget interface separates accounting from the policy that classifies individual failures. [Retry budget design and example](https://docs.rs/tower/latest/tower/retry/budget/index.html).

## Circuit breaking and dependency isolation

### 7. [sony/gobreaker](https://github.com/sony/gobreaker)

**Go — focused circuit breaker with generic results in v2.** A compact study in making a state machine safe while arbitrary protected work runs concurrently.

- **C1:** Request admission records a generation and bucket age; completion checks them before updating current statistics. This prevents old inflight requests from contaminating a reset generation. The implementation handles panics as failed executions and then re-panics. [v2 implementation](https://raw.githubusercontent.com/sony/gobreaker/master/v2/gobreaker.go).
- **C2:** Generic execution, configurable trip predicates, separate successful/excluded-error classification, state-change hooks, and fixed or rolling windows let applications choose failure semantics without changing the breaker. The repository's settings guide and the source make those extension points explicit.

### 8. [nodeshift/opossum](https://github.com/nodeshift/opossum)

**JavaScript/Node.js — promise-based circuit breaking with events and fallback.** Study the interactions between admission, timeouts, result filtering, caching, and observable breaker state.

- **C1:** The implementation combines a concurrency semaphore, a minimum request-volume threshold, rolling failure statistics, half-open recovery, and optional abort-controller handling. It also distinguishes errors that should count toward breaker failure from errors merely returned to the caller. [Circuit implementation](https://raw.githubusercontent.com/nodeshift/opossum/main/lib/circuit.js).
- **C2:** It wraps arbitrary asynchronous actions and exposes fallback functions, lifecycle events, configurable cache transport, and state initialization for short-lived processes. The source also exposes request coalescing as a distinct mechanism from caching.

The hosted API page inspected identifies itself as version 8.1.3, while the repository describes newer behavior; use the implementation and documentation matching the intended package version. [Versioned API surface](https://nodeshift.dev/opossum/).

### 9. [Shopify/semian](https://github.com/Shopify/semian)

**Ruby with a C extension — circuit breakers and host-wide bulkheads for external dependencies.** Study how Ruby exception handling interacts with operating-system resource accounting.

- **C1:** The C resource layer releases Ruby's global VM lock while waiting for a semaphore, uses `rb_ensure` to release an acquired resource after the protected block, distinguishes missing semaphores from timeouts, and handles races around deletion and worker deregistration. [Resource implementation](https://raw.githubusercontent.com/Shopify/semian/main/ext/semian/resource.c).
- **C2:** Named resources and driver integration apply the mechanisms to database and HTTP access. Circuit state is local to a worker, while SysV semaphore bulkheading coordinates access across processes on a host; these are deliberately different sharing scopes.

The repository explains `SEM_UNDO` recovery on process exit and explicitly cautions about bulkheading in threaded environments. Those operating assumptions are part of the design to study, not portable guarantees across Ruby deployment models.

### 10. [jlouis/fuse](https://github.com/jlouis/fuse)

**Erlang — named circuit breakers, fault injection, and OTP monitoring integration.** Valuable for studying a deliberately explicit consistency/performance tradeoff.

- **C1:** The documented `sync` path routes queries through a `gen_server`; `async_dirty` reads ETS directly and is explicitly **not linearizable**. Administrative disable state dominates resets/reinstallation until explicitly reenabled. The README describes sequential and parallel QuickCheck models for command interleavings.
- **C2:** Named fuses, configurable failure windows, wrapper execution, injectable failure rates, statistics plugins, and events separate protection from the application protocol.
- **C3:** ETS is configured for concurrent reads, while state mutation and melting use server calls. This keeps the fast query path structurally distinct from the failure path and makes its weaker consistency visible. [fuse_server implementation](https://raw.githubusercontent.com/jlouis/fuse/master/src/fuse_server.erl).

QuickCheck tests require the separate EQC tool and are not all in the normal CI chain, according to the repository; their existence is evidence of a testing approach, not a claim they were run for this report.

### 11. [ackintosh/ganesha](https://github.com/ackintosh/ganesha)

**PHP — circuit breaking with rate/count strategies and storage adapters.** Study how per-service failure statistics survive PHP request lifecycles and how storage capabilities affect breaker semantics.

- **C1:** The rate strategy explicitly branches on sliding versus tumbling window support; the latter examines current and previous windows. Minimum request counts, failure proportions, rejection counts, and half-open timing interact in the decision. These are concrete failure-accounting semantics to inspect, without assuming cross-process transitions are globally atomic. [Rate strategy implementation](https://raw.githubusercontent.com/ackintosh/ganesha/master/src/Ganesha/Strategy/Rate.php).
- **C2:** Strategy and storage interfaces separate decisions from Redis, Memcached, MongoDB, or local storage. Guzzle integration supports configurable service-name extraction, so an application can group dependencies more precisely than one breaker per client object. The repository documents both adapters and middleware extension points.

### 12. [Netflix/Hystrix](https://github.com/Netflix/Hystrix)

**Java — historical command-based dependency isolation. Maintenance mode, not an actively developed recommendation.** The repository explicitly says Netflix will no longer actively review issues, merge pull requests, or release versions; it identifies 1.5.18 as the final release.

- **C1:** The execution flow integrates rolling breaker health, bounded thread pools/queues or semaphores, timeout handling, and fallback. Its documentation acknowledges that interrupting a timed-out command cannot force uncooperative work to stop, so a pool may remain occupied after the caller receives a timeout. [Execution and isolation design](https://github.com/Netflix/Hystrix/wiki/How-it-Works).
- **C2:** Commands provide synchronous, future, and observable execution over shared infrastructure, with request caching and collapsing as additional abstractions.
- **C3:** Separate dependency pools constrain cascading resource exhaustion. The design explains the cost and isolation implications, making this useful historical context for newer semaphore-based and adaptive libraries. [How it works](https://github.com/Netflix/Hystrix/wiki/How-it-Works).

## Retry engines and retrying HTTP clients

### 13. [jd/tenacity](https://github.com/jd/tenacity)

**Python — generic synchronous and asynchronous retry engine.** Study retrying as a composition of stopping, waiting, failure classification, and per-call state. Although descended from `retrying`, Tenacity documents substantial independent evolution and API differences; the ancestor is not counted separately.

- **C1:** `stop_after_delay` may overshoot because of the final sleep; `stop_before_delay` evaluates elapsed time plus the upcoming sleep. This distinction is encoded directly and should not be confused with forcibly interrupting a running attempt. [Stop strategy source](https://raw.githubusercontent.com/jd/tenacity/main/tenacity/stop.py).
- **C2:** Decorators and code-block iteration share retry state and pluggable callbacks. `AsyncRetrying` drives attempt/sleep actions, supports awaitable callbacks, and chooses a compatible asynchronous sleep implementation. [AsyncRetrying source](https://github.com/jd/tenacity/blob/main/tenacity/asyncio/__init__.py).

### 14. [hashicorp/go-retryablehttp](https://github.com/hashicorp/go-retryablehttp)

**Go — HTTP client with retry policy and backoff hooks.** Its value for study is the protocol and resource-lifecycle work behind an apparently small wrapper.

- **C1:** The implementation stops retries after context cancellation, distinguishes terminal transport failures, honors `Retry-After` on relevant responses, and parses both delta-seconds and HTTP dates. Request bodies must be replayable across attempts. [Client implementation](https://raw.githubusercontent.com/hashicorp/go-retryablehttp/main/client.go).
- **C2:** Retry decisions, delay computation, logging, and error handling are configurable. `StandardClient()` exposes a standard `*http.Client`, while multiple body representations provide a practical integration boundary for existing code. The README and source document these seams.

Study replay mechanics separately from application idempotency: the ability to resend bytes does not establish that repeating a remote operation is semantically safe.

## Adaptive concurrency and flow control

### 15. [Netflix/concurrency-limits](https://github.com/Netflix/concurrency-limits)

**Java — adaptive concurrency estimation and enforcement for clients and services.** Study how congestion-control ideas translate into admission control rather than a fixed requests-per-second quota.

- **C1:** `Gradient2Limit` reasons about bursty request latency, biased minimum-RTT estimates, smoothed baselines, bounded gradients, and transitions into and out of overload. These numerical choices affect stability and unnecessary rejection. [Gradient2Limit design and implementation](https://raw.githubusercontent.com/Netflix/concurrency-limits/main/concurrency-limits-core/src/main/java/com/netflix/concurrency/limits/limit/Gradient2Limit.java).
- **C2:** Limit-estimation algorithms are separated from enforcement strategies; the repository documents simple inflight limits, partitioned capacity, and client/server gRPC integrations.
- **C3:** Its architectural objective is to shed load before growing queues exhaust resources. Comparing estimated capacity with inflight work exposes the latency/throughput tradeoff directly, rather than depending on a previously measured static RPS ceiling.

### 16. [alibaba/Sentinel](https://github.com/alibaba/Sentinel)

**Java — flow control, circuit breaking, and overload protection; focus on `sentinel-core`.** The repository also contains adapters and operational tooling, but is counted once. Study the separation between resource identity, statistics, and admission rules.

- **C1:** `LeapArray` maps time to circular buckets, validates the window partition, uses compare-and-set for missing buckets, and a separate lock when resetting expired buckets. Concurrent rollover is a concrete invariant underlying the rate and health measurements. [LeapArray implementation](https://raw.githubusercontent.com/alibaba/Sentinel/master/sentinel-core/src/main/java/com/alibaba/csp/sentinel/slots/statistic/base/LeapArray.java).
- **C2:** A chain of slots separates tracing, runtime statistics, flow control, and other decisions. Nodes distinguish resource totals from calling contexts and origins, allowing policies to reuse common measurements. [Core architecture](https://github.com/alibaba/Sentinel/wiki/How-it-Works).
- **C3:** Sliding-window aggregation and specialized update paths address the cost of measuring traffic on every protected access.

## Rate limiting, quota accounting, and scheduling

### 17. [bucket4j/bucket4j](https://github.com/bucket4j/bucket4j)

**Java — token buckets with local concurrency strategies and distributed integrations.** Study numerical precision together with optimistic state transitions and configuration changes.

- **C1:** The repository documents integer-based accounting. The lock-free implementation copies bucket state, refills and consumes against the copy, and commits with compare-and-set; failed commits reload state and retry. Reservation and diagnostic operations operate on the same state model. [LockFreeBucket source](https://raw.githubusercontent.com/bucket4j/bucket4j/master/bucket4j-core/src/main/java/io/github/bucket4j/local/LockFreeBucket.java).
- **C2:** Buckets expose immediate consumption, reservations, probes, listener decoration, and configuration replacement. Local and distributed backends broaden this beyond a single HTTP middleware.
- **C3:** The project explicitly addresses synchronization choices and allocation pressure. The source makes the CAS/state-copy tradeoff reviewable; the README also explains asynchronous distributed APIs to avoid blocking application threads during network access.

### 18. [boinkor-net/governor](https://github.com/boinkor-net/governor)

**Rust — in-memory GCRA rate limiting.** The verified canonical owner is `boinkor-net`; older references found during discovery use `antifuchs`. Study a time-based algorithm with replaceable clocks, state storage, and middleware.

- **C1:** GCRA turns burst tolerance and emission intervals into a theoretical arrival time. The implementation uses saturating subtraction when computing admissibility and performs state measurement/replacement through the storage abstraction. [GCRA source](https://docs.rs/governor/latest/src/governor/gcra.rs.html).
- **C2:** Direct and per-key limiters share the same model; custom clocks support `no_std` environments and deterministic testing, and keyed stores can be substituted. Nonzero quota types encode configuration constraints. [User guide](https://docs.rs/governor/latest/governor/_guide/index.html).
- **C3:** Atomic time state and keyed maps avoid storing a log of every request, offering a different memory/performance profile from exact sliding-window logs.

### 19. [golang/time](https://github.com/golang/time)

**Go — `golang.org/x/time/rate`, a concurrent token-bucket library. Official substantive GitHub mirror:** the repository names `go.googlesource.com/time` as its upstream and Gerrit as the contribution system.

- **C1:** Reservations can be cancelled, but restoration must account for later reservations so their tokens are not incorrectly refunded. The limiter also handles contexts, burst limits, changing rates, and special infinite-rate behavior under a mutex. [rate.go implementation and contracts](https://raw.githubusercontent.com/golang/time/master/rate/rate.go).
- **C2:** `Allow`, `Reserve`, and `Wait` expose rejection, explicit future scheduling, and cancellable blocking as separate choices over one accounting mechanism. Their multi-token variants support weighted work, not just one-request-at-a-time middleware.

The relevant subsystem is `rate`; this entry does not rate every supplementary time package in the repository.

### 20. [uber-go/ratelimit](https://github.com/uber-go/ratelimit)

**Go — blocking leaky-bucket pacing.** A deliberately small but substantive implementation for studying the hot path of a limiter shared across goroutines.

- **C1:** The atomic implementation reserves the next permission time through a compare-and-swap loop, caps accumulated slack after idle periods, and sleeps only after winning the reservation. This makes concurrent pacing and burst credit explicit. [Atomic implementation](https://raw.githubusercontent.com/uber-go/ratelimit/main/limiter_atomic_int64.go).
- **C3:** Cache-line padding surrounds the shared timestamp to address false sharing. A clock abstraction separates timing from the algorithm; the small `Take` path makes the overhead decisions easy to inspect.

The repository deliberately positions this as a simple, low-overhead API and points complex use cases toward `x/time/rate`. It also documents Windows timer-precision limitations. No historical benchmark numbers are treated here as current cross-library comparisons.

### 21. [go-redis/redis_rate](https://github.com/go-redis/redis_rate)

**Go and Redis Lua — distributed GCRA quota accounting.** Study how an admission decision, its timing result, and state expiration fit into one Redis script.

- **C1:** The script obtains Redis server time, shifts the epoch to reduce floating-point precision problems, computes theoretical arrival time, and updates state with an expiration derived from recovery time. Its comments explicitly discuss the finite precision horizon. [Lua algorithms](https://raw.githubusercontent.com/go-redis/redis_rate/v10/lua.go).
- **C2:** The two script forms support all-or-nothing weighted admission and admission up to the available amount, returning allowed/remaining capacity plus retry/reset timing. Keys permit independent quotas for different resources.
- **C3:** One stored time value per key and server-side decision logic avoid per-request event logs and client-side read/modify/write races. The source credits its `redis-gcra` ancestry; this report counts only this Go integration and implementation.

### 22. [SGrondin/bottleneck](https://github.com/SGrondin/bottleneck)

**JavaScript/CoffeeScript and Redis Lua — queued job scheduling and rate limiting.** Study the combination of minimum spacing, concurrency limits, reservoirs, priorities, and distributed admission.

- **C1:** The Redis datastore registers clients, sends heartbeats, reacts to capacity messages, and recovers from missing settings or unknown-client errors by reinitializing or reregistering. Disconnect handling distinguishes shared from owned connections. [RedisDatastore implementation](https://raw.githubusercontent.com/SGrondin/bottleneck/master/src/RedisDatastore.coffee).
- **C2:** Promise/callback scheduling, function wrapping, keyed groups, and configurable queue overflow strategies apply beyond one HTTP client. The repository documents how unfinished jobs can occupy concurrency slots and why expiration matters.

The inspected [release page](https://github.com/SGrondin/bottleneck/releases) marks v2.19.5 latest and describes a clustering race fix under inconsistent networking. This supports the failure-mode study; it does not establish a current maintenance cadence.

### 23. [animir/node-rate-limiter-flexible](https://github.com/animir/node-rate-limiter-flexible)

**JavaScript/Node.js — rate-limit counters with interchangeable storage backends and failure handling.** Useful for studying a common counter API across memory and external stores.

- **C1:** The Redis implementation atomically initializes expiration, increments the counter, and retrieves TTL in Lua; it repairs a missing expiration. It also validates integer point consumption and distinguishes client readiness across Redis client implementations. [Redis limiter source](https://raw.githubusercontent.com/animir/node-rate-limiter-flexible/master/lib/RateLimiterRedis.js).
- **C2:** Common consumption/results, penalties, rewards, blocks, and multiple backends support resource quotas and abuse prevention. Store failure can be handled with an insurance limiter; changing window duration affects new keys differently from existing keys. [Configuration semantics](https://github.com/animir/node-rate-limiter-flexible/wiki/Options).
- **C3:** Local blocking of already-exhausted keys can avoid repeated external-store operations during heavy rejected traffic. This is a specific architectural optimization documented in the repository, not evidence that every backend has identical consistency guarantees.

### 24. [alisaifee/limits](https://github.com/alisaifee/limits)

**Python — rate-limit strategies and storage interfaces with synchronous/asynchronous APIs.** Study the deliberate choice among precise logs, cheap counters, and approximations.

- **C1:** Fixed windows permit boundary bursts, moving windows inspect the oldest relevant timestamps, and sliding-window counters weight the previous bucket before rounding. The documentation explains the accuracy implications rather than treating these algorithms as interchangeable. [Strategy guide](https://limits.readthedocs.io/en/stable/strategies.html).
- **C2:** A common `hit`, `test`, and window-statistics interface accepts resource identifiers and weighted cost. Strategy implementations delegate storage-specific atomic operations through capability interfaces. [Strategy implementation](https://raw.githubusercontent.com/alisaifee/limits/master/limits/strategies.py).
- **C3:** The documented single-counter, request-log, and two-counter designs expose memory/accuracy tradeoffs clearly, making this a useful comparison against token buckets and GCRA.

### 25. [vutran1710/PyrateLimiter](https://github.com/vutran1710/PyrateLimiter)

**Python — multi-rate, per-key limiting with pluggable algorithms and persistent backends.** The inspected default branch goes beyond the older leaky-bucket tagline: it documents sliding-log, fixed-window, and GCRA/token-bucket choices, plus a breaking v3-to-v4 migration.

- **C1:** The Redis log-bucket script checks every configured rate before insertion and returns the blocking timestamp from that same atomic decision. Weighted insertion is batched to respect Lua argument limits. Caller-supplied timestamps make clock selection an explicit distributed-system concern. [Redis bucket source](https://raw.githubusercontent.com/vutran1710/PyrateLimiter/master/pyrate_limiter/buckets/redis_bucket.py).
- **C2:** Separate limiter, bucket factory, clock, algorithm, and backend responsibilities support multiple quotas, key routing, blocking/nonblocking acquisition, and synchronous/asynchronous calls.
- **C3:** Algorithm-supplied window bounds keep the Lua storage operation independent of policy, while returning waiting information in the original operation avoids a second lookup.

Use documentation matching the installed release; features on the inspected branch are not asserted to exist in older v3 packages.

### 26. [mjpieters/aiolimiter](https://github.com/mjpieters/aiolimiter)

**Python/asyncio — weighted leaky-bucket admission.** A compact example with meaningful scheduler, cancellation, and fairness behavior.

- **C1:** Waiters are ordered by requested capacity and insertion order; cancelled/completed waiters are removed before waking the next task. It uses the event loop's clock and detects reuse across closed loops. Small requests can consequently pass before larger ones near saturation. [Leaky-bucket implementation](https://raw.githubusercontent.com/mjpieters/aiolimiter/main/src/aiolimiter/leakybucket.py).
- **C3:** A heap and one scheduled wakeup replace separate timeout loops for every blocked task. The source makes this scheduling optimization directly inspectable.
- **C4:** The dated changelog spans 2019–2024 and records Python API compatibility fixes, removal of Python 3.6 support, memory reduction with slots, the single-timeout/heap redesign, and loop-reuse recovery. [Changelog](https://raw.githubusercontent.com/mjpieters/aiolimiter/main/CHANGELOG.md).

This limits admission rate; it does not itself bound how many admitted operations remain in flight.

### 27. [ExHammer/hammer](https://github.com/ExHammer/hammer)

**Elixir — rate limiting with ETS and atomic-counter backends.** Study how BEAM-native storage and supervision shape a reusable limiter. Redis and Mnesia adapters are separate repositories and are not separately counted here.

- **C1:** Algorithm choices expose fixed-window boundary bursts, per-key window alignment, and token/leaky-bucket behavior. Backend lifecycle includes expiry cleanup; documented cleanup callbacks cannot prevent deletion merely by raising. [ETS backend contracts](https://hexdocs.pm/hammer/Hammer.ETS.html).
- **C2:** Applications define limiter modules through a common backend interface, select algorithms, and use resource keys with per-call limits. Supervision and cleanup are explicit rather than hidden global configuration.
- **C3:** The atomic backend uses Erlang atomics for counter operations, while the ETS backend has a process responsible for table creation and cleanup. Comparing those paths reveals the cost of shared-state access and process messaging. [Atomic backend architecture](https://hexdocs.pm/hammer/Hammer.Atomic.html).

## Search coverage, exclusions, and limitations

Discovery used more than six distinct live search formulations, including JVM circuit-breaker/policy libraries; .NET pipelines and hedging; Go breakers and retry clients; Python retry and limiter backends; Node.js clustered scheduling and counter stores; Rust GCRA and Tower middleware; Ruby isolation; Erlang/Elixir breakers and atomic limits; PHP circuit breakers; and adaptive concurrency control. Follow-up searches used algorithm terms such as token bucket, leaky bucket, GCRA, retry budgets, and distributed rate limiting. Later queries increasingly returned already-selected projects, thin integrations, forks, and demonstrations; the final BEAM search added Hammer for a distinct implementation family.

The selection spans composition frameworks, compact state machines, OS semaphore isolation, asynchronous wait queues, Redis scripts, pluggable persistent storage, and feedback controllers. The list extends slightly beyond 25 because PHP and BEAM libraries add useful language and runtime coverage. It is not ranked by popularity or stars.

Important exclusions include application demos and tutorial replicas; `tower-governor` and HTTP transport wrappers whose underlying mechanisms are already represented; the Cockatiel fork `carbonteq/resilience`, for which this search did not establish sufficient independent evolution; and Tenacity wrappers where the underlying engine is the stronger study target. Gubernator was discovered but left outside this library-centered selection because its principal presentation is a distributed rate-limit service. This is a scope choice, not a quality judgment. C/C++-specific library coverage remains limited; Semian's native extension supplies the inspected C material, but this is not a comprehensive C++ survey.

Every retained canonical GitHub repository page was opened, and each entry has additional opened primary documentation or implementation evidence. Some GitHub blob pages and documentation redirects failed to render; source content was then read through working raw GitHub URLs or official generated API documentation. Raw source is used as additional evidence only when it is a different implementation file, not another rendering of the same README.

No repositories were cloned, dependencies installed, candidate code executed, benchmarks rerun, or maintainers contacted. Links to default branches and `latest` documentation can change. Maintenance is not inferred from a recent crawl, push, or star count: Hystrix's declared status and Go's mirror status are explicit, while other entries make no blanket active-maintenance promise. Release/version mismatches observed for Cockatiel, Opossum, and PyrateLimiter are noted above. C4 is credited only where the inspected dated history supports it. The report is a guide to substantive code and tradeoffs, not an audit that every component satisfies all its intended guarantees.
