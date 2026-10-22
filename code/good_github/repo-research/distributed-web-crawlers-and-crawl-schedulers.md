# Distributed web crawlers and crawl schedulers

Research date: **2026-10-09**.

This selection covers distributed fetching systems, persistent URL frontiers, scheduling inside substantial crawler frameworks, crawl-job orchestration, and focused or freshness-aware scheduling algorithms. These are different layers: a process launcher does not supply URL-level deduplication, and a concurrent local crawler is not automatically a distributed crawler. Each entry identifies its layer and offers concrete code or documentation to study. The 22 repositories span Java, Python, Go, TypeScript, and Rust, including archival, search-engine, extraction, and academic communities.

Repository identities and archive status were checked through GitHub repository pages or its public API. Implementation links refer to the inspected branches, which can move and can contain changes newer than published releases. Archived and historical selections are explicitly identified. An unarchived repository is not, by itself, evidence of active maintenance. The criteria below describe engineering substance worth studying, not a certification that every implementation is correct or appropriate for production.

## Criteria legend

- **C1 — Correctness:** meaningful invariants, concurrent state transitions, numerical semantics, adversarial inputs, or recovery and failure modes.
- **C2 — Reusable abstractions:** substantial interfaces and components usable across different crawling workloads.
- **C3 — Performance with structure:** concrete resource or throughput constraints addressed by an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, or deliberate complexity management; repository age alone does not qualify.

## Web-scale and search-engine crawlers

### 1. [apache/nutch](https://github.com/apache/nutch)

**Language / role:** Java; Hadoop-based batch crawling and recrawl scheduling. Official Apache repository.

Nutch is useful for understanding how a durable crawl database becomes bounded, partitioned fetch work. Its generator filters eligible records, ranks them, applies host limits, and partitions the selected URLs for fetching. Study this alongside the fetch-schedule policy rather than treating the system as one large downloader.

- **C1:** Generation checks whether a URL is due and tracks generation timestamps to avoid immediately selecting the same work again. The adaptive scheduler adjusts intervals after modified and unmodified responses, validates host-specific bounds, and explicitly discusses instability from overly aggressive adjustment factors. See [AdaptiveFetchSchedule.java](https://github.com/apache/nutch/blob/master/src/java/org/apache/nutch/crawl/AdaptiveFetchSchedule.java).
- **C2 / C3:** Fetch scheduling is a replaceable policy, while MapReduce stages perform eligibility selection, score ordering, host/domain/IP partitioning, and crawl-database updates. This separates freshness decisions from the mechanics of distributing a large fetch list. See [Generator.java](https://github.com/apache/nutch/blob/master/src/java/org/apache/nutch/crawl/Generator.java).

The distinguishing tradeoff is batch coordination: inspect the interval between selection, fetching, and database updates when comparing it with streaming frontiers.

### 2. [apache/stormcrawler](https://github.com/apache/stormcrawler)

**Language / role:** Java; distributed streaming crawler components built on Apache Storm. This is the current Apache repository identity, rather than a separate entry for the former DigitalPebble location.

StormCrawler offers a contrasting architecture to Nutch: work moves through a long-running topology, with fetching and persistence/scheduling as separate responsibilities. Engineers can study how Storm's message lifecycle interacts with a crawler's own waiting queues.

- **C1 / C3:** The fetcher manages worker threads, per-queue crawl-delay decisions, a bound on queued URLs, and timeouts for work that waits too long. Its queue-timeout path acknowledges a tuple without fetching it, making the interaction between topology timeouts and persisted crawl state particularly important. See [FetcherBolt.java](https://github.com/apache/stormcrawler/blob/main/core/src/main/java/org/apache/stormcrawler/bolt/FetcherBolt.java).
- **C2:** The default scheduling policy maps fetch outcomes to different retry or revisit intervals, supports metadata-specific overrides, and represents “never fetch again” explicitly. The policy is separate from the fetcher. See [DefaultScheduler.java](https://github.com/apache/stormcrawler/blob/main/core/src/main/java/org/apache/stormcrawler/persistence/DefaultScheduler.java).

This is a collection of crawler building blocks; the final topology and persistence integration determine the complete system's guarantees.

### 3. [internetarchive/heritrix3](https://github.com/internetarchive/heritrix3)

**Language / role:** Java; archival crawler with a substantial persistent, polite frontier. Included for its scheduler architecture, without assuming native cluster coordination for every deployment.

Heritrix is especially instructive when many hosts must remain pending while only a small working set is immediately eligible. The frontier models ready, in-process, snoozed, and future work separately, rather than using one undifferentiated URL queue.

- **C1:** The frontier keeps an explicit set of queues with outstanding URIs, uses a uniqueness filter for already included URLs, and documents initialization needed after checkpoint restoration. Queue-state transitions and recovery are central parts of the abstraction.
- **C2 / C3:** Queue precedence policies, budgets, and error penalties are configurable. Short snoozes use an in-memory delay queue; longer waits and overflow can reside on disk. The implementation also chooses whether the collection of queue objects should remain in memory based on its expected size.

These claims and the principal reading entry point are in [WorkQueueFrontier.java](https://github.com/internetarchive/heritrix3/blob/master/engine/src/main/java/org/archive/crawler/frontier/WorkQueueFrontier.java). It is a strong study of balancing crawl fairness, host restraint, and memory consumption within one frontier.

### 4. [LAW-Unimi/BUbiNG](https://github.com/LAW-Unimi/BUbiNG)

**Language / role:** Java; decentralized broad crawler from the Laboratory for Web Algorithmics. **Historical selection:** the checked GitHub metadata reports its latest push in November 2021; current maintenance is not assumed.

BUbiNG combines autonomous agents with a carefully documented local scheduling structure. Its “workbench” is particularly valuable because the code explains the invariant that connects authority-level and IP-level politeness.

- **C1:** A workbench entry holds visit states for an IP. Ordering uses the maximum of the IP's next-eligible time and the earliest authority's next-eligible time. Acquiring a visit state removes the containing entry until release, preventing another local fetching thread from simultaneously acquiring the same IP. See [Workbench.java](https://github.com/LAW-Unimi/BUbiNG/blob/master/src/it/unimi/di/law/bubing/frontier/Workbench.java).
- **C3:** Agents use consistent hashing for coordination, while URL caches, sieve storage, fetch buffers, and the workbench have separately explained memory and I/O costs. The [official configuration and architecture overview](https://law.di.unimi.it/software/bubing-docs/overview-summary.html) connects tuning choices to those components.

A crucial documented limit: IP politeness is not guaranteed across multiple agents that encounter different hosts sharing an IP. The local invariant must not be promoted into a cluster-wide guarantee.

### 5. [yacy/yacy_search_server](https://github.com/yacy/yacy_search_server)

**Language / role:** Java; peer-to-peer search-engine monorepo, counted once for its crawler and host-balancing subsystems.

YaCy offers a different operating model from a centrally managed crawl cluster. Its source includes both local crawl queues and URLs delegated to remote peers, alongside persistent host-specific queues.

- **C1:** `HostBalancer` explicitly requires links from a host to be returned from the lowest outstanding crawl depth, so that click-depth semantics remain meaningful. This is an ordering invariant beyond ordinary URL deduplication. See [HostBalancer.java](https://github.com/yacy/yacy_search_server/blob/master/source/net/yacy/crawler/HostBalancer.java).
- **C3:** Host queues are reconstructed from persistent directories, with optional asynchronous initialization for large unfinished crawls. Fetch execution uses a bounded worker queue; shutdown accounts for waking blocked workers, while remote crawl delegation has separate state. See [CrawlQueues.java](https://github.com/yacy/yacy_search_server/blob/master/source/net/yacy/crawler/data/CrawlQueues.java).

Study the boundaries between host ordering, worker execution, and peer delegation. The broader search and indexing code is outside this entry's scope.

### 6. [StractOrg/stract](https://github.com/StractOrg/stract)

**Language / role:** Rust; search-engine monorepo with a distributed crawler under `crates/core/src/crawler`. **Archived repository**, retained as a historical implementation study.

Stract's crawler starts with a crawl plan, assigns site work through coordination components, and writes fetched content to WARC. It is a useful Rust counterpoint to the Java and Python systems in this selection.

- **C1:** The module documentation states the one-worker-per-site politeness rule. The worker additionally checks domain membership, already-crawled URLs, retry limits, supported schemes, robots rules, and ports before fetching. See the [crawler module](https://github.com/StractOrg/stract/blob/main/crates/core/src/crawler/mod.rs) and [worker.rs](https://github.com/StractOrg/stract/blob/main/crates/core/src/crawler/worker.rs).
- **C3:** Tokio worker tasks and shared WARC output are separated from job assignment. Router connections use bounded retry backoff and timeouts; workers maintain configurable crawl delays and adjust politeness in response to fetching outcomes, including HTTP 429 responses. The worker source exposes these mechanisms directly.

The study target is the archived crawler subsystem, not an assertion about the current hosted Stract service or the maintenance of the entire search product.

## Shared URL frontiers and distributed queues

### 7. [crawler-commons/url-frontier](https://github.com/crawler-commons/url-frontier)

**Language / role:** Java and Protocol Buffers; crawler-independent gRPC frontier API, service, and client in one repository.

This is one of the clearest places to study a frontier as a separate service. Queue keys and crawl IDs are distinct concepts, and the API distinguishes newly discovered URLs from updates to previously issued URLs.

- **C1:** URLs remain in transit until updated or their requestability delay expires. The service documents atomic per-queue eligibility decisions involving blocks, politeness delays, crawl limits, and in-process caps. See the [API contract](https://github.com/crawler-commons/url-frontier/blob/master/API/README.md).
- **C2 / C3:** The protocol supports different crawler clients; service implementations include in-memory and RocksDB-backed storage. The sharded service assigns queue ownership by hashing over a common node list and applies ingestion backpressure. See the [service architecture](https://github.com/crawler-commons/url-frontier/blob/master/service/README.md).

The service documentation also identifies consequential limits: changing cluster membership remaps ownership without migrating data; broadcasts are not atomic; control settings and leases are not persisted with URL records. Restarting requires clients to restore those settings, and in-flight URLs may be issued again.

### 8. [scrapinghub/frontera](https://github.com/scrapinghub/frontera)

**Language / role:** Python; reusable crawl-frontier framework with distributed strategy and database workers. Not archived when checked; no current maintenance claim is inferred from that status.

Frontera is a strong example of separating “which URL deserves attention?” from HTTP fetching and storage. Its manager pipeline is shared between local and distributed operation, so the extension model remains recognizable across deployment scales.

- **C2:** Manager, middleware, canonical-URL solver, backend, queue, metadata, and state abstractions isolate policy from storage and transport. The fetcher can be Scrapy or another crawler.
- **C1 / C3:** Distributed operation separates sharded spiders, strategy workers, and database workers. Spider-log, scoring-log, and spider-feed streams carry different stages of the feedback loop. Host-based stream partitioning is the documented mechanism for keeping a host with one spider; database workers inspect consumer offsets before generating more batches.

The [architecture document](https://github.com/scrapinghub/frontera/blob/master/docs/source/topics/architecture.rst) is the main entry point. The [custom strategy guide](https://crawl-frontier.readthedocs.io/en/latest/topics/custom_crawling_strategy.html) explains how scheduling, request state, and stopping conditions are exposed to application policy. Deployment partitioning remains part of the politeness assumptions.

### 9. [rmax/scrapy-redis](https://github.com/rmax/scrapy-redis)

**Language / role:** Python; Redis-backed Scrapy scheduler, duplicate filter, queues, and spider components. Counted once, without treating historical owner URLs or small downstream variants as independent projects.

This is a compact but substantive shared-queue design. It is particularly useful for comparing the guarantees of Redis data structures with the stronger lease-and-acknowledgment contracts of a dedicated frontier.

- **C1:** Priority dequeue uses a Redis transaction to combine range selection and removal, preventing workers from independently selecting the same sorted-set head. FIFO and LIFO use Redis list pops. See [queue.py](https://github.com/rmax/scrapy-redis/blob/master/src/scrapy_redis/queue.py).
- **C2:** Queue and serializer classes are replaceable, and the scheduler composes them with the duplicate filter. Persistence, startup flushing, and idle behavior are explicit settings. See [scheduler.py](https://github.com/rmax/scrapy-redis/blob/master/src/scrapy_redis/scheduler.py).

The inspected queue pops destructively and exposes no processing lease or acknowledgment in that abstraction. Consequently, atomic dequeue should not be read as crash-safe completion or exactly-once crawling. The project itself points users toward richer frontiers for advanced expiration and prioritization needs.

### 10. [istresearch/scrapy-cluster](https://github.com/istresearch/scrapy-cluster)

**Language / role:** Python; Kafka-fed distributed Scrapy workers with Redis coordination. **Archived repository**; the inspected default branch is `dev`, which the README distinguishes from the older stable `master` branch.

Scrapy Cluster adds crawl-job identity, domain queues, and coordinated throttling to the basic shared-Scrapy-queue model. It is useful for studying interactive crawl requests that coexist with ongoing deeper traversals.

- **C1:** Deduplication is scoped by `crawlid`, allowing independent jobs to revisit the same URL. Failed requests can return to the cluster at lower priority, and cookie handling separates unrelated long-running jobs. The [crawler design document](https://github.com/istresearch/scrapy-cluster/blob/dev/docs/topics/crawler/design.rst) explains these boundaries and also records a scheduler idle/pending-state workaround.
- **C2 / C3:** Domain- and spider-specific queues support heterogeneous spiders and shared throttling across machines. Priorities decrease as traversal expands, while a higher-priority submitted job can move ahead of older work. See [distributed_scheduler.py](https://github.com/istresearch/scrapy-cluster/blob/dev/crawler/crawling/distributed_scheduler.py).

Read the documentation's guarantee language together with the implementation and its disclosed workarounds; this report does not independently establish lossless operation under every failure.

## Browser-based crawling and archival state

### 11. [internetarchive/brozzler](https://github.com/internetarchive/brozzler)

**Language / role:** Python; distributed Chrome/Chromium crawler using RethinkDB crawl state and integration with archival tooling.

Brozzler schedules sites as well as pages, which makes browser ownership and long-lived sessions first-class concerns. This differs from dispatching isolated HTTP requests to interchangeable workers.

- **C1:** Site acquisition uses a conditional database update, with recovery for claims considered stale. Page acquisition relies on the assumption that only the claiming worker is processing that site. Release, finish, and retry-after paths make the ownership lifecycle visible. See [frontier.py](https://github.com/internetarchive/brozzler/blob/master/brozzler/frontier.py).
- **C2 / C3:** Jobs aggregate seeds with scope and limits, while independently launched workers use shared state. Link scheduling distinguishes canonicalization for scope decisions from URLs used for fetching, then batches existing-page lookup and updates. The same frontier source shows these mechanics; the [job configuration reference](https://github.com/internetarchive/brozzler/blob/master/job-conf.rst) is the application-facing entry point.

The code is especially useful for analyzing stale-owner recovery and the assumptions needed to avoid two browsers processing one site's state simultaneously.

### 12. [webrecorder/browsertrix-crawler](https://github.com/webrecorder/browsertrix-crawler)

**Language / role:** TypeScript; browser-based archival crawler with Redis crawl state, concurrent workers, and restartable archival output.

Browsertrix Crawler exposes the coordination needed when a browser visit can fail after some resources have already been archived. Its Redis representation separates queued, pending, failed, and completed work instead of treating browser completion as an instantaneous operation.

- **C1:** Lua commands combine uniqueness checks with insertion, move queued URLs into pending state, associate expiring ownership markers with started work, and requeue work whose ownership marker has expired. Unlocking checks the owner's identifier. See [state.ts](https://github.com/webrecorder/browsertrix-crawler/blob/main/src/util/state.ts).
- **C2 / C3:** The crawl-state layer supports limits, retries, and serialization independently of browser activity. Documented shutdown modes coordinate page completion, pending asynchronous requests, WARC/WACZ output, and Redis state saving; periodic state files provide another restart input. See [state saving and interruption options](https://crawler.docs.browsertrix.com/user-guide/common-options/).

The selection is the crawler repository itself; the separate Browsertrix management application is not counted again here. Inspect queue recovery together with archival finalization when evaluating interruption behavior.

### 13. [apify/crawlee](https://github.com/apify/crawlee)

**Language / role:** TypeScript; reusable HTTP and browser crawling framework. Counted once for its request-queue and crawler infrastructure.

Crawlee is valuable for studying the contract between a crawler, its dynamic work source, and a replaceable storage backend. The inspected `master` queue implementation may be ahead of a released package; use the matching version when applying these details.

- **C1 / C2:** Requests have explicit unique keys, handled state, and reclaim paths. A temporarily empty queue is distinguished from completed processing. Reservation duration is raised rather than lowered when multiple consumers share the queue, and backend hooks can extend a particular request's processing time. See [request-queue.ts](https://github.com/apify/crawlee/blob/master/packages/core/src/storages/request-queue.ts).
- **C3 / C4:** Local deduplication caches and background batch addition reduce storage traffic and startup blocking. The [changelog](https://github.com/apify/crawlee/blob/master/CHANGELOG.md) records several years of queue evolution, including request locking, lock clearing on reclaim, mutex and deadlock fixes, and the change in default queue implementation.

Distributed behavior depends on the chosen storage backend. A local queue implementation should not be assumed to supply the same cross-process reservation semantics as a shared service.

## Programmable crawler frameworks with substantial schedulers

### 14. [scrapy/scrapy](https://github.com/scrapy/scrapy)

**Language / role:** Python; extensible crawling engine with a pluggable request scheduler. Included for the crawl scheduler, not as a claim that core Scrapy supplies a built-in distributed frontier.

Scrapy gives a precise, widely useful separation between request production, scheduling, and downloading. Its scheduler contract explains why “no request ready now” and “no pending work remains” are different answers.

- **C1:** The scheduler handles duplicate rejection, priority order, separate start-request queues, and memory-versus-disk queues. It documents how concurrent downloading changes observable traversal order and how unserializable requests remain in memory even when a job directory is configured.
- **C2 / C3:** A small engine-facing interface allows replacement schedulers without rewriting spiders or downloader middleware. Configurable FIFO/LIFO storage, priority queues, and disk-backed pending work let applications change traversal and memory behavior independently.

Both criteria are directly supported by [scheduler.py and its embedded documentation](https://github.com/scrapy/scrapy/blob/master/scrapy/core/scheduler.py). The [distributed-crawl guidance](https://github.com/scrapy/scrapy/blob/master/docs/topics/practices.rst) explicitly describes external partitioning and multiple Scrapyd instances rather than claiming native distributed execution.

### 15. [gocolly/colly](https://github.com/gocolly/colly)

**Language / role:** Go; crawler framework with a reusable concurrent request queue. This entry concerns local scheduling and storage extension points, not a turnkey distributed service.

Colly is a useful smaller codebase for studying crawl termination while callbacks can discover and enqueue more work. Its queue has enough machinery to make the distinction between an empty pending list and an idle crawler concrete.

- **C1:** The queue loop tracks active requests as well as stored requests and uses wake and completion channels when deciding whether to continue. The storage interface explicitly requires concurrent safety. Request serialization and copying at the storage boundary are also visible.
- **C2 / C3:** `Queue` consumes an injected `Storage` through a fixed worker count. The default in-memory implementation has a capacity limit, while alternative storage implementations can be supplied without replacing the collector or queue driver.

The compact [queue.go](https://github.com/gocolly/colly/blob/master/queue/queue.go) is the main reading entry point. Its `Run` contract also restricts direct use of the storage while the queue is running, a useful reminder that an interface being replaceable does not eliminate lifecycle assumptions.

### 16. [code4craft/webmagic](https://github.com/code4craft/webmagic)

**Language / role:** Java; modular crawler framework with Redis scheduling for distributed workers. The inspected default branch is `develop`.

WebMagic separates downloading, page processing, scheduling, and result pipelines. Its distributed scheduler is simple enough to inspect alongside the worker lifecycle rather than learning a large deployment system first.

- **C2:** The Redis implementation participates in scheduler, monitoring, and duplicate-removal interfaces. It uses task-specific namespaces and preserves richer request metadata separately from the URL queue. See [RedisScheduler.java](https://github.com/code4craft/webmagic/blob/develop/webmagic-extension/src/main/java/us/codecraft/webmagic/scheduler/RedisScheduler.java).
- **C1 / C3:** The spider coordinates its running state, thread pool, empty-queue waiting, and completion checks. It polls again after observing no live worker, handles interruption, and signals the scheduler as request processing finishes. See [Spider.java](https://github.com/code4craft/webmagic/blob/develop/webmagic-core/src/main/java/us/codecraft/webmagic/Spider.java).

The inspected Redis scheduler performs deduplication, URL insertion, and metadata writes as separate operations, and pops URLs destructively. Those boundaries are worth analyzing; shared Redis storage alone does not establish transactional enqueue or crash-safe acknowledgment.

### 17. [Boris-code/feapder](https://github.com/Boris-code/feapder)

**Language / role:** Python; crawler framework with Redis-backed distributed work, task/batch variants, request buffers, and parser workers. Its primarily Chinese documentation adds a substantive ecosystem beyond the usual Scrapy-centered selection.

Feapder is interesting for the intermediate layer between a shared durable queue and local parser threads. A collector reserves batches of eligible work into a bounded local queue while separate buffers handle requests and items.

- **C1:** Collection selects Redis entries whose score is due and moves their score to a future lost-request timeout, making delayed recovery part of the scheduling model. See [collector.py](https://github.com/Boris-code/feapder/blob/master/feapder/core/collector.py).
- **C2 / C3:** The scheduler composes a collector, request buffer, item buffer, and parser controls; supports multiple parser instances; and controls thread count and lifecycle. Its completion detection inspects several pipeline stages repeatedly because those stages are not observed atomically. See [scheduler.py](https://github.com/Boris-code/feapder/blob/master/feapder/core/scheduler.py).

This is useful for examining how batching reduces coordination traffic while enlarging the amount of reserved local work. The completion checks and timeout reservation should be read as implementation mechanisms, not a proven exactly-once protocol.

### 18. [binux/pyspider](https://github.com/binux/pyspider)

**Language / role:** Python; message-queue-connected crawler processes with recurring-task scheduling and a management UI. **Archived repository**; historical architecture study.

Pyspider makes the continuous nature of crawling explicit: the scheduler decides whether a task is new or old enough to revisit, and separately deployed fetchers and processors report results and newly discovered work.

- **C1:** The task queue distinguishes delayed, runnable, and processing tasks. Timed-out processing work returns to the priority queue; a sequence value breaks equal-priority ties to avoid starvation under sustained arrivals. See [task_queue.py](https://github.com/binux/pyspider/blob/master/pyspider/scheduler/task_queue.py).
- **C2 / C3:** Replaceable processes communicate through message queues, allowing fetch and processing capacity to be increased independently. The scheduler applies token-bucket traffic control and handles periodic and failed tasks. See the [architecture document](https://github.com/binux/pyspider/blob/master/docs/Architecture.md).

The architecture explicitly permits only one scheduler in that implementation. Distributed fetchers and processors therefore must not be confused with a replicated or horizontally scalable scheduling authority.

## Crawl-job orchestration

### 19. [crawlab-team/crawlab](https://github.com/crawlab-team/crawlab)

**Language / role:** Go backend with a web frontend; distributed management and scheduling of crawler processes written in multiple languages. Counted once for the monorepo's task scheduler and execution architecture.

Crawlab operates above URL frontiers: a scheduled unit is a crawler process. The architecture separates master-side management, worker task handlers, MongoDB operational state, and file distribution through SeaweedFS, with gRPC communication between nodes.

- **C2:** Workers can execute crawler programs independently of their language or scraping framework. Task identity and result integration are supplied around the process boundary. See the [repository's architecture and integration documentation](https://github.com/crawlab-team/crawlab#architecture).
- **C1:** The current scheduler distinguishes cancellation of pending jobs from cancellation of jobs running on local or remote nodes. Startup explicitly marks pending/running tasks abnormal and clears queue records; it does not silently promise to resume all previous work. See [service_v2.go](https://github.com/crawlab-team/crawlab/blob/main/core/task/scheduler/service_v2.go).

This makes a useful study of cancellation and restart reconciliation across database state, worker messages, and operating-system processes. URL-level politeness and deduplication remain responsibilities of the launched crawlers.

### 20. [scrapy/scrapyd](https://github.com/scrapy/scrapyd)

**Language / role:** Python and Twisted; deployment daemon and crawl-job scheduler for Scrapy spiders.

Scrapyd is a smaller alternative to a full management platform, useful for understanding the execution service at each node of a crawl fleet. It controls spider processes rather than individual URL scheduling.

- **C1 / C3:** The launcher maintains a bounded set of process slots, connects process completion to slot reuse, records finished jobs, and supports a configured process limit or a CPU-derived default. See [launcher.py](https://github.com/scrapy/scrapyd/blob/master/scrapyd/launcher.py).
- **C2:** Polling is separated behind an interface and adapts synchronous or asynchronous project queues. Work is popped only while launcher consumers are waiting; the source explicitly handles a pop returning no message when another instance shares the queue. See [poller.py](https://github.com/scrapy/scrapyd/blob/master/scrapyd/poller.py).

This is a good reference for backpressure between durable job queues and process execution. It is not, by itself, a global multi-node placement service or distributed URL frontier.

## Focused crawling and freshness policy

### 21. [VIDA-NYU/ache](https://github.com/VIDA-NYU/ache)

**Language / role:** Java; focused crawler with classifiers, relevance-based link selection, persistent frontier storage, and recrawl policy.

ACHE belongs here because its main scheduling question is which discovered links merit the available crawl budget. It is a valuable comparison with breadth-first or purely time-ordered frontiers; this entry does not assert a distributed deployment feature.

- **C2:** Frontier management accepts separate selectors for new crawling and recrawling, link filters, and configurable classifiers. The [strategy guide](https://github.com/VIDA-NYU/ache/blob/master/docs/crawling-strategies.rst) explains how scope, relevance, and maximum depth compose; some advanced subsections in that guide remain incomplete.
- **C1 / C3:** The scheduler loads selected links from the disk frontier into an in-memory politeness scheduler, excludes robots-disallowed records, tracks pending work separately from immediately available links, and guards asynchronous queue reload with an atomic flag. See [CrawlScheduler.java](https://github.com/VIDA-NYU/ache/blob/master/ache/src/main/java/achecrawler/link/frontier/CrawlScheduler.java).

Study the boundary between classifier scores, link selection, and host eligibility. A highly relevant link can still be temporarily ineligible, and an empty in-memory queue need not mean that the frontier is exhausted.

### 22. [microsoft/Optimal-Freshness-Crawl-Scheduling](https://github.com/microsoft/Optimal-Freshness-Crawl-Scheduling)

**Language / role:** Python with NumPy/SciPy; research implementations and experimental material for crawl freshness and active cache synchronization. **Research artifact**, not a production crawler service.

This repository adds a numerical scheduling perspective that queue implementations alone do not supply. Its primary documentation connects the code to NeurIPS 2019 and ICML 2020 experiments and describes the associated crawl-observation dataset.

- **C1:** The freshness code learns change rates differently for complete and incomplete observations. It uses monotone bisection with explicit tolerances, bounded bandwidth allocation, and a saturation loop that keeps crawl probabilities within their admissible range. See [LambdaCrawlExps.py](https://github.com/microsoft/Optimal-Freshness-Crawl-Scheduling/blob/master/LambdaCrawlExps.py).
- **C3:** The same implementation separates rate estimation, scheduling-policy solvers, approximations, and trace evaluation, allowing study of computation and freshness tradeoffs under a fixed crawl budget. The companion [sync_bandits.py](https://github.com/microsoft/Optimal-Freshness-Crawl-Scheduling/blob/master/sync_bandits.py) contains cost-generator abstractions and synchronous/asynchronous learning experiments for synchronization policies.

The code's optimality and learning interpretation depend on its mathematical and observation assumptions. The repository includes data associated with a politeness-constrained paper, but this entry does not imply that every paper's algorithm is supplied as a deployable implementation.

## Coverage, search process, and limits

Discovery used substantially more than six distinct live search formulations. Search angles included distributed crawler architecture; Storm/Hadoop/Redis/Kafka designs; crawl frontiers and gRPC/RocksDB storage; Go, Rust, C++, Scala, and Erlang implementations; Chinese-language framework names and scheduler components; browser-based archival crawlers; peer-to-peer and focused search; crawler process orchestration; and freshness optimization and online learning. Follow-up searches for persistent frontiers and freshness scheduling mostly returned already-covered systems, adapters, design exercises, and newer projects whose broad claims did not justify replacing the more directly inspected selections.

Every retained repository's exact GitHub identity was opened through its repository page or checked with the GitHub API. Each also had an additional primary implementation or architecture source read; source paths were confirmed against retrieved files or repository tree listings. Sources above are project-owned documentation or code. Architectural lessons and caveats are grounded interpretations of those sources, not results from running the software. No repositories were cloned, dependencies installed, candidate code executed, or external services modified.

The selection deliberately excludes awesome-lists, generic system-design exercises, small demonstration crawlers, data-analysis packages that merely consume crawl archives, and generic queues or browser automation libraries without a substantial crawl-scheduling layer. Thin Scrapy-to-frontier adapters were useful discovery leads but were not counted separately from the substantive frontier implementations. Historical owner aliases and routine forks were not counted twice. Browsertrix's separate management application and Common Crawl's older crawler were not investigated to the same implementation depth and are not included; no completeness claim is made for those families. UbiCrawler itself was excluded because the laboratory states that it is not publicly distributed, while its open-source successor BUbiNG is included. See the [laboratory's software description](https://law.di.unimi.it/software.php).

The result is a selection guide, not a ranking or a deployment recommendation. Java and Python remain prominent in the verified set; a token project was not added simply to fill a language slot. Archive status, historical snapshots, research assumptions, and distinctions between local, shared-queue, and fully distributed operation are material to the choices above. Performance mechanisms are described without adopting unverified throughput numbers or treating stars as quality evidence.
