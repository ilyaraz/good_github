# Cryptographic primitive libraries

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing reusable cryptographic building blocks: symmetric encryption, authentication, hashes, elliptic-curve and pairing arithmetic, post-quantum mechanisms, and verified arithmetic generation. It includes general toolkits and focused implementations, from compact portable C to SIMD kernels and proof-oriented code. For broader toolkits, the relevant primitive subsystem is identified. This is an engineering study guide, not a security certification or an assertion that every algorithm, backend, or release is equally suitable for deployment.

Criteria used:

- **C1 — Difficult correctness:** numerical or representation invariants, adversarial inputs, side channels, concurrency, or failure-state behavior.
- **C2 — Reusable abstractions:** substantial interfaces or components supporting multiple algorithms, constructions, or applications.
- **C3 — Performance with structure:** concrete resource or throughput constraints addressed through understandable implementation boundaries.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility work, testing, migration guidance, or complexity management.

Criterion assignments are judgments grounded in the linked primary material. A documented contract demonstrates a correctness obligation; it does not by itself prove that every implementation satisfies it. Repository identity and an additional primary source were opened for every selection. Source links generally follow development branches and can change.

## Portable libraries and general-purpose toolkits

### 1. [jedisct1/libsodium](https://github.com/jedisct1/libsodium)

**Language/role:** C; portable cryptographic library with substantial independent evolution from NaCl. Study how low-level primitives become APIs that manage sequencing, authentication, and key state for applications.

- **C1:** The encrypted-stream design binds message order to evolving state, distinguishes final-message and rekey tags, and rekeys before the underlying counter wraps. Its decryption contract releases plaintext only after authentication succeeds. The documented algorithm makes the nonce and state transitions inspectable. [Secretstream design and API](https://doc.libsodium.org/secret-key_cryptography/secretstream).
- **C2:** The same push/pull abstraction supports file chunks and network messages of varying sizes, associated data, automatic nonce handling, and explicit key rotation. This is a useful example of packaging a construction without exposing every bookkeeping obligation to callers. [Secretstream design and API](https://doc.libsodium.org/secret-key_cryptography/secretstream).

The repository distinguishes feature-bearing point releases from compatible stable updates. Its [ChangeLog](https://raw.githubusercontent.com/jedisct1/libsodium/master/ChangeLog) is a second entry point for portability fixes, additional test vectors, and backend replacement.

### 2. [LoupVaillant/Monocypher](https://github.com/LoupVaillant/Monocypher)

**Language/role:** C; compact, directly embeddable implementations of authenticated encryption, hashing, password hashing, key exchange, and signatures. Study a small implementation surface with unusually explicit caller obligations.

- **C1:** The AEAD interface specifies nonce uniqueness, permitted buffer aliasing, authentication-before-decryption, and chunk-size limits. Its incremental ratchet detects reordering but leaves truncation detection to the application—a valuable boundary to study rather than overlook. [AEAD manual](https://monocypher.org/manual/aead).
- **C3:** The repository explains the BLAKE2 loop-unrolling option as a code-size versus execution-speed decision that can reverse on embedded processors. The core can be incorporated as a C source/header pair, with optional Ed25519 functionality separated. These choices keep performance tuning understandable within a small codebase.

The root page also documents sanitizer, Valgrind, coverage, and formal-analysis workflows. Its development tree is explicitly distinguished from published releases.

### 3. [libtom/libtomcrypt](https://github.com/libtom/libtomcrypt)

**Language/role:** C; modular toolkit for ciphers, hashes, modes, random generators, and public-key cryptography. Study descriptor-driven polymorphism without a language-level object system.

- **C2:** Cipher, hash, PRNG, and multiprecision-arithmetic operations pass through descriptor tables containing function pointers. Algorithm registration and interchangeable mathematics providers let higher-level constructions share interfaces. [Developer manual, modularity and descriptor sections](https://raw.githubusercontent.com/libtom/libtomcrypt/develop/doc/crypt.tex).
- **C1:** RSA APIs distinguish operation execution from the validity of decoded padding or signatures through a separate status output. The manual also explains OAEP/PSS parameters and encoding constraints. This makes it a useful study of error contracts where a successful function call must not be mistaken for successful authentication. [RSA sections of the manual](https://raw.githubusercontent.com/libtom/libtomcrypt/develop/doc/crypt.tex).

The verified repository uses the `develop` branch. The wide algorithm catalog includes compatibility-oriented choices; inclusion here does not recommend every listed primitive.

### 4. [randombit/botan](https://github.com/randombit/botan)

**Language/role:** C++; broad toolkit. The relevant subsystem is its primitive and cipher-mode API, rather than its TLS or certificate stack. Study runtime algorithm selection combined with explicit implementation capabilities.

- **C2:** `BlockCipher` exposes factory creation, key-length validation, key clearing, block processing, and creation of fresh unkeyed objects. The documented algorithm-name round trip is a concrete abstraction invariant. [Block-cipher API](https://botan.randombit.net/handbook/api_ref/block_cipher.html).
- **C3:** `provider()`, `parallelism()`, and `parallel_bytes()` expose backend identity and useful batching information without requiring callers to depend on one instruction set. The same API supports processor-specific AES implementations. [Block-cipher API](https://botan.randombit.net/handbook/api_ref/block_cipher.html).

The repository also describes fine-grained module selection and side-channel testing. The API documentation clearly distinguishes raw block ciphers from complete authenticated encryption constructions.

### 5. [weidai11/cryptopp](https://github.com/weidai11/cryptopp)

**Language/role:** C++; cryptographic class library. Study how algorithm interfaces, byte pipelines, and performance hints coexist in a large reusable API.

- **C2:** `BufferedTransformation` supports attached transformations, channels, message boundaries, copying, and consuming transfers. Cipher and stream interfaces specify block-size requirements so filters can buffer appropriately. [Core interfaces in `cryptlib.h`](https://raw.githubusercontent.com/weidai11/cryptopp/master/cryptlib.h).
- **C1:** Nonblocking transfers explicitly track partial progress and ownership of unconsumed data. Key loading is separately documented from key validation, preventing an important conceptual conflation. These contracts expose correctness problems beyond the arithmetic itself. [Core interfaces](https://raw.githubusercontent.com/weidai11/cryptopp/master/cryptlib.h).
- **C3:** `OptimalNumberOfParallelBlocks` and `AdvancedProcessBlocks` provide structured routes to batching and bit-sliced implementations, including flags controlling counters, XOR placement, and traversal direction.

This is especially useful for engineers comparing object-oriented composition with the descriptor approach in LibTomCrypt.

### 6. [microsoft/SymCrypt](https://github.com/microsoft/SymCrypt)

**Language/role:** C and assembly; core primitive library used by Microsoft products. Study the contracts needed to share low-level cryptography across user-mode and kernel-mode environments.

- **C1:** The public header prohibits arbitrary copying of internal objects and documents concurrent access through const versus mutable parameters. It specifically requires synchronization when publishing initialized state to another thread. Checked builds and fatal-error semantics make misuse handling explicit. [Public API and operational contracts](https://raw.githubusercontent.com/microsoft/SymCrypt/main/inc/symcrypt.h).
- **C2:** Caller-provided storage, reusable expanded keys, and environment-selection mechanisms support different runtime contexts while keeping algorithms behind a common C API. The header distinguishes the supported public surface from unstable low-level interfaces. [Public header](https://raw.githubusercontent.com/microsoft/SymCrypt/main/inc/symcrypt.h).

The same header records side-channel exceptions for certain implementations; it does not support a blanket constant-time claim. That qualification is part of the codebase's study value.

### 7. [intel/cryptography-primitives](https://github.com/intel/cryptography-primitives)

**Language/role:** C and assembly; Intel-oriented primitive toolkit, including the `sources/ippcp/crypto_mb` subsystem. Study batching independent cryptographic operations to work around dependency chains within individual operations.

- **C3:** The multi-buffer design explains why carry propagation limits parallelism inside RSA arithmetic, then distributes independent requests across SIMD lanes. It documents different instruction-set requirements for its kernels. [Multi-buffer architecture](https://github.com/intel/cryptography-primitives/blob/develop/sources/ippcp/crypto_mb/Readme.md).
- **C1:** Constant-execution testing is specified by function, parameter set, platform, and compiler scope. The project explicitly distinguishes the guarantees for release branches from the development branch. This is concrete evidence of managing secret-dependent behavior across optimized implementations. [Constant-time testing scope](https://github.com/intel/cryptography-primitives/blob/develop/CONST_TIME_EXECUTION_TESTING.md).

Counted once, including its multi-buffer component. The repository's `develop` branch is a development snapshot, not automatically equivalent to an official production release.

## Language-level interfaces and composition

### 8. [RustCrypto/block-ciphers](https://github.com/RustCrypto/block-ciphers)

**Language/role:** Rust; monorepo of raw block-cipher crates. The strongest study target here is **`aes`**, not an undifferentiated endorsement of every crate.

- **C2:** Implementations share the `cipher` traits, allowing modes, MACs, and AEAD constructions in the wider RustCrypto ecosystem to be generic over a block cipher. This cleanly separates primitive implementation from construction semantics.
- **C1, C3:** AES combines a portable fixsliced implementation without lookup tables or data-dependent branches with hardware backends selected through CPU detection. Its compact software option trades throughput for code size, while multi-block methods exploit instruction-level parallelism. [AES backend and API documentation](https://docs.rs/aes/latest/aes/).

The root README explicitly says that only the AES crate has the stated constant-time implementation and third-party audit, and warns about the other ciphers. The monorepo is counted once.

### 9. [dalek-cryptography/curve25519-dalek](https://github.com/dalek-cryptography/curve25519-dalek)

**Language/role:** Rust; monorepo containing Curve25519/Ristretto arithmetic, Ed25519 signatures, and X25519 key exchange. Study how a cryptographic algebraic abstraction can remove protocol-level hazards.

- **C1:** Ristretto encoding, decoding, and equality operate on quotient-group representatives; decoding accepts canonical coset encodings. Scalars have their own canonical representation, and constant-time versus variable-time multiplication interfaces are distinguished. [Ristretto module design](https://docs.rs/curve25519-dalek/latest/curve25519_dalek/ristretto/index.html).
- **C2:** `RistrettoPoint` presents a prime-order group over an underlying cofactored Edwards curve, so downstream protocols need not repeatedly implement cofactor workarounds. Scalar, compressed-point, basepoint-table, and multiscalar interfaces offer reusable building blocks. [Ristretto module design](https://docs.rs/curve25519-dalek/latest/curve25519_dalek/ristretto/index.html).

The signature and key-exchange crates are included in this single repository entry, not counted as separate projects.

### 10. [briansmith/ring](https://github.com/briansmith/ring)

**Language/role:** Rust with C and assembly; cryptographic implementation and Rust API with substantial BoringSSL/OpenSSL ancestry. Study ownership-oriented API contracts over lower-level implementations.

- **C1:** `NonceSequence::advance` must never repeat a nonce, and failure must be permanent once the sequence is exhausted. The documented design intentionally avoids `Clone` and `Copy` on the abstraction, although implementors remain responsible for satisfying the contract. [NonceSequence API](https://docs.rs/ring/latest/ring/aead/trait.NonceSequence.html).
- **C2:** The trait separates nonce policy from AEAD processing and can enforce per-key record limits. It illustrates how an extensible interface can carry a security invariant across different application policies. [NonceSequence API](https://docs.rs/ring/latest/ring/aead/trait.NonceSequence.html).

**Status qualification:** The current root README explicitly describes the project as an experiment and discourages assuming general-purpose suitability. It is retained for its independently developed API and implementation structure, not as a maintenance or deployment recommendation.

### 11. [bcgit/bc-java](https://github.com/bcgit/bc-java)

**Language/role:** Java; **official GitHub mirror** of Bouncy Castle's Java distribution. Focus on the `core` lightweight primitive API and its relationship to the JCA provider.

- **C2:** The lightweight API supplies algorithms independently of the JCA layer; provider infrastructure and protocol packages build above it. This is a substantive example of keeping primitive code reusable across several integration environments. [Official architecture and documentation guide](https://www.bouncycastle.org/documentation/documentation-java/).
- **C1:** `GCMBlockCipher` checks cipher block size, nonce presence, key initialization, and reuse of the previous nonce/key combination within the instance. It maintains separate authentication state and a remaining-block counter. [GCM implementation](https://raw.githubusercontent.com/bcgit/bc-java/main/core/src/main/java/org/bouncycastle/crypto/modes/GCMBlockCipher.java).

The local reuse check is not a global nonce registry. Study the code as an example of which invariants a reusable mode can enforce itself and which remain application responsibilities.

### 12. [paulmillr/noble-curves](https://github.com/paulmillr/noble-curves)

**Language/role:** TypeScript/JavaScript; elliptic-curve arithmetic and signature constructions. Study reusable mathematics under a runtime whose type system and timing behavior differ substantially from native code.

- **C2:** The Weierstrass implementation constructs curve-specific point classes from shared machinery. Its design commentary explains why structural TypeScript types are insufficient for preventing accidental interaction between points from different curves. [Weierstrass implementation and type rationale](https://raw.githubusercontent.com/paulmillr/noble-curves/main/src/abstract/weierstrass.ts).
- **C1:** Runtime class identity enforces part of that separation. The repository additionally documents property-based, cross-library, Wycheproof, and fuzz testing, alongside detailed limits of its timing mitigations.

The root security section explicitly qualifies algorithmic constant-time intentions because of JIT compilation and garbage collection, and identifies limitations for some secret-scalar operations. Retain those qualifications when studying or adopting the API; audit labels are not universal guarantees.

### 13. [cloudflare/circl](https://github.com/cloudflare/circl)

**Language/role:** Go; classical and post-quantum cryptographic primitives, with supporting constructions. Focus on primitive implementations and shared KEM interfaces.

- **C2:** A KEM `Scheme` covers generation, encapsulation, decapsulation, serialization, sizes, and deterministic derivation. Keys identify their scheme, while `AuthScheme` extends the interface for authenticated encapsulation. [KEM API](https://pkg.go.dev/github.com/cloudflare/circl/kem).
- **C1:** The API distinguishes type mismatches, malformed encodings, wrong ciphertext lengths, and invalid keys; deterministic operations impose explicit seed-length contracts. This provides a concrete study of making heterogeneous mechanisms obey a coherent failure model. [KEM API](https://pkg.go.dev/github.com/cloudflare/circl/kem).

The repository identifies some content as experimental and lists packages with known timing caveats. Consequently, neither API stability nor constant-time behavior should be inferred uniformly across this collection.

### 14. [mirage/mirage-crypto](https://github.com/mirage/mirage-crypto)

**Language/role:** OCaml with C primitives; symmetric cryptography, public-key operations, elliptic curves, and randomness. It is a substantively evolved fork of `ocaml-nocrypto`, not a duplicate wrapper.

- **C2:** Algorithms share OCaml module signatures; the API emphasizes input-to-output composition, with incremental Poly1305 contexts and separate packages for public-key cryptography and randomness. [Public interface](https://raw.githubusercontent.com/mirage/mirage-crypto/main/src/mirage_crypto.mli).
- **C1, C4:** The dated 2020–2026 changelog records package separation, platform CI, an AEAD interface transition, runtime CPU detection, OpenSSL key interoperability, and later fixes for block-count bounds and randomness after `fork`. It also documents the 2024 buffer/API migration and removal of hashing into a separate library. [Change history](https://raw.githubusercontent.com/mirage/mirage-crypto/main/CHANGES.md).

Study both the functional surface and the release history: the latter shows how runtime integration and security contracts evolve together.

## Verification-oriented primitive implementations

### 15. [hacl-star/hacl-star](https://github.com/hacl-star/hacl-star)

**Language/role:** F*/Low*, generated C, and verified assembly; research home of HACL*, ValeCrypt, and EverCrypt. These subsystems count once.

- **C1:** The project connects primitive implementations to proofs of memory safety, functional correctness, and secret independence. This supplies a study path from mathematical specifications through executable implementation, with explicitly scoped timing properties.
- **C2, C3:** HACL* exposes individual primitive APIs, Vale supplies optimized assembly cores, and EverCrypt combines implementations behind algorithm-family interfaces and runtime selection. Algorithm agility and machine-dependent dispatch are separate architectural dimensions. [HACL*/Vale/EverCrypt architecture](https://hacl-star.github.io/HaclValeEverCrypt.html).

The repository explicitly directs production integrators to HACL packages. The architecture manual is useful conceptual evidence, but some compiler naming reflects an earlier version of the project; the root README describes the current KaRaMeL extraction path.

### 16. [mit-plv/fiat-crypto](https://github.com/mit-plv/fiat-crypto)

**Language/role:** Coq/Rocq, extracted generator tooling, and generated arithmetic code. Included for its reusable cryptographic arithmetic implementations and their synthesis machinery, rather than as a complete encryption API.

- **C1:** Correct-by-construction arithmetic addresses modular reduction, carries, word bounds, and representation conversions. The project's BoringSSL integration notes distinguish scalar, group, and field operations, showing why verified field routines do not automatically establish a verified end-to-end signature implementation. [Integration analysis](https://raw.githubusercontent.com/mit-plv/fiat-crypto/master/boringssl_notes.md).
- **C2, C3:** The generator accepts modulus and machine-word parameters and supports strategies including unsaturated Solinas and word-by-word Montgomery arithmetic. The documented examples generate different 32-bit and 64-bit implementations from shared machinery.

The root usage guide is the generator entry point. The linked integration analysis is explicitly historical, dated June 2020; it is cited for decomposition and proof boundaries, not current BoringSSL coverage.

### 17. [formosa-crypto/libjade](https://github.com/formosa-crypto/libjade)

**Language/role:** Jasmin and assembly with EasyCrypt proofs; reusable classical and post-quantum primitive implementations. Study the boundary between proof assumptions and C callers.

- **C1:** The KEM documentation states allocation sizes, non-overlap, randomness, and concurrent-access obligations. The project separately describes compiler-preserved properties and interactive correctness/security proofs, explicitly identifying the latter as incomplete for many implementations. [KEM API contracts](https://github.com/formosa-crypto/libjade/blob/main/doc/api.md).
- **C2:** Algorithm, architecture, and implementation are explicit in exported names. Individual release components provide a header, assembly, Jasmin source, example, and build description for incorporation into higher-level libraries. This is a reusable primitive collection rather than one opinionated provider API.

The documented release platform is AMD64/System V, and development branches are not promised the same assurance as releases. The [proof tree](https://github.com/formosa-crypto/libjade/tree/main/proof) gives a second entry point, but its existence must not be mistaken for complete proof coverage.

## Elliptic-curve and pairing arithmetic

### 18. [bitcoin-core/secp256k1](https://github.com/bitcoin-core/secp256k1)

**Language/role:** C with optional architecture-specific code; focused secp256k1 operations, signatures, and related modules. Study how internal arithmetic invariants enable optimizations while keeping the public API narrow.

- **C1:** Field elements track implicit magnitude and normalization properties that constrain legal operations. `VERIFY` builds materialize these properties and check consistency. Constant-time and variable-time normalization operations have distinct contracts. [Field interface](https://raw.githubusercontent.com/bitcoin-core/secp256k1/master/src/field.h).
- **C3:** The same field interface supports different limb layouts, with optimized operations selected underneath it. Non-verification builds remove checking metadata and map operations directly to backend implementations. The root implementation notes explain the complementary field/scalar layers and avoidance of runtime heap allocation.

The repository warns that its strongest testing and interface assumptions center on Bitcoin use cases. It remains a strong arithmetic study target without implying equal validation for every application.

### 19. [supranational/blst](https://github.com/supranational/blst)

**Language/role:** C and assembly with language bindings; BLS12-381 arithmetic and signatures. Study a runtime-neutral primitive core and aggregation interface.

- **C1:** The documented pairing workflow distinguishes group checks for public keys from signature checks, and makes domain separation explicit. Its lower-level API offers both checked aggregation and separate group-validation operations. [API declarations](https://raw.githubusercontent.com/supranational/blst/master/bindings/blst.h).
- **C2, C3:** Miller loops, final exponentiation, serialization, and opaque pairing contexts are exposed separately. Per-thread aggregation contexts can be merged, letting language bindings own scheduling and memory management while sharing the arithmetic core. The root tutorial explains this workflow and its validation responsibilities.

The project describes formal verification as ongoing; this report does not elevate that to a completed proof of the entire library. Its portable fallback and optimized assembly serve different platform requirements within one repository.

### 20. [relic-toolkit/relic](https://github.com/relic-toolkit/relic)

**Language/role:** C; research-oriented arithmetic and cryptographic meta-toolkit. Study a configurable family of implementations rather than one fixed parameter/backend combination.

- **C2:** Configuration separates multiprecision integers, prime and binary fields, extension fields, curve families, pairings, and higher constructions. It also selects memory policy and arithmetic backends. [Configuration interface](https://raw.githubusercontent.com/relic-toolkit/relic/main/include/relic_conf.h.in).
- **C3:** Choices include Karatsuba depth, reduction and inversion algorithms, coordinate systems, precomputation tables, scalar-multiplication windows, and lazy extension-field reduction. Those named choices make algorithmic tradeoffs directly inspectable. [Configuration interface](https://raw.githubusercontent.com/relic-toolkit/relic/main/include/relic_conf.h.in).

**Research qualification:** The root README calls the software alpha quality and warns that configurations can be insecure, API compatibility may change, and side-channel protections are not universal. Its value here is experimentation and architectural study, supported by its documented test/benchmark focus.

### 21. [herumi/mcl](https://github.com/herumi/mcl)

**Language/role:** C++ with C interfaces and low-level optimized code; finite-field and pairing-based cryptography. Study the separation of arithmetic types, serialization, and subgroup validation.

- **C1:** The API distinguishes field, G1, G2, and target-group values. G1/G2 deserialization checks subgroup order, while target-group deserialization requires a separate validity check when needed. String conversion and optional order-check controls make these differences explicit. [Detailed API](https://raw.githubusercontent.com/herumi/mcl/master/api.md).
- **C2:** The same arithmetic and pairing machinery is available through C and C++ interfaces, with typed operations and reusable representations for several supported curves. [Detailed API](https://raw.githubusercontent.com/herumi/mcl/master/api.md).

The root README also records breaking library-layout and CPU-requirement changes in major versions. Do not infer universal binary compatibility or one fixed hardware baseline from its portability goals.

### 22. [mratsim/constantine](https://github.com/mratsim/constantine)

**Language/role:** Nim with assembly and C/Rust/Go interfaces; arithmetic for elliptic curves, pairings, commitments, and proof-system workloads. Study cryptographic computation together with the scheduler that feeds it.

- **C1:** The performance documentation describes stress testing for contention, nested parallelism, conditional work, and extreme load imbalance. Its threadpool is a separately understandable concurrency component rather than an unexplained parallel loop around arithmetic. [Performance and parallelism design](https://raw.githubusercontent.com/mratsim/constantine/master/README-PERFORMANCE.md).
- **C3:** Adaptive lazy loop splitting, shared-memory work stealing, and eventcount/futex backoff address scheduling costs. Benchmarks are divided by field arithmetic, scalar multiplication, pairings, and multiscalar multiplication, helping distinguish arithmetic bottlenecks from parallel overhead. [Performance design](https://raw.githubusercontent.com/mratsim/constantine/master/README-PERFORMANCE.md).

The repository distinguishes constant-time operations from explicitly variable-time ones. No numerical speed ranking is inferred from its benchmark illustrations.

## Post-quantum integration and hash/permutation libraries

### 23. [open-quantum-safe/liboqs](https://github.com/open-quantum-safe/liboqs)

**Language/role:** C and optimized implementation code; post-quantum KEM/signature library with substantial upstream integration, testing, and dispatch infrastructure. Study unifying independently developed algorithms without hiding their differences.

- **C2:** `OQS_KEM` stores algorithm identity/version, security metadata, lengths, and operation pointers. Its API distinguishes enumeration from whether an algorithm was enabled at build time, and specifies caller-owned buffer sizes. [KEM interface](https://raw.githubusercontent.com/open-quantum-safe/liboqs/main/src/kem/kem.h).
- **C3:** Distribution builds perform runtime CPU dispatch; single-machine builds can select a specific microarchitecture. Algorithm subsets and alternative providers make code size and performance explicit configuration decisions. [Build/dispatch architecture](https://github.com/open-quantum-safe/liboqs/blob/main/CONFIGURE.md).

This is more than a generated binding, but implementations are often imported from other projects. The root table distinguishes standardized and experimental families and upstream maintenance tiers; inclusion does not imply uniform maturity across them.

### 24. [XKCP/XKCP](https://github.com/XKCP/XKCP)

**Language/role:** C and assembly; Keccak/Xoodoo permutations and constructions including SHA-3, SHAKE, and related functions. Study an especially clear separation between portable constructions and optimized state transformations.

- **C2, C3:** The SnP interface hides a permutation's state representation behind operations; PlSnP extends the approach to parallel states. Portable high-level constructions sit above architecture-specific permutation implementations, including SIMD variants. The root architecture discussion explains the boundary and source organization.
- **C1:** The hash interface records rate/capacity constraints, domain-separation suffixes, bit-level input conventions, and fixed-output versus extendable-output behavior. [FIPS 202 hash interface](https://raw.githubusercontent.com/XKCP/XKCP/master/lib/high/Keccak/FIPS202/KeccakHash.h).

This repository is counted once, including its compact standalone implementations and `libXKCP`. Experimental constructions are identified separately in the project overview; the presence of standardized SHA-3 does not standardize every component.

### 25. [BLAKE3-team/BLAKE3](https://github.com/BLAKE3-team/BLAKE3)

**Language/role:** Rust, C, and assembly; official BLAKE3 implementations. Study how one hash construction supports both a small explanatory implementation and several optimized execution strategies.

- **C1:** The reference implementation explicitly separates chunk state, parent outputs, root output, and mode flags. Its chaining-value stack merges completed subtrees as chunks arrive, making incremental tree-shape invariants visible. [Reference implementation](https://raw.githubusercontent.com/BLAKE3-team/BLAKE3/master/reference_impl/reference_impl.rs).
- **C3:** The optimized implementations add SIMD backends, CPU detection, and optional multithreading around the same tree construction. Keeping the reference implementation alongside them provides a readable comparison point; root documentation also identifies test vectors covering modes, varied lengths, and extended output.

Hashing, keyed hashing, and key derivation share the incremental interface with distinct domain flags. The library itself should not be confused with a complete verified-streaming protocol, which the README discusses through the separate Bao project.

## Coverage, search process, and limitations

Twelve meaningfully different live discovery queries covered portable C and NaCl-style APIs; Rust/no-std primitives; HACL*/Fiat formal verification; C++ and operating-system toolkits; Java and JavaScript libraries; Go, OCaml, and Nim implementations; post-quantum collections; pairing libraries; compact embedded cryptography; Keccak/BLAKE3 implementations; Intel/embedded architecture; and functional-language constant-time work. Follow-up reads used repository pages, official manuals, generated API documentation, source files, and changelogs. Later searches mostly repeated established candidates or found adjacent verification tools and wrappers; the Intel multi-buffer design supplied one additional distinct architecture worth retaining.

Selection deliberately favors primitive implementation structure over TLS protocol engines, certificate processing, cryptocurrency applications, or complete proof systems. OpenSSL-family TLS stacks, Mbed TLS, and wolfSSL were not expanded into separate entries; this is a scope choice, not a judgment against their primitive implementations. Thin bindings, tutorial code, awesome lists, and duplicated forks were excluded. PQClean appeared in discovery, but its collection/integration role overlaps the selected post-quantum material and was not independently expanded here. Additional noble and RustCrypto repositories were likewise not enumerated solely to increase the count. BearSSL's official material appeared in search, but an official substantive GitHub mirror was not established, so no guessed mirror is listed.

Bouncy Castle is explicitly labeled as an official mirror. NaCl-derived libsodium, BoringSSL-derived ring, and nocrypto-derived mirage-crypto are retained because the inspected material shows substantial independent implementation, API, or release evolution. No retained repository page displayed an archive designation in the inspected view; this is not a claim that every repository has an active maintenance commitment. Research-oriented status and incomplete proof coverage are identified where the primary sources state them. C4 is assigned only where dated evolution and complexity-management evidence were read, rather than inferred from age or recent activity.

The report is selective rather than exhaustive, with stronger coverage of native systems libraries and elliptic-curve arithmetic than of every language ecosystem. Web retrieval sometimes failed for individual GitHub/raw URLs; successful alternate pages were read before retaining the corresponding evidence. No candidate code was executed, cloned, installed, or benchmarked. No independent security audit or reproduction of formal proofs was performed.
