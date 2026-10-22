# Database failover and recovery systems

Research date: **2026-10-09**

This selection covers 24 GitHub repositories implementing database primary election, failover, fencing integration, backup consistency, point-in-time recovery, and restoration after topology changes. It includes dedicated tools and three explicitly bounded subsystems within larger database repositories: Vitess VTOrc, Redis Sentinel, and TiDB BR. The emphasis is on mechanisms an experienced engineer can study, not installation recipes or a ranking of deployment recommendations. Recovery guarantees depend on configuration and failure assumptions; inclusion does not certify every component or deployment mode.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial conditions, or failure handling.
- **C2 — Abstractions:** substantial, reusable interfaces or architectural components serving multiple use cases.
- **C3 — Performance:** real resource or latency constraints addressed through understandable architecture.
- **C4 — Evolution:** documented development across years, accompanied by compatibility work, testing, or complexity management.

## PostgreSQL failover orchestration

### 1. [patroni/patroni](https://github.com/patroni/patroni)

**Python; PostgreSQL high-availability controller.** Study how a controller reconciles database replication state with leadership recorded in an external distributed configuration store. Its synchronous and quorum replication modes expose the distinction between a live replica and a replica that can safely inherit acknowledged transactions.

- **C1:** The synchronous-mode documentation specifies ordering invariants between the configuration store's `/sync` state and PostgreSQL's synchronous standby configuration. Quorum mode reasons about intersection between acknowledgment and promotion sets. These are concrete distributed-state invariants, with documented exceptions for transactions that override synchronous commit. See [replication modes](https://patroni.readthedocs.io/en/latest/replication_modes.html).
- **C4:** The [release history](https://github.com/patroni/patroni/blob/master/docs/releases.rst) documents evolution from 2016 through 2026, including automated acceptance testing, PostgreSQL-version compatibility, `pg_rewind` handling, and watchdog/client-shutdown ordering fixes. This supports studying how a long-lived failover controller absorbs new database behavior and subtle operational failures.

### 2. [hapostgres/pg_auto_failover](https://github.com/hapostgres/pg_auto_failover)

**C; PostgreSQL monitor extension and keeper processes.** A useful contrast to controllers backed by a generic consensus store: the monitor itself uses PostgreSQL and assigns desired states to keepers.

- **C1:** Its finite-state machine distinguishes losing a standby from losing a primary. When replication becomes unavailable, it can relax synchronous replication while withholding automatic failover; a returning former primary is reconciled through rewind or a fresh copy. Monitor failure preserves existing replication but removes the ability to coordinate subsequent transitions.
- **C2:** Monitor, keeper, formation, and group abstractions separate policy from local execution. Groups support independent replication sets, including the groups needed by Citus, while keepers repeatedly converge local PostgreSQL to assigned states.

The primary reading entry point for both criteria is the detailed [architecture and state-machine documentation](https://pg-auto-failover.readthedocs.io/en/main/architecture.html). Study its transition conditions and reduced-availability states, rather than treating every failure as an immediate promotion trigger.

### 3. [EnterpriseDB/repmgr](https://github.com/EnterpriseDB/repmgr)

**C; PostgreSQL replication administration and repmgrd automatic failover.** Study a toolchain combining operator-directed cloning, switchover and rejoin with daemon-driven failure decisions.

- **C1:** Location-aware failover prevents promotion when no reachable node remains in the old primary's location, reducing the chance that an isolated site promotes a second primary. The documentation explains degraded monitoring and the conditions under which witness placement helps. See [network splits and failover](https://www.repmgr.org/docs/current/repmgrd-network-split.html).
- **C4:** The [project history](https://github.com/EnterpriseDB/repmgr/blob/master/HISTORY) records releases from 2010 onward, PostgreSQL-major-version adaptations, extension upgrade-path fixes, witness metadata fixes, and changes to rewind/rejoin behavior. These demonstrate sustained management of compatibility and recovery edge cases, rather than age alone.

Its location and witness logic is especially useful for understanding how operational topology becomes part of a failure detector's correctness assumptions.

### 4. [sorintlab/stolon](https://github.com/sorintlab/stolon)

**Go; PostgreSQL HA with keeper, sentinel, and proxy processes.** The repository was not archived when checked, but its recorded last push was July 2024. It is included as a quieter architectural reference, without implying current maintenance coverage.

- **C1:** The proxy drops connections when it cannot obtain a sufficiently consistent cluster view, and closes connections to an obsolete primary. The design explicitly warns that restoring stale control-store data can resurrect an old leadership view. This makes client routing and control-store recovery part of the safety model.
- **C2:** Keepers manage local PostgreSQL, sentinels compute the desired cluster view, and proxies route connections. Store implementations support different coordination environments, while the process boundaries permit container, VM, and conventional host deployments.

Read the [architecture document](https://github.com/sorintlab/stolon/blob/master/doc/architecture.md), especially the interactions between cluster state, local convergence, and proxy behavior. The separation offers a compact comparison with both integrated operators and monitor/keeper designs.

### 5. [ClusterLabs/PAF](https://github.com/ClusterLabs/PAF)

**Perl; PostgreSQL Automatic Failover resource agent for Pacemaker.** This is database-specific integration with a general cluster manager. The repository was not archived when checked; its recorded last push was June 2024, so the documentation should be read with its platform/version context in mind.

- **C1:** PAF relies on real fencing to establish that an unreachable former primary cannot continue writing. Its [fencing discussion](https://clusterlabs.github.io/PAF/fencing.html) distinguishes shutting off an unsafe node from merely losing communication with it.
- **C2:** The OCF resource-agent model exposes start, stop, monitor, promote, demote, and notification behavior to Pacemaker. PostgreSQL instances begin as standbys, while promotion scores and replication-lag policy influence which one becomes primary. The [configuration reference](https://clusterlabs.github.io/PAF/configuration.html) explains how these reusable cluster-manager actions map onto PostgreSQL operations.

Study this repository when the question is how database semantics fit into an established fencing and resource-management framework.

### 6. [cloudnative-pg/cloudnative-pg](https://github.com/cloudnative-pg/cloudnative-pg)

**Go; Kubernetes operator for PostgreSQL lifecycle, failover, and recovery.** Study the boundary between a Kubernetes reconciliation loop and the database instance manager.

- **C1:** Failover first marks the target primary as pending and stops WAL receivers before election and promotion. Current development documentation also separates a promotion lease from primary isolation: the lease alone cannot fence a primary that has lost API connectivity. These are explicit safeguards and limitations around timelines and competing writers. See [automated failover](https://github.com/cloudnative-pg/cloudnative-pg/blob/main/docs/src/failover.md).
- **C2:** Declarative `Cluster` resources combine replication, scheduling across failure zones, application services, and replica clusters. The [architecture document](https://github.com/cloudnative-pg/cloudnative-pg/blob/main/docs/src/architecture.md) clearly bounds automatic orchestration to one Kubernetes cluster; cross-cluster disaster-recovery coordination requires an additional actor.

The same failover document makes the recovery-time versus data-preservation tradeoff of shutdown delays explicit. Default-branch documentation can describe behavior newer than a deployed release.

## MySQL and MariaDB topology recovery

### 7. [openark/orchestrator](https://github.com/openark/orchestrator)

**Go; MySQL replication topology discovery and recovery. Archived upstream.** Retained as a historical implementation with substantial topology reasoning, not as an actively maintained deployment recommendation.

- **C1:** Selecting the replica with the most advanced log position is insufficient: promotion must also account for replication compatibility, binlog formats, versions, and intermediate-primary topology. Recovery blocking intervals and abortable pre-failover hooks address repeated or inappropriate recovery attempts.
- **C2:** Recovery strategies span Oracle MySQL GTID, MariaDB GTID, Pseudo-GTID, and binlog-server configurations. The separation between topology analysis, recovery actions, and external hooks is reusable across considerably different replication arrangements.

Start with [topology recovery](https://github.com/openark/orchestrator/blob/master/docs/topology-recovery.md), which explains candidate selection, intermediate-primary recovery, and hooks. Forks are not counted as additional projects here. VTOrc below is retained separately because its Vitess-specific architecture substantively changes discovery, synchronization, and persistent state.

### 8. [yoshinorim/mha4mysql-manager](https://github.com/yoshinorim/mha4mysql-manager)

**Perl; MySQL Master High Availability manager. Historical reference.** The repository was not archived when checked, but its recorded last push was August 2020. The companion node package is part of this design, not an additional selection.

- **C1:** MHA compares replica relay-log progress, recovers differential events, and applies missing events before promotion. The recovery sequence treats replicas as potentially containing different surviving portions of the failed primary's transaction history.
- **C2:** Manager/node separation isolates coordination from log-processing helpers. Hooks for secondary failure checks, forced shutdown, address changes, and reporting let the same core recovery sequence fit different network and operational environments.

Read the [architecture wiki](https://github.com/yoshinorim/mha4mysql-manager/wiki/Architecture). Its most instructive topic is recovery from unequal replica progress, including the dependency on reachable logs and external checks; it should not be read as an unconditional zero-data-loss guarantee.

### 9. [signal18/replication-manager](https://github.com/signal18/replication-manager)

**Go; MySQL/MariaDB replication management with database and proxy integration.** A substantive, less widely cited example of combining cluster failover policy with operational orchestration.

- **C1:** The [failover implementation](https://github.com/signal18/replication-manager/blob/develop/cluster/cluster_fail.go) guards against concurrent failovers, refreshes and evaluates candidates, and distinguishes planned switchover work such as handling long-running writes, freezing the previous primary, and applying relay logs. GTID/crash state is carried through the transition rather than reducing failover to a routing change.
- **C2:** The [project overview](https://github.com/signal18/replication-manager/blob/develop/README.md) describes multi-cluster management, multiple database families and replication arrangements, and integration with HAProxy, ProxySQL, and MaxScale. The implementation exposes topology-specific decisions and external actions through a shared cluster-management structure.

Study the sequencing and error paths in the failover code; the existence of these mechanisms does not establish that every supported topology has identical guarantees.

### 10. [cybozu-go/moco](https://github.com/cybozu-go/moco)

**Go; Kubernetes operator for MySQL using semi-synchronous replication.** MOCO is useful for studying a deliberately constrained topology and its consequences for automated recovery.

- **C1:** Its clustering logic distinguishes healthy, degraded, failed, and lost states; excludes replicas with errant GTIDs; and freezes the old primary before waiting for a switchover candidate to catch up. Its semi-synchronous acknowledgment configuration is an essential assumption, not an incidental tuning choice. See [clustering and state transitions](https://github.com/cybozu-go/moco/blob/main/docs/clustering.md).
- **C2:** The [design document](https://github.com/cybozu-go/moco/blob/main/docs/design.md) separates the `MySQLCluster` API, controllers, instance agents, and database clustering logic. Cloning, restoration, and external replication are incorporated into the same lifecycle model.

External fencing is outside the documented design scope. That boundary, and the manual intervention required for some errant-transaction cases, make this a useful study of the limits of an operator's automation.

### 11. [vitessio/vitess](https://github.com/vitessio/vitess)

**Go; selected subsystem: VTOrc, Vitess's MySQL failure detector and topology repairer.** Counted once as a monorepo; the selection is specifically about VTOrc and its interaction with tablets and the topology service.

- **C1:** Recovery acquires a shard lock and refreshes observations before acting. This prevents multiple repair actors from independently changing a shard based on stale polling results. See [VTOrc architecture](https://vitess.io/docs/24.0/reference/vtorc/architecture/).
- **C2:** Vitess's topology service supplies desired topology and durable metadata, while VTOrc maintains reconstructible local observations and delegates work through tablet interfaces. This supports independently restartable repair processes within a larger database control plane.

The [project's explanation of VTOrc's evolution](https://vitess.io/blog/2022-09-21-vtorc-vitess-native-orchestrator/) documents its origin in Orchestrator and substantive divergence: topology-service discovery, shard locking, ephemeral local state, and removal of general hierarchical-replication requirements. Those changes justify treating it as a distinct implementation here.

## Redis failover

### 12. [redis/redis](https://github.com/redis/redis)

**C; selected subsystem: Sentinel.** Study a failover service whose failure detector, election state, reconfiguration steps, and client-discovery role coexist with asynchronous database replication.

- **C1:** Sentinel distinguishes an individual observer's failure suspicion from a quorum judgment and requires majority authorization for failover. The [Sentinel documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/) also explains why acknowledged writes can still be lost with asynchronous replication: election agreement does not imply durable replication of every write.
- **C3:** The [Sentinel implementation](https://github.com/redis/redis/blob/unstable/src/sentinel.c) has explicit promotion/reconfiguration states and reference-counted connection structures shared when the same Sentinel peer monitors multiple masters. Sharing links avoids redundant connections and ping traffic as monitored topologies grow. Replica reconfiguration concurrency is separately controllable.

The bounded study target is `src/sentinel.c`, rather than Redis's entire command engine. Its combination of epochs, observer state, shared networking, and staged reconfiguration makes scaling and failure semantics visible together.

## PostgreSQL and MySQL backup recovery

### 13. [pgbackrest/pgbackrest](https://github.com/pgbackrest/pgbackrest)

**C; PostgreSQL physical backup, WAL archiving, and restore.** A strong study target for recoverability as an end-to-end property of manifests, archived logs, filesystem state, and restartable work.

- **C1:** Restore loads a backup manifest, verifies timeline suitability, and clears stale archive-spool state that could otherwise acknowledge the wrong cluster's WAL. The [restore command implementation](https://github.com/pgbackrest/pgbackrest/blob/main/src/command/restore/restore.c) also preserves a manifest to support restarting a delta restore and tracks checksum errors through job results.
- **C3:** Restore builds work queues and executes them through parallel protocol clients, with periodic memory-context resets. The [project overview](https://github.com/pgbackrest/pgbackrest/blob/main/README.md) connects this structure to parallel backup/restore, delta copying, streaming compression, and asynchronous WAL handling.

Follow the command's validation, remapping, queue processing, and final synchronization phases. They provide a readable route through a performance-sensitive implementation without requiring a study of every storage backend first.

### 14. [EnterpriseDB/barman](https://github.com/EnterpriseDB/barman)

**Python; PostgreSQL backup catalog, WAL management, and local/remote/cloud recovery.** Study how recovery becomes a composition of operations with database-version and target-time constraints.

- **C1:** The [recovery executor](https://github.com/EnterpriseDB/barman/blob/REL_3_X_master/src/barman/recovery_executor.py) validates point-in-time targets, including rejecting a target before backup completion and gating some targets by PostgreSQL version. Recovery also handles tablespace relocation and different execution environments.
- **C2:** Executor variants and recovery-operation classes separate download, rsync, decrypt, decompress, and combine steps. These abstractions support filesystem, snapshot, and incremental recovery paths without making each a completely independent workflow.
- **C4:** [Release notes](https://github.com/EnterpriseDB/barman/blob/REL_3_X_master/RELNOTES.md) span 2012–2026 and record concrete compatibility and failure fixes. For example, recent WAL-restore changes prefer a complete segment over a same-named partial segment and handle cloud-client endpoint behavior consistently.

The executor and release notes together show both the abstraction design and the kinds of real edge cases that reshape it.

### 15. [wal-g/wal-g](https://github.com/wal-g/wal-g)

**Go; database-aware backup and log archiving across object-storage backends.** The PostgreSQL path is the most detailed recovery study entry point here; the repository also contains support for other database families.

- **C1:** The [PostgreSQL guide](https://github.com/wal-g/wal-g/blob/master/docs/PostgreSQL.md) describes preventing conflicting WAL overwrites, verifying archive continuity, and distinguishing missing segments that may still be uploading from segments considered lost. Delta restoration depends on the required chain of backup and WAL data being available.
- **C2:** [Storage implementations and configuration](https://github.com/wal-g/wal-g/blob/master/docs/STORAGES.md) separate database-specific backup behavior from S3, GCS, Azure, Swift, SSH, filesystem, and other storage choices. Retries, transfer behavior, and backend-specific controls remain visible behind that common organization.

Concurrency and archive granularity also expose practical object-request and transfer tradeoffs. Study one database/backend pair deeply before extrapolating: a common repository does not imply identical recovery semantics across all supported databases.

### 16. [postgrespro/pg_probackup](https://github.com/postgrespro/pg_probackup)

**C core with a substantial Python test suite; PostgreSQL physical and incremental backup.** A less ubiquitous selection with unusually explicit alternatives for discovering changed database pages.

- **C3:** PAGE mode derives changed blocks from WAL; DELTA mode scans files and examines page LSNs; PTRACK uses a page-tracking extension. These make the CPU, read-I/O, and integration tradeoffs of incremental backup concrete. See the [backup modes and architecture overview](https://github.com/postgrespro/pg_probackup/blob/master/README.md).
- **C1:** The [merge tests](https://github.com/postgrespro/pg_probackup/blob/master/tests/merge_test.py) construct full/incremental chains, merge them under different compression and parallelism conditions, restore into a replacement data directory, and compare restored contents. This exercises the critical invariant that transforming the backup chain preserves the recoverable database.

Study backup-chain transformation and its tests together. Physical-format and PostgreSQL-version compatibility matter, and PTRACK's extension requirement should not be confused with the requirements of the other modes.

### 17. [percona/percona-xtrabackup](https://github.com/percona/percona-xtrabackup)

**C/C++; hot physical backup and preparation for MySQL-family servers.** Study the division between copying a changing database and preparing a transactionally consistent restore image.

- **C1:** Data files are copied at different moments while redo is captured; the prepare phase applies recovery logic to reconcile the result. Locking and log-coordinate handling vary with the database engines involved. The [implementation overview](https://docs.percona.com/percona-xtrabackup/8.4/how-xtrabackup-works.html) explains why a live file copy alone is insufficient.
- **C3:** Parallel copying and throughput throttling address competition with foreground database work. The [throttling guide](https://docs.percona.com/percona-xtrabackup/8.4/throttling-backups.html) explains the harder interaction: a backup that cannot keep up may encounter redo wraparound, while registering as a redo consumer can instead delay server writes.

This is a particularly useful example of performance settings becoming correctness and availability constraints. The linked documentation is for the 8.4 line; compatibility must be evaluated against the intended server version.

### 18. [mydumper/mydumper](https://github.com/mydumper/mydumper)

**C; parallel logical backup and restore for MySQL/MariaDB.** This complements physical-backup implementations by exposing how many SQL-export workers obtain a coherent snapshot.

- **C1:** Snapshot establishment coordinates worker transactions before releasing protective locks. The [locking documentation](https://mydumper.github.io/mydumper/docs/html/locks.html) distinguishes global-lock, lock-all, GTID-based, and lock-avoiding modes; some modes explicitly sacrifice consistency, while others verify state and abort on unsafe changes.
- **C3:** The [project overview](https://github.com/mydumper/mydumper/blob/master/README.md) describes concurrent export/import and work split across tables/files. This architecture reduces serial dumping bottlenecks while retaining an explicit synchronization phase for the snapshot boundary.

Study the lock-mode matrix alongside the worker model. Parallelism is not itself a consistency strategy, and behavior differs for transactional data, nontransactional tables, and concurrent DDL.

## Distributed database restoration

### 19. [percona/percona-backup-mongodb](https://github.com/percona/percona-backup-mongodb)

**Go; coordinated MongoDB replica-set and sharded-cluster backup and recovery.** Study how a backup spans multiple participants while using the database's own coordination collections.

- **C1:** The [logical-backup implementation](https://github.com/percona/percona-backup-mongodb/blob/dev/pbm/backup/logical.go) reconciles shard progress through running/dump-complete barriers, captures oplog boundaries, and coordinates a common final timestamp. It also waits for temporary users/roles state to reach a secondary before dumping from it. These are concrete consistency obligations beyond independently exporting collections.
- **C2:** The [architecture documentation](https://docs.percona.com/percona-backup-mongodb/latest/details/architecture.html) separates CLI control, an agent at each eligible database node, coordination metadata, and backup storage. The same structure serves replica sets and sharded deployments without requiring a separate coordination service.

This is reusable system architecture, not a claim of a supported Go library API: the project identifies the CLI as its supported public interface.

### 20. [thelastpickle/cassandra-medusa](https://github.com/thelastpickle/cassandra-medusa)

**Python; Apache Cassandra backup and cluster restoration.** A useful recovery-specific codebase for understanding node identity, token placement, and the difference between copying files and streaming data into a new topology.

- **C1:** The [full-cluster restore guide](https://github.com/thelastpickle/cassandra-medusa/blob/master/docs/Restoring-a-full-cluster.md) addresses preserving target-node identity, preventing accidental rejoining of the source cluster, matching token/rack arrangements, and starting seed nodes in the appropriate order. These are distributed-system recovery invariants that a successful object download cannot establish.
- **C2:** The same guide separates in-place restoration, restoration to another cluster with matching topology, and restoration through `sstableloader` when topology changes. Storage integration and backup coordination are shared, while placement-sensitive restore paths differ.

The [repository overview](https://github.com/thelastpickle/cassandra-medusa/blob/master/README.md) gives supported storage options and operating constraints. Study the direct-copy versus streaming decision: the latter accommodates new placement at additional network and disk cost.

### 21. [scylladb/scylla-manager](https://github.com/scylladb/scylla-manager)

**Go; selected scope: ScyllaDB backup and restore orchestration.** The broader manager also performs other operational tasks; the recovery pipeline is the reason for inclusion.

- **C1:** Restore records and removes materialized views, temporarily disables tombstone garbage collection, restores data, repairs replicas, and then reinstates those settings and views. This sequence addresses data consistency during a prolonged distributed restore. The documentation also states limitations around schema matching, CDC, and LWT state.
- **C3:** SSTable bundles are assigned in batches to nodes with adequate free space, downloaded and loaded in parallel, then repaired. A specialized matching-topology path avoids some redistribution work. These phases reveal where local capacity, streaming, and replica consistency constrain throughput.

Read [table restoration](https://github.com/scylladb/scylla-manager/blob/master/docs/source/restore/restore-tables.rst) for both criteria, followed by the [repository overview and test matrix](https://github.com/scylladb/scylla-manager/blob/master/README.md). The documented restore restrictions prevent treating every backup as a complete reconstruction of all database state.

### 22. [pingcap/tidb](https://github.com/pingcap/tidb)

**Go; selected subsystem: BR under `br/`, for TiDB distributed backup and restore.** Counted once in its current monorepo location; the former standalone BR repository is not counted separately.

- **C1:** BR preserves the backup snapshot against garbage collection, retries work affected by Region changes, and records data/file checksums. During restore, newly allocated table and index identifiers require rewriting stored keys before ingestion. See the [snapshot architecture](https://docs.pingcap.com/tidb/stable/br-snapshot-architecture/).
- **C3:** Control work is separated from TiKV workers that transfer SST files. Restore splits and scatters Regions across nodes, while download/ingestion concurrency and queue limits address uneven resource use and coordinator memory pressure. See the [snapshot guide's performance discussion](https://docs.pingcap.com/tidb/stable/br-snapshot-guide/).

Study the orchestration in `br/` together with its TiKV-facing protocol. This is a cluster-wide physical recovery system, with compatibility and system-table restrictions; the report makes no portable throughput claim from the documentation's deployment-specific measurements.

## SQLite recovery and failover

### 23. [benbjohnson/litestream](https://github.com/benbjohnson/litestream)

**Go; continuous SQLite disaster-recovery replication to external storage.** Its purpose is backup and restoration of embedded databases; automatic primary election is not its central abstraction.

- **C1:** The current v0.5 architecture holds a SQLite read transaction to control WAL checkpoint recycling, captures committed transaction boundaries, and checks continuity of transaction IDs during restoration. A missing transaction interval is a recovery failure, not merely an absent object to skip.
- **C3:** LTX files, multiple compaction levels, and snapshots reduce the volume of small files that restoration must process. Compaction also affects the available recovery granularity because restoration consumes whole LTX ranges.

Read [how Litestream works](https://litestream.io/how-it-works/) for the capture, compaction, retention, and restore pipeline. This is asynchronous protection: the recoverable state depends on what reached external storage. Older descriptions of Litestream's generations/shadow-WAL design should not be silently substituted for the current architecture.

### 24. [superfly/litefs](https://github.com/superfly/litefs)

**Go; FUSE-based SQLite replication with lease-controlled primary selection.** The repository describes LiteFS as beta; it is included for its concrete replication and failover design, not an assurance of production suitability.

- **C1:** The filesystem layer observes SQLite transaction completion, replicas reject writes, and a lease service chooses the primary. Replication compares transaction IDs and database checksums; divergent replicas can require a fresh snapshot. Asynchronous failover can discard transactions that exist only on the former primary.
- **C3:** LTX files carry changed pages, and a rolling database checksum updates from page checksums rather than hashing the entire database after every transaction. This keeps divergence detection tied to changed-page work while maintaining an understandable file format and replication protocol.

The [architecture document](https://github.com/superfly/litefs/blob/main/docs/ARCHITECTURE.md) is the entry point for both criteria. Its separation of FUSE, lease, and HTTP replication interfaces also makes the interaction between an embedded database and external coordination unusually accessible.

## Search coverage and limitations

Discovery used live web searches across more than six distinct angles: PostgreSQL monitor/keeper and consensus-store failover; Pacemaker fencing/resource agents; MySQL GTID and relay-log topology recovery; Kubernetes database operators; PostgreSQL WAL/PITR and page-incremental backup; physical versus parallel logical MySQL backup; MongoDB sharded backup barriers; Cassandra/Scylla topology-aware restoration; TiDB distributed snapshot recovery; and SQLite filesystem/log replication. Additional language-oriented searches and SQL Server/Oracle HA/DR searches were used to look beyond the dominant Go, C/C++, Python, and Perl projects. Later searches increasingly returned already-covered projects, broad database engines, operational recipes, or tutorials rather than additional distinct recovery implementations.

Every retained canonical GitHub repository was opened or checked through the GitHub API. For each, at least one additional primary document or source file was opened and read; the cited entry points contain implementation, architecture, recovery procedure, tests, or concrete evolution evidence. Repository metadata was checked for archival and recent activity. An old last-push timestamp is reported as an observation, not proof of abandonment; recent activity is not treated as evidence of quality or long-term support. C4 is used only where release histories supply substantive evolution evidence.

Generic backup frameworks, deployment-only wrappers, awesome lists, tutorial clusters, and broad database engines without a bounded recovery study target were excluded. Oracle and SQL Server searches mostly surfaced tooling around proprietary engines or operational examples rather than comparable inspectable failover cores. PostgreSQL and MySQL consequently receive greater coverage. Related forks were not multiplied into independent selections; VTOrc's separate inclusion is supported by its documented architectural divergence. No unofficial mirror is presented as an upstream project.

This is a source-based selection guide, not a benchmark, compatibility certification, or full correctness audit. No candidate code was run, and no failure-injection experiments were performed. The criteria judgments are grounded engineering inferences from the linked primary material. Default-branch sources and versioned documentation may describe different release states, and recovery guarantees remain conditional on the documented topology, replication mode, storage behavior, and fencing assumptions.
