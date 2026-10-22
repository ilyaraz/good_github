# Decimal arithmetic and exact monetary calculation libraries

Research date: **2026-10-09**.

This report selects **27 GitHub repositories** implementing decimal arithmetic or substantial currency-aware monetary abstractions. It covers arbitrary-precision engines, bounded and hybrid representations, explicit rounding contexts, integer minor units, rational intermediate calculations, and allocation. CPython is included only for its decimal subsystem; general binary floating-point libraries and financial applications are outside scope.

“Exact” has several meanings here. Exact representation of a decimal input does not guarantee exact division, unlimited magnitude, or preservation of every intermediate digit. The entries identify these boundaries because they are central to the engineering value of this category. This is a source-reading selection guide, not a correctness certification or a ranking of production readiness.

Criteria legend:

- **C1 — Difficult correctness:** numerical semantics, invariants, concurrency, hostile inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces and models supporting multiple applications.
- **C3 — Performance with structure:** concrete representation or algorithm choices addressing resource constraints through understandable architecture.
- **C4 — Sustained evolution:** dated evidence of years of compatibility work, testing, or complexity management. Repository age and popularity alone do not qualify.

## Arbitrary-precision engines and configurable decimal semantics

### [python/cpython](https://github.com/python/cpython)

**Language/role:** C and Python; the standard-library `decimal` subsystem within the CPython monorepo.

Study how a language runtime exposes decimal arithmetic with preserved significance, signed zero, exceptional values, and independently configurable arithmetic policy. The separation between stored digits and the context governing an operation is especially useful when designing accounting APIs.

- **C1:** Precision, exponent limits, rounding modes, sticky signal flags, and traps make inexactness observable; trapping `Inexact` can enforce an exact-arithmetic contract. The [decimal reference](https://docs.python.org/3/library/decimal.html) explains these semantics and their interactions.
- **C2:** The same value/context model supports fixed-place financial calculations and scientific decimal arithmetic. The [test harness](https://raw.githubusercontent.com/python/cpython/main/Lib/test/test_decimal.py) applies arithmetic specification cases and Python behavior tests to both C-backed and pure-Python implementations, exposing the reusable contract and its implementation boundary.

Entry points: the decimal reference and `Lib/test/test_decimal.py` linked above. The repository is counted once; its unrelated runtime components are not part of this selection.

### [cockroachdb/apd](https://github.com/cockroachdb/apd)

**Language/role:** Go; arbitrary-precision decimals with explicit contexts and condition reporting.

Study an arithmetic engine designed to make numeric failure handling usable by database and application code. Values carry coefficients and exponents; contexts supply precision, rounding, exponent bounds, and trap policy.

- **C1:** The [context implementation](https://raw.githubusercontent.com/cockroachdb/apd/master/context.go) handles signaling NaNs, invalid infinity operations, cancellation signs, quotient remainders, and subnormal rounding. It documents concurrent use as safe when the context is not being mutated, and permits destination/operand aliasing.
- **C2:** Separating `Decimal` from `Context` lets callers reuse values under different arithmetic policies and inspect conditions independently of returned errors.
- **C3:** The repository explains its `BigInt` small-value storage with a `math/big` fallback and its effort to return errors for computations requiring excessive resources. This is a useful counterpart to engines that expose effectively unbounded operations without an application-facing resource policy.

Entry point: `context.go`; the repository overview supplies the representation and resource-policy rationale.

### [shopspring/decimal](https://github.com/shopspring/decimal)

**Language/role:** Go; immutable decimal values backed by an arbitrary-size integer and a decimal exponent.

Study a convenient value API whose rounding policy differs materially from significant-digit context engines: basic addition, subtraction, and multiplication preserve decimal results, while division needs a finite-place policy.

- **C1:** The [implementation](https://raw.githubusercontent.com/shopspring/decimal/master/decimal.go) distinguishes exact operations from division precision, copies incoming big integers to protect immutability, and bounds exponents accepted by decoding paths. The decoding bound does not impose a universal bound on arithmetic or every constructor.
- **C2:** A single value type integrates arithmetic, string conversion, JSON, and database use. These boundaries are valuable to study because passing exact values through a binary floating-point consumer can defeat the representation's purpose.

Entry points: `decimal.go` and the [changelog](https://raw.githubusercontent.com/shopspring/decimal/master/CHANGELOG.md), which documents decoding-limit behavior, rounding fixes, and compatibility changes. The project acknowledges an earlier implementation lineage; that ancestor is not counted separately here.

### [ericlagergren/decimal](https://github.com/ericlagergren/decimal)

**Language/role:** Go; a mutable, `math/big`-style decimal engine with configurable arithmetic contexts.

Study how a decimal implementation combines compact common-case storage with a broad numerical model. This design is distinct from immutable money-oriented Go libraries.

- **C1:** The [core implementation](https://raw.githubusercontent.com/ericlagergren/decimal/master/big.go) models signed zero, infinities, quiet/signaling NaNs and diagnostic information, and total ordering over decimal representations. These are more demanding semantics than ordering finite mathematical values alone.
- **C2:** `Big` carries a context and exposes receiver-based operations; the repository also documents arithmetic modes and a mathematical-function package. Callers can compose numerical algorithms without reducing the library to currency-specific rules.
- **C3:** The same implementation keeps small coefficients in a compact integer and uses `big.Int` when necessary. The explicit representation split provides a concrete place to study allocation avoidance and transition invariants.

Entry point: `big.go`, particularly the `Big` representation, context fields, forms, and ordering code.

### [MikeMcl/decimal.js](https://github.com/MikeMcl/decimal.js)

**Language/role:** JavaScript; arbitrary-precision decimal floating-point with significant-digit rounding.

Study a configurable decimal arithmetic system that rounds calculations to a chosen significant-digit precision, including operations beyond division. Cloned constructors provide independent configurations for different consumers in one application.

- **C1:** The [implementation](https://raw.githubusercontent.com/MikeMcl/decimal.js/master/decimal.js) separates precision, exponent bounds, rounding, and modulo conventions, and implements mathematical functions whose cancellation and rounding behavior require careful treatment.
- **C2:** Constructor cloning and the broad arithmetic/transcendental API support reusable numerical components without requiring one shared configuration.
- **C4:** The [dated changelog](https://raw.githubusercontent.com/MikeMcl/decimal.js/master/CHANGELOG.md) spans 2014–2025. It records numerical fixes, including inverse-cosine cancellation near one and signed-zero behavior, alongside TypeScript and package-export compatibility work.

Entry points: `decimal.js` and `CHANGELOG.md`. Its significant-digit policy is a key selection distinction from the next project.

### [MikeMcl/bignumber.js](https://github.com/MikeMcl/bignumber.js)

**Language/role:** JavaScript; arbitrary-precision decimal arithmetic emphasizing exact basic operations and configurable decimal-place rounding.

Study a separate numerical design by the same author: addition, subtraction, and multiplication are not rounded to a global significant-digit budget. Division and other inherently limited operations have explicit precision policies.

- **C1:** The [implementation](https://raw.githubusercontent.com/MikeMcl/bignumber.js/main/bignumber.js) uses coefficient arrays, exponent/sign state, and carefully bounded JavaScript-number intermediates. It separates rounding and modulo policies and handles invalid inputs and exceptional values.
- **C2:** Independent constructor configurations, base conversion, formatting, and fraction conversion make this a general numerical building block rather than a currency wrapper.
- **C4:** The [changelog](https://raw.githubusercontent.com/MikeMcl/bignumber.js/main/CHANGELOG.md) provides dated history from 2012 through 2026, including module-format changes, type-import tests, and representation validation work.

Entry points: `bignumber.js` and `CHANGELOG.md`. This is a distinct implementation and API contract, not a second count of `decimal.js`.

### [ericmj/decimal](https://github.com/ericmj/decimal)

**Language/role:** Elixir; arbitrary-precision decimal values with BEAM-process-local arithmetic contexts.

Study how decimal policy fits a concurrent language runtime. A process can use its own rounding and signal configuration without changing another process's arithmetic environment.

- **C1:** The [context implementation](https://raw.githubusercontent.com/ericmj/decimal/main/lib/decimal/context.ex) stores context in the process dictionary and restores an earlier context with `try/after` around scoped execution. That restoration is an important exception-path invariant. The repository also documents parsing and output limits for potentially excessive digit counts and exponents.
- **C2:** Precision, rounding, exponent limits, flags, and traps are factored into a reusable `Context` separate from immutable decimal values. Scoped context changes support libraries that need local policy.

Entry point: `lib/decimal/context.ex`. Input/output bounds and context result limits address different resource risks; the latter alone do not bound the size of existing operands.

### [ruby/bigdecimal](https://github.com/ruby/bigdecimal)

**Language/role:** C and Ruby; Ruby's native arbitrary-precision decimal library and mathematical support.

Study numerical algorithms together with the runtime integration needed to expose them safely as a native extension: allocation, Ruby object lifetime, exceptions, and precision all interact.

- **C1:** The [C implementation](https://raw.githubusercontent.com/ruby/bigdecimal/master/ext/bigdecimal/bigdecimal.c) includes exponent-overflow handling, rounding machinery, and Ruby memory-management integration. The [change history](https://raw.githubusercontent.com/ruby/bigdecimal/master/CHANGES.md) documents fixes involving precision loss, out-of-bounds access, GC guards, and Ractor-related behavior.
- **C3:** The implementation has distinct multiplication and division algorithm thresholds; the change history describes number-theoretic-transform multiplication and Newton–Raphson division. This gives concrete algorithm-selection structure to inspect without relying on headline benchmark claims.

Entry points: `ext/bigdecimal/bigdecimal.c` and `CHANGES.md`. Algorithm and fix descriptions refer to the inspected development source, not an assurance that every installed Ruby version includes them.

### [brick/math](https://github.com/brick/math)

**Language/role:** PHP; immutable big integers, decimals, and rational numbers.

Study a numeric hierarchy that makes exact conversions and rounding obligations explicit. `BigRational` is particularly relevant when a calculation must postpone decimal rounding until a later boundary.

- **C1:** The [decimal implementation](https://raw.githubusercontent.com/brick/math/main/src/BigDecimal.php) enforces a canonical integer-string representation and a nonnegative scale. It distinguishes an exact conversion of a binary float's value from a conversion based on its shorter decimal representation, and rejects nonfinite floats.
- **C2:** The repository's integer/decimal/rational family shares conversion and arithmetic abstractions; conversions that cannot produce an exact finite decimal require a rounding decision. The decimal class delegates arithmetic through a calculator registry rather than embedding every integer backend in the public value type.

Entry point: `src/BigDecimal.php`. The repository overview supplies examples of the three numeric types and exact-conversion failures. This arithmetic foundation is distinct from `brick/money`'s currency and allocation domain model below.

### [akubera/bigdecimal-rs](https://github.com/akubera/bigdecimal-rs)

**Language/role:** Rust; arbitrary-size integer coefficients with decimal scale, explicit rounding contexts, and borrowed decimal views.

Study the boundary between owning a potentially large number and operating on references to it. The library is useful for comparing arbitrary-size decimals with Rust's bounded decimal alternatives.

- **C1:** The [context API](https://docs.rs/bigdecimal/latest/bigdecimal/struct.Context.html) makes precision and rounding explicit for operations such as multiplication and inversion. Defaults can be build-configured, so applications needing reproducible policy should supply their context.
- **C2:** The [source](https://raw.githubusercontent.com/akubera/bigdecimal-rs/trunk/src/lib.rs) separates `BigDecimal`, `BigDecimalRef`, contexts, rounding, parsing, serialization, and arithmetic modules. Owned/borrowed forms and destination-oriented operations provide reusable building blocks for larger calculations.

Entry points: `src/lib.rs` and the `Context` API. **Version caveat:** the repository warns that its development branch is being rewritten; published `docs.rs` documentation and `trunk` are different version surfaces and should not be assumed identical.

### [ionspin/kotlin-multiplatform-bignum](https://github.com/ionspin/kotlin-multiplatform-bignum)

**Language/role:** Kotlin; a multiplatform big-number implementation, included specifically for its decimal subsystem.

Study an arithmetic engine implemented in shared Kotlin rather than a uniform-looking API over different platform decimal engines. Decimal values hold a big-integer significand, exponent, and optional arithmetic mode.

- **C1:** The [decimal implementation](https://raw.githubusercontent.com/ionspin/kotlin-multiplatform-bignum/main/bignum/src/commonMain/kotlin/com/ionspin/kotlin/bignum/decimal/BigDecimal.kt) resolves operand modes, rejects incompatible rounding policies, and uses quotient/remainder information to distinguish exact ties from values beyond a tie. Unbounded-mode division can reject a nonterminating result.
- **C2:** [DecimalMode](https://raw.githubusercontent.com/ionspin/kotlin-multiplatform-bignum/main/bignum/src/commonMain/kotlin/com/ionspin/kotlin/bignum/decimal/DecimalMode.kt) combines precision, rounding, and optional scale, validates incompatible combinations, and can be supplied per operation. The surrounding project provides common numeric interfaces and serialization support.

Entry points: `BigDecimal.kt` and `DecimalMode.kt`. **Status caveat:** the repository describes pre-1.0 API evolution and experimental WebAssembly support; its cross-platform behavior should not be presumed uniform without checking the chosen target.

## Bounded, hybrid, and type-directed decimal representations

### [boostorg/decimal](https://github.com/boostorg/decimal)

**Language/role:** C++; decimal floating-point types with IEEE-oriented and separately documented fast variants.

Study decimal interchange representation and rounding at the level of bounded integer intermediates. The canonical repository is now under `boostorg`; the earlier `cppalliance/decimal` address redirects there.

- **C1:** The [division implementation](https://raw.githubusercontent.com/boostorg/decimal/develop/include/boost/decimal/detail/div_impl.hpp) retains quotient/remainder information for tie handling, compares a remainder without overflowing a doubled value, accounts for rounding carry, and defers subnormal rounding to avoid double rounding.
- **C2:** Decimal32/64/128 families and standard-library-like mathematical and conversion facilities provide reusable numerical types. IEEE-oriented types and fast variants have different guarantees and should be selected deliberately.
- **C3:** The [decimal64 representation](https://raw.githubusercontent.com/boostorg/decimal/develop/include/boost/decimal/decimal64_t.hpp) packs state into bounded storage, while arithmetic is split into specialized helper modules and intermediate widths.

Entry points: `detail/div_impl.hpp` and `decimal64_t.hpp`. These links inspect `develop`; they do not establish availability in a particular installed Boost release.

### [govalues/decimal](https://github.com/govalues/decimal)

**Language/role:** Go; finite decimal arithmetic with **19 total digits**, deliberately excluding NaNs, infinities, and signed zero.

Study a restricted numeric model designed around predictable behavior and resource use. Its meaning of an “exact” operation is especially worth reading before adoption.

- **C1:** The [package design documentation](https://github.com/govalues/decimal/blob/main/doc.go) distinguishes integer digits from caller-designated significant fractional places. `Exact` variants can reject loss of significant fractional information; ordinary operations may round fractional results. Underflow can round to zero.
- **C2:** Arithmetic, scale-sensitive operations, and serialization/database boundaries share one documented value model. Omitting exceptional floating-point values simplifies the domain while changing the range of supported algorithms.
- **C3:** Operations first attempt exact `uint64` arithmetic. On overflow they repeat with higher-precision `big.Int` intermediates before rounding to the public representation. The two-stage design makes the common-case optimization and fallback visible.

Entry point: `doc.go`, particularly representation, arithmetic, rounding, and significant-digit rules. Nineteen digits here is not nineteen places after the decimal point.

### [quagmt/udecimal](https://github.com/quagmt/udecimal)

**Language/role:** Go; fixed-point decimals with up to **19 fractional places**, a 128-bit coefficient path, and a big-integer fallback.

Study a hybrid representation aimed at avoiding allocation for common financial magnitudes while preserving a larger coefficient range when necessary.

- **C1:** The repository documents truncation when results exceed the supported fractional precision and exposes explicit rounding operations. That distinction matters: “no implicit rounding” does not mean every result retains every digit.
- **C3:** The [coefficient implementation](https://github.com/quagmt/udecimal/blob/master/bint.go) separates a `u128` representation from an optional `big.Int`, detects the fallback state, and returns a copy when exposing a big integer. This is a concrete place to inspect overflow transitions and aliasing protection.

Entry point: `bint.go`, read alongside the repository's precision and rounding examples. Allocation avoidance applies to the bounded path; operations requiring the big-integer path should not be described as universally allocation-free.

### [paupino/rust-decimal](https://github.com/paupino/rust-decimal)

**Language/role:** Rust; bounded decimal values with a 96-bit coefficient and scale up to 28.

Study a fixed-size value representation with explicit construction and overflow contracts, together with the integration work needed for databases and serialization.

- **C1:** The [Decimal API](https://docs.rs/rust_decimal/latest/rust_decimal/struct.Decimal.html) distinguishes fallible construction, panicking constructors, checked arithmetic, and saturating operations. Scale limits and coefficient limits are separate constraints; 28 places does not imply arbitrary magnitude at that scale.
- **C2:** Numeric traits, macros, rounding strategies, and optional database/Serde support make the value usable across application layers while retaining decimal semantics.

Entry point: the `Decimal` API, especially representation, `try_*` constructors, and checked operations. **Branch caveat:** the repository describes `master` as development toward a new major version and directs stable backward-compatible fixes to `v1`; choose documentation and source for the intended major version.

### [neogenie/fastnum](https://github.com/neogenie/fastnum)

**Language/role:** Rust; generic bounded signed and unsigned decimal families, with arithmetic contexts and exceptional-condition signaling.

Study an alternative to both heap-backed arbitrary precision and a single fixed coefficient width. The decimal model includes control state and extra precision information alongside its coefficient.

- **C1:** The [crate documentation](https://docs.rs/fastnum/latest/fastnum/) explains inexact, rounded, subnormal, and underflow conditions, configurable traps, and quantization. A decimal representation still rounds results such as one third; configured traps may turn conditions into panics.
- **C2:** Generic coefficient widths, signed/unsigned types, and context-controlled arithmetic support several precision budgets through one design.
- **C3:** The documented layout uses a fixed-width coefficient and a control block rather than allocating a growing coefficient. Const evaluation and `no_std` support make the resource model relevant beyond ordinary server applications.

Entry point: the crate documentation's representation, context, and arithmetic-condition sections. The library's “exact precision” terminology should be interpreted within its bounded decimal rules.

### [tools4j/decimal4j](https://github.com/tools4j/decimal4j)

**Language/role:** Java; long-backed fixed-point arithmetic with scales from zero through eighteen.

Study the tradeoff between convenient decimal objects and direct arithmetic on unscaled primitive longs. Scale, overflow policy, and rounding can be selected independently.

- **C1:** The [DecimalArithmetic design guide](https://github.com/tools4j/decimal4j/wiki/DecimalArithmetic-API) describes arithmetic specialized by scale, rounding mode, and overflow mode. Checked and unchecked overflow are distinct contracts, not interchangeable implementation details.
- **C2:** Scale types, immutable/mutable decimal values, and the lower-level `DecimalArithmetic` interface provide several reusable access layers for the same numerical policies.
- **C3:** The primitive interface accepts and returns unscaled longs, avoiding decimal-object creation in an arithmetic loop. Factories tied to scale metrics keep that optimization separate from application-specific calculation logic.

Entry point: the `DecimalArithmetic` wiki guide; the repository overview connects it to the public decimal types. No current release-cadence claim is inferred from the existence of this design.

### [fpco/safe-decimal](https://github.com/fpco/safe-decimal)

**Language/role:** Haskell; decimal scale and rounding encoded in types, parameterized over the underlying integral representation.

Study how static policy selection can coexist with explicit runtime arithmetic failure. It is a useful counterpoint to context objects and mutable global rounding settings.

- **C1:** The [bounded-arithmetic implementation](https://raw.githubusercontent.com/fpco/safe-decimal/master/src/Numeric/Decimal/BoundedArithmetic.hs) checks signed/unsigned bounds and special division cases, including division by zero and the minimum signed value divided by minus one. Failures are carried by an `Arith` result rather than silently wrapping.
- **C2:** The [decimal module](https://raw.githubusercontent.com/fpco/safe-decimal/master/src/Numeric/Decimal.hs) parameterizes scale, rounding policy, and backing number type. `Arith` can be converted into `Maybe`, `Either`, or exception-capable computations, making the same arithmetic useful in different error-handling styles.

Entry points: `Numeric/Decimal.hs` and `Numeric/Decimal/BoundedArithmetic.hs`. The study value rests on these concrete abstractions; this report makes no claim about current maintenance cadence.

## Currency-aware money, allocation, and rational intermediate amounts

### [brick/money](https://github.com/brick/money)

**Language/role:** PHP; immutable monetary values built on `brick/math`, including rational intermediate money.

Study how a domain library determines *when* a number should become a currency amount with a particular representable increment. Cash rounding and accounting precision need not be the same boundary.

- **C1:** [RationalMoney](https://raw.githubusercontent.com/brick/money/main/src/RationalMoney.php) retains rational amounts through intermediate operations, checks currencies, and defers conversion into a rounded `Money` context. The repository's allocation examples demonstrate distributing indivisible remainders rather than independently rounding every share.
- **C2:** Default, cash-increment, custom-scale, and automatic contexts express different money policies. `Money` and `RationalMoney` give applications distinct types for settled amounts and exact intermediate calculations.

Entry point: `src/RationalMoney.php`, with the repository's context and allocation guide. This repository earns its place through monetary policy and domain invariants; `brick/math` is separately included for the underlying numerical implementation.

### [moneyphp/money](https://github.com/moneyphp/money)

**Language/role:** PHP; integer-minor-unit monetary values with currencies and calculator abstractions.

Study a money model that stores amounts as integer numeric strings, keeping currency identity separate from numeric magnitude and delegating arithmetic to a calculator.

- **C1:** The [Money implementation](https://raw.githubusercontent.com/moneyphp/money/master/src/Money.php) validates integer amounts, rejects incompatible currencies in operations, and includes ratio-based allocation with remainder handling. Those invariants matter more than formatting a decimal with a currency symbol.
- **C2:** Money, Currency, calculator interfaces, and surrounding formatting/conversion facilities form reusable domain boundaries. Integer storage can support amounts beyond a native machine integer, subject to the selected arithmetic backend.

Entry point: `src/Money.php`, especially amount validation, currency checks, rounding modes, and allocation. This is an integer monetary model, so multiplication or division that produces fractional minor units still needs an explicit policy.

### [RubyMoney/money](https://github.com/RubyMoney/money)

**Language/role:** Ruby; monetary values, currency metadata, exchange-bank abstractions, and allocation.

Study how a broad money API manages the interaction between integer subunits, higher-precision calculations, and evolving default behavior.

- **C1:** The [allocation implementation](https://raw.githubusercontent.com/RubyMoney/money/main/lib/money/money/allocation.rb) works with the remaining amount and remaining proportions, supporting whole-unit truncation, a chosen decimal cutoff, or unrounded splits. Its Rational conversion uses configurable BigDecimal precision, a boundary that should be inspected when exact fractions matter.
- **C2:** Currency data, configurable rounding, allocation, and exchange-bank interfaces cover distinct monetary operations without embedding all policy in an amount string. The [changelog](https://raw.githubusercontent.com/RubyMoney/money/main/CHANGELOG.md) shows why explicit configuration matters: major-version changes include default currency and rounding behavior.

Entry points: `lib/money/money/allocation.rb` and `CHANGELOG.md`. Findings about unreleased changes describe `main`, not every published gem version.

### [dinerojs/dinero.js](https://github.com/dinerojs/dinero.js)

**Language/role:** TypeScript/JavaScript; immutable monetary calculations parameterized by a numeric calculator.

Study an architecture in which amount, currency, and scale are independent data, while arithmetic is supplied through a generic calculator. This enables number and big-integer usage without duplicating the domain algorithms.

- **C1:** The [allocation API](https://raw.githubusercontent.com/dinerojs/dinero.js/main/packages/dinero.js/src/core/api/allocate.ts) validates ratios and normalizes their scale before distribution. The [distribution implementation](https://raw.githubusercontent.com/dinerojs/dinero.js/main/packages/dinero.js/src/core/utils/distribute.ts) tracks a remainder, handles its sign, and explicitly guards against a loop that stops making progress under floating-point precision loss.
- **C2:** Calculator-parameterized core functions separate numerical operations from monetary rules and public validation. They are useful examples of reusable arithmetic-independent domain logic.

Entry points: core `api/allocate.ts` and `utils/distribute.ts`. **Exactness caveat:** the loop guard exposes a real boundary; using JavaScript `number` beyond its safe integer range does not preserve arbitrary-size exact allocation. This entry follows the inspected `main` layout, not older Dinero v1 examples.

### [JavaMoney/jsr354-ri](https://github.com/JavaMoney/jsr354-ri)

**Language/role:** Java; Moneta, the reference implementation of the JSR 354 money and currency API.

Study a standards-oriented monetary system with interchangeable amount implementations, explicit monetary contexts, and provider-based services.

- **C1:** The [Money implementation](https://raw.githubusercontent.com/JavaMoney/jsr354-ri/master/moneta-core/src/main/java/org/javamoney/moneta/Money.java) is immutable, uses `BigDecimal`, and retains a `MonetaryContext` that governs calculation precision. Construction and operations therefore involve both amount invariants and context semantics; a decimal backend does not make every division exact.
- **C2:** `MonetaryAmount` implementations, currency services, contexts, and conversion/provider modules provide extensible interfaces for applications and infrastructure. The repository distinguishes the BigDecimal-based `Money` from the bounded `FastMoney` alternative.

Entry point: `moneta-core/.../Money.java`; the repository overview maps the core and conversion modules. The monorepo is counted once rather than counting each amount implementation or service module separately.

### [JodaOrg/joda-money](https://github.com/JodaOrg/joda-money)

**Language/role:** Java; monetary value objects with currency-scale and unrestricted-scale variants.

Study a deliberately small domain distinction with large consequences: `Money` uses the currency's decimal places, while `BigMoney` permits additional scale for intermediate calculations.

- **C1:** The [user guide](https://www.joda.org/joda-money/userguide.html) makes conversion from `BigMoney` to `Money` a rounding boundary. It also explains scale normalization and value behavior rather than presenting arbitrary decimal precision as sufficient monetary policy.
- **C2:** `BigMoneyProvider`, extensible currency data, and immutable formatters allow integration without coupling every caller to a single concrete amount class.
- **C4:** The [dated change report](https://www.joda.org/joda-money/changes-report.html) spans 2009–2025 and records scale/equality fixes, an Android decimal-compatibility workaround, currency-data changes, and separate Java compatibility tracks for major versions.

Entry points: the user guide and change report. This is a particularly clear codebase to study when the main question is where accounting precision should become payable currency precision.

### [RemyDuijkeren/NodaMoney](https://github.com/RemyDuijkeren/NodaMoney)

**Language/role:** C#/.NET; monetary values with context-controlled rounding and currency registration.

Study a domain model that pays close attention to physical value layout and read-heavy metadata access, alongside ordinary amount/currency correctness.

- **C1:** The [Money implementation](https://raw.githubusercontent.com/RemyDuijkeren/NodaMoney/master/src/NodaMoney/Money.cs) applies context rounding at construction and implements currency-aware, scale-insensitive value equality, including zero handling. These details keep representation differences such as trailing zeros from becoming accidental economic differences.
- **C2:** Monetary contexts and currency definitions separate calculation policy from individual amounts, enabling different currency and rounding requirements.
- **C3:** The implementation packs monetary metadata alongside decimal coefficient fields. The [currency registry](https://raw.githubusercontent.com/RemyDuijkeren/NodaMoney/master/src/NodaMoney/CurrencyRegistry.cs) uses target-framework-specific lookup structures, including frozen dictionaries on newer .NET and synchronized replacement paths on older targets.

Entry points: `Money.cs` and `CurrencyRegistry.cs`. These are concrete layout and lookup optimizations; no numerical speedup is inferred without running a relevant workload.

### [py-moneyed/py-moneyed](https://github.com/py-moneyed/py-moneyed)

**Language/role:** Python; Decimal-backed money and currency domain objects.

Study a relatively focused library whose substance is in dimensional rules and interoperability rather than implementing another coefficient arithmetic engine.

- **C1:** The [class implementation](https://raw.githubusercontent.com/py-moneyed/py-moneyed/master/src/moneyed/classes.py) requires a currency, rejects addition across currencies and multiplication of two monetary values, and returns a dimensionless Decimal when dividing compatible money values. These are explicit domain invariants beyond decimal accuracy.
- **C2:** Currency metadata, formatting integration, cached currency-specific zero values, and subclass-preserving arithmetic support application and framework use. Money/scalar and Money/Money operations deliberately have different result types.

Entry point: `src/moneyed/classes.py`. Arithmetic ultimately follows Python Decimal behavior and its context; the wrapper does not make finite-context operations unconditionally exact. The repository's acknowledged earlier `python-money` lineage is not counted as another project.

### [gborough/safemoney](https://github.com/gborough/safemoney)

**Language/role:** OCaml; **explicitly experimental** monetary abstractions using integer discrete amounts and rational quantities.

Study a less common design that separates currency subunit scales, discrete amounts, rational quantities, and exchange operations. Its value here is the representation and abstraction experiment, not a production-readiness claim.

- **C1:** The [discrete amount implementation](https://raw.githubusercontent.com/gborough/safemoney/main/lib/discrete.ml) validates positive scale components, stores amounts with arbitrary-size integers, and checks scale compatibility during arithmetic. String-based serialized integer components avoid routing large values through binary floating-point numbers.
- **C2:** The repository documents `Discrete`, `Quotient`, scale construction, and exchange abstractions, supporting custom currencies and rational intermediate amounts rather than hard-coding two decimal places.

Entry point: `lib/discrete.ml`, alongside the repository's type and exchange examples. **Qualification:** the inspected dynamic operations can raise `ScaleTypeMismatch` at runtime; the README's type-safety language should not be read as a blanket compile-time proof for every public operation.

## Search coverage, exclusions, and limits

Discovery used more than six meaningfully different live query families: Go arbitrary-precision contexts and resource limits; Rust bounded versus arbitrary-size decimals; C/C++ IEEE decimal32/64/128; Java fixed-point arithmetic and JSR 354; JavaScript significant-digit arithmetic and bigint-backed money allocation; PHP/Ruby money and remainder distribution; Elixir process contexts; Haskell and OCaml monetary types; .NET money layouts; Python decimal/money libraries; and a final Kotlin/Swift multiplatform pass. Follow-up searches targeted rounding code, coefficient representations, source trees, tests, API guides, changelogs, and canonical repository locations.

Every retained repository's GitHub landing page was opened, and at least one additional primary source containing implementation or substantive API/design material was read. Source excerpts and documentation were inspected, rather than treating search snippets as verification. Later queries produced diminishing returns, chiefly platform adapters, narrower variants, and already-covered designs, although the final multiplatform pass added the Kotlin engine. The selection extends beyond 25 because these 27 include distinct arithmetic architectures and monetary domain layers across several language communities, not just alternative packages with the same surface API.

Important selection boundaries:

- Standalone upstream **mpdecimal** was not assigned an invented GitHub home. The search did not establish a qualifying canonical standalone GitHub repository; CPython's decimal subsystem is included on its own verified merits. Unofficial vendoring copies are not counted as independent engines.
- The currently opened [`k0001/safe-money`](https://github.com/k0001/safe-money) page did not expose the substantive historical Haskell library described by older references, so it was excluded. `fpco/safe-decimal` provides a separately verified Haskell entry.
- Small variants such as `big.js` and `decimal.js-light` were not needed to repeat already-covered JavaScript design space. Generic binary multiprecision libraries, currency-formatting-only packages, rate-API clients, tutorials, finance applications, and wrapper-only candidates were outside the retained selection.
- Distinct dependent projects such as `brick/math` and `brick/money` are retained because one implements numeric abstractions and the other substantial monetary policy. No upstream/fork pair is counted twice merely for shared code, and monorepos are counted once.

This was read-only source research: no candidate code was run, dependencies installed, performance reproduced, or complete correctness audit performed. Performance conclusions are limited to observed layouts, allocation paths, and algorithm structure. **C4** is awarded only where inspected dated history supports it; otherwise inclusion rests on the other criteria, not an inferred maintenance claim. Development branches, published API documentation, and historical changelogs can describe different versions, and relevant caveats appear in the entries. Mutable source links are useful navigation points but are not immutable audit snapshots. The shortlist is broad rather than exhaustive, especially for platform-specific Swift/Kotlin adapters and non-GitHub upstreams.
