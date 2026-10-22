# Memory allocators

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing general-purpose heaps, hardened allocators, bounded embedded allocation, arenas and allocator composition, kernel slab allocation, and GPU/heterogeneous-memory pools. The emphasis is on code that exposes difficult engineering decisions and useful implementation structure. Language bindings alone, allocator benchmarks alone, garbage collectors, and ordinary application object pools are outside this report. Monorepositories appear once, with the relevant subsystem identified.

Criteria legend:

- **C1 — Correctness:** demanding invariants, concurrency, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces and mechanisms supporting different applications.
- **C3 — Performance:** concrete latency, throughput, locality, fragmentation, or memory-budget constraints addressed through an understandable architecture.
- **C4 — Evolution:** documented development over years accompanied by compatibility work, testing, or complexity management.

The criteria judgments below are engineering assessments grounded in the linked primary material. They are not proofs of correctness or claims that every component is exemplary. Links within each entry are the recommended documentation/source entry points; repository headings link to verified canonical GitHub URLs.

## General-purpose concurrent heaps

### 1. [microsoft/mimalloc](https://github.com/microsoft/mimalloc)

**C; general-purpose allocator and independently managed heaps.** Study how page-local bookkeeping keeps the ordinary allocation path small while supporting frees from other threads. The currently inspected default branch is `main3`; older design descriptions should not automatically be applied to this version.

- **C1:** The [deallocation implementation](https://raw.githubusercontent.com/microsoft/mimalloc/main3/src/free.c) separates local freeing from atomic remote freeing, handles abandoned-page collection, and explains why certain page fields remain safe to read concurrently. Padding checks, alignment recovery, and ownership transitions intersect in the same path.
- **C3:** The [design overview](https://github.com/microsoft/mimalloc#readme) explains per-page free-list sharding, separate local and concurrent lists, and empty-page purging. These mechanisms address contention, locality, and retained physical memory rather than relying on a single throughput claim.

### 2. [microsoft/snmalloc](https://github.com/microsoft/snmalloc)

**C++; message-passing allocator with explicit platform and pointer abstractions.** A particularly useful comparison with shared free-list designs: remote deallocations return to the owning allocator through message passing, while allocation backing is assembled from multiple range-management layers.

- **C1:** The [strict-provenance design](https://raw.githubusercontent.com/microsoft/snmalloc/main/docs/StrictProvenance.md) distinguishes pointers to internal chunks, client allocations, and unvalidated client input. Its `CapPtr` annotations and CHERI treatment make pointer authority and bounds explicit, including limitations on ordinary architectures.
- **C2 / C3:** [Address-space orchestration](https://github.com/microsoft/snmalloc/blob/main/docs/AddressSpace.md) traces a request through slab refill, separate metadata allocation, thread-local buddy allocators, commit handling, global locking, and the platform abstraction layer. This is a concrete study in composing reusable layers while keeping common requests local.

### 3. [jemalloc/jemalloc](https://github.com/jemalloc/jemalloc)

**C; configurable general-purpose heap with profiling and control interfaces.** Study the interaction between arenas, thread caches, purging, and operational observability, then compare that architecture with the project's ongoing internal simplification.

- **C2 / C3:** The [tuning guide](https://github.com/jemalloc/jemalloc/blob/dev/TUNING.md) explains how arena count trades contention against fragmentation, how decay changes CPU-versus-memory costs, and how explicit arenas and extent hooks support application-specific memory management.
- **C1 / C4:** The [release changelog](https://github.com/jemalloc/jemalloc/blob/dev/ChangeLog) records production testing in the 2022 and 2026 releases, C23 and C++ compatibility fixes, thread-cache initialization and teardown hazards, overflow checks, and removal of cyclic internal dependencies. This is evidence of sustained evolution and complexity management, not merely repository age. The repository was **not archived** when checked.

### 4. [google/tcmalloc](https://github.com/google/tcmalloc)

**C++; Google's contemporary TCMalloc implementation.** Study a deliberately separated front end, transfer/cache middle layer, and page-allocation back end. This is a separate evolving implementation from gperftools below.

- **C1:** The [design document](https://raw.githubusercontent.com/google/tcmalloc/master/docs/design.md) describes the single-accessor assumptions of front-end caches, allocation-size classification and alignment, and recovery of allocation metadata during deallocation. These are important invariants at the boundary between fast paths and shared state.
- **C3:** The same document explains why per-thread cache memory can scale poorly with thread count, motivates per-CPU caching, and separates cache refill from operating-system allocation. It also describes the hugepage-aware back end, making memory-footprint and translation-locality tradeoffs inspectable.

### 5. [gperftools/gperftools](https://github.com/gperftools/gperftools)

**C++; TCMalloc subsystem within a performance-tools repository.** Focus on the allocator, its thread caches, central free lists, and page heap. The project explicitly distinguishes itself from Google's newer TCMalloc, so these are not duplicate entries for a simple fork.

- **C3:** The [allocator design](https://raw.githubusercontent.com/gperftools/gperftools/master/docs/tcmalloc.adoc) explains local cache refill and scavenging, moving unused objects back to central structures. It marks historical benchmark discussion as obsolete and adds modern commentary; the architecture is more useful here than old timings.
- **C1 / C4:** [NEWS](https://github.com/gperftools/gperftools/blob/master/NEWS) documents continuing portability and allocator-semantics work. In 2026, C23 sized deallocation required changing `realloc` heuristics; macOS page sizing and Windows commit-versus-allocation granularity also receive explicit fixes. Combined with the design's documented long evolution, these are concrete compatibility examples.

### 6. [mjansson/rpmalloc](https://github.com/mjansson/rpmalloc)

**C; thread-caching allocator with configurable virtual-memory providers.** Study the mapping from aligned spans to pages and blocks, and how ownership makes local operations cheap. The inspected development branch is `develop`.

- **C1:** The [implementation](https://raw.githubusercontent.com/mjansson/rpmalloc/develop/rpmalloc/rpmalloc.c) routes cross-thread frees to a deferred list and performs their accounting at the owner. It also documents allocator-finalization hazards when runtime allocations still depend on overridden `malloc` functions.
- **C2 / C3:** The [implementation overview](https://github.com/mjansson/rpmalloc#readme) explains span-address masking instead of lookup tables, page types containing size-class blocks, and customizable map/commit/decommit/unmap callbacks. Those provide reusable integration points with explicit locality and virtual-memory tradeoffs. Invalid-pointer hardening is not its stated goal.

### 7. [emeryberger/Hoard](https://github.com/emeryberger/Hoard)

**C++; scalable heap organized around superblocks and heap layers.** Study how local allocation and global memory reuse coexist, especially when different threads allocate and free the same workload's objects.

- **C1:** [`HoardManager`](https://github.com/emeryberger/Hoard/blob/master/src/include/hoard/hoardmanager.h) drains delayed frees before transferring a superblock and adjusting utilization statistics. Owner changes, locking, and threshold decisions must agree; the code makes these dependencies visible.
- **C3:** The [project's architectural motivation](https://github.com/emeryberger/Hoard#readme) centers on allocator contention, false sharing, and memory blowup. The manager implementation bins superblocks by utilization and returns sufficiently empty ones to a parent heap, providing a concrete mechanism to study behind those goals.

### 8. [uxlfoundation/oneTBB](https://github.com/uxlfoundation/oneTBB)

**C++; `tbbmalloc` and `tbbmalloc_proxy` subsystems of oneTBB.** Counted once for its allocator, not its task scheduler. Study how a scalable allocator exposes both C allocation functions and C++ integration without coupling every caller to internal slab management.

- **C1 / C3:** The [front end](https://github.com/uxlfoundation/oneTBB/blob/master/src/tbbmalloc/frontend.cpp) separates owner-local fields from atomic public free lists to reduce false sharing. Bootstrap allocation, orphaned blocks, remote frees, and thread shutdown add correctness obligations around the ordinary fast path.
- **C2:** The [allocator interface](https://github.com/uxlfoundation/oneTBB/blob/master/include/oneapi/tbb/scalable_allocator.h) includes aligned allocation, allocator controls, C++ allocator support, and raw pool callbacks with fixed-pool and retention policies. These are substantive integration abstractions, beyond a replacement `malloc` symbol.

## Fragmentation and virtual-memory research designs

### 9. [plasma-umass/Mesh](https://github.com/plasma-umass/Mesh)

**C++; research-origin allocator that recovers fragmented physical memory through meshing.** Study the distinction between an object's virtual address and the physical backing of its page. The repository includes the PLDI 2019 work, but its current implementation should be read on its own terms.

- **C1:** The [meshable arena](https://github.com/plasma-umass/Mesh/blob/master/src/meshable_arena.h) write-protects a region before meshing, updates its miniheap mapping, and remaps it to another region's backing. Fork handling and restoration of mappings show that transparent reclamation involves more than free-list manipulation.
- **C3:** The [global heap](https://github.com/plasma-umass/Mesh/blob/master/src/global_heap.h) separates size-class and arena locking, tracks empty/partial/full miniheaps, and drains pending partial lists. Comments explain races that require a separate pending-list link. It is a useful study of fragmentation reduction alongside concurrent allocation structure; savings depend on workload fragmentation.

### 10. [cksystemsgroup/scalloc](https://github.com/cksystemsgroup/scalloc)

**C++; research allocator using virtual spans and reusable global span structures.** Useful for studying uniform treatment of small and larger objects through virtual-address-space layout. Treat it as a research implementation requiring environment-specific evaluation, as its own documentation advises; the API reported its last push in June 2025, not an archival flag.

- **C1:** [`Span`](https://github.com/cksystemsgroup/scalloc/blob/master/src/span.h) tracks atomic ownership, epoch/state bits, separate local and remote free lists, and transitions among hot, full, reusable, and floating states. Correct reuse depends on these transitions agreeing across threads.
- **C3:** The [design overview](https://github.com/cksystemsgroup/scalloc#readme) ties virtual spans and global reclamation to locality, memory reuse, and false-sharing avoidance. It also discloses substantial virtual-address-space use and operating-system configuration assumptions. Algorithmic bounds are qualified by synchronization costs.

## Hardened and fault-tolerant allocation

### 11. [GrapheneOS/hardened_malloc](https://github.com/GrapheneOS/hardened_malloc)

**C, with C++ allocation entry points; security-focused general-purpose heap.** Study how a large 64-bit address space permits metadata isolation, size-class separation, guarded regions, and delayed reuse. This is a substantive implementation, despite design inspiration from OpenBSD malloc.

- **C1:** The [core allocator](https://raw.githubusercontent.com/GrapheneOS/hardened_malloc/main/h_malloc.c) maintains allocation and quarantine bitmaps, validates slab metadata lookup, selects randomized free slots, and checks for writes after free. These mechanisms address adversarial heap corruption, not just valid-call behavior.
- **C3:** The [core-design and scalability documentation](https://github.com/GrapheneOS/hardened_malloc#readme) explains separate metadata regions, independent arenas, and per-size-class locking. It discusses the performance and address-space consequences of hardening and intentionally targets 64-bit systems. Security properties remain configuration-dependent.

### 12. [llvm/llvm-project](https://github.com/llvm/llvm-project)

**C++; Scudo standalone allocator in `compiler-rt/lib/scudo/standalone`.** This monorepository is included specifically for Scudo. Study how security checks are layered over different small- and large-allocation mechanisms.

- **C1:** The [Scudo design document](https://www.llvm.org/docs/ScudoHardenedAllocator.html) describes checksummed chunk headers, allocation-state and API-family validation, and atomic header updates that avoid double fetching. Guarded mappings and optional quarantine address different corruption and reuse hazards.
- **C2 / C3:** The same document separates primary size-class allocation, secondary mapped allocation, thread-data registries, and quarantine. Exclusive versus shared cache registries make scalability policy configurable. The [standalone source tree](https://github.com/llvm/llvm-project/tree/main/compiler-rt/lib/scudo/standalone) exposes these components and their tests. Quarantine is documented as costly and disabled by default; its availability is not an unconditional protection claim.

### 13. [emeryberger/DieHard](https://github.com/emeryberger/DieHard)

**C++; DieHard, DieHarder, and Exterminator research family, counted as one repository.** Study probabilistic tolerance of memory errors and the tensions it creates with ordinary allocator optimizations. Historical papers describe earlier versions; the [current project documentation](https://github.com/emeryberger/DieHard/blob/master/README.md) distinguishes adaptive heaps and a scalable mode, and says Windows is currently unsupported.

- **C1:** The [cross-thread free pool](https://github.com/emeryberger/DieHard/blob/master/src/include/globalfreepool.h) deliberately stores pending frees in external ring buffers rather than overwriting freed objects with list pointers. Its producer reservation, publication, owner-only draining, and full-queue behavior expose demanding concurrency invariants.
- **C3:** That queue batches remote frees and separates counters by cache line, while the documented scalable mode uses per-thread heaps and atomic allocation bitmaps. This provides an inspectable approach to reducing synchronization without immediately destroying the contents of freed objects. Probabilistic mitigation is not a guarantee that erroneous programs become correct.

## Embedded, bounded, and explicitly supplied heaps

### 14. [mattconte/tlsf](https://github.com/mattconte/tlsf)

**C; compact Two-Level Segregated Fit implementation.** A valuable historical reference for real-time allocation. Its README history reaches from 2006 to 2016; GitHub reported the last push in November 2021. It was not archived, but should not be described as actively maintained on that evidence.

- **C1:** [`tlsf.c`](https://github.com/mattconte/tlsf/blob/master/tlsf.c) maintains physical-neighbor information alongside indexed free lists, handles split/coalesce transitions, guards oversized bin indices, and checks agreement between bitmap state and list contents.
- **C3 / C4:** The [design and version history](https://github.com/mattconte/tlsf#readme) explains bitmap-based bounded lookup and records multi-pool support, alignment validation, 64-bit support, integrity checks, and `realloc` fixes over multiple years. Thread safety is explicitly the caller's responsibility. Bounded allocator bookkeeping does not bound copying, external locking, or operating-system activity.

### 15. [spaskalev/buddy_alloc](https://github.com/spaskalev/buddy_alloc)

**C, usable from C++; single-header buddy allocator for caller-supplied arenas.** Study a deliberately restricted allocator with predictable metadata sizing, rather than a process-wide heap replacement.

- **C1:** The [header and API contracts](https://raw.githubusercontent.com/spaskalev/buddy_alloc/main/buddy_alloc.h) specify resize failure when live allocations would fall outside a shrunken arena, preserve existing allocations on failure, and distinguish embedded metadata from externally stored metadata.
- **C2 / C3:** The [implementation explanation](https://github.com/spaskalev/buddy_alloc#readme) describes a bitset-backed binary tree whose nodes summarize available allocation sizes, masking for non-power-of-two arenas, and a placement preference that preserves larger free regions. Embedded relocatable arenas and arena walking support uses beyond ordinary `malloc`. Shared access requires external synchronization.

### 16. [yvt/rlsf](https://github.com/yvt/rlsf)

**Rust; TLSF implementation for bare-metal and hosted use.** This is a separate Rust implementation, with a low-level supplied-pool allocator and a higher-level global allocator. It is useful alongside the C TLSF reference because lifetimes and configurable bitmap types become part of the design.

- **C1:** The [allocator core](https://github.com/yvt/rlsf/blob/main/crates/rlsf/src/tlsf.rs) documents bitmap/list equivalence, pool lifetime tracking, header size bits, sentinel invariants, and unsafe pointer preconditions. Its diagram maps the two-level index directly to free blocks.
- **C2 / C3:** The [API and tradeoff discussion](https://github.com/yvt/rlsf#readme) exposes bin-count parameters, caller-provided pools, and `GlobalTlsf`. It explicitly discusses fragmentation versus free-list count, lack of concurrent pool access, and the global allocator's inability to return pages to the system. The bounded-time claim concerns the core algorithm, not arbitrary lock contention.

### 17. [SFBdragon/talc](https://github.com/SFBdragon/talc)

**Rust; extensible allocator for `no_std` and WebAssembly.** Study the separation between free-space management, supplying backing memory, and synchronization. The current source has `Talc`, `TalcCell`, and `TalcLock` roles rather than one universal interface.

- **C1:** The [core implementation](https://github.com/SFBdragon/talc/blob/master/talc/src/base/mod.rs) tracks size-bucketed gap lists with an availability bitmap and uses explicit unsafe allocation preconditions. Its comments distinguish exclusive mutable access from the wrappers required for shared allocation.
- **C2 / C3:** The same source defines separate `Source` and `Binning` policies: one acquires/reclaims backing memory, while the other classifies free chunks and occupancy. These let embedded and WebAssembly integrations vary without replacing the allocator core. The [project overview](https://github.com/SFBdragon/talc#readme) also documents Miri/fuzz testing and cautions that hosted concurrent allocators have different maturity and integration strengths.

## Arenas and allocator composition

### 18. [fitzgen/bumpalo](https://github.com/fitzgen/bumpalo)

**Rust; bump arena with arena-backed collections and optional boxed values.** Study how a very small allocation mechanism grows into a reusable library once lifetimes, fallible initialization, and destruction semantics are handled explicitly.

- **C1:** The [implementation](https://github.com/fitzgen/bumpalo/blob/main/src/lib.rs) contains a rewind guard for failed initialization: it rewinds only if the guarded allocation is still the most recent one. This avoids invalidating later allocations made during initialization. The source also distinguishes allocation failure from initializer failure.
- **C2 / C3:** The [arena documentation](https://github.com/fitzgen/bumpalo#readme) explains chunk growth, mass reset, arena-bound collection lifetimes, and optional `Box` destruction. Bulk reclamation suits phase-oriented work, but ordinary arena reset does not run every allocated value's destructor; that semantic choice is central to using the abstraction correctly.

### 19. [foonathan/memory](https://github.com/foonathan/memory)

**C++; allocator concepts, pools, stacks, arenas, and standard-library adapters.** Study how a byte-oriented allocation model can interoperate with C++ containers while allowing policy composition. GitHub's last-push metadata was May 2025; no claim of current maintenance cadence is made.

- **C2:** The [library overview](https://github.com/foonathan/memory#readme) distinguishes `RawAllocator` and `BlockAllocator`, then connects them through traits, references, standard allocator adapters, smart-pointer deleters, and tracking wrappers. The library implements allocation strategies as well as adapters.
- **C1 / C3:** [`memory_pool.hpp`](https://github.com/foonathan/memory/blob/main/include/foonathan/memory/memory_pool.hpp) shows an arena divided into fixed-size nodes and policy-controlled free lists. It documents minimum block sizes, container proxy-node overhead, and ownership transfer on moves: memory must not be returned through a moved-from pool. Those contracts connect performance specialization to C++ lifetime correctness.

## Kernel allocation

### 20. [torvalds/linux](https://github.com/torvalds/linux)

**C; SLUB and allocation APIs in the official GitHub mirror of Linus Torvalds's kernel tree.** Counted once, specifically for `mm/slub.c` and kernel allocation contracts. Study how allocator invariants change when interrupts, reclaim, NUMA nodes, and memory hotplug are involved.

- **C1 / C3:** The [current SLUB implementation](https://github.com/torvalds/linux/blob/master/mm/slub.c) begins with its lock ordering, per-CPU caching strategy, atomic freeing, and partial/full/frozen slab states. It explicitly describes quarantining structurally inconsistent slabs from further allocation and avoiding centralized locks where possible. These details are version-sensitive; older SLUB articles may describe different state meanings.
- **C2:** The [allocation guide](https://github.com/torvalds/linux/blob/master/Documentation/core-api/memory-allocation.rst) separates object, virtual-region, and page allocation, then explains flags governing sleeping, reclaim, emergency reserves, and accounting. This is a reusable policy interface whose correctness depends on the caller's execution context.

## GPU and heterogeneous-memory allocation

### 21. [GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator](https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator)

**C++ implementation with a C API; Vulkan device-memory allocation.** Study suballocation where memory-type selection, buffer/image granularity, mapping, and device budgets matter as much as finding free bytes.

- **C1:** [`vk_mem_alloc.h`](https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator/blob/master/include/vk_mem_alloc.h) contains allocation metadata validation, physical-neighbor and free-list structures, and a granularity handler associated with its TLSF metadata. The public documentation also explains mapping and non-coherent-memory constraints.
- **C2 / C3:** The [custom-pool guide](https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator/blob/master/docs/html/custom_memory_pools.html) describes per-memory-type default pools, fixed or bounded custom pools, preallocation, and linear allocation modes. Together with the source's TLSF and linear implementations, this offers real policy choices for transient resources versus general workloads.

### 22. [GPUOpen-LibrariesAndSDKs/D3D12MemoryAllocator](https://github.com/GPUOpen-LibrariesAndSDKs/D3D12MemoryAllocator)

**C++; Direct3D 12 heap and placed-resource allocation.** Related to Vulkan Memory Allocator and sharing some code, but retained separately for substantive D3D12-specific resource, heap-tier, and residency-budget integration.

- **C1:** The [resource-allocation description](https://github.com/GPUOpen-LibrariesAndSDKs/D3D12MemoryAllocator#readme) explains alignment and the differing resource-separation rules of D3D12 heap tiers. Resource placement must honor those rules as well as allocator bookkeeping.
- **C2 / C3:** The [implementation](https://github.com/GPUOpen-LibrariesAndSDKs/D3D12MemoryAllocator/blob/master/src/D3D12MemAlloc.cpp) separates linear and TLSF block metadata. TLSF tracks physical neighbors, free-list bitmaps, allocation counts, and a validation pass. Custom pools and the virtual-allocation API reuse these mechanisms for different resource lifetimes and for suballocation without creating actual GPU memory.

### 23. [Traverse-Research/gpu-allocator](https://github.com/Traverse-Research/gpu-allocator)

**Rust; native allocator implementation for Vulkan, DirectX 12, and Metal.** This is not a generated wrapper around AMD's allocators. Study how graphics back ends share allocation policy while API-specific code handles resource binding and platform details.

- **C1:** The [free-list suballocator](https://github.com/Traverse-Research/gpu-allocator/blob/main/src/allocator/free_list_allocator/mod.rs) checks adjacent allocation types for granularity conflicts, aligns offsets, splits and merges chunks, and updates linked-neighbor identifiers. Its core explicitly denies unsafe code, leaving low-level API operations to other layers.
- **C2 / C3:** The same implementation realizes a best-fit `SubAllocator` with allocation reporting, while the [usage documentation](https://github.com/Traverse-Research/gpu-allocator/blob/main/README.md) demonstrates the corresponding allocation descriptions and lifetime cleanup across three graphics APIs. Shared suballocation logic and configurable block sizes address both reuse and fragmentation.

### 24. [rapidsai/rmm](https://github.com/rapidsai/rmm)

**C++/CUDA with Python interfaces; NVIDIA RMM memory resources.** Study allocation as a composable resource and the additional ordering requirements introduced by asynchronous GPU work. Current source paths differ from older releases that put these resources under `mr/device`.

- **C1 / C3:** The [stream-ordered resource base](https://github.com/rapidsai/rmm/blob/main/cpp/include/rmm/mr/detail/stream_ordered_memory_resource.hpp) separates per-stream free pools and records CUDA events on deallocation. It centralizes ordering logic while delegating block splitting and pool expansion, exposing why host-side `free` is insufficient to establish device-side reuse safety.
- **C2:** The [pool resource](https://github.com/rapidsai/rmm/blob/main/cpp/include/rmm/mr/pool_memory_resource.hpp) defines a coalescing best-fit suballocator backed by an upstream resource, with shared internal ownership, thread-safe operations, and explicit initial/maximum pool sizes. The current interface uses CUDA memory-resource concepts; it should not be confused with older RMM API descriptions.

### 25. [llnl/Umpire](https://github.com/llnl/Umpire)

**C++; allocation strategies for NUMA and GPU memory resources.** Study how a scientific-computing memory manager supplies reusable pooling policy over different upstream devices. The repository contains the pool implementation, not only dispatch wrappers.

- **C1 / C3:** [`QuickPool.cpp`](https://github.com/LLNL/Umpire/blob/develop/src/umpire/strategy/QuickPool.cpp) searches a size-ordered map for a suitable chunk, splits allocations, tracks releasable capacity, and responds to upstream allocation failure by releasing free chunks and retrying. This makes pressure recovery and fragmentation accounting concrete.
- **C2:** [`QuickPool.hpp`](https://github.com/LLNL/Umpire/blob/develop/src/umpire/strategy/QuickPool.hpp) exposes an underlying `Allocator`, separate initial/subsequent growth sizes, alignment, and selectable coalescing heuristics. The strategy interface separates those reusable policies from the choice of host, NUMA, or device memory.

## Coverage, search process, and limitations

Discovery used more than six distinct live query formulations, covering: general-purpose `malloc` replacements and message passing; hardened heaps and Scudo; embedded/real-time TLSF and buddy allocation; Rust `no_std`, WebAssembly, and arenas; GPU allocation for Vulkan, D3D12, Metal, and CUDA; C++ allocator composition; NUMA/HPC memory resources; virtual-span/meshing research; probabilistic hardening; and Zig's repository migration. Follow-up queries and source-tree traversal increasingly returned the same allocator families, thin bindings, benchmarks, or small teaching examples. DieHard was retained from the final hardening sweep because its fault-tolerance constraints added a distinct design angle.

Every retained repository's canonical URL, default branch, and archival status was checked through GitHub repository metadata. Each also had additional primary documentation or source opened and read; architecture claims do not rely on search snippets. None of these 25 repositories was marked archived at the time of checking. That flag is not evidence of active maintenance: the especially old TLSF push and the 2025 metadata for scalloc and foonathan/memory are called out above. C4 is awarded for documented evolution and engineering changes, never for creation dates or push recency alone.

The report avoids counting TLSF ports, allocator bindings, or benchmark harnesses as additional implementations without a substantive reason. RLSF is retained as a distinct Rust implementation; Google's TCMalloc and gperftools have documented separate evolution; the two AMD libraries have significant different graphics-API integration. Scudo, oneTBB allocation, Linux SLUB, and the DieHard family each count only once. The Linux entry is explicitly an official GitHub mirror. Zig was excluded because its [official GitHub README](https://github.com/ziglang/zig/blob/master/README.md) states that the project moved to Codeberg and that the repository is not mirrored.

This is a broad selection, not a census: it does not systematically cover every libc allocator, persistent-memory allocator, managed-language runtime, or GPU research prototype. PartitionAlloc and further research allocators are also outside this selection. No candidate code was executed, dependencies installed, or comparative benchmarks reproduced. Numerical speed rankings and unconditional hardening guarantees are intentionally absent; deployment suitability requires workload- and version-specific evaluation.
