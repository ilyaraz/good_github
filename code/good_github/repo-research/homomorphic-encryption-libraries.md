# Homomorphic encryption libraries

Research date: **2026-10-09**.

This selection covers 24 GitHub repositories implementing fully, leveled, or partially homomorphic encryption, plus a substantive encrypted-tensor layer. It spans packed polynomial arithmetic, Boolean and integer bootstrapping, GPU implementations, and additive encryption. Historical and archived implementations are included where their engineering remains instructive and are labeled explicitly. This is a source-based study guide, not a security audit or a claim that every component is exemplary; the criterion assignments are engineering judgments grounded in the linked material.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, adversarial inputs, or failure modes.
- **C2 — Reusable abstractions:** substantial interfaces and layers supporting multiple operations or applications.
- **C3 — Performance with structure:** concrete resource or throughput constraints addressed through understandable architecture.
- **C4 — Sustained evolution:** years of changes accompanied by evidence of compatibility handling, testing, or complexity management.

## Packed arithmetic and general foundations

### [microsoft/SEAL](https://github.com/microsoft/SEAL)

**Language/role:** C++ core with .NET integration; BFV, BGV, and CKKS library. A strong starting point for studying how a cryptographic evaluator makes mathematical preconditions visible in an application API.

- **C1:** Evaluation operations distinguish coefficient and NTT representations and require compatible parameter identifiers, ciphertext levels, and, where applicable, scales. These are operation-specific contracts rather than a single generic validity check.
- **C3:** Relinearization controls ciphertext growth; memory-pool handles expose allocation policy. The evaluator also documents keeping intermediate products in NTT form to avoid repeated transforms when accumulating ciphertext–plaintext products.

Study entry point: the [evaluator interface and its operation contracts](https://raw.githubusercontent.com/microsoft/SEAL/main/native/src/seal/evaluator.h). Read it alongside the repository's scheme overview to connect user-visible errors with representation and memory decisions.

### [openfheorg/openfhe-development](https://github.com/openfheorg/openfhe-development)

**Language/role:** C++; general HE framework covering packed arithmetic, Boolean-oriented schemes, multiparty operations, and scheme switching. The relevant subsystem is the PKE context and its scheme implementations; this monorepo counts once.

- **C1:** `CryptoContextImpl` binds cryptographic objects to their creating context. Plaintext construction checks level bounds and scheme-specific restrictions, including differences among BFV multiplication techniques and CKKS scaling modes. Incorrect combinations cannot be understood solely from an integer “level.”
- **C2:** A templated context coordinates keys, plaintext factories, evaluation, and serialization across schemes. It is useful for studying the tension between a common application API and genuinely different underlying algorithms.

Study entry point: [cryptocontext.h](https://raw.githubusercontent.com/openfheorg/openfhe-development/main/src/pke/include/cryptocontext.h), particularly context identity, scheme verification, and plaintext construction. The repository overview supplies the broader BFV/BGV/CKKS and BinFHE capability map.

### [homenc/HElib](https://github.com/homenc/HElib)

**Language/role:** C++; BGV and CKKS with packed arithmetic. Especially instructive for explicit mathematical bookkeeping and the evolution of a research implementation into a broader library.

- **C1:** Ciphertext parts must share a prime set. The ciphertext abstraction tracks noise bounds and scheme-dependent factors; low-level operations carry obligations to restore or update those quantities. High-level multiplication and automorphisms coordinate relinearization rather than treating it as an incidental optimization. See [Ctxt.h](https://raw.githubusercontent.com/homenc/HElib/master/include/helib/Ctxt.h).
- **C4:** The [change history](https://raw.githubusercontent.com/homenc/HElib/master/CHANGES.md) documents testing and CI work, a CKKS vulnerability mitigation, ContextBuilder and serialization API changes, and deprecations across the 2020–2023 period. This is concrete evidence of managing compatibility and correctness over time, not an inference from repository age.

Those two files are the study entry points. The historical change record is not a claim about present maintenance cadence.

### [tuneinsight/lattigo](https://github.com/tuneinsight/lattigo)

**Language/role:** Go; RNS-based HE with reusable RLWE/RGSW foundations, packed schemes, circuits, and multiparty protocols.

- **C1:** The RLWE evaluator validates metadata, degrees, NTT state, and batching compatibility, and reports absent evaluation keys. These checks expose invariants shared by higher-level schemes. See the [core evaluator](https://raw.githubusercontent.com/tuneinsight/lattigo/main/core/rlwe/evaluator.go).
- **C2:** The repository separates ring arithmetic, cryptographic primitives, schemes, and circuits. Its [changelog](https://raw.githubusercontent.com/tuneinsight/lattigo/main/CHANGELOG.md) makes the cost of maintaining these boundaries visible: circuit/package moves, BFV integration with BGV, renamed operations, and altered concurrency APIs require explicit migration guidance.

Study the evaluator and changelog together. In particular, the changelog records changes to copying and thread-safety behavior; concurrency assumptions should be checked against the exact version being studied rather than generalized from one source comment.

### [apple/swift-homomorphic-encryption](https://github.com/apple/swift-homomorphic-encryption)

**Language/role:** Swift; BFV library with private-information-retrieval applications. The relevant core is `Sources/HomomorphicEncryption`; PIR and nearest-neighbor components are not counted separately.

- **C1:** The scheme protocol differentiates coefficient and evaluation representations in ciphertext types. Conversion functions, minimum noise-budget semantics, and scheme-bound contexts make representation and decryption constraints explicit.
- **C2:** `HeScheme` uses associated scalar, key, and ciphertext-auxiliary types, with encoding and decoding requirements. This is a useful example of fitting cryptographic algebra into a language's generic and concurrency-oriented type system while permitting application layers above it.

Study entry points: the [HeScheme protocol](https://github.com/apple/swift-homomorphic-encryption/blob/main/Sources/HomomorphicEncryption/HeScheme.swift) and the [core source directory](https://github.com/apple/swift-homomorphic-encryption/tree/main/Sources/HomomorphicEncryption). The repository also explains why cross-module specialization matters to the performance of these abstractions.

### [tlepoint/fhe.rs](https://github.com/tlepoint/fhe.rs)

**Language/role:** Rust; experimental, unaudited HE implementation with a substantial BFV API. Useful for studying parameter and evaluation abstractions without assuming production stability.

- **C1:** The documented ciphertext–scalar dot product rejects mismatched parameter sets and ciphertext component counts. Modulus-switching levels and encodings are explicit types, making compatibility a central API concern.
- **C2:** Parameter builders, evaluation-key builders, multiplication strategies, and precomputed ciphertext–plaintext contexts separate application choices from reusable arithmetic machinery. Plaintext-vector traits and encodings broaden the interface beyond a single example circuit.

Study entry point: the [BFV API reference](https://docs.rs/fhe/latest/fhe/bfv/index.html), especially `ContextLevel`, `CipherPlainContext`, `Multiplicator`, and `dot_product_scalar`. This reference supplies concrete type and error semantics beyond the repository's feature summary.

### [FeanorTheElf/fheanor](https://github.com/FeanorTheElf/fheanor)

**Language/role:** Rust; alpha research toolkit for experimenting with HE schemes, rings, and bootstrapping. This is the substantive destination of the older `he-ring` project, which is not counted again.

- **C1:** RNS conversion is treated as more than algebraic base change: rounded BFV/BGV rescaling, representative-preserving lifts, and conversions retaining shared RNS factors have different semantics. The [RNS conversion module](https://docs.rs/fheanor/latest/fheanor/rns_conv/index.html) exposes those distinctions directly.
- **C2:** `RNSOperation` and alternative conversion implementations sit within a framework of interchangeable ring, gadget, and circuit machinery. It is a useful study of making research substitutions possible without rewriting an entire HE implementation.

Study entry points: the RNS module and the repository's architecture discussion. The project explicitly accepts API instability and does not make side-channel resistance a design goal; its value here is as an experimental implementation framework.

### [minshinfo/HIENAA.jl](https://github.com/minshinfo/HIENAA.jl)

**Language/role:** Julia; BFV, BGV, and CKKS research implementation, including unusually broad cyclotomic-ring choices for BFV/BGV subject to documented factorization restrictions.

- **C1:** The BFV operator maps logical levels to RNS-chain lengths, checks that ciphertext size agrees with its level, and rejects attempts to move to a higher level. Encoding distinguishes packed slots from coefficient vectors and checks dimensions.
- **C3:** Operators retain ciphertext and tensor scratch buffers, precompute per-level modulus information, and drop unnecessary moduli before further arithmetic. Allocation and arithmetic size are therefore visible architectural decisions.

Study entry point: [the BFV operator implementation](https://raw.githubusercontent.com/minshinfo/HIENAA.jl/main/src/bfv/operator.jl). The repository's examples additionally show parameter sketches, polynomial evaluation, and deriving rotation-key requirements from a plaintext matrix. Treat this as research code; the source still exposes unfinished areas and open noise-estimation work.

## Boolean, integer, and programmable bootstrapping libraries

### [zama-ai/tfhe-rs](https://github.com/zama-ai/tfhe-rs)

**Language/role:** Rust with accelerator components; TFHE-based Boolean and integer computation. The short-integer and integer layers are one repository, not separate candidates.

- **C1:** Integer server keys derive degree limits from message and carry capacity. Radix arithmetic reserves room for carries, while CRT arithmetic uses different bounds; limits on aggregating ciphertexts also account for noise. These constraints explain why ordinary integer identities need specialized encrypted implementations.
- **C2:** The integer layer reuses short-integer server keys while providing radix and CRT organizations. Compressed server-key types preserve the distinction between transport/storage representation and evaluation representation.
- **C3:** Parallel radix/CRT modules and compressed evaluation keys address computation and key-size costs through identifiable layers.

Study entry point: [integer/server_key/mod.rs](https://raw.githubusercontent.com/zama-ai/tfhe-rs/main/tfhe/src/integer/server_key/mod.rs), especially maximum-degree calculations, aggregate-size limits, and compressed-key types.

### [tfhe/tfhe](https://github.com/tfhe/tfhe)

**Language/role:** C/C++; original TFHE implementation. A historical reference for the gate-bootstrapping pipeline; the README highlights its older 1.1 release and points to newer implementations for further capabilities.

- **C1:** Bootstrapping composes torus modulus switching, blind rotation, extraction of an LWE sample, and key switching. Correctness depends on the representation and parameter relationship at each transition.
- **C3:** Bootstrapping keys are converted to the Fourier domain in advance. Blind rotation skips zero rotations and alternates accumulator buffers around external products, exposing both the mathematical loop and its allocation strategy.

Study entry point: [lwe-bootstrapping-functions-fft.cpp](https://raw.githubusercontent.com/tfhe/tfhe/master/src/libtfhe/lwe-bootstrapping-functions-fft.cpp). It is a particularly compact bridge from a TFHE algorithm description to executable control flow. Inclusion is for implementation study, not an assertion of current maintenance.

### [virtualsecureplatform/TFHEpp](https://github.com/virtualsecureplatform/TFHEpp)

**Language/role:** C++; a separately implemented, template-oriented TFHE library, described by its authors as written from scratch rather than a thin binding to the original.

- **C1:** Bootstrapping and key-switch templates enforce parameter relationships with static assertions, including dimension requirements and restrictions on block-binary variants. Torus rounding during modulus switching remains explicit in the implementation.
- **C3:** Related blind-rotation algorithms have FFT, NTT, and other transform variants. Key prefetching and avoidance of unnecessary copies are visible in the same code, enabling comparison of low-level performance choices without losing the algorithm's structure.

Study entry point: [gatebootstrapping.hpp](https://raw.githubusercontent.com/virtualsecureplatform/TFHEpp/master/include/tfhe/gatebootstrapping.hpp). Compare overloads and parameter types rather than reading only the high-level gate API; much of the project's engineering interest lies in those implementation alternatives.

### [sp301415/tfhe-go](https://github.com/sp301415/tfhe-go)

**Language/role:** Go with optimized arithmetic components; TFHE and multi-key TFHE. The repository describes ongoing API instability and unaudited status.

- **C1:** An evaluator owns mutable scratch storage and is documented as unsafe for concurrent use. `SafeCopy` creates independent working buffers while sharing the large evaluation key. This is a concrete ownership contract that a service using a worker pool must respect.
- **C3:** The evaluator retains accumulators, Fourier polynomials, lookup-table buffers, a decomposer, and polynomial-evaluation machinery. Reuse removes repeated allocation from expensive bootstrapping paths while the copy operation establishes the parallelism boundary.

Study entry point: [tfhe/evaluator.go](https://raw.githubusercontent.com/sp301415/tfhe-go/master/tfhe/evaluator.go). The generic torus interface and explicit evaluation-buffer structure make this a useful comparison with C++ template implementations and Rust ownership-based designs.

### [antoniocgj/MOSFHET](https://github.com/antoniocgj/MOSFHET)

**Language/role:** C; research-oriented TFHE implementation with alternative bootstrapping techniques. A less prominent codebase with substantive algorithmic implementation rather than a wrapper or tutorial.

- **C1:** Bootstrap routines explicitly manage torus precision offsets, decomposition, and the relationship between lookup tables and blind rotation. Ordinary, unfolded, and multivalue variants make their differing intermediate representations inspectable.
- **C3:** Unfolded bootstrapping changes the number and organization of key elements, revealing a storage/computation tradeoff. Multivalue bootstrapping separates a reusable first phase from output-specific evaluation, so shared work is represented directly in the API and implementation.

Study entry point: [src/bootstrap.c](https://raw.githubusercontent.com/antoniocgj/MOSFHET/main/src/bootstrap.c), including key creation, ordinary/unfolded blind rotation, and the two multivalue phases. Its research orientation should not be mistaken for evidence of broad production hardening.

### [lducas/FHEW](https://github.com/lducas/FHEW)

**Language/role:** C++; historical FHEW implementation. The repository explicitly says not to expect maintenance and identifies its release as an older alpha.

- **C1:** `HomGate` combines gate encoding, accumulator evaluation, membership testing, key switching, and modulus switching. It also checks for certain dependent inputs and terminates with an error requesting independent ciphertexts—a consequential API restriction for circuit construction.
- **C3:** The accumulator path keeps only the needed ciphertext component, uses gadget decomposition, and multiplies against precomputed Fourier-domain bootstrapping keys. The code exposes where the arithmetic work is concentrated.

Study entry point: [FHEW.cpp](https://github.com/lducas/FHEW/blob/master/FHEW.cpp), especially `AddToACC`, `MemberTest`, and `HomGate`. This is valuable as a compact historical implementation and comparison point, with its limitations kept visible.

## GPU implementations

### [encryptorion-lab/phantom-fhe](https://github.com/encryptorion-lab/phantom-fhe)

**Language/role:** C++/CUDA; GPU implementation of BFV, BGV, and CKKS. Although it incorporates ideas and modified code from other libraries, its CUDA execution architecture makes it a substantive separate implementation.

- **C1:** Key switching maps coefficients and RNS towers onto GPU threads, uses wide intermediate accumulation and modular reduction, and distinguishes BFV technique-specific level handling from BGV/CKKS chain semantics.
- **C3:** The key-switch path is decomposed into modulus-up conversion, inner products, and modulus-down conversion. Device buffers, asynchronous copies, and stream arguments make memory traffic and execution ordering available for inspection.

Study entry point: [eval_key_switch.cu](https://raw.githubusercontent.com/encryptorion-lab/phantom-fhe/main/src/eval_key_switch.cu). The repository labels the library as research software, limits its tested GPU configurations, and does not claim production readiness; those qualifications matter when interpreting its optimization work.

### [enCRYPTON-labs/HEonGPU](https://github.com/enCRYPTON-labs/HEonGPU)

**Language/role:** C++/CUDA; GPU HE framework. This is the canonical repository reached from the former `Alisah-Ozcan/HEonGPU` address; the two names are not separate entries. The opened overview lists BFV, CKKS, and TFHE, with BGV described as forthcoming.

- **C2:** Scheme-specific host contexts connect parameter generation, keys, encoders, ciphertexts, and operators. The BFV specialization demonstrates how an application-facing context can organize a large collection of scheme-dependent constants.
- **C3:** That context maintains host and device vectors for NTT, RNS conversion, and decryption precomputations, and exposes memory-pool configuration. These structures support the repository's broader emphasis on reducing transfers and coordinating CUDA streams.

Study entry point: the [generated BFV context source listing](https://heongpu.readthedocs.io/en/latest/full_api/program_listing_file_src_include_heongpu_host_bfv_context.cuh.html). It provides substantially more architectural evidence than an accelerator feature list alone.

### [nucypher/nufhe](https://github.com/nucypher/nufhe)

**Language/role:** Python with generated GPU computation through CUDA/OpenCL tooling; TFHE-style Boolean FHE. **Archived on 2023-11-21.**

- **C1:** The implementation guide explains when floating-point FFT arithmetic can represent the needed coefficient calculations and contrasts that reasoning with exact NTT arithmetic. Numerical precision is tied to coefficient ranges and polynomial size rather than assumed.
- **C3:** Its tangent-FFT organization uses a smaller transform plus parallel pre/postprocessing and GPU-friendly memory access. The NTT alternative exploits a specially structured modulus to replace expensive operations with cheaper reductions and shifts.

Study entry point: [implementation details](https://nufhe.readthedocs.io/en/latest/implementation_details.html). This archived project remains unusually useful for understanding why a mathematically equivalent polynomial multiplication algorithm can map very differently onto a GPU.

### [vernamlab/cuFHE](https://github.com/vernamlab/cuFHE)

**Language/role:** C++/CUDA; historical GPU library for TFHE-style gate evaluation. The README identifies its older 1.0 beta release; no current maintenance claim is made here.

- **C1:** Bootstrap initialization converts and installs device evaluation keys; cleanup and synchronization surround their lifetime. The implementation's global device state makes initialization, reuse, and teardown part of the correctness contract, in addition to torus decomposition.
- **C3:** Bootstrapping keys are cached in NTT form, key-switch work is distributed across CUDA threads, and the API exposes streams for gate execution. This permits study of device-resident key reuse and concurrent circuit scheduling.

Study entry point: [bootstrap_gpu.cu](https://raw.githubusercontent.com/vernamlab/cuFHE/master/cufhe/lib/bootstrap_gpu.cu). Read allocation and initialization routines together with kernels: the performance story depends on what remains resident between calls, not just on an isolated kernel.

### [scale-snu/cheddar-fhe](https://github.com/scale-snu/cheddar-fhe)

**Language/role:** C++/CUDA; research GPU implementation focused on CKKS evaluation. “Swift” in its description refers to speed, not the Swift programming language.

- **C1:** Modulus conversion and rescaling are explicit operations with cached conversion factors and word-parameterized arithmetic. The design is useful for examining rounded rescaling across RNS levels and the implications of narrower arithmetic.
- **C3:** `ModSwitchHandler` combines NTT and elementwise handlers, device-vector views, precomputation, and a fused modulus-down/rescale operation. These interfaces expose the implementation structure behind the project's 32-bit GPU arithmetic approach.

Study entry point: [ModSwitch.h](https://raw.githubusercontent.com/scale-snu/cheddar-fhe/main/include/core/ModSwitch.h). A material boundary is stated in the repository: its client encryption/decryption and randomness utilities are for testing and carry no security guarantees. Study it as a server-side evaluation implementation, not a complete deployment-ready cryptosystem.

## Encrypted tensor abstractions

### [OpenMined/TenSEAL](https://github.com/OpenMined/TenSEAL)

**Language/role:** C++ with Python bindings; encrypted vector/tensor operations built on SEAL. Included because the tensor algorithms and data layout form a substantive layer beyond generated bindings.

- **C1:** A logical CKKS vector may span multiple ciphertexts. The implementation records chunk lengths, trims decrypted padding, and warns that several matrix/convolution operations are unavailable once a vector requires multiple chunks. Empty inputs and slot capacity are explicit concerns.
- **C2:** Vector and tensor operations, encrypted contexts, and serialization lift low-level cryptographic primitives into reusable algebra. The layer must reconcile ordinary shape semantics with batching and slot replication rather than simply forward arithmetic calls.

Study entry point: [ckksvector.cpp](https://raw.githubusercontent.com/OpenMined/TenSEAL/main/tenseal/cpp/tensors/ckksvector.cpp), beginning with construction, chunking, and decryption. Its power implementation also provides a readable example of arranging expensive encrypted multiplications.

## Additive and partially homomorphic encryption

### [data61/python-paillier](https://github.com/data61/python-paillier)

**Language/role:** Python; Paillier arithmetic with signed and floating-point encodings. It supports ciphertext addition and multiplication by plaintext scalars, not arbitrary ciphertext multiplication.

- **C1:** `EncodedNumber` maps signed values into a modular domain with an overflow-detection region and represents nonintegers through a mantissa and exponent. Exponent alignment changes precision and range; the documentation explicitly notes cases where lowering an exponent can overflow without warning.
- **C2:** Encoding, encrypted-number operations, and key objects are separate abstractions. Alternative encoding bases and documented interoperability concerns make the API useful for multiple numeric applications rather than one aggregation demo.

Study entry point: the [PHE API and encoding documentation](https://python-paillier.readthedocs.io/en/develop/phe.html). Also note its explanation that the exposed exponent can reveal information about precision. This is an instructive example of the gap between mathematically valid modular arithmetic and application-level numeric correctness.

### [n1analytics/javallier](https://github.com/n1analytics/javallier)

**Language/role:** Java; Paillier with configurable numeric encodings. Treat it as a historical library: the opened release history ends with the 0.6.0 release in 2017, which is not evidence of present maintenance.

- **C1:** The encoding implementation checks base and precision constraints, derives signed and unsigned ranges, rejects nonfinite floating-point inputs, and factors values into significand/exponent form. The repository also documents a limitation: additions involving widely separated exponents can produce undetected overflow.
- **C2:** An `EncodingScheme` separates numeric representation from the Paillier context and encrypted values. Release notes explain that separation and subsequent arithmetic fixes, making the abstraction's evolution inspectable.

Study entry points: [StandardEncodingScheme.java](https://raw.githubusercontent.com/n1analytics/javallier/master/src/main/java/com/n1analytics/paillier/StandardEncodingScheme.java) and the [release history](https://github.com/n1analytics/javallier/releases). Compare this design with python-paillier to study similar numerical hazards in different language APIs.

### [intel/pailliercryptolib](https://github.com/intel/pailliercryptolib)

**Language/role:** C++; Intel Paillier Cryptosystem Library. **Archived on 2025-06-30**, with an explicit notice that Intel has ceased maintenance.

- **C2:** The implementation separates big integers, plaintext/ciphertext containers, keys, and modular exponentiation. Its reusable additive-encryption API is more substantial than a standalone protocol example.
- **C3:** Intel's implementation article explains batched modular exponentiation using AVX-512 IFMA, plus CRT and Damgård–Jurik–Nielsen techniques. This is concrete evidence of reorganizing expensive arithmetic around hardware and algorithmic constraints, rather than relying on an unqualified speed claim.

Study entry points: the [IPCL source subsystem](https://github.com/intel/pailliercryptolib/tree/development/ipcl) and Intel's [technical implementation article](https://www.intel.com/content/www/us/en/developer/articles/technical/homomorphic-encryption/iso-compliant-paillier-cryptosystem-library.html). The article is an older design account; its benchmark results are not treated as current cross-library comparisons.

### [facebookresearch/Cupcake](https://github.com/facebookresearch/Cupcake)

**Language/role:** Rust; additive-only Fan–Vercauteren encryption for vectors. **Archived on 2025-07-17.** Its deliberately restricted operation set distinguishes it from general FHE libraries.

- **C1:** Plaintext vectors inhabit a fixed-size modular domain, and deserialized ciphertexts require the appropriate scheme context before operations resume. The API makes those algebraic and state-restoration requirements explicit.
- **C2:** Separate traits cover key generation, public/secret-key encryption, additive homomorphism, ciphertext–plaintext addition, and serialization. Rerandomization is a further reusable operation, useful when studying how an additive encryption component fits into larger protocols.

Study entry point: the [crate API guide](https://docs.rs/Cupcake/latest/cupcake/), including the trait-based examples and context-aware deserialization. The repository endorses only one default parameter set; the generic-looking interface should not be read as validation of arbitrary parameters.

## Coverage, search method, and limitations

Discovery used separate live searches for: (1) BFV/BGV/CKKS libraries and RNS architecture; (2) TFHE, programmable bootstrapping, and Boolean/integer APIs; (3) CUDA/GPU HE and transform implementations; (4) Python, Java, and C++ Paillier; (5) Rust HE libraries and modular research frameworks; (6) Go implementations and multiparty variants; (7) Swift and Julia implementations; and (8) tensor-oriented HE libraries. Follow-up searches targeted less prominent projects, source files, release histories, and archived status. Later broad GPU and language-specific searches mostly repeated already inspected implementations or returned wrappers, applications, and exploratory examples; the selection stopped after those searches yielded little additional distinct coverage.

Every retained canonical GitHub page was opened, and at least one separate technical primary source was read for each entry. The linked entry points are those actually inspected; they include source files, generated source listings, API documentation, and an official engineering article. Repository headings serve as the source for scope and explicit repository status. Individual implementations were not installed, cloned, executed, benchmarked, or audited. Branch links and `latest` documentation can change, and search retrieval sometimes serves cached or versioned documentation; this report does not assert synchronization between every documentation page and repository head.

Pure compiler/transpiler projects, application-specific demos, arithmetic-only dependencies, tutorial/toy implementations, and generated bindings were excluded from the core selection. TenSEAL is retained for its own tensor layout and operation logic. [ToyFHE.jl](https://github.com/JuliaCrypto/ToyFHE.jl) was inspected but excluded because its own documentation presents it as a partial toy implementation with major unresolved limitations. The old `he-ring` redirect and the old HEonGPU owner path were not counted separately. No mirror is presented as an independent project, and independently implemented TFHE-family libraries are distinguished from mere forks or bindings.

Some attempted primary pages, notably HEAAN's repository and several deeper source pages for other candidates, could not be retrieved through the browser. HEAAN was therefore not retained; this is a verification limitation, not a judgment that it lacks technical merit. For retained projects, accessible technical primary sources supplied the required additional evidence. Archived and research-only entries broaden the architectural comparison but should not be interpreted as current support recommendations. C4 is assigned sparingly: old release dates, recent pushes, popularity, and archive age alone do not establish sustained engineering quality.
