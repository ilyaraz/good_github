# Physical units and dimensional analysis libraries

Research date: 2026-10-09.

This selection covers 25 GitHub repositories implementing physical quantities, unit conversion, dimensional arithmetic, or dimensionless-group construction. It spans compile-time checking, runtime representations and parsers, scientific arrays, application-facing APIs, and symbolic/numerical dimensional analysis. Astropy and Math.js are included specifically for their units subsystems; each larger repository counts once. The emphasis is on code an experienced engineer can study, rather than unit-catalog size or popularity.

Criteria used below:

- **C1 — Correctness:** difficult invariants, numerical semantics, invalid-input handling, or failure modes.
- **C2 — Abstractions:** substantial reusable models and extension mechanisms serving multiple use cases.
- **C3 — Performance:** concrete computational constraints addressed through an understandable design.
- **C4 — Evolution:** documented changes over multiple years together with compatibility, testing, or complexity management.

The criteria are evidence-grounded assessments of study value, not certifications of correctness. Performance discussions describe mechanisms; no benchmarks were independently run. A repository's inclusion does not imply current maintenance or production readiness. Version-specific and documented limitations are called out where material.

## Compile-time quantities and dimensional algebra

### 1. [mpusz/mp-units](https://github.com/mpusz/mp-units)

**C++ — quantity specifications, units, representations, and affine points.** Study how a library models distinctions beyond matching dimensional exponents.

- **C1:** Quantity specifications distinguish physical meanings that can share dimensions. Separately, `quantity_point` combines a quantity with an origin, allowing temperature readings and positions to follow affine-space rules. The design separates quantity character, dimension, reference, and numerical representation instead of making a unit tag carry every responsibility.
- **C2:** User-defined base dimensions, quantity equations, named/scaled units, numerical representations, and absolute or relative origins compose through a common framework. This is a substantial example of using concepts and non-type template parameters to build a domain model.

Entry point: the [design overview](https://mpusz.github.io/mp-units/latest/users_guide/framework_basics/design_overview/) explains the dependency graph and provides the actual template forms. The [quantity-point reference](https://mpusz.github.io/mp-units/latest/reference/api_reference/mrdocs/mp_units/quantity_point-08/) exposes its constrained operations. These are development-facing documentation; avoid assuming every described facility exists in older releases.

### 2. [aurora-opensource/au](https://github.com/aurora-opensource/au)

**C++ — physical quantities with explicit conversion-risk policies.** Especially useful for studying integer conversions and an API that makes numerical tradeoffs visible.

- **C1:** Conversions account for source representation, destination representation, and unit ratio. Au distinguishes overflow from truncation, exposes selective policy overrides, and supplies runtime checks for individual values. Its default compile-time policy is explicitly a risk heuristic: an allowed conversion can still overflow for some inputs.
- **C2:** Quantities, quantity points, magnitudes, unit composition, and customizable representations supply reusable building blocks. Runtime checking is deliberately separate from the application's error-handling choice.
- **C3:** The conversion design precomputes thresholds so individual-value overflow checks can reduce to comparisons, keeping the safety mechanism understandable.

Entry points: [conversion risks](https://aurora-opensource.github.io/au/main/discussion/concepts/conversion_risks/) and the [documentation map](https://aurora-opensource.github.io/au/main/). The latter also explains compile-time construction of combined conversion factors.

### 3. [boostorg/units](https://github.com/boostorg/units)

**C++ — Boost's generic dimensional-analysis module.** A useful contrasting design based on typelists, rational exponents, and template metaprogramming.

- **C1:** Equivalent dimension expressions must reduce to identical types regardless of ordering or repeated factors. The implementation orders fundamental dimensions and removes zero exponents; unique dimension ordinals are enforced through the base-dimension machinery.
- **C2:** Base-dimension tags, rational exponent pairs, and normalized composite dimensions form an extensible algebra. This is worth studying independently of the supplied SI catalog because applications can define their own dimensions and composite expressions.

Entry point: the [dimensional-analysis implementation explanation](https://www.boost.org/doc/libs/1_73_0/doc/html/boost_units/Dimensional_Analysis.html) develops the normalization invariant and shows `base_dimension`, `dim`, and `make_dimension_list`. This deliberately linked historical Boost 1.73 documentation explains the design; it is not a claim about the latest release's compiler requirements.

### 4. [nholthaus/units](https://github.com/nholthaus/units)

**C++ — header-only quantity types, conversions, and numerical integration.** Study how readable names survive a heavily templated implementation.

- **C1:** Conversion-aware deduction preserves an integral representation only where appropriate and promotes otherwise. Its internals also document an include-order failure involving specialization after instantiation, and the move to an ADL overload mechanism for resolving named conversion-factor types.
- **C2:** Named quantity classes derive from a common `unit` implementation, while a trait layer preserves their names through construction and arithmetic. The separation between representation, conversion factor, and scale supports extension without copying the numerical core.

Entry points: [named-type internals](https://github.com/nholthaus/units/blob/main/docs/explain/internals-named-types.md) and the [manual index](https://github.com/nholthaus/units/blob/main/docs/README.md). **Version caveat:** the inspected main branch documents C++23 and the 3.x design; the repository's short description still mentions C++14, which belongs to the older line.

### 5. [iliekturtles/uom](https://github.com/iliekturtles/uom)

**Rust — quantity types normalized to a selected system of base units.** Study the boundary between compile-time dimensional safety and representability of stored numbers.

- **C1:** Quantity arithmetic rejects dimension mismatches, but normalization introduces separate numerical constraints: an integer quantity stored in meters cannot represent a centimeter. The documentation explicitly discusses precision and storage limits instead of equating dimensional safety with numerical exactness.
- **C2:** `system!`, quantity definitions, alternate base-unit choices, storage-type features, and `no_std` support form a reusable framework rather than a fixed collection of structs.
- **C3:** Normalizing at boundaries removes repeated unit conversion from ordinary quantity arithmetic. The `autoconvert` feature documents a compiler/code-generation tradeoff for non-floating representations.

Entry points: the [design and feature documentation](https://docs.rs/uom/latest/uom/) and the [`system!` macro contract](https://docs.rs/uom/latest/uom/macro.system.html).

### 6. [paholg/dimensioned](https://github.com/paholg/dimensioned)

**Rust — type-level arrays of exponents and generated unit systems.** A compact way to study dimensional arithmetic before const-generic approaches.

- **C1:** A system type such as `SI<V, U>` separates its numerical value from a type-level exponent array. Addition requires matching types; multiplication combines values and adds the unit exponents. Correctness depends on preserving this correspondence through trait implementations.
- **C2:** `make_units!` generates a system type, derived-unit aliases, constants, formatting, and arithmetic traits. The library includes multiple systems and permits new ones, with numerical storage remaining generic.

Entry points: [how the representation works](https://docs.rs/dimensioned/latest/dimensioned/) and the detailed [`make_units!` guide](https://docs.rs/dimensioned/latest/dimensioned/macro.make_units.html). The latter explains the distinct treatment of floating and integer constants and optional formatting generation. The inspected published documentation is for 0.8.0; this report makes no release-cadence claim.

### 7. [Tehforsch/diman](https://github.com/Tehforsch/diman)

**Rust — const-generic dimensions and a procedural unit-system language.** Useful for comparing compiler-facing representations with `uom` and `dimensioned`.

- **C1:** `Quantity<S, D>` carries a structured dimension constant. Arithmetic changes that constant, dimensionless-only methods have restricted availability, and unit definitions may include an expected dimension to catch mistakes in definitions themselves.
- **C2:** The unit-system macro defines quantity and dimension types, base/derived dimensions, units, prefixes, aliases, and constants. Generated types belong to the consuming code's system, enabling custom methods and domains beyond the supplied SI system.

Entry points: the [quantity model and feature documentation](https://docs.rs/diman/latest/diman/) and [`unit_system!` reference](https://docs.rs/diman/latest/diman/macro.unit_system.html). **Limitation:** the inspected documentation requires unstable Rust features and warns that APIs may change. Its macro and crate pages were served from different published versions, so this is an architectural comparison, not a pinned compatibility guide.

### 8. [bjornbm/dimensional](https://github.com/bjornbm/dimensional)

**Haskell — statically checked physical dimensions using DataKinds and type families.** Study a dimensional numerical API with polymorphic number representations.

- **C1:** Dimension multiplication, division, powers, and roots are expressed at the type level; incompatible arithmetic fails during type checking. The API separately represents units and quantities, and conversion uses explicit multiplication/division by units.
- **C2:** The `Dimensional` data family, unit/quantity aliases, dimension operations, collections, numerical conversions, and extensible unit definitions form a general numerical layer. The seven SI base dimensions are the intended physical model, rather than arbitrary relativistic combinations.

Entry point: the extensive [module documentation](https://hackage-content.haskell.org/package/dimensional-1.6.2/docs/Numeric-Units-Dimensional.html), including type signatures and worked compiler failures. The repository is the DataKinds/type-family variant; older names and related dimensional-vector projects are not counted again. Compiler error readability remains a documented tradeoff.

## Runtime unit engines and interoperability

### 9. [LLNL/units](https://github.com/LLNL/units)

**C++ — runtime units, measurements, and textual conversion.** A useful comparison with template-heavy C++ libraries, particularly for units arriving through I/O.

- **C1:** Unit arithmetic includes exponent operations, special flags, invalid-root handling, and distinctions between full equality and base-dimension equivalence. These rules must remain consistent with parsing and conversion.
- **C2:** The library represents units independently from measurements and provides runtime string input/output, including engineering-oriented cases such as per-unit quantities.
- **C3:** The documented base representation packs exponents and flags into bitfields. This makes the size/range tradeoff visible rather than hiding it behind a generic container.

Entry points: the [user-guide overview](https://units.readthedocs.io/en/latest/) and [unit-base implementation details](https://units.readthedocs.io/en/latest/details/unit_base.html). **Limitation:** the latter documents restricted exponent ranges and special handling of square-root frequency, including an algebraic exception. Those details describe the documented representation, not universal exact symbolic algebra.

### 10. [Unidata/UDUNITS-2](https://github.com/Unidata/UDUNITS-2)

**C — unit systems, unit-expression parsing, and reusable converters.** Study a low-level API underlying scientific-data integrations.

- **C1:** Units belong to a particular unit system; conversions distinguish invalid arguments, different systems, and dimensionally meaningless requests. The API makes ownership and lifetime explicit for units, systems, and converters, and documents parsing failures and offset/logarithmic syntax.
- **C2:** Database loading, programmatic unit construction, identifier mappings, visitors, parsing, formatting, and conversion are separate operations over reusable objects.
- **C3:** A converter can be constructed once and applied to scalar values or arrays. The array functions explicitly permit overlapping or identical input/output storage, a concrete memory-management concern.

Entry point: the [C API guide](https://docs.unidata.ucar.edu/udunits/current/udunits2lib.html), especially unit-system ownership, conversion, and error handling. This is the official Unidata GitHub repository, rather than an independently counted language binding or unofficial mirror.

### 11. [LHNCBC/ucum-lhc](https://github.com/lhncbc/ucum-lhc)

**JavaScript — UCUM validation and conversion from the US National Library of Medicine.** Study the interface between formal unit syntax and messy application input.

- **C1:** Validation first consults known codes, then parses compound expressions, with separate invalid/error outcomes and optional corrections or suggestions. The changelog records concrete failures involving annotations, special-unit exponents, invalid-character loops, and substance-dependent conversions requiring charge information.
- **C2:** Validation, conversion to base units, commensurability queries, and suggested alternatives are distinct public operations. The source separates dimensions, units, prefixes, tables, and unit strings.
- **C4:** The inspected history spans at least 2020–2026 and records compatibility changes, API migrations, and added functional tests, including tests imported from the UCUM Java suite.

Entry points: the [source-module map](https://github.com/LHNCBC/ucum-lhc/tree/master/source) and [detailed changelog](https://github.com/LHNCBC/ucum-lhc/blob/master/CHANGELOG.md). The repository README supplies the validation pipeline and return-object contracts.

## Scientific arrays and dynamic numerical computing

### 12. [hgrecco/pint](https://github.com/hgrecco/pint)

**Python — configurable unit registries and quantities over multiple numerical types.** Study how runtime definitions and numerical protocols meet nontrivial unit semantics.

- **C1:** Offset temperatures and temperature differences have different arithmetic rules. Pint creates delta counterparts and rejects ambiguous operations by default; a registry option changes conversion behavior explicitly.
- **C2:** A `UnitRegistry` owns definitions, parsing, and quantity construction, while magnitudes can use ordinary numbers, Decimal/Fraction, or NumPy arrays. Unit definitions live outside the numerical implementation.
- **C4:** The changelog documents 2020–2025 evolution in array protocols, pickle compatibility, automatic documentation tests, benchmarks, and compatibility refactoring. It also records fixes for unintended operand mutation and NaN conversion behavior.

Entry points: [temperature-conversion semantics](https://pint.readthedocs.io/en/stable/user/nonmult.html) and [CHANGES](https://github.com/hgrecco/pint/blob/master/CHANGES). These provide stronger evidence than the README's broad test-coverage claim, which is not treated here as independently verified coverage.

### 13. [yt-project/unyt](https://github.com/yt-project/unyt)

**Python — NumPy array subclasses with unit objects and configurable unit systems.** Study unit metadata propagation in bulk scientific calculations.

- **C1:** Arithmetic rejects incompatible dimensions, while electromagnetic conversion documents the boundary between simple CGS/MKS conversions and compound expressions requiring physical context. Temperature differences and unit simplification have their own rules.
- **C2:** Unit objects, scalar quantities, arrays, function-contract decorators, and customizable base/derived unit systems support reuse beyond a fixed astronomy catalog.
- **C3:** The API distinguishes copying conversions from explicit in-place conversions for large arrays and notes overhead from dimensional decorators on small arrays.

Entry point: the substantive [usage and unit-system guide](https://unyt.readthedocs.io/en/stable/usage.html). **Semantic caveat:** the guide permits some logarithmic/transcendental operations by discarding input units; users should inspect those rules rather than assume uniformly strict dimensional rejection.

### 14. [astropy/astropy](https://github.com/astropy/astropy)

**Python — specifically the `astropy.units` subsystem.** Study how a unit-aware array type integrates with a larger numerical ecosystem.

- **C1:** Dimensionless quantities may still have scale, so interaction with scalars requires simplification. Dtype selection and integer-to-float promotion also affect correctness during conversion. Subclassing hooks propagate units and choose result subclasses when operations change physical type.
- **C2:** `Quantity` extends `numpy.ndarray` and can participate in functions, vectors, and table columns. Its subclass protocol supports specialized types such as angles without forcing every result to retain an inappropriate subclass.
- **C3:** `copy=False` and the shift operators support views and in-place conversion; the documentation demonstrates shared-memory consequences rather than treating copy avoidance as an invisible optimization.

Entry point: the [Quantity guide](https://docs.astropy.org/en/stable/units/quantity.html), especially NumPy integration, dimensionless quantities, copy behavior, and subclassing. The rest of Astropy is outside this entry's assessment.

### 15. [python-quantities/python-quantities](https://github.com/python-quantities/python-quantities)

**Python — NumPy-compatible quantities, compound units, and uncertainties.** Useful for comparing explicit simplification and mutation policies with Pint and unyt.

- **C1:** A failed dimensional conversion leaves the original quantity unchanged, and unit definitions themselves are protected from in-place modification. Uncertainty arithmetic explicitly assumes uncorrelated inputs, making repeated-variable expressions a correctness concern.
- **C2:** Quantities, custom `UnitQuantity` definitions, preserved `CompoundUnit` expressions, configurable simplification systems, and `UncertainQuantity` offer reusable numerical abstractions.

Entry point: the [detailed tutorial](https://python-quantities.readthedocs.io/en/latest/user/tutorial.html). **Limitations:** temperatures are treated as differences, not absolute affine readings; the documentation explicitly says that Celsius-to-Kelvin conversion does not add an offset. The same guide contains a warning about incomplete test coverage and production use. Inclusion reflects implementation-study value, not a production endorsement.

### 16. [JuliaPhysics/Unitful.jl](https://github.com/JuliaPhysics/Unitful.jl)

**Julia — units and dimensions encoded in quantity type parameters.** Study how dispatch and staged computation can share a dimensional model.

- **C1:** Unit objects retain rational exponents, prefixes, and an affine translation parameter. Dimensionless quantities can still carry scaled units, so dimensionlessness does not erase every conversion obligation.
- **C2:** `Quantity{T,D,U}` separates numerical backing, dimensions, and units. `FreeUnits`, `ContextUnits`, and `FixedUnits` implement different promotion policies, including contextual preferences and disabling automatic conversion.
- **C3:** Encoding units in types permits staged functions to move unit computations to compilation while preserving dispatch on physical dimensions. This advantage depends on the compiler being able to infer the involved types.

Entry point: the [types and representation guide](https://juliaphysics.github.io/Unitful.jl/stable/types/). The design is particularly informative beside DynamicQuantities, which makes a different choice about where dimensions live.

### 17. [JuliaPhysics/DynamicQuantities.jl](https://github.com/JuliaPhysics/DynamicQuantities.jl)

**Julia — quantity types with dimensions stored as values.** Study an alternative suited to calculations whose resulting dimensions vary dynamically.

- **C1:** Runtime dimensional checks accompany arithmetic and unit stripping. Symbolic units can preserve the user's expression before expansion into base units, separating representation choices from dimensional validity.
- **C2:** Quantities, dimension accessors, symbolic units, array facilities, and conversion to/from Unitful support several computational styles. The API also exposes fixed-rational dimension machinery.
- **C3:** Keeping dimensions out of type parameters avoids repeated specialization and type instability when dimensions cannot be inferred. The README includes both dynamic and statically inferable examples, explicitly showing that Unitful can benefit when static inference succeeds.

Entry point: the [API documentation source](https://github.com/JuliaPhysics/DynamicQuantities.jl/blob/main/docs/src/api.md), alongside the architectural explanation in the repository README. Some rendered documentation pages were unavailable during research; the numerical speed ratios in the README were not adopted as general performance claims.

### 18. [r-quantities/units](https://github.com/r-quantities/units)

**R with native integration — unit metadata propagated through vectors, arrays, and data frames.** This is a substantial R semantic layer over UDUNITS, not merely a generated conversion wrapper.

- **C1:** Addition, comparison, concatenation, and summary operations must convert compatible inputs consistently; products and powers derive new units. The documented rule of converting to the first argument's unit makes result-unit selection explicit.
- **C2:** `Ops`, `Math`, and `Summary` method groups integrate units with ordinary R calculations, while date/time conversion and data-frame columns preserve them through common analytical workflows. User-defined and compound units extend the model.

Entry point: the [measurement-units vignette](https://github.com/r-quantities/units/blob/main/vignettes/measurement_units_in_R.Rmd), including method-group behavior and integration limits. A unit-bearing matrix/array has one shared unit for its elements; this is not a model for arbitrary heterogeneous-dimensional matrices.

## Application APIs and object models

### 19. [unitsofmeasurement/indriya](https://github.com/unitsofmeasurement/indriya)

**Java — reference implementation of JSR 385.** Study an implementation beneath a standardized quantity/unit interface.

- **C1:** The unit abstraction documents symmetry of physical conversions and compatibility according to a dimensional model. System units and converters are explicit concepts, with different failure conditions for incommensurable or unconvertible requests.
- **C2:** Product, transformed, alternate, and annotated units fit a shared `Unit` implementation. Formatting/parsing and numerical converter operations are separate collaborators, allowing composition rather than a table of pairwise conversion methods.

Entry point: [`AbstractUnit.java`](https://github.com/unitsofmeasurement/indriya/blob/master/src/main/java/tech/units/indriya/AbstractUnit.java), whose implementation and documentation expose the unit hierarchy, compatibility methods, and converter relationships. The repository identifies Java 8 as its baseline and a separate Java 11 requirement for JPMS use; those requirements should be checked against the chosen release.

### 20. [angularsen/UnitsNet](https://github.com/angularsen/UnitsNet)

**C# — typed quantities generated from shared quantity/unit definitions.** Study the engineering of a large API whose catalog, conversions, and localization must evolve together.

- **C1:** Definitions distinguish dimensional exponents from the intermediate conversion unit. Forward and reverse expressions must be inverses; affine and logarithmic arithmetic models have separate schema rules. The schema warns that permissive deserialization leaves some mistakes to compilation or testing.
- **C2:** JSON definitions drive quantity types, enums, conversion expressions, abbreviations, and optional generation behavior. This makes catalog expansion and customized generation part of the architecture rather than handwritten duplication.

Entry point: the [quantity and unit definition schema](https://github.com/angularsen/UnitsNet/blob/master/Docs/quantity-and-unit-definition-schema.md). **Version caveat:** the inspected README labels master as v6 prerelease and describes backports to the v5 maintenance branch. Generated quantities are part of this substantive implementation; separate generated ports are not counted as additional projects.

### 21. [typelevel/squants](https://github.com/typelevel/squants)

**Scala — quantity classes and a dimensional domain-specific language.** Study an application-oriented object model with unit-aware equality, ordering, and ranges.

- **C1:** The common quantity implementation converts operands before addition, comparison, and equality. Hashing normalizes through a dimension's primary unit, making equality/hash consistency across units an explicit implementation concern. Approximate equality uses a quantity-valued tolerance.
- **C2:** `Quantity[A]`, `UnitOfMeasure[A]`, `Dimension[A]`, and `QuantityRange[A]` share conversion and numerical behavior across domain-specific quantities. The self-type/generic pattern constrains same-quantity operations without requiring callers to manipulate exponent vectors.

Entry point: the verified [`Quantity.scala` source](https://raw.githubusercontent.com/typelevel/squants/master/shared/src/main/scala/squants/Quantity.scala). Its conversion, rounding, equality, hashing, and range methods provide a focused reading path; the larger README documents the surrounding dimensional DSL.

### 22. [josdejong/mathjs](https://github.com/josdejong/mathjs)

**JavaScript — specifically Math.js's `Unit` datatype and unit arithmetic.** Study integration of units into an expression evaluator and general mathematics API.

- **C1:** Unit-string parsing has its own precedence rules, distinct from the general expression parser. The documentation demonstrates how implicit multiplication can change a denominator, and discusses surprising behavior of offset temperature scales in arithmetic.
- **C2:** Unit values, valueless units, custom base/derived units, prefixes, aliases, offsets, and named dimensions participate in ordinary mathematical and array operations. This offers a reusable extension surface beyond simple scalar conversion.

Entry point: the [units datatype guide](https://mathjs.org/docs/datatypes/units.html). Study parser boundaries and custom-unit registration together; neither syntactic acceptance nor successful conversion alone guarantees that an offset-temperature calculation expresses the intended physics. The broader Math.js repository is counted once, solely for this subsystem.

### 23. [gentooboontoo/js-quantities](https://github.com/gentooboontoo/js-quantities)

**JavaScript — standalone quantities, parsing, conversion, and batch converters.** Originally a Ruby Units port, it has a separate JavaScript implementation and release history.

- **C1:** Compatibility checks, unit-preserving arithmetic, precision rounding, and parsing failures have distinct APIs. The history records fixes for unreasonable exponents causing allocation failure, regex loops, inconsistent product units, and conversion rounding.
- **C2:** The `Qty` abstraction supports composition, inverse quantities, formatted output, aliases, and reusable `swiftConverter` functions for values or arrays.
- **C4:** The inspected changelog spans 2013–2023 and documents deprecation compatibility, conversion-cache changes, parser fixes, and array conversion support. The README also describes Jasmine tests and a performance-regression harness.

Entry point: the [changelog](https://github.com/gentooboontoo/js-quantities/blob/master/CHANGELOG.md), read with the README's conversion API. Its inspected release history ends at 1.8.0 in 2023; no active-maintenance claim is made. `swiftConverter` explicitly trades away rounding handling.

### 24. [olbrich/ruby-units](https://github.com/olbrich/ruby-units)

**Ruby — parsed quantities, extensible definitions, and numerical/time integration.** Study a dynamic object model where definition updates interact with parsing caches.

- **C1:** The implementation distinguishes absolute temperatures from differential degrees, rejects adding two absolute temperatures, and handles their subtraction differently. Unit parsing prefers longer names, with explicit invalidation of memoized regexes when definitions change.
- **C2:** Definition registration separates unit and prefix metadata; unit objects combine numerical values with numerator/denominator structure. The wider API integrates formatting and time/date arithmetic, giving the core conversion model multiple consumers.

Entry points: [`lib/ruby_units/unit.rb`](https://github.com/olbrich/ruby-units/blob/master/lib/ruby_units/unit.rb) and the [historical changelog](https://github.com/olbrich/ruby-units/blob/master/CHANGELOG.txt). The latter records cached-definition redefinition fixes and Ruby/test-harness migrations. The README acknowledges allocation costs and prioritizes accurate general conversion over raw arithmetic throughput.

## Constructing dimensionless groups

### 25. [saadgroup/BuckinghamPy](https://github.com/saadgroup/BuckinghamPy)

**Python — reusable Buckingham Pi analysis with symbolic output.** A smaller scientific codebase that adds a distinct problem: discovering dimensionless groups from variables rather than attaching units to numbers.

- **C1:** The implementation parses dimensional expressions, constructs an exponent matrix, rejects singular repeating-variable selections, calculates null spaces, and reconstructs symbolic Pi terms. The inspected implementation uses floating-point determinant/SVD calculations followed by rational approximation, making tolerance and reconstruction behavior important correctness topics.
- **C2:** Variables, dimensional expressions, an optional non-repeating variable, existing dimensionless terms, and returned Pi-term sets form a reusable analysis API independent of its notebook GUI.
- **C3:** The code limits processed selections and deduplicates Pi sets using canonical keys invariant to term order and inversion, replacing permutation-style comparison.

Entry point: [`buckinghampi.py`](https://github.com/saadgroup/BuckinghamPy/blob/master/buckinghampy/buckinghampi.py). **Limitations:** the default selection cap means output is not exhaustive. The code materializes combinations before slicing, so the cap does not bound combination-generation memory. This is a numerical-design case study, not an exact-algebra guarantee.

## Coverage and search notes

Live web discovery used more than six distinct formulations, including C++ compile-time units; Rust `uom`/const generics; Python physical quantities; Julia static versus dynamic dimensions; Java/.NET/Scala measurement APIs; Haskell/R/Ruby libraries; JavaScript quantity conversion; UCUM parsers; and Buckingham Pi/nondimensionalization. Follow-up searches examined runtime-versus-compile-time alternatives and less common Go, Elm, and Idris approaches. Later broad searches mostly returned already represented architectures; the UCUM and Buckingham searches produced the two distinct additions above.

Every retained repository's GitHub page was opened to verify its owner/path. At least one additional primary documentation, implementation, or change-history page was opened and read for each entry; substantive architectural material was inspected either there or in the repository's detailed README. GitHub file viewers sometimes required targeted searches within the opened file to reach implementation text. Unavailable rendered pages were replaced with accessible primary material where possible. DynamicQuantities' rendered documentation remained partly unavailable, so its README and checked-in API documentation are the evidence used here.

The selection spans twelve implementation-language ecosystems and several scales, from BuckinghamPy's focused algorithm to the Astropy and Math.js subsystems. R `units` is retained alongside UDUNITS because its vector semantics and method integration are substantive independent work. JS-quantities is retained alongside Ruby Units because it is a separately evolved language port, not a repository fork counted twice.

Excluded were awesome-lists and comparison indexes as final entries, unit tables without substantial library behavior, tutorial/example collections, unrelated pulsar-timing PINT results, and generated UnitsNet ports. Duplicate mp-units repository identities were not counted separately. Whole languages or compiler-native units features were outside the library scope. GNU Units was not added through an unofficial GitHub mirror; this report does not attempt exhaustive coverage of software hosted elsewhere. Additional small C++ and research prototypes were discovered but not pursued once their architecture overlapped the verified selections.

No candidate code was cloned, installed, or executed. C4 is assigned only where inspected change records establish multi-year evolution with concrete compatibility or testing work. Other entries may also have long histories, but age, commit totals, and stars were not used to infer that criterion. This report is a selection guide: the stated limitations and design tradeoffs are part of why these repositories are useful to study.
