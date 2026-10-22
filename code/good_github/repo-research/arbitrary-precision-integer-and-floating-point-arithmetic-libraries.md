# Arbitrary-precision integer and floating-point arithmetic libraries

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories implementing reusable arbitrary-precision integers, binary or decimal floating-point numbers, and closely related rational and ball arithmetic. Arbitrary-coefficient decimal libraries are included even when they describe their arithmetic as fixed-point; those cases are labeled. Two standard-library monorepos are included only for their arithmetic subsystems. The emphasis is on representations, arithmetic contracts, allocation strategies, rounding, and implementation boundaries that an experienced engineer can study.

Every repository page and at least one separate implementation or technical documentation source was opened. Criteria below are evidence-based selection judgments, not certifications of correctness, security, or uniform code quality. In particular, arbitrary precision does not imply correctly rounded transcendental functions, constant-time execution, or unlimited practical resource use.

**Criteria legend**

- **C1 — Difficult correctness:** representation invariants, numerical semantics, aliasing, exceptional values, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components serving multiple arithmetic and application use cases.
- **C3 — Performance with structure:** explicit algorithm, storage, or allocation choices whose architectural tradeoffs can be inspected.
- **C4 — Sustained evolution:** changes across years accompanied by compatibility work, regression fixes, tests, or complexity management.

## Native engines and C++ arithmetic systems

### 1. [libtom/libtommath](https://github.com/libtom/libtommath)

**C — portable multiple-precision integers.** A particularly approachable implementation for studying how arithmetic dispatch, build-time capabilities, and limb constraints fit together. The repository also describes differential test generation against an alternative multiple-precision implementation.

- **C1:** Multiplication has separate squaring paths, propagates errors, and normalizes the sign of zero. Its Comba path is guarded by both workspace and operand-size conditions, making carry and storage requirements visible at the dispatch boundary.
- **C3:** The same dispatcher selects ordinary, Comba, Karatsuba, Toom, and unbalanced multiplication paths according to operand shapes, thresholds, and compiled-in capabilities. This is useful material for understanding why a single asymptotically attractive algorithm is insufficient.

Both criteria can be studied directly in the compact [multiplication dispatcher, `mp_mul.c`](https://raw.githubusercontent.com/libtom/libtommath/develop/mp_mul.c).

### 2. [boostorg/multiprecision](https://github.com/boostorg/multiprecision)

**C++ — generic numeric front end with native and external arithmetic backends.** The relevant scope includes arbitrary-length `cpp_int` and the number/backend abstraction; some other supplied types deliberately have fixed or compile-time precision.

- **C1:** `cpp_int_backend` makes signedness, checked versus unchecked behavior, and precision bounds explicit. Its documentation spells out overflow and negative-bitwise-operation behavior, including the limitations of signed-magnitude representation.
- **C2:** Backend parameters separate minimum inline storage, maximum precision, allocation, and checking policy. A common numeric interface can therefore serve dynamically growing integers and deliberately bounded variants without hiding the differing contracts.
- **C3:** Inline capacity and move support expose allocation tradeoffs through the type design rather than an opaque implementation setting.

Start with the detailed [C++ integer backend guide](https://www.boost.org/doc/libs/latest/libs/multiprecision/doc/html/boost_multiprecision/tut/ints/cpp_int.html).

### 3. [bluescarni/mppp](https://github.com/bluescarni/mppp)

**C++ — integer, rational, real, and complex arithmetic over GMP-family engines.** This is a substantive storage and interoperability layer, useful for studying when a wrapper becomes an arithmetic system of its own.

- **C2:** `integer<SSize>` combines a C++ value interface with access to GMP-compatible views. The documentation specifies overlapping-argument behavior and the lifetimes associated with external views.
- **C3:** Small integers occupy inline limbs and promote transparently to dynamic storage; demotion is explicit. One- and two-limb cases have specialized operations, larger static values use low-level GMP routines, and dynamic values use the higher-level GMP representation. This creates a readable boundary between custom fast paths and delegated arithmetic.

The [integer architecture and API guide](https://bluescarni.github.io/mppp/integer.html) is the best entry point for storage transitions, aliasing, and backend interaction. Inclusion is based on those implementation choices, not merely its binding to GMP.

### 4. [libntl/ntl](https://github.com/libntl/ntl)

**C++ — number-theory library; relevant subsystems are `ZZ` integers and `RR` arbitrary-precision reals.** Study the scalar layer beneath the larger modular, polynomial, and algebraic APIs.

- **C1:** `RR` uses an integer mantissa and machine-sized exponent, with normalized nonzero mantissas and a unique zero representation. Its guide distinguishes correctly rounded basic operations from weaker guarantees for transcendental functions, documents ties-to-even, and supplies precision save/restore through `RRPush`. It also defines errors where other floating-point systems might produce infinity or NaN. See the [RR contract](https://raw.githubusercontent.com/libntl/ntl/main/doc/RR.txt).
- **C2:** `ZZ` combines managed arbitrary-length integer storage with reusable modular arithmetic, number-theoretic operations, and combined operations. This makes it valuable for tracing how a general scalar abstraction supports specialized mathematics. See the [ZZ interface and representation documentation](https://raw.githubusercontent.com/libntl/ntl/main/doc/ZZ.txt).

### 5. [flintlib/flint](https://github.com/flintlib/flint)

**C — arithmetic and computer-algebra monorepo; focus on `fmpz`, `arf`, `arb`, and `acb`.** FLINT incorporates Arb; the former separate Arb project is not counted again. Its scalar arithmetic is a useful bridge between exact integer computation and rigorous approximate computation.

- **C1:** An Arb ball represents a midpoint plus an error radius and must enclose the exact image of the input set. The documentation explains containment, special values, precision escalation, and why a result can be valid without being a tight enclosure.
- **C2:** The same scalar contract extends into vector and higher-level numerical work, with explicit construction, conversion, comparison, and error-bound operations.
- **C3:** The midpoint uses arbitrary precision while the radius uses a smaller fixed-precision magnitude representation. This is a concrete cost/accuracy division within the data model.

Read the [Arb implementation-facing manual](https://raw.githubusercontent.com/flintlib/flint/main/doc/source/arb.rst), especially its representation, accuracy, and precision-control sections.

## Rust implementations and numerical type design

### 6. [rust-num/num-bigint](https://github.com/rust-num/num-bigint)

**Rust — general-purpose `BigInt` and `BigUint`.** Useful for connecting canonical limb storage to Rust ownership and ecosystem integration.

- **C1:** Equality, ordering, and hashing rely on normalized digits. The [BigUint implementation](https://raw.githubusercontent.com/rust-num/num-bigint/main/src/biguint.rs) makes these assumptions explicit and separates arithmetic, conversion, and serialization concerns into modules.
- **C3:** Storage reuse appears in `clone_from`, while the release history records small-value storage and division/conversion improvements rather than treating allocation as incidental.
- **C4:** The [release notes](https://raw.githubusercontent.com/rust-num/num-bigint/main/RELEASES.md) document years of compiler-version compatibility work, target fixes, conversion-rounding corrections, allocation improvements, and regression backports. They also record limits on deserialization preallocation, showing how robustness concerns enter a general numeric library.

This is a strong study target for the relationship between a compact core type and the maintenance burden of many conversion and integration surfaces.

### 7. [mhogrefe/malachite](https://github.com/mhogrefe/malachite)

**Rust — natural, integer, rational, and floating-point arithmetic suite.** Especially useful for explicit ownership choices, algorithm documentation, and deliberately structured test data. The project documents API instability and an incomplete floating-point offering; treat its components individually.

- **C1:** Its comparison with FLINT explains canonical small/large representations and test generation with long runs of zero or one bits, which deliberately exercise carries and borrows. This is more informative than simply claiming randomized testing. See the [integer representation and testing comparison](https://www.malachite.rs/mapping/flint-integers/).
- **C3:** A `Natural` can hold a machine word inline or own a limb vector. Borrowed, owned, and assignment forms expose opportunities for allocation reuse. The [floating-point crate documentation](https://docs.rs/malachite-float/latest/malachite_float/) also makes time and additional-memory complexity, demos, and benchmarks part of the engineering interface.

Study the ownership and testing structure before extrapolating any project-specific benchmark result to another workload.

### 8. [cmpute/dashu](https://github.com/cmpute/dashu)

**Rust — integers, floating-point numbers, and rationals in a shared arithmetic suite.** The floating-point subsystem provides an unusually clear example of encoding numerical policy in types.

- **C1:** `FBig` parameters encode the radix and rounding mode. Operators restrict which types can be mixed, avoiding implicit base or rounding-policy changes. Context-level operations expose rounding information for callers that need to reason about approximation.
- **C2:** `FBig` separates a significand/exponent representation from a precision-and-rounding context. This supports ordinary operator syntax and more explicit numerical workflows over the same underlying model.

The [FBig documentation](https://docs.rs/dashu-float/latest/dashu_float/struct.FBig.html) contains the representation, context, conversion, and operator contracts. Read it alongside the [floating-point module guide](https://docs.rs/dashu-float/latest/dashu_float/) to understand how type-level policies compose with runtime precision.

### 9. [stencillogic/astro-float](https://github.com/stencillogic/astro-float)

**Rust — arbitrary-precision binary floating-point arithmetic and expression evaluation.** The repository describes a progression of multiplication algorithms including Karatsuba, Toom–Cook, and Schönhage–Strassen.

- **C1:** The technical documentation defines word-based mantissas, exponent and sign handling, subnormals, propagated inexactness, and error-bearing NaN results. Requested precision is rounded to the implementation's word granularity. Its stated correct-rounding guarantees have an explicit exception for `RoundingMode::None`.
- **C2:** Contexts, a reusable constant cache, and expression support provide structure for computations that need consistent precision and rounding across many operations.
- **C3:** Lazy constant computation and caching complement the size-dependent arithmetic algorithms, making repeated high-precision evaluation an explicit design concern.

The [crate's technical documentation](https://docs.rs/astro-float/latest/astro_float/) is a useful entry point for both the numerical contract and the execution model.

### 10. [akubera/bigdecimal-rs](https://github.com/akubera/bigdecimal-rs)

**Rust — arbitrary-coefficient decimal arithmetic.** The repository warns of substantial rewriting, so this is a source-study selection rather than a claim of settled API design.

- **C1:** The representation combines a `BigInt` coefficient with a signed scale. Division must account for scale, remainder, precision limits, and final rounding; hashing also needs to reconcile numerically equivalent values with trailing decimal zeros.
- **C2:** The implementation distinguishes owning `BigDecimal` values from borrowed `BigDecimalRef` views and separates arithmetic, conversion, parsing, and formatting modules. This is useful for studying how an arbitrary-precision value type expands without forcing every operation to copy the coefficient.

Start in [`src/lib.rs`](https://raw.githubusercontent.com/akubera/bigdecimal-rs/trunk/src/lib.rs), which includes the representation, division logic, and borrowed-value interface. The repository overview supplies the integration context, including serialization choices that preserve decimal information.

## Scientific and managed-language arithmetic

### 11. [mpmath/mpmath](https://github.com/mpmath/mpmath)

**Python — arbitrary-precision real and complex numerical computing.** A strong choice for following a compact scalar representation into a broad collection of numerical functions.

- **C1:** The technical guide explains normalization of integer mantissa and binary exponent, rounding at the working precision, and cancellation. It carefully distinguishes guarantees for basic arithmetic from higher functions that may use heuristic extra precision or fail on difficult inputs.
- **C2:** The scalar layer supports reusable mathematical functions and higher numerical algorithms under a shared precision model. The documentation helps callers understand when they must increase precision themselves rather than assuming the library can infer the desired accuracy.

Read the [technical description of floating-point arithmetic](https://raw.githubusercontent.com/mpmath/mpmath/master/docs/technical.rst). The repository also documents testing and limitations, including shared precision-setting concerns. This is particularly useful for learning how a user-facing numerical API should explain uncertainty and implementation limits.

### 12. [mtommila/apfloat](https://github.com/mtommila/apfloat)

**Java — arbitrary-precision real and complex arithmetic with extensible storage and algorithm backends.** Its strongest architectural lesson is how very large operands change the storage problem as well as the multiplication algorithm.

- **C2:** A high-level arithmetic layer delegates through `ApfloatImpl` and a service-provider interface. Builder factories construct storage, convolution, and transform strategies, keeping numerical algorithms distinct from representation-specific services.
- **C3:** The SPI explicitly accommodates in-memory arrays and disk-backed storage with block iterators. Operand-size-dependent convolution and transform choices make memory requirements and algorithm selection visible architectural decisions.

The [SPI package design documentation](https://www.apfloat.org/apfloat_java/docs/org/apfloat/spi/package-summary.html) explains these boundaries in detail; the [Java API overview](https://www.apfloat.org/apfloat_java/docs/) provides the higher-level context. No comparative throughput claim is needed to see why this design is substantial.

### 13. [peteroupc/Numbers](https://github.com/peteroupc/Numbers)

**C# — arbitrary-precision binary and decimal floats, integers, and rationals.** Study it for its explicit treatment of arithmetic context and exceptional conditions.

- **C1:** `EContext` distinguishes precision, rounding, exponent limits, status flags, and traps. The documentation separates rounded, inexact, subnormal, and underflow conditions. Configuration is largely immutable, but enabled status flags are mutable and require care when contexts are shared between threads.
- **C2:** A common context abstraction supports unlimited-precision use and predefined arithmetic policies, while callers can derive modified contexts through fluent methods. This is a reusable policy object rather than precision being scattered across individual operations.

Read the [EContext API contract](https://peteroupc.github.io/Numbers/docs/PeterO.Numbers.EContext.html) and its [implementation](https://raw.githubusercontent.com/peteroupc/Numbers/master/Numbers/PeterO/Numbers/EContext.cs). These are particularly useful for examining the tension between convenient shared configuration and mutable diagnostic state.

### 14. [attaswift/BigInt](https://github.com/attaswift/BigInt)

**Swift — signed and unsigned arbitrary-precision integers with value semantics.** The library combines copy-on-write storage with a conventional limb engine, exposing both language-integration and numerical-algorithm concerns.

- **C1:** The division implementation spells out normalization, quotient estimation, overshoot correction, and full-width division preconditions. Carefully selected overflow operations are part of the algorithm rather than accidental arithmetic wraparound.
- **C3:** The repository documents switching between ordinary and Karatsuba multiplication, together with configurable thresholds. Copy-on-write representation provides a separate storage-level optimization that must remain consistent with value semantics.

Begin with [`Sources/Division.swift`](https://raw.githubusercontent.com/attaswift/BigInt/master/Sources/Division.swift), then use the [source directory](https://github.com/attaswift/BigInt/tree/master/Sources) to follow neighboring arithmetic operations. Division is a particularly concrete entry point for studying how mathematical preconditions become machine-word checks.

### 15. [ocaml/Zarith](https://github.com/ocaml/Zarith)

**OCaml and C — arbitrary-precision integers and rationals integrated with the OCaml runtime.** Although it uses GMP, its representation and garbage-collector integration are substantial engineering in their own right.

- **C1:** Integers that fit the runtime's immediate representation must remain unboxed; larger blocks must have normalized nonzero leading limbs. Comparison, hashing, and marshalling must agree with those representation invariants.
- **C3:** Small arithmetic can use OCaml fast paths, while large values occupy runtime-managed blocks and invoke low-level GMP operations. This avoids treating every arithmetic value as a separately allocated foreign object.

The comments and implementation in [`caml_z.c`](https://raw.githubusercontent.com/ocaml/Zarith/master/caml_z.c) explain the representation contract and runtime hooks. The repository overview additionally describes its legacy integer-interface compatibility. Study this code when the interesting problem is integrating a bignum engine with a managed heap.

### 16. [ionspin/kotlin-multiplatform-bignum](https://github.com/ionspin/kotlin-multiplatform-bignum)

**Kotlin — shared arbitrary-precision integer and decimal implementation for multiple platforms.** The repository documents differential testing against Java numeric types, evolving APIs, and experimental platform support; portability should not be mistaken for identical maturity on every target.

- **C1:** `BigInteger` maintains a relationship between sign and magnitude, validates parsed bases and input forms, and exposes defensive copying around its backing words. These are useful boundaries to inspect alongside the cross-implementation tests described by the project.
- **C2:** Public numeric, narrowing, and bitwise interfaces are separated from a chosen arithmetic engine operating on word arrays. This lets the common Kotlin layer serve platforms without depending on a JVM-only integer implementation.

Read the [common BigInteger implementation](https://raw.githubusercontent.com/ionspin/kotlin-multiplatform-bignum/main/bignum/src/commonMain/kotlin/com/ionspin/kotlin/bignum/integer/BigInteger.kt), particularly construction and the calls into `chosenArithmetic`.

### 17. [verement/decimal-arithmetic](https://github.com/verement/decimal-arithmetic)

**Haskell — experimental arbitrary-precision decimal arithmetic with type-level precision and rounding.** Included for a distinct numerical-policy design; recent maintenance was not established, and the published API explicitly labels itself experimental.

- **C1:** Parsing rounds to the selected precision, NaN affects equality differently from total ordering, and infinite-precision values do not support every operation. These contracts prevent a superficially familiar numeric type from silently promising ordinary real-number laws.
- **C2:** `Decimal p r` separates precision and rounding through type classes. Precision constructors compose to arbitrary sizes, while the same framework offers an unlimited-precision form and decimal interchange encodings.

The versioned [Numeric.Decimal guide](https://hackage.haskell.org/package/decimal-arithmetic-0.5.1.0/docs/Numeric-Decimal.html) documents both the design and the limitations. It is useful for comparing type-directed policy selection with the runtime context objects used by several other projects in this report.

## JavaScript and service-oriented decimal systems

### 18. [MikeMcl/decimal.js](https://github.com/MikeMcl/decimal.js)

**JavaScript — arbitrary-precision decimal floating-point arithmetic.** Useful for examining a full numerical contract built on the host language's ordinary number and array facilities.

- **C1:** The [implementation](https://raw.githubusercontent.com/MikeMcl/decimal.js/master/decimal.js) represents values through sign, exponent, and base-10,000,000 digit chunks. Central rounding/finalization logic coordinates multiple rounding modes, exceptional values, and exponent limits; this is much more than decimal string formatting.
- **C2:** Significant-digit precision applies throughout arithmetic, with a broad operation set and independently configurable cloned constructors for separate numerical policies.
- **C4:** The [changelog](https://raw.githubusercontent.com/MikeMcl/decimal.js/master/CHANGELOG.md) spans years of concrete maintenance: immutability regressions, low-exponent infinite loops, TypeScript compatibility, cancellation-sensitive calculations, and BigInt or signed-zero behavior. This makes numerical corner cases and language interoperability visible parts of the project's evolution.

The source and changelog together are better study material than the size of the public method list alone.

### 19. [indutny/bn.js](https://github.com/indutny/bn.js)

**JavaScript — arbitrary-precision integers with modular-reduction contexts.** Its integer-only scope complements decimal.js and avoids confusing integer arithmetic with approximate decimal computation.

- **C1:** The implementation uses 26-bit words within JavaScript numbers. Reduction operations verify positivity and that operands belong to the same reduction context, making context identity part of arithmetic correctness.
- **C2:** General integers, modular values, specialized prime reductions, Montgomery arithmetic, byte-order conversion, and in-place operation conventions share one reusable numeric interface.
- **C3:** Explicit in-place methods and specialized reduction paths expose both allocation and repeated-modular-operation costs.

Read [`lib/bn.js`](https://raw.githubusercontent.com/indutny/bn.js/master/lib/bn.js), moving from the word representation to the `Red` and Montgomery implementations. These features are not evidence of constant-time behavior; that property was not assessed.

### 20. [cockroachdb/apd](https://github.com/cockroachdb/apd)

**Go — arbitrary-precision decimals with explicit arithmetic contexts and conditions.** Study the separation of the decimal value from the policy for operating on it, then inspect the coefficient-storage optimization beneath that API.

- **C1:** The repository describes precision, exponent limits, traps, and condition reporting. At the storage layer, promotion from inline words to a `big.Int` allocation must preserve sign, aliasing, and the validity of temporary views.
- **C2:** Decimal values and contexts are separate abstractions, so the same stored value can participate in computations with different rounding or error-handling requirements.
- **C3:** The internal integer keeps small coefficients in an inline 128-bit buffer and adapts to `math/big` through carefully managed views. Its implementation makes allocation avoidance—and the associated unsafe representation assumptions—inspectable.

Start with [`bigint.go`](https://raw.githubusercontent.com/cockroachdb/apd/master/bigint.go). It is an unusually concrete example of optimizing a widely reused arithmetic dependency without replacing its entire algorithm collection.

### 21. [ericlagergren/decimal](https://github.com/ericlagergren/decimal)

**Go — arbitrary-precision decimal floating-point arithmetic with mathematical functions.** Its per-value context and compact coefficient path provide a different design from apd's separate context/value approach.

- **C1:** The implementation distinguishes signed zero, infinities, quiet/signaling NaNs, and status conditions. The inspected overflow helper also documents a legacy case that produces infinity where a largest finite value would be expected; the selection therefore does not endorse blanket specification conformance.
- **C2:** The repository exposes Go-oriented and General Decimal Arithmetic operating modes, with a reusable mathematical layer including continued fractions and transcendental functions.
- **C3:** `Big` stores a small coefficient in a `uint64` and uses `big.Int` when the value grows. Form bits, exponent, and precision are kept alongside this compact/inflated distinction.

The [Big representation and special-value handling](https://raw.githubusercontent.com/ericlagergren/decimal/master/big.go) is the most instructive entry point, including the documented overflow limitation.

### 22. [shopspring/decimal](https://github.com/shopspring/decimal)

**Go — arbitrary-precision fixed-point decimals with an arbitrary-size coefficient and bounded exponent representation.** This is the explicitly fixed-point inclusion: it belongs for its bignum arithmetic and decimal semantics, not for implementing a general binary floating-point system. The project acknowledges its origin as a heavily modified fork of `fpd.Decimal`; that ancestor is not separately counted.

- **C1:** Immutable arithmetic must avoid exposing mutable coefficient aliases. The inspected implementation also bounds exponents during decoding to limit resource expansion from hostile textual inputs; those decoding limits do not universally bound arithmetic or constructors.
- **C2:** The value type combines configurable division behavior with JSON, XML, and database interfaces, making preservation of decimal values across application boundaries part of the abstraction.

Read [`decimal.go`](https://raw.githubusercontent.com/shopspring/decimal/master/decimal.go), particularly coefficient construction, decoding limits, and the serialization/database surfaces. This is useful for studying the consequences of bringing exact decimal values into ordinary service code.

### 23. [brick/math](https://github.com/brick/math)

**PHP — immutable arbitrary-precision integers, decimals, and rationals with interchangeable calculators.** Its native implementation and shared algorithms make it more substantial than an extension wrapper.

- **C1:** The internal calculator contract requires canonical decimal strings without leading zeros or negative zero. Public conversions distinguish exact results from operations requiring rounding, while bounded parsing addresses inputs that could expand into unexpectedly large values.
- **C2:** GMP, BCMath, and native PHP calculators implement common primitives. Shared higher operations, including GCD and modular inverse, are built above those primitives, and the public number classes do not require callers to select a backend.

The [Calculator abstraction](https://raw.githubusercontent.com/brick/math/main/src/Internal/Calculator.php) is a compact entry point for the normalization contract and the boundary between backend-specific primitives and reusable algorithms. The repository guide explains the immutable public types and parsing policies.

## Standard-library implementations

### 24. [golang/go](https://github.com/golang/go)

**Go and assembly — `src/math/big` only; official GitHub mirror of the Go source repository.** Counted once for `Int`, `Rat`, and `Float`, not for the surrounding compiler and runtime.

- **C1:** Natural-number limbs are normalized, little-endian words; zero and leading-word rules matter to comparison and arithmetic. Internal alias detection also relies on storage-capacity assumptions that differ from the public API's supported operand/result aliasing. See [`nat.go`](https://raw.githubusercontent.com/golang/go/master/src/math/big/nat.go).
- **C2:** A consistent receiver-as-result API spans integers, rationals, and floating-point values. Useful zero values and documented aliasing rules support composition without concealing mutability. See the [package design documentation](https://raw.githubusercontent.com/golang/go/master/src/math/big/doc.go).
- **C3:** Reusing result receivers and existing limb capacity is a deliberate allocation strategy. The public conventions and internal storage helpers make that performance contract legible.

### 25. [openjdk/jdk](https://github.com/openjdk/jdk)

**Java — `java.base/java.math`, specifically BigInteger and BigDecimal.** Counted once for these reusable arithmetic implementations rather than for the JDK as a whole.

- **C1:** BigInteger reconciles a sign/magnitude implementation with externally specified integer bit semantics. BigDecimal must separately manage coefficient, scale, rounding, nonterminating division, and the distinction between numerical comparison and representation-sensitive equality. See [BigInteger.java](https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/share/classes/java/math/BigInteger.java) and [BigDecimal.java](https://raw.githubusercontent.com/openjdk/jdk/master/src/java.base/share/classes/java/math/BigDecimal.java).
- **C2:** Immutable values, explicit arithmetic contexts, conversions, and well-specified scale behavior support many applications through a stable conceptual interface.
- **C3:** BigInteger's multiplication implementation dispatches among ordinary, Karatsuba, and Toom–Cook algorithms using explicit thresholds; conversion machinery also caches reusable radix powers. The source is useful for seeing how specialized algorithms coexist behind a single general-purpose value type.

## Search coverage, exclusions, and limits

Discovery used more than six distinct live-search formulations, including broad arbitrary-precision C/C++ libraries; Rust integer and floating-point implementations; JavaScript decimal and modular integer libraries; Go General Decimal Arithmetic systems; rigorous ball arithmetic; Java transform/storage architectures; C# and Swift bignums; and OCaml, Haskell, Kotlin, and Fortran implementations. Follow-up searches examined official repository identity, design documentation, source files, release notes, and test descriptions. Later language-specific and mirror searches increasingly returned already-covered libraries, narrow bindings, fixed-width types, or unverified ports, producing diminishing returns.

The selection deliberately includes several architectural families: native limb engines, backend-generic C++, managed-runtime integration, type-directed rounding, rigorous enclosures, disk-backed arithmetic, small-value optimization, and service-oriented decimal serialization. Evidence supports the mechanisms described; the judgment that a mechanism is especially instructive is the report's own assessment. Repository popularity was not a selection criterion.

Important boundaries and exclusions:

- **GMP and MPFR:** foundational to this ecosystem, but no official substantive GitHub mirror was verified in this search. GMP's [development page](https://gmplib.org/devel/) and MPFR's [source-control instructions](https://www.mpfr.org/git.html) identify their own development infrastructure. Unverified GitHub copies were not substituted merely to fill the list. The same verification constraint prevented inclusion of some mpdecimal and Fortran candidates.
- **No double-counting:** Arb is covered within FLINT; each monorepo appears once. The historical ancestor of shopspring/decimal is not another entry. Closely related JavaScript decimal libraries were not all included simply to increase the count.
- **Implementation threshold:** generated wrappers, tutorial bignums, awesome lists, and fixed-width-only arithmetic were excluded. mp++ and Zarith remain because their storage, runtime, and interoperability designs are substantial beyond calling another library.
- **Maintenance and versions:** C4 is awarded where concrete multi-year maintenance evidence was inspected. A public repository or an old creation date alone was not treated as evidence of active maintenance. Experimental or evolving interfaces are identified where documented. Published documentation and moving default branches can represent different versions; this is a research-date selection guide, not a pinned dependency audit.
- **Validation limits:** this was read-only research. Candidate code was not cloned, installed, executed, benchmarked, or formally verified. Performance discussion describes identifiable design choices rather than independently measured speed. No constant-time or universal correct-rounding guarantee is inferred from arbitrary precision alone.
