# Database proxies and sharding middleware

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing protocol-aware database proxies, connection multiplexers, SQL sharding middleware, and routing layers for Redis, Memcached, Cassandra/CQL, and ClickHouse. It includes both general middleware and proxies specialized for a distributed database. The relevant subsystem is identified for larger repositories. Storage engines, generic TCP/HTTP reverse proxies, application-only connection-pool libraries, and deployment wrappers are outside this scope.

These are engineering study recommendations, not a claim that every component is exemplary or suitable for a new production deployment. Criterion judgments are grounded in the linked designs and implementations; they are not independent correctness audits or benchmark results. Repository identity, default branch, and archival status were checked through GitHub's API. None of the retained repositories was marked archived at that check. Specific historical, low-activity, licensing, and mirror qualifications appear below; absence of an activity qualification is not a maintenance guarantee.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, protocol or numerical semantics, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable structures supporting multiple policies, workloads, or integrations.
- **C3 — Performance and structure:** concrete resource or latency constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development with evidence of compatibility work, testing, or complexity management. Age or a recent push alone does not establish this criterion.

## SQL sharding and general relational proxies

### 1. [vitessio/vitess](https://github.com/vitessio/vitess)

**Go; MySQL sharding and cluster middleware.** Study the VTGate query-routing subsystem and its Vindexes: the boundary between SQL planning, logical row placement, and physical shard destinations. This monorepo counts once; the selection concerns VTGate and related routing abstractions rather than every Vitess service.

- **C1:** Vindex contracts distinguish unique and nonunique destinations, verification of keyspace mappings, lookup-entry creation/deletion/update, and mappings that cannot serve as primary Vindexes. Those distinctions expose the invariants a sharded write path must preserve.
- **C2:** Single-column, multicolumn, reversible, sequential, and lookup interfaces allow different partitioning schemes to participate in the same planner. Cost estimates guide selection without hard-coding one hashing strategy. Start with [the Vindex interfaces and registry](https://github.com/vitessio/vitess/blob/main/go/vt/vtgate/vindexes/vindex.go), then the [VTGate source and associated executor/transaction tests](https://github.com/vitessio/vitess/tree/main/go/vt/vtgate).

### 2. [apache/shardingsphere](https://github.com/apache/shardingsphere)

**Java; JDBC middleware and wire-protocol sharding proxy.** The relevant monorepo subsystems are ShardingSphere-Proxy and the shared sharding kernel. Study how logical SQL becomes one or more physical queries through parsing, routing, rewriting, execution, and merging.

- **C1:** Routing must distinguish equality, ranges, missing shard keys, binding-table joins, and unbound-table joins. The documented examples show why preserving table relationships changes the actual set of SQL statements executed.
- **C3:** Direct routing can bypass parsing and merging, while unbound joins can produce a Cartesian expansion of routes. These explicit tradeoffs make the [route-engine design](https://shardingsphere.apache.org/document/current/en/reference/sharding/route/) useful for studying fan-out costs. The [proxy subsystem](https://github.com/apache/shardingsphere/tree/master/proxy) is the implementation entry point. Some prose in the current design documentation retains historical roadmap wording; it should not be treated as a current release commitment.

### 3. [sysown/proxysql](https://github.com/sysown/proxysql)

**C++; protocol-aware MySQL and PostgreSQL proxy.** The strongest inspected example is MySQL connection multiplexing: deciding when a frontend session can safely share backend connections.

- **C1:** Active transactions, locks, temporary tables, text-protocol prepared statements, session variables, and `LAST_INSERT_ID()` introduce different connection-affinity requirements. Disabling multiplexing does not itself disable hostgroup routing, an important distinction for temporary-table correctness.
- **C3:** The thread-pool and backend-sharing design reduces connection overhead, while selective pinning and multiplex delays preserve session behavior. The [multiplexing documentation](https://proxysql.com/documentation/multiplexing/) explains both mechanisms and their limits. The repository's [library implementation](https://github.com/sysown/proxysql/tree/v3.0/lib) is the corresponding source entry point; the inspected default branch was `v3.0`.

### 4. [mariadb-corporation/MaxScale](https://github.com/mariadb-corporation/MaxScale)

**C++; MariaDB/MySQL statement-routing proxy.** Study the public **24.02 source line**, particularly read/write splitting and transaction replay. The repository README describes version-specific Business Source License terms and conversion dates; this entry does not assume that later commercial product versions are represented by this GitHub tree.

- **C1:** Replay checks response consistency and treats a connection loss around `COMMIT` specially because replay can duplicate a transaction whose outcome is unknown. Replay size, time, and attempt limits bound recovery behavior. See [ReadWriteSplit's replay and safe-commit design](https://github.com/mariadb-corporation/MaxScale/blob/24.02/Documentation/Routers/ReadWriteSplit.md).
- **C2:** Listeners, services, filters, routers, monitors, and backend-server states form a reusable processing model. The distinction between connection routing and statement routing is explicit in the [configuration architecture](https://github.com/mariadb-corporation/MaxScale/blob/24.02/Documentation/Getting-Started/Configuration-Guide.md).

### 5. [XiaoMi/Gaea](https://github.com/XiaoMi/Gaea)

**Go; multitenant MySQL sharding and read/write routing.** A useful less internationally prominent example of operating many logical database namespaces behind shared proxies. Its README identifies borrowed parser/protocol components and separately developed planning, backend, and management modules.

- **C1:** Configuration replacement uses copy-on-write, an atomic active-index switch, serialized writers, and delayed resource cleanup. The cluster update protocol has separate prepare/commit steps and explicitly discusses failed commits and idempotent retries; it should not be mistaken for a general consensus guarantee.
- **C2:** Namespace configuration groups authorization, routing, slices, and operational settings into a common replacement lifecycle. Study [the hot-reload design](https://github.com/XiaoMi/Gaea/blob/main/docs/config-reloading.md) alongside [the proxy/control-plane architecture](https://github.com/XiaoMi/Gaea/blob/main/docs/architecture.md). The design material is principally Chinese.

### 6. [actiontech/dble](https://github.com/actiontech/dble)

**Java; MySQL sharding middleware with distributed-query and XA machinery.** DBLE explicitly derives from Mycat but documents substantial separate work on MySQL compatibility, complex queries, and transactions; it is retained as a distinct evolution, not as an additional copy of Mycat.

- **C1:** XA recovery coordinates asynchronous `XA RECOVER` jobs, waits for completion, handles unavailable instances, and updates participant recovery state after commit/rollback callbacks. [XAHandler](https://github.com/actiontech/dble/blob/master/src/main/java/com/actiontech/dble/backend/mysql/nio/handler/transaction/xa/XAHandler.java) exposes these failure and synchronization paths.
- **C2:** Relational plan nodes, visitors, optimizers, and shared expressions support sharded joins and other complex SQL beyond simple key-to-server dispatch. Explore [the planning subsystem](https://github.com/actiontech/dble/tree/master/src/main/java/com/actiontech/dble/plan). Its narrower MySQL focus and separate recovery machinery make it a useful comparison with ShardingSphere.

### 7. [flike/kingshard](https://github.com/flike/kingshard)

**Go; comparatively compact MySQL sharding proxy.** Study SQL predicate analysis and per-shard rewriting in a smaller codebase than Vitess or DBLE. Its documented transaction support is limited to a single node; do not infer distributed atomicity.

- **C1:** Range boundaries, reversed comparisons, `IN` lists, hash rules, and date partitions require different shard-selection logic. [The plan builder](https://github.com/flike/kingshard/blob/master/proxy/router/planbuilder.go) includes boundary adjustments and grouping of values for rewritten statements.
- **C2:** A common `Plan` carries criteria, shard/node selections, grouped insert rows, and rewritten SQL, while [shard implementations](https://github.com/flike/kingshard/blob/master/proxy/router/shard.go) share hash/range/date interfaces. This is a useful study of the boundary between generic planning and partition-specific semantics, not an endorsement of all input-validation choices.

## Proxies specialized for distributed SQL systems

### 8. [pingcap/tiproxy](https://github.com/pingcap/tiproxy)

**Go; TiDB connection migration and load-balancing proxy.** TiProxy's distinct problem is moving established sessions during backend lifecycle changes. It is a database-specific proxy, not an independent storage sharder; its README records its origin in Weir.

- **C1:** The linked session-manager proposal details exporting/importing session state, token-based reauthentication, transaction-status tracking, and waiting for transactions or cursors before migration. It explicitly identifies temporary-table/lock limitations and uncertainty after an unanswered commit.
- **C3:** Discovery and connection redistribution address long-lived application pools that would otherwise leave new servers underused or disconnect clients during maintenance. Read the [session-manager design](https://github.com/pingcap/tidb/blob/master/docs/design/2022-07-20-session-manager.md) together with [TiProxy's implementation tree](https://github.com/pingcap/tiproxy/tree/main/pkg). The proposal is historical design evidence, not proof that every planned capability shipped.

### 9. [oceanbase/obproxy](https://github.com/oceanbase/obproxy)

**C++; OceanBase Database Proxy, also called ODP.** Study partition-aware routing to OceanBase servers. The backend database owns storage partitioning; this project implements the routing layer in front of it.

- **C1:** Routing carries cluster/tenant versions, timeout and cancellation actions, and reference-counted table/partition metadata. The distinction between cached and remotely obtained entries makes metadata freshness and object lifetime visible concerns.
- **C2:** SQL parsing, table lookup, partition-ID calculation, partition-location lookup, and caller notification are separate continuation stages. [ObMysqlRoute](https://github.com/oceanbase/obproxy/blob/master/src/obproxy/proxy/route/ob_mysql_route.h) is a particularly useful architectural map; the broader [route subsystem](https://github.com/oceanbase/obproxy/tree/master/src/obproxy/proxy/route) contains caches and processors for table, partition, routine, and server information. The English README is sparse, so this assessment relies chiefly on source inspection.

## PostgreSQL pooling, routing, and sharding

### 10. [pgbouncer/pgbouncer](https://github.com/pgbouncer/pgbouncer)

**C; lightweight PostgreSQL connection pooler.** Study how transaction pooling preserves selected protocol semantics while sharing backend sessions.

- **C1:** Protocol-level prepared statements are renamed, tracked per client, and prepared on demand on the selected backend. SQL-level `PREPARE` has different behavior, and schema changes can invalidate cached result types.
- **C3:** Global query deduplication, per-backend LRU limits, and bounded packet-rewrite buffers expose the memory/CPU tradeoff of compatibility. These mechanisms are explained in [the prepared-statement configuration design](https://github.com/pgbouncer/pgbouncer/blob/master/doc/config.md#max_prepared_statements).
- **C4:** [The changelog](https://github.com/pgbouncer/pgbouncer/blob/master/NEWS.md) documents concrete evolution from 2017 cancellation/TLS fixes through 2026 parameter tracking, driver compatibility, packet handling, and build-system transition. This is stronger evidence than repository age alone.

### 11. [yandex/odyssey](https://github.com/yandex/odyssey)

**C; multithreaded PostgreSQL pooler and router.** Study an explicit coroutine/message-passing architecture organized around client lifecycles and shared server pools.

- **C1:** Cleanup distinguishes an in-progress query requiring cancellation from an abandoned transaction requiring rollback before reuse. Routing must also associate cancellation keys with the correct backend.
- **C2:** Machinarium provides scheduling/networking primitives, Kiwi supplies protocol construction and validation, and the router owns attachment, detachment, limits, and queuing.
- **C3:** Worker threads host many client coroutines; a special single-worker path avoids interthread wakeup overhead. [The internals document](https://github.com/yandex/odyssey/blob/master/docs/development/internals.md) connects these choices to the [source modules](https://github.com/yandex/odyssey/tree/master/sources).

### 12. [pgagroal/pgagroal](https://github.com/pgagroal/pgagroal)

**C; PostgreSQL pooler using processes and shared memory.** A valuable architectural counterpoint to single-event-loop and shared-thread poolers.

- **C1:** Connection ownership moves through atomic states for initialization, use, validation, flushing, and removal. Worker-process isolation reduces the blast radius of an individual connection crash, while shared pool state introduces cross-process lifecycle invariants.
- **C3:** Fixed worker communication buffers avoid per-message allocation, and selectable I/O backends separate event handling from pooling. The architecture also documents that connection acquisition is not ordered fairly among processes.
- **C2:** Pipeline callbacks abstract client/server communication and lifecycle hooks. Start with [the architecture document](https://github.com/pgagroal/pgagroal/blob/master/doc/ARCHITECTURE.md), which links the pool, memory, message, event, and pipeline implementations.

### 13. [pgpool/pgpool2](https://github.com/pgpool/pgpool2)

**C; PostgreSQL pooling, read routing, and cluster middleware — official GitHub mirror.** The repository explicitly identifies itself as a mirror of the upstream PostgreSQL-hosted Git repository; development submissions are handled upstream.

- **C1:** Load balancing depends on transaction isolation, prior writes, volatile functions, locking reads, temporary/unlogged tables, replication lag, and protocol behavior. A query beginning with `SELECT` is insufficient evidence that it is safe to route to a standby.
- **C3:** Session-level versus statement-level balancing and lag thresholds offer explicit throughput/consistency tradeoffs. [The load-balancing design](https://github.com/pgpool/pgpool2/blob/master/doc/src/sgml/loadbalance.sgml) is substantive implementation-oriented documentation, with the broader [manual source](https://github.com/pgpool/pgpool2/tree/master/doc/src/sgml) organizing pooling, failover, watchdog, and recovery behavior. Retaining this substantive official mirror satisfies the GitHub-only scope.

### 14. [postgresml/pgcat](https://github.com/postgresml/pgcat)

**Rust; PostgreSQL pooling, replica routing, and experimental sharding.** Study Tokio-based pooling together with PostgreSQL-compatible shard hashing. The README explicitly labels sharding and mirroring experimental.

- **C1:** [The sharding implementation](https://github.com/postgresml/pgcat/blob/main/src/sharding.rs) reproduces PostgreSQL bigint partition hashing, including signed-key folding and wrapping arithmetic, and contains expected shard-assignment tests tied to SQL fixtures.
- **C3:** A multithreaded asynchronous runtime, transaction/session pooling, backend health checks, and replica selection address connection and query-distribution costs; the README distinguishes session-affinity limitations in transaction mode.

Activity qualification: the [repository API](https://api.github.com/repos/postgresml/pgcat) reported its last push as **2025-02-27**. The README's development-status wording should not be taken as independently verified current maintenance.

### 15. [pgdogdev/pgdog](https://github.com/pgdogdev/pgdog)

**Rust; PostgreSQL pooler, query load balancer, and sharding proxy.** A separate implementation from PgCat, useful for studying the interaction between SQL-aware routing and session cleanup.

- **C1:** The proxy distinguishes read-only transactions from transactions that may write and handles abandoned-transaction rollback, connection resynchronization, and session parameters when sharing backend connections. Its README also distinguishes routing after promotion from actually orchestrating database failover.
- **C2:** Runtime-loaded plugin libraries allow behavior changes without recompiling the proxy; protocol handling provides a common basis for connection-state operations.
- **C3:** Tokio-based asynchronous processing and multiplexing make multicore connection handling part of the architecture. See [the architecture overview](https://docs.pgdog.dev/architecture/). The monorepo includes enterprise-related material; this selection does not assume every advertised enterprise feature is part of the open implementation.

### 16. [supabase/supavisor](https://github.com/supabase/supavisor)

**Elixir; clustered multitenant PostgreSQL connection pooler.** Study dynamic tenant pools and the separation between an inbound client node and the node owning backend connections.

- **C1:** The README architecture describes competing pool startups, convergence to one pool, and pool recreation after node loss. The [manager implementation](https://github.com/supabase/supavisor/blob/main/lib/supavisor/manager.ex) makes admission limits, terminating states, parameter-status propagation, and bounded graceful draining concrete.
- **C2:** Tenant supervision, pool managers, client handlers, and database handlers separate distributed lifecycle management from wire-protocol handling. [The Supavisor module tree](https://github.com/supabase/supavisor/tree/main/lib/supavisor) is a useful entry into that decomposition.
- **C3:** Session and transaction modes enforce different client limits, while shared tenant pools constrain backend connection consumption. Some README future-work sections lag implementation; source behavior is the stronger evidence here.

### 17. [pg-sharding/spqr](https://github.com/pg-sharding/spqr)

**Go; PostgreSQL query router and sharding system.** Study explicit routing policies, delayed backend acquisition, and the boundary between single-shard and multishard transaction handling.

- **C1:** Documentation distinguishes best-effort commits, which can partially succeed, from prepare/commit coordination. It also warns that scatter queries do not provide consistent cross-shard snapshots.
- **C3:** Transaction commands and parameters can be buffered until a shard is selected, while routing policies can reject expensive or ambiguous multishard execution. See [distributed transactions and virtual queries](https://github.com/pg-sharding/spqr/blob/master/docs/sharding/distributed_transactions.mdx) and [the router subsystem](https://github.com/pg-sharding/spqr/tree/master/router).

Material limitation: the inspected document explicitly says the router is an **ephemeral coordinator without a separate persistent coordinator service**. Prepared transactions can therefore become orphaned after failure; the existence of a 2PC option is not evidence of complete durable recovery.

## Redis and Memcached routing layers

### 18. [twitter/twemproxy](https://github.com/twitter/twemproxy)

**C; Redis/Memcached sharding and connection-consolidation proxy.** Study the `mbuf` data path, request fragmentation, and failure-driven changes to a hash ring.

- **C1:** Ejecting a failed backend changes key placement; pending backend work can outlive a client's timeout, and the proxy itself does not retry requests. [The operational design notes](https://github.com/twitter/twemproxy/blob/master/notes/recommendation.md) make these failure semantics explicit.
- **C3:** Reused buffers avoid payload copying, but buffer size trades memory per connection against syscall overhead. Fragmented multi-key requests multiply buffer requirements. The same notes explain this design rather than merely claiming speed.

Historical/low-activity selection: the [repository API](https://api.github.com/repos/twitter/twemproxy) reported its last push as **2024-03-29**. Redis compatibility should be checked command by command rather than inferred from the README's broad protocol claim.

### 19. [CodisLabs/codis](https://github.com/CodisLabs/codis)

**Go with a modified Redis server in C; proxy-based Redis sharding and online slot migration.** Count the proxy, dashboard, and bundled server work as one repository.

- **C1:** Online migration requires coordinated slot ownership and proxy metadata updates. The architecture specifies at most one dashboard per product cluster and requires cluster changes to pass through it.
- **C2:** Proxying, cluster control, storage metadata, and administration are separate components; metadata storage has interchangeable ZooKeeper, etcd, and filesystem implementations. [The component architecture and tutorial](https://github.com/CodisLabs/codis/blob/master/doc/tutorial_en.md) explains their responsibilities.

Historical/low-activity selection: that tutorial identifies a **Redis 3.2.8-derived server**, and the [repository API](https://api.github.com/repos/CodisLabs/codis) reported its last push as **2024-04-15**. Treat its Redis comparison table as historical context, not a current comparison of Redis Cluster capabilities.

### 20. [joyieldInc/predixy](https://github.com/joyieldInc/predixy)

**C++; multithreaded Redis Sentinel/Cluster proxy.** Study how a proxy supports several backend topologies while preserving command-specific behavior. Transactions are documented as limited to a single Redis group in Sentinel mode.

- **C1:** [ClusterServerPool](https://github.com/joyieldInc/predixy/blob/master/src/ClusterServerPool.cpp) builds slot-to-group mappings, parses node roles, filters failing/handshaking nodes, and updates primary/replica membership. Topology changes interact directly with request routing.
- **C2:** Common server-pool and server-group abstractions support distinct Cluster, Sentinel, and standalone implementations, alongside separate request/response parsers and network multiplexers in [the source tree](https://github.com/joyieldInc/predixy/tree/master/src).

Historical/low-activity selection: the [repository API](https://api.github.com/repos/joyieldInc/predixy) reported its last push as **2024-07-19**. The README's comparative benchmark claims are not used as quality evidence.

### 21. [Netflix/dynomite](https://github.com/Netflix/dynomite)

**C; distributed sharding/replication layer for Redis and Memcached.** This is a substantive distributed-storage middleware layer, with peer forwarding and cross-datacenter replication, rather than simply another local connection pool.

- **C1:** Configurable local consistency distinguishes one replica, quorum responses, and checksum-matching safe quorum. Nondeterministic/keyless commands require exceptions, and cross-region replication remains asynchronous. See [the consistency design](https://github.com/Netflix/dynomite/wiki/Consistency).
- **C2:** The middleware colocates with a storage engine and routes either locally or through peer proxies while preserving the engine's client protocol. [The architecture](https://github.com/Netflix/dynomite/wiki/Architecture) explains this separation.

Historical/low-activity selection: the README says `master` is unmaintained and describes `dev` as unstable; the inspected default branch was `dev`. The [repository API](https://api.github.com/repos/Netflix/dynomite) reported its last push as **2024-05-20**.

### 22. [facebook/mcrouter](https://github.com/facebook/mcrouter)

**C++; Memcached protocol router.** Included as a key-value/cache routing specialization. Study composable route handles for hashing, replication, shadowing, failover, and cache warming.

- **C1:** [FailoverRoute](https://github.com/facebook/mcrouter/blob/main/mcrouter/routes/FailoverRoute.h) preserves lease-get/lease-set pairing by mapping returned tokens to the selected child, checks changed destination counts, and considers failure domains during retries. Generic retrying would not preserve those semantics.
- **C2:** Templated route handles and policies compose across [the routing subsystem](https://github.com/facebook/mcrouter/tree/main/mcrouter/routes), including operation selectors, shadow routes, and layered caches.
- **C3:** Failover rate limiting and request-local fiber state make overload and concurrency part of the routing design. The project's very large throughput claims are unnecessary to establish these concrete engineering constraints.

## Analytical and CQL proxies

### 23. [ContentSquare/chproxy](https://github.com/ContentSquare/chproxy)

**Go; ClickHouse HTTP proxy and load balancer.** This is a community project, not the official ClickHouse server repository. Study how HTTP cancellation, query execution, user quotas, and shared response caching interact.

- **C1:** [The proxy implementation](https://github.com/ContentSquare/chproxy/blob/master/proxy.go) responds to client disconnects and deadline expiry by attempting to kill the database query; timeout handling also penalizes the selected host. Closing the HTTP request alone is not treated as sufficient cleanup.
- **C3:** Bounded queues, concurrency limits, response caches, and coordination of identical concurrent queries protect database capacity. [The configuration reference](https://github.com/ContentSquare/chproxy/blob/master/config/README.md) documents cache sharing, payload limits, and request admission controls, making the resource model inspectable.

### 24. [datastax/zdm-proxy](https://github.com/datastax/zdm-proxy)

**Go; Cassandra/CQL live-migration proxy.** Study a migration data path that sends writes to both source and target clusters while selecting where reads are served.

- **C1:** Successful writes require acknowledgments from both clusters at the requested consistency level. Lightweight transactions can apply differently on the two clusters, while only one cluster's applied result is returned; reconciliation can therefore be necessary.
- **C2:** Origin/target roles, primary read selection, optional asynchronous secondary reads, and protocol-version negotiation provide a reusable migration boundary for supported CQL-compatible backends. The [failure-semantics FAQ](https://github.com/datastax/zdm-proxy/blob/main/faq.md) explains why this is not an indefinite disaster-recovery system: it lacks cross-cluster repair.

The README is the source for current configuration names; the FAQ contains older setting names, so use it primarily for the inspected consistency rationale.

### 25. [datastax/cql-proxy](https://github.com/datastax/cql-proxy)

**Go; CQL compatibility sidecar and backend connection proxy.** Distinct from ZDM's dual-write migration role: this project lets existing drivers reach supported database services through a local endpoint.

- **C1:** [Request lifecycle management](https://github.com/datastax/cql-proxy/blob/main/proxycore/requests.go) allocates and recycles finite protocol stream IDs, tracks concurrent requests, and explicitly treats connection closure as ambiguous about whether a request was executed.
- **C3:** [Connection pools](https://github.com/datastax/cql-proxy/blob/main/proxycore/connpool.go) choose the least-busy connection, establish connections concurrently, maintain heartbeats, and reconnect according to a policy. Protocol negotiation and keyspace initialization are part of connection readiness.

Compatibility limitation: the README explains that presenting one endpoint can conflict with drivers' token-aware topology expectations; some drivers need a different balancing policy. This is a useful example of middleware changing what a client can infer about its backend cluster.

## Coverage, search process, and limits

Discovery used more than six distinct live search formulations, including: general SQL sharding/Vitess/ShardingSphere architecture; MySQL multiplexing and ProxySQL/MaxScale; Chinese-community MySQL middleware Gaea/DBLE/Kingshard; PostgreSQL poolers in C, Rust, and Elixir; SPQR and PostgreSQL sharding; Redis/Twemproxy/Codis/Predixy; Dynomite and Mcrouter distributed routing; ClickHouse HTTP proxies; Cassandra migration and CQL compatibility; OceanBase partition-aware proxies; and follow-up searches for Cetus, Corvus, and lesser-known middleware. Later searches increasingly returned already-covered families, forks, generic proxies, and peripheral tools, with CQL Proxy adding the final distinct implementation.

Every retained repository's canonical identity was verified through the GitHub API. Repository material and at least one additional primary document or source file were read for each entry; a raw copy of the same README was not counted as that additional source. The report uses implementation/design evidence rather than stars or unattributed benchmark numbers. No candidate code was executed and no repositories were cloned.

Important boundaries and exclusions:

- Generic infrastructure proxies such as HAProxy/Envoy and privileged-access gateways are outside this selection unless their database-specific routing implementation is the primary subject. Cloud authentication tunnels and deployment-only repositories likewise do not add another sharding implementation.
- Full database engines and embedded routers inside very large server repositories were not added simply because those systems support sharding. TiProxy and ODP qualify because they are substantive, separate proxy projects.
- Mycat descendants were not counted indiscriminately. DBLE's documented separate evolution justified retaining it; Gaea's acknowledged reused modules are disclosed rather than presented as wholly novel implementations.
- Additional candidates such as Cetus, WeScale, and Corvus were surfaced but not promoted without the same depth of verification. He3Proxy results primarily pointed to Gitee; no verified substantive official GitHub mirror was established. Their omission is not a negative quality judgment.
- GitHub push timestamps describe repository activity, not support commitments. Older Redis projects remain valuable historical designs but are not asserted to support modern Redis behavior. Pgpool-II is the explicitly identified official mirror; MaxScale is qualified by its public source line and license terms.
- Chinese documentation and source-heavy projects received substantive inspection, but this is not an exhaustive review of every language community or commercial implementation. Sources on moving branches can change after the research date. No independent workload measurements, formal proofs, or deployment validation were performed.
