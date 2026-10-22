# Trusted execution runtimes and enclave frameworks

Research date: **2026-10-09**.

This report selects 24 substantial GitHub codebases implementing trusted execution environments (TEEs), enclave operating environments, language SDKs, or reusable confidential application frameworks. It covers Intel SGX, Arm TrustZone and secure partitions, RISC-V protection mechanisms, and confidential virtual machines. Host-side runtimes are included when they implement meaningful enclave lifecycle and resource management. General cryptography libraries, attestation-only utilities, tutorials, and ordinary process sandboxes are outside scope.

These are engineering study recommendations, not security certifications. Criteria describe concrete complexity and useful design material; they do not imply that every component is exemplary. Historical implementations remain valuable and are explicitly identified. A repository without a status warning is not thereby asserted to be actively maintained.

**Criteria legend**

- **C1 — Difficult correctness:** security boundaries, adversarial inputs, concurrency, state invariants, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and components supporting different applications or platforms.
- **C3 — Performance with structure:** explicit treatment of execution, memory, or communication costs within an understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, coordinated testing, or complexity management.

## Linux application environments

### 1. [gramineproject/gramine](https://github.com/gramineproject/gramine)

**Languages / role:** C and assembly; a library OS for running Linux applications, including inside SGX enclaves. Formerly Graphene. Study the division between Linux syscall emulation in the LibOS and the platform adaptation layer (PAL), rather than treating enclave execution as a simple loader feature.

- **C1:** The performance documentation explains why data returned from an untrusted host must be copied into enclave memory to avoid time-of-check/time-of-use races. It also exposes the semantic and implementation costs of emulated syscalls.
- **C2:** The LibOS, PAL, and supported C-library arrangements separate application compatibility from platform-specific execution.
- **C3:** Documentation connects OCALL transitions, asynchronous exits, copying, and syscall choices to profiling facilities. This makes bottlenecks traceable to architecture; no benchmark speedup is assumed here.

**Entry points:** [Build and component structure](https://gramine.readthedocs.io/en/latest/devel/building.html); [performance analysis](https://gramine.readthedocs.io/en/latest/performance.html). The latter also documents an insecure exitless option; its presence should not be read as a production recommendation.

### 2. [occlum/occlum](https://github.com/occlum/occlum)

**Languages / role:** Rust and C; a multiprocess LibOS inside a single SGX enclave. Its process model, filesystem choices, and enclave resource configuration provide a useful comparison with Gramine. Processes sharing one enclave should not be assumed to have ordinary Linux address-space isolation.

- **C1:** The EDMM guide distinguishes initial allocations from maxima and explains failure-prone differences when the same configuration runs on hardware without dynamic enclave memory management. A configured maximum is not automatically an effective physical-memory limit.
- **C2:** The repository combines a reusable Linux application environment with hashed read-only storage, encrypted writable storage, and explicitly untrusted host filesystems.
- **C3:** EDMM configuration addresses startup and memory commitment by allocating resources on demand, while retaining a non-EDMM execution path. The guide makes the compatibility cost of large maxima explicit.

**Entry point:** [EDMM configuration and implementation limitations](https://github.com/occlum/occlum/blob/master/docs/edmm/edmm_config_guide.md).

### 3. [microsoft/mystikos](https://github.com/microsoft/mystikos)

**Languages / role:** Primarily C; a Linux-compatible LibOS with a C runtime, kernel, and target-call interface supporting SGX and a Linux execution target. **Archived on January 5, 2026**; the former `deislabs/mystikos` URL redirects here.

- **C1:** The kernel limitations document is particularly instructive about semantic compromises: process-like execution can share an address space, thread availability can produce `EAGAIN`, and monotonic-looking host time does not establish a trusted clock. Filesystem backends also differ in persistence and trust.
- **C2:** The separation of application C runtime, LibOS kernel, and TCALL target interface makes the implementation reusable across host and enclave targets. Engineers can study which Linux contracts remain intact and which require application constraints.

**Entry point:** [Kernel limitations and execution semantics](https://github.com/microsoft/mystikos/blob/main/doc/kernel-limitations.md). This is a historical architecture reference, not a maintained deployment recommendation.

## Enclave SDKs and language runtimes

### 4. [intel/confidential-computing.sgx.sdk](https://github.com/intel/confidential-computing.sgx.sdk)

**Languages / role:** C, C++, assembly, and OCaml tooling; Intel's SGX SDK and enclave runtime. This is the SDK repository split out of the consolidated SGX project beginning with release 2.30, rather than a second independent implementation of `linux-sgx`.

- **C1:** The runtime architecture separates untrusted loading and ECALL/OCALL dispatch from the trusted runtime linked into an enclave. Metadata parsing and the create/load/initialize/delete lifecycle provide concrete invariants to follow across this boundary.
- **C2:** The enclave-common API, platform abstractions, trusted runtime libraries, and simulation counterparts support applications and higher-level enclave frameworks. Study how hardware execution, simulation, and mitigation-specific builds share components without having identical behavior.

**Entry point:** [Enclave runtime architecture and source tree](https://github.com/intel/confidential-computing.sgx.sdk/tree/main/enclave_runtime). The [consolidated parent repository](https://github.com/intel/confidential-computing.sgx) documents the repository reorganization; it is not counted separately.

### 5. [openenclave/openenclave](https://github.com/openenclave/openenclave)

**Languages / role:** C and C++; a host/enclave SDK with platform abstractions and C/C++ runtime support. The repository describes SGX support and an OP-TEE preview; those should not be interpreted as equivalent maturity levels.

- **C1:** Its TLS design makes subtle language-runtime obligations explicit: an enclave thread is associated with a host thread for an ECALL, thread-local storage is initialized, nontrivial C++ constructors have defined triggering behavior, and destructors run when the enclave-thread lifetime ends.
- **C2:** Those language facilities sit behind reusable host/enclave APIs. The documented local-exec TLS model also shows how a general C/C++ abstraction must be constrained for an enclave's loading and linking environment.

**Entry points:** [Thread-local storage design](https://github.com/openenclave/openenclave/blob/master/docs/ThreadLocalSupport.md); [changelog and compatibility changes](https://github.com/openenclave/openenclave/blob/master/CHANGELOG.md). The changelog distinguishes additions, deprecations, and breaking changes; this report does not infer long-term compatibility from version numbers alone.

### 6. [fortanix/rust-sgx](https://github.com/fortanix/rust-sgx)

**Languages / role:** Rust; components of Fortanix Enclave Development Platform, including the enclave runner, SGX interfaces, and IPC support. The enclave implementation of Rust's standard library lives in the Rust compiler repository, so this repository is not the whole toolchain.

- **C1:** The architecture explains its deliberately small usercall ABI, consistent buffer handling, and defenses against malicious host responses, untrusted-memory races, and inadvertent information disclosure through representations.
- **C2:** Rust applications access familiar standard-library facilities while a replaceable runner translates usercalls into host operations. This separation is useful for studying how a language runtime can expose ordinary I/O without making the host part of the trusted computing base.

**Entry point:** [EDP architecture and usercall boundary](https://edp.fortanix.com/docs/concepts/architecture/). Treat the security discussion as design rationale, not a proof that every unsafe boundary is correct.

### 7. [apache/teaclave-sgx-sdk](https://github.com/apache/teaclave-sgx-sdk)

**Languages / role:** Rust; trusted runtime, standard-library support, boundary tooling, and application libraries for SGX. The current v2 work is a runtime redesign, not merely Rust bindings around every Intel SDK operation.

- **C1:** Its security model specifies adversarial ECALL arguments, OCALL results, and concurrently mutable shared memory. Overflow-safe range checks, EDL direction annotations, and the consequences of bypassing generated checks are concrete review targets. It also distinguishes sealed-data integrity from freshness.
- **C2:** Trusted and untrusted crate families, `std` and `no_std` support, asynchronous application integrations, and an enclave testing framework make this a reusable Rust execution environment. The model clearly includes linked dependencies in the application's trusted computing base.

**Entry point:** [Security model and runtime boundary responsibilities](https://github.com/apache/teaclave-sgx-sdk/blob/main/docs/security-model.md). This SDK is counted independently of the former Teaclave confidential-computing service, which is excluded below.

### 8. [apache/teaclave-trustzone-sdk](https://github.com/apache/teaclave-trustzone-sdk)

**Languages / role:** Rust; SDK for OP-TEE trusted applications and their normal-world clients. Study how a typed language interface maps onto GlobalPlatform-style runtime parameter tags and host-controlled buffers.

- **C1:** The parameter migration guide introduces distinct input, output, and in/out wrappers while retaining runtime validation of the four parameter slots. It covers wrong-tag rejection, bounded allocation, and when to copy input instead of retaining host-controlled references.
- **C2:** Reusable parameter traits, conversion macros, and trusted-application lifecycle APIs replace repeated unsafe decoding in individual services. The migration from a generic unsafe parameter API is a concrete example of improving an abstraction while exposing compatibility implications.

**Entry point:** [Typed OP-TEE parameter migration](https://github.com/apache/teaclave-trustzone-sdk/blob/main/docs/optee-utee-parameter-migration.md). This complements, rather than duplicates, the OP-TEE operating system entry.

### 9. [edgelesssys/ego](https://github.com/edgelesssys/ego)

**Languages / role:** Go and C++; a Go enclave SDK with compiler integration, signing/loading tools, and attestation and sealing APIs. It builds on Edgeless RT; that dependency is not counted as another selection here.

- **C1:** The TLS guide explains why a conventional host certificate store is not automatically trustworthy inside an enclave. It describes embedding roots into measured application code and binding an enclave-generated public key to attestation evidence.
- **C2:** A Go toolchain and enclave-aware libraries let many ordinary Go applications use confidential execution, while higher-level attested TLS helpers package a protocol that otherwise requires each application to coordinate measurement verification and key authentication.

**Entry point:** [TLS trust and attested connections](https://docs.edgeless.systems/ego/knowledge/tls). This is especially useful for engineers who need to understand the trust consequences of familiar standard-library networking APIs.

### 10. [R3Conclave/conclave-core-sdk](https://github.com/R3Conclave/conclave-core-sdk)

**Languages / role:** Kotlin, Java, and C++; a JVM-oriented SGX application framework. **The repository states that Conclave is discontinued and no longer actively maintained.**

- **C1:** Its architecture ties enclave identity, signing policy, security status, and communication keys together. `EnclaveInstanceInfo` and `EnclaveConstraint` illustrate the difference between accepting one exact code measurement and accepting an authorized signer, while the host forwards encrypted messages.
- **C2:** Separate client, untrusted host, and enclave APIs make the transport-independent Mail abstraction reusable across services. The host HotSpot JVM and the enclave's separate runtime also reveal where ordinary JVM expectations meet native enclave constraints.

**Entry point:** [Architecture, roles, attestation, and Mail](https://github.com/R3Conclave/conclave-core-sdk/blob/master/docs/docs/architecture.md). Retained for its unusually clear application protocol and language-runtime design, with its discontinued status explicit.

### 11. [google/asylo](https://github.com/google/asylo)

**Languages / role:** C++; a framework abstracting enclave applications from execution backends, with protocol-buffer interfaces and security-oriented communication facilities. **Archived on April 17, 2026**; older README descriptions of activity should not override the archive banner.

- **C1:** `TrustedApplication` specifies initialization, invocation, finalization, and status propagation. Its object-lifetime contract is unusual and important: the runtime does not invoke the application destructor, so cleanup must follow the documented lifecycle rather than ordinary RAII assumptions.
- **C2:** An abstract application class with protobuf configuration, request, and response messages gives different applications a common runtime interface. Backend separation and simulation support make the project useful for studying enclave-independent development and testing.

**Entry point:** [TrustedApplication lifecycle interface](https://github.com/google/asylo/blob/master/asylo/platform/core/trusted_application.h). The historical value is in its explicit contracts and reusable framework, not a claim of current support.

## Secure operating systems, monitors, and embedded execution

### 12. [OP-TEE/optee_os](https://github.com/OP-TEE/optee_os)

**Languages / role:** C and assembly; the secure-world operating system in OP-TEE. Study trusted threads, secure monitor calls, interrupt handling, and the execution environment for trusted applications.

- **C1:** The core architecture distinguishes fast and yielding secure monitor calls, explains thread suspension and resumption, and describes secure/nonsecure context transitions and foreign-interrupt handling. Correct context restoration is essential to preserving isolation through asynchronous events.
- **C2:** Trusted-application execution and secure services run above common core facilities while architecture and platform code handle machine-specific mechanisms.
- **C4:** The inspected changelog spans releases from 2018 through 2026 and connects changes to coordinated `optee_os`, client, test, and build releases. This supplies evidence of sustained integration and complexity management beyond repository age.

**Entry points:** [Core architecture](https://optee.readthedocs.io/en/latest/architecture/core.html); [release history](https://github.com/OP-TEE/optee_os/blob/master/CHANGELOG.md).

### 13. [TrustedFirmware-M/trusted-firmware-m](https://github.com/TrustedFirmware-M/trusted-firmware-m)

**Languages / role:** Primarily C; secure processing and partition management for constrained systems, especially Arm microcontrollers. **Official read-only GitHub mirror**; its README identifies the Trusted Firmware upstream repository.

- **C1:** The secure partition manager's IPC backend maintains per-partition execution contexts and supports stronger isolation levels. The alternative Secure Function backend shares an execution context and has a narrower isolation model. These are consequential security and scheduling differences, not interchangeable build switches.
- **C2:** A shared API frontend and interchangeable backends allow secure services to target different resource and isolation requirements.
- **C3:** The backend guide explicitly trades memory and call overhead against isolation capability: direct secure-function execution is cheaper but limited to isolation level 1.

**Entry point:** [Secure partition manager backends](https://trustedfirmware-m.readthedocs.io/en/latest/integration_guide/spm_backends.html). The GitHub mirror is substantive source code; this report does not assume instantaneous upstream synchronization.

### 14. [usbarmory/GoTEE](https://github.com/usbarmory/GoTEE)

**Languages / role:** Go and assembly; a TamaGo-based monitor and trusted execution framework for embedded systems, with Arm TrustZone and RISC-V privilege support. It offers execution contexts and communication interfaces usable by applets in multiple languages.

- **C1:** The examples exercise isolation failures, including forbidden secure-memory and peripheral accesses. A soft-lockstep example executes a deterministic applet in separate physical memory mappings and compares execution at monitor calls, with fault injection to test divergence handling.
- **C2:** The monitor supports trusted applications alongside richer operating environments, and exposes syscall/RPC boundaries rather than embedding one fixed application. The lockstep example demonstrates how those boundaries can support another execution policy.

**Entry point:** [Examples, isolation checks, and soft lockstep](https://github.com/usbarmory/GoTEE/wiki/Examples). The repository notes emulation-only testing for its RISC-V target and incomplete hardware-security emulation in QEMU; those limit what the examples establish.

### 15. [keystone-enclave/keystone](https://github.com/keystone-enclave/keystone)

**Languages / role:** C, C++, and assembly; a RISC-V enclave security monitor, runtime, and SDK monorepo. **The project states that active development and maintenance have stopped and it is transitioning to emeritus status.**

- **C1:** Its separation of an untrusted host, supervisor-level enclave runtime, and user-level enclave application exposes multiple protection boundaries. Shared memory and edge calls cross those boundaries; PMP configuration and platform-supplied roots of trust underpin isolation and attestation.
- **C2:** The SDK's host-side enclave object, edge libraries, runtime services, and attestation support allow different enclave applications and runtime choices. Eyrie is a concrete runtime, not the definition of every possible Keystone enclave.

**Entry point:** [SDK roles, loading, and edge calls](https://github.com/keystone-enclave/keystone/blob/master/docs/source/Keystone-Applications/SDK-Basics.rst). The root of trust is a platform obligation; a hardware demonstration without it does not establish equivalent production security.

### 16. [Penglai-Enclave/Penglai-Enclave-sPMP](https://github.com/Penglai-Enclave/Penglai-Enclave-sPMP)

**Languages / role:** C and assembly; an experimental RISC-V enclave implementation integrating a monitor, driver, and SDK. The verified default branch is **`opensbi`**; older BBL material and other Penglai variants should not be conflated with this implementation.

- **C1:** The monitor maintains per-hart enclave state and spinlock-protected metadata, including allocation, invalid/fresh lifecycle states, teardown, and protection transitions. Release notes explicitly discuss concurrency fixes and memory reclamation, making failure handling a concrete study topic.
- **C2:** The monitor/driver/application split and OpenSBI integrations provide reusable enclave execution services rather than a single research application. Release notes document OCALL, shared-memory, and attestation capabilities.

**Entry points:** [Enclave state and lifecycle implementation](https://github.com/Penglai-Enclave/Penglai-Enclave-sPMP/blob/opensbi/opensbi-1.2/lib/sbi/sm/enclave.c); [releases and compatibility notes](https://github.com/Penglai-Enclave/Penglai-Enclave-sPMP/releases). No capabilities specific to other Penglai monitor variants are attributed here.

### 17. [openeuler-mirror/secGear](https://github.com/openeuler-mirror/secGear)

**Languages / role:** C, Rust, and OCaml tooling; a common enclave SDK spanning backends including SGX, Kunpeng TrustZone, and Penglai. **Official openEuler GitHub mirror**: the project's [quick-start information identifies its GitHub mirror organization](https://www.openeuler.org/en/wiki/about/quick-start/); Gitee is the primary development location.

- **C2:** Host/enclave APIs and EDL-generated boundary code allow applications to share structure across TEE backends. The development guide also exposes backend-specific limits, preventing the common interface from hiding every capability difference.
- **C3:** Its switchless path uses shared-memory queues and worker threads, with busy/wakeup modes, affinity options, retries, and fallback. The guide explains CPU contention and worker-pool configuration, so the optimization is understandable as a scheduling and resource tradeoff.

**Entry point:** [Application development and feature guide, in Chinese](https://github.com/openeuler-mirror/secGear/blob/master/docs/HelloWorld%E5%BC%80%E5%8F%91%E6%B5%81%E7%A8%8B%E5%92%8C%E7%89%B9%E6%80%A7%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97.md). Mirror freshness was not independently established.

## Portable execution and confidential application frameworks

### 18. [enarx/enarx](https://github.com/enarx/enarx)

**Languages / role:** Rust; a WebAssembly-oriented confidential execution system with hardware-specific backends, including SGX and SEV-family support. Its core abstraction is a protected execution instance called a Keep.

- **C1:** The SGX thread implementation tracks enclave entry/resume state and nested exception depth, manages thread-control resources, preserves calling-convention state, and dispatches Sallyport requests. Explicit overflow and invalid-exit handling make this a substantial state-machine study.
- **C2:** `Backend`, `Keep`, and `Thread` interfaces separate support probing, loading, measurement, spawning, and execution. Hardware shims and the WebAssembly execution layer can consequently evolve behind common lifecycle concepts.

**Entry points:** [Backend and execution interfaces](https://github.com/enarx/enarx/blob/main/src/backend/mod.rs); [SGX thread implementation](https://github.com/enarx/enarx/blob/main/src/backend/sgx/thread.rs). Some website documents describe design plans; the claims here rely on inspected implementation rather than assuming every plan shipped.

### 19. [veracruz-project/veracruz](https://github.com/veracruz-project/veracruz)

**Languages / role:** Primarily Rust; a policy-driven framework for confidential computations involving multiple principals, with WebAssembly execution and supporting trusted-runtime services. **Archived on February 18, 2026**, with the project transitioning to emeritus status.

- **C1:** TLS terminates inside the trusted runtime while an untrusted server routes communications. Global policy, program ABI validation, and controlled native-module invocation make data authorization and execution boundaries explicit rather than trusting the transport host.
- **C2:** Separate session management, execution engine, transport protocol, runtime manager, and platform-service components support different isolates and execution strategies. A freestanding execution engine permits application testing outside an enclave; a support library abstracts the program ABI.

**Entry point:** [Component map and native-module execution rules](https://github.com/veracruz-project/veracruz/blob/main/docs/COMPONENTS.md). Its native execution paths have different portability and sandboxing properties from WebAssembly; they should not be treated as one uniform isolation mechanism.

### 20. [project-oak/oak](https://github.com/project-oak/oak)

**Languages / role:** Rust and C++; a monorepo for confidential computing, including Oak Restricted Kernel, container-based execution, attestation, and secure sessions. Counted once. The relevant runtime implementations span small restricted guests and Linux-based container environments.

- **C1:** The Restricted Kernel's boot path brings together page tables, allocation, platform state, and private versus guest-host shared memory. Those distinctions are security-critical in an encrypted VM: placing a buffer in the wrong memory domain changes who can observe it.
- **C2:** Platform and boot interfaces, attestation components, and session abstractions support different confidential applications. The repository's architecture connects measured execution and key authentication to encrypted client communication rather than presenting VM isolation alone as an application protocol.

**Entry point:** [Restricted Kernel initialization and memory structure](https://github.com/project-oak/oak/blob/main/oak_restricted_kernel/src/lib.rs). The repository root supplies the broader relationship between restricted-kernel and container runtimes; neither subsystem is counted as a separate repository.

### 21. [microsoft/CCF](https://github.com/microsoft/CCF)

**Languages / role:** Primarily C++, with JavaScript/TypeScript application interfaces and supporting components; a framework for confidential, auditable distributed services. This entry concerns an application framework built on TEEs, not a hardware monitor.

- **C1:** CCF's Raft-derived consensus commits at signed transaction boundaries. The architecture explains unsigned-tail handling, transaction identity versus final commitment, membership changes, and process-bound node identities. These create correctness obligations beyond ordinary encrypted request handling.
- **C2:** Replicated key/value state, application endpoints, encrypted ledger persistence, and programmable consortium governance provide reusable service-building abstractions. The inspected overview describes AMD SEV-SNP-backed nodes and distinguishes public from private ledger data.

**Entry points:** [Framework and trust model](https://ccf.dev/main/overview/what_is_ccf.html); [consensus architecture](https://ccf.dev/main/architecture/consensus/index.html). This is a strong selection for engineers interested in the intersection of enclave trust, replication, and recovery semantics.

### 22. [wasm-micro-runtime/wasm-micro-runtime](https://github.com/wasm-micro-runtime/wasm-micro-runtime)

**Languages / role:** C and C++; a portable WebAssembly runtime. **The relevant subsystem is its Linux SGX port**, not every target supported by the wider runtime. The current canonical repository is under `wasm-micro-runtime`, following the former Bytecode Alliance location.

- **C1:** The SGX guide documents adaptation of WASI file operations onto enclave protected-file facilities. Seek, positioned I/O, and file-extension behavior require emulation, while shrinking files is unsupported. These semantic gaps matter when applications assume ordinary filesystem behavior.
- **C2:** Trusted/untrusted libraries, EDL integration, interpreter and AOT execution, and explicit module lifecycle APIs let many Wasm applications share the enclave runtime.
- **C3:** Minimal builds and optional facilities control the OCALL and runtime footprint; enclave memory and thread configuration remain visible to the integrator.

**Entry point:** [Linux SGX integration, APIs, and protected filesystem](https://github.com/wasm-micro-runtime/wasm-micro-runtime/blob/main/doc/linux_sgx.md). The upstreamed SGX work is counted here rather than listing a related fork as another independent runtime.

## Container integration and enclave lifecycle management

### 23. [inclavare-containers/inclavare-containers](https://github.com/inclavare-containers/inclavare-containers)

**Languages / role:** Go and C; enclave container runtime infrastructure. Relevant components include the `rune` OCI runtime, `shim-rune`, and the enclave runtime PAL. The monorepo is counted once, independently of the underlying enclave runtimes it can host.

- **C1:** PAL v2 distinguishes initialization, process creation, actual execution, signaling, and destruction. PID and standard-stream parameters, explicit error returns, and version negotiation expose lifecycle invariants that are easy to blur when adapting a container API to an enclave.
- **C2:** The PAL decouples OCI/container orchestration from enclave runtime implementations. Its documented fallback to v1 when the version symbol is absent illustrates how the interface accommodates backends with different ABI generations.

**Entry points:** [PAL specification](https://github.com/inclavare-containers/inclavare-containers/blob/master/rune/libenclave/internal/runtime/pal/spec.md); [PAL v2 process lifecycle](https://github.com/inclavare-containers/inclavare-containers/blob/master/rune/libenclave/internal/runtime/pal/spec_v2.md). Protocol structure, rather than repository popularity, motivates this selection.

### 24. [aws/aws-nitro-enclaves-cli](https://github.com/aws/aws-nitro-enclaves-cli)

**Languages / role:** Rust and C; host-side Nitro Enclaves tooling and execution management. Despite its CLI name, the repository includes substantial per-enclave processes, image loading, resource allocation, and driver interaction. It does **not** contain the Nitro hypervisor implementation.

- **C1:** The enclave process coordinates socket events, signals, termination work, and cleanup. The resource manager adds checked image-offset arithmetic, memory/CPU validation, locking, and differentiated cleanup behavior after failed launches.
- **C2:** `EnclaveManager` and resource handles separate image/resource setup, start, inspection, termination, and driver operations. This is reusable infrastructure for arbitrary enclave images, not a thin wrapper around one confidential application.

**Entry points:** [Enclave process and event handling](https://github.com/aws/aws-nitro-enclaves-cli/blob/main/src/enclave_proc/mod.rs); [resource manager and lifecycle](https://github.com/aws/aws-nitro-enclaves-cli/blob/main/src/enclave_proc/resource_manager.rs). Its inclusion is specifically for host runtime engineering; it does not imply that all security enforcement is inspectable in this repository.

## Coverage, search method, and limitations

Live discovery used more than six meaningfully distinct search formulations. Search angles included SGX library OS architecture and dynamic memory; enclave SDKs and boundary generators; Rust trusted runtimes and typed OP-TEE APIs; Go and JVM enclave frameworks; Arm secure-world operating systems and microcontroller partition managers; RISC-V monitors and PMP; enclave WebAssembly execution; confidential VM kernels and distributed services; and OCI/Nitro lifecycle management. Follow-up searches checked official mirrors, canonical repository moves, archives, and less prominent projects such as GoTEE, Penglai, and secGear. Later searches mostly returned already-covered families, wrappers, or adjacent attestation tools.

Every selected canonical GitHub repository was opened, and each entry has at least one additional opened primary document or source file with architectural or implementation substance. Search snippets were discovery aids only. Evidence was read from official repositories and project documentation; candidate code was not cloned, installed, or executed. The classification under C1–C4 is an engineering judgment grounded in those sources, not a formal audit or a measured performance comparison. No unsupported numerical speedups are used.

The selection deliberately includes SDKs, monitors, language environments, and application frameworks because they expose different parts of trusted execution. Several entries share dependencies, but are separate substantive implementations: the Rust and Go SDKs add runtime and language contracts; OP-TEE and its Rust SDK occupy different layers; OCI integrations are distinct from their hosted LibOSes. Monorepos, renamed repositories, and upstreamed forks are counted only once. The two official mirrors are identified explicitly.

Important exclusions include generic sandbox runtimes without a demonstrated TEE subsystem, attestation-only libraries, sample collections, and public SCONE materials for which this search did not establish a substantive public GitHub core-runtime implementation. Android Trusty was not retained because a suitable official substantive GitHub mirror was not verified. The current [apache/teaclave repository](https://github.com/apache/teaclave) is a landing point for SDK work and describes the former FaaS implementation as deprecated; the two inspected SDK repositories are included instead of counting that landing page or incompletely verified legacy tree. These are search and scope limitations, not judgments that excluded systems lack engineering merit.

Maintenance evidence is reported conservatively: archival or discontinuation notices are explicit, experimental and emulation limitations are preserved, and no recent push is used to establish C4. Mutable branch and documentation links reflect the research date; support matrices and source organization can change. For a new deployment, current advisories, hardware support, and project support status require a separate assessment.
