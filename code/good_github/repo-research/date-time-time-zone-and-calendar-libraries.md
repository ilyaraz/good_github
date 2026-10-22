# Date, time, time zone, and calendar libraries

Research date: **2026-10-09**.

This report selects **26 GitHub repositories** for studying date/time representations, time-zone conversion, calendrical arithmetic, recurrence, business calendars, and scientific time. It includes standalone libraries and explicitly identified subsystems of larger repositories. The emphasis is on implementation decisions an experienced engineer can inspect, rather than popularity or a recommendation to adopt every project. Criterion judgments are grounded engineering assessments of the linked material; they are not certifications of correctness or uniform code quality.

**Criteria legend**

- **C1 — Difficult correctness:** invariants, numerical semantics, ambiguous inputs, concurrency, or failure handling.
- **C2 — Reusable abstractions:** substantial representations and interfaces supporting multiple applications.
- **C3 — Performance with structure:** concrete resource or execution constraints addressed through understandable architectural choices.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility work, tests, or explicit complexity management.

The links within each entry are reading entry points as well as evidence. Source links reflect the branches inspected; development branches can differ from published packages.

## Time-zone engines and data infrastructure

### 1. [eggert/tz](https://github.com/eggert/tz)

**C; IANA time-zone code and database.** Study the boundary between historical rule data, compiled TZif files, and a portable C runtime. This is the development repository identified by [IANA's acquisition documentation](https://data.iana.org/time-zones/tz-link.html), rather than an unrelated data mirror. IANA cautions that untagged development commits receive less testing than releases.

- **C1:** The runtime validates TZif count fields and block lengths before decoding, handles both timestamp widths, and explicitly accommodates transitions outside the host's `time_t` range. These are concrete malformed-input and numerical-boundary problems. Start with [`localtime.c`, especially `tzloadbody`](https://raw.githubusercontent.com/eggert/tz/main/localtime.c).
- **C4:** The [NEWS history](https://raw.githubusercontent.com/eggert/tz/main/NEWS) connects fixes for post-2037/2038 conversion failures in 2015 with later POSIX/C portability changes and compatibility links in subsequent releases. It demonstrates continuing management of code, data, and downstream compatibility, not merely an old repository date.

### 2. [google/cctz](https://github.com/google/cctz)

**C++; civil-time arithmetic and time-zone conversion alongside `std::chrono`.** This is a particularly focused study of how separating concepts can simplify an API: absolute time belongs to `chrono`, civil fields to one library, and geographical zone rules to another.

- **C1:** Local-to-absolute conversion produces `UNIQUE`, `SKIPPED`, or `REPEATED`, with pre-transition, transition, and post-transition answers. The convenience conversion additionally documents an ordering-preservation guarantee. The definitions and worked DST examples are in [`time_zone.h`](https://github.com/google/cctz/blob/master/include/cctz/time_zone.h).
- **C2:** The [repository's architectural overview](https://github.com/google/cctz#overview) explains two cooperating libraries, rather than one overloaded timestamp object. Civil dates and months can be manipulated without selecting a zone; zone conversion composes with existing `chrono::time_point` types.

### 3. [bxparks/AceTime](https://github.com/bxparks/AceTime)

**C++; Arduino and resource-constrained time-zone calculations.** Study how a time-zone implementation changes when allocation and memory budgets are design inputs, and when applications may include only selected zone data.

- **C3:** The [design discussion](https://github.com/bxparks/AceTime#motivation-and-design-considerations) states that the C++ classes avoid heap allocation, use small value objects, and concentrate complicated memory handling in the `ZoneProcessor` hierarchy. This is a concrete architecture for constrained targets, not an unsupported speed claim.
- **C2:** The [user guide](https://github.com/bxparks/AceTime/blob/develop/USER_GUIDE.md) separates `TimeZone`, generated `ZoneInfo`, processors of different capabilities, and `ZoneManager` caches. Applications can manage processors explicitly or through a manager.
- **C1:** That same guide exposes disambiguation when converting local fields and documents representable-date and generated-database limits. Basic, extended, and complete processors have different coverage; they should not be treated as interchangeable implementations with identical limits.

### 4. [tzinfo/tzinfo](https://github.com/tzinfo/tzinfo)

**Ruby; IANA zone lookup and conversion.** Study how to isolate the source of zone data from interval lookup and local-time ambiguity.

- **C1:** [`TransitionsDataTimezoneInfo`](https://raw.githubusercontent.com/tzinfo/tzinfo/master/lib/tzinfo/data_sources/transitions_data_timezone_info.rb) requires ordered transitions, distinguishes timestamps with and without known offsets, and searches all applicable periods for a local timestamp. Boundary comparisons deliberately account for fractional seconds without rounding them away.
- **C2:** The [repository documentation](https://github.com/tzinfo/tzinfo) describes Ruby-module data and system zoneinfo data sources, while exposing common `Timezone` conversion and period interfaces. This supports applications with different deployment environments.
- **C3:** The transition implementation uses binary search to locate a relevant region, then bounds the local-time candidate search. It also contains a fallback implementation for Ruby versions lacking the corresponding array search operation.

### 5. [JuliaTime/TimeZones.jl](https://github.com/JuliaTime/TimeZones.jl)

**Julia; time-zone-aware extensions to Julia's date types.** Study how an additional temporal type can integrate with an existing language-level date/period model while preserving zone invariants.

- **C1:** The [type guide](https://juliatime.github.io/TimeZones.jl/stable/types/) documents errors for nonexistent and ambiguous local times, occurrence selection for repeated times, and the requirement that `ZonedDateTime` remain in the correct zone without manual normalization. It also explains limits of precomputed future transitions.
- **C2:** `TimeZone` has separate fixed-offset and variable-transition implementations, while `ZonedDateTime` participates in period arithmetic and date-format parsing. The [repository overview](https://github.com/JuliaTime/TimeZones.jl) also identifies TZif reading as a supported input route. The abstraction is broader than a table of current UTC offsets.

## Temporal type systems and general-purpose arithmetic

### 6. [HowardHinnant/date](https://github.com/HowardHinnant/date)

**C++; calendar and time-zone libraries built on `chrono`.** Study the connection between field-based dates, serial day counts, typed durations, and clock/zone conversion. The repository also identifies the relationship of its date and zone facilities to C++20 standardization.

- **C2:** The [date design and reference](https://howardhinnant.github.io/date/date.html) describes interoperable field and time-point types rather than replacing `chrono`. The repository adds ISO-week, Julian, and Islamic calendar libraries using that foundation.
- **C1:** The [time-zone reference](https://howardhinnant.github.io/date/tz.html) explicitly models unique, nonexistent, and ambiguous local times through `local_info`, and separates local from system time. It also covers leap-second-aware clocks and their conversions.
- **C3:** The date documentation explains how improved C++14 `constexpr` support moves computations from runtime to compile time while retaining a C++11 mode. This makes the portability/performance tradeoff inspectable.

### 7. [nodatime/nodatime](https://github.com/nodatime/nodatime)

**C#; a semantic date/time API for .NET.** Study how distinct types encode distinctions that a single general-purpose date object tends to obscure.

- **C2:** The [core-concepts guide](https://nodatime.org/3.2.x/userguide/concepts) separates `Instant`, calendar-dependent local dates, local times, offsets, and `DateTimeZone`. Calendar identity is part of the model rather than just a formatting option.
- **C1:** [`DateTimeZone.MapLocal` and `AtStartOfDay`](https://raw.githubusercontent.com/nodatime/nodatime/main/src/NodaTime/DateTimeZone.cs) reveal the implementation behind zero/one/two-result local mappings. Start-of-day conversion handles missing midnight and detects an entirely skipped date. Caller-supplied resolvers make ambiguity policy explicit without duplicating the mapping algorithm.

### 8. [JodaOrg/joda-time](https://github.com/JodaOrg/joda-time)

**Java; historical date/time API with multiple chronologies.** This is an architectural and compatibility study choice. The [repository explicitly says](https://github.com/JodaOrg/joda-time) development is limited principally to keeping zone data current and asks Java 8+ users to migrate to `java.time`; it is not presented here as a new-development default.

- **C2:** The [chronology design](https://www.joda.org/joda-time/key_chronology.html) splits calculations between `Chronology`, `DateTimeField`, and `DurationField`, applying time zones through a decorator. This is a substantial reusable model for multiple calendar systems.
- **C3:** The same design document explains why chronology, field, and zone implementations are maintained as singletons: setup costs are shared, while ordinary API values bear most subsequent allocation/garbage-collection costs. It is useful for examining the cost of an object-oriented temporal abstraction.

### 9. [MenoData/Time4J](https://github.com/MenoData/Time4J)

**Java; civil, historical, multi-calendar, and scientific temporal calculations.** Study a broader problem domain than ISO business dates, including leap seconds and calendar-specific chronology rules. The [release page](https://github.com/MenoData/Time4J/releases) lists v5.9.4; the older version mentioned in the README should not be mistaken for the latest release.

- **C1:** [`TimeScale`](https://raw.githubusercontent.com/MenoData/Time4J/master/base/src/main/java/net/time4j/scale/TimeScale.java) defines different POSIX and UTC semantics, including how leap seconds map to POSIX values and how earlier timestamps are interpreted. It also describes limitations of conversions between scales.
- **C2:** [`Chronology`](https://raw.githubusercontent.com/MenoData/Time4J/master/base/src/main/java/net/time4j/engine/Chronology.java) binds a temporal type to element rules, a merger, and optional extensions. The immutable rule collections and specialized integer-rule lookup provide an implementation-level entry into the extensible calendar engine.

### 10. [Kotlin/kotlinx-datetime](https://github.com/Kotlin/kotlinx-datetime)

**Kotlin; multiplatform date/time API.** Study a deliberately restricted ISO-oriented API and the work needed to keep its behavior coherent across platforms and evolving standard-library types.

- **C2:** The [design overview](https://github.com/Kotlin/kotlinx-datetime#design-overview) distinguishes physical instants from local civil fields. Calendar-based adjustments to instants require an explicit zone, and separate date, time, period, and unit types give this policy a reusable API shape.
- **C1:** The [changelog](https://github.com/Kotlin/kotlinx-datetime/blob/master/CHANGELOG.md) records unified admissible date ranges across platforms, a Darwin fallback when zone files are unavailable, and Windows behavior when DST transitions are disabled. These expose real cross-platform failure modes.
- **Compatibility evidence:** The same changelog documents migration aliases for `Instant`/`Clock` and restoration of JVM binary compatibility. These are specific evolution examples; no maintenance-duration claim is needed to qualify this entry.

### 11. [chronotope/chrono](https://github.com/chronotope/chrono)

**Rust; general-purpose Gregorian dates and times.** Study an established model built around timezone-parameterized values and explicit conversion outcomes. Its limitations are part of its educational value: the README distinguishes leap-second representation from complete leap-second support.

- **C1:** The [`LocalResult` reference](https://docs.rs/chrono/latest/chrono/offset/enum.LocalResult.html) specifies unique, ambiguous, and nonexistent mappings. It also states that a missing result can reflect unavailable zone data, an OS error, or overflow, and describes where unwrapping may panic.
- **C2:** Those mapping results support operations such as choosing an occurrence or mapping the contained values, while the [repository](https://github.com/chronotope/chrono) documents allocation, standard-library, clock, serialization, and arbitrary-value features. Engineers can examine how a core temporal model integrates with different runtime and serialization environments without assuming every deployment has the same facilities.

### 12. [BurntSushi/jiff](https://github.com/BurntSushi/jiff)

**Rust; zoned date/time arithmetic inspired by Temporal.** Study the API consequences of treating zone-aware calendar arithmetic as a central operation.

- **C1:** The [design rationale](https://raw.githubusercontent.com/BurntSushi/jiff/master/DESIGN.md) explains why adding a day to a zoned datetime is not interchangeable with adding a fixed number of hours. `Span` retains individual calendar units so arithmetic can apply the zone's rules.
- **C2:** That rationale also separates `Span` from `SignedDuration` and abstracts system versus bundled zone-data discovery behind the same public interface. These support calendar calculations, elapsed-time calculations, and cross-platform deployment without conflating their semantics.
- **C3:** The author explicitly describes the greater storage/computation cost of a field-based span and the lighter fixed-duration alternative. This is a documented design tradeoff, not a benchmark ranking.

### 13. [js-temporal/temporal-polyfill](https://github.com/js-temporal/temporal-polyfill)

**TypeScript/JavaScript; implementation of Temporal's date/time model.** Study specification-oriented API implementation and the complexity of preserving calendar and zone identity. The README documents its origin in the proposal polyfill and its separate migration/release work; the proposal repository is not counted again here.

- **C1:** [`zoneddatetime.ts`](https://raw.githubusercontent.com/js-temporal/temporal-polyfill/main/lib/zoneddatetime.ts) handles offset preference during rounding, DST disambiguation, calendar compatibility in localized formatting, and zone transitions. These operations require more state than an epoch timestamp alone.
- **C2:** The implementation separates instant, plain date/time, and zoned representations, with explicit conversion methods and internal abstract operations. The [repository documentation](https://github.com/js-temporal/temporal-polyfill) describes the package boundary and migration from 0.4 to 0.5. This is a substantial implementation, not a generated wrapper; the report makes no independent claim about the current standards-stage wording in its README.

## Application-facing date/time libraries

### 14. [date-fns/date-fns](https://github.com/date-fns/date-fns)

**TypeScript; functional date utilities, with related zone/UTC packages in the current monorepo.** Study how reusable functions can work with JavaScript's existing date representation while compensating for its surprising arithmetic.

- **C1:** [`addMonths`](https://raw.githubusercontent.com/date-fns/date-fns/main/pkgs/core/src/addMonths/index.ts) explicitly clamps month ends, makes a zero-month operation a no-op to avoid a DST disturbance, and preserves the original time when the target month's last day has a transition. The comments explain why simpler setter-based implementations fail.
- **C2:** The [repository](https://github.com/date-fns/date-fns) describes pure functions, independent imports, locales, and typed date inputs. `addMonths` additionally shows construction/context hooks for date subtypes. These are reusable composition mechanisms rather than a single application-specific date helper.

The verified current path is under `pkgs/core/src`; older `src/...` source links no longer identify this file on `main`. The monorepo is counted once.

### 15. [moment/luxon](https://github.com/moment/luxon)

**JavaScript; immutable datetime, duration, and interval API using native internationalization.** Study the tradeoff between delegating zone/locale data to the host and providing explicit higher-level arithmetic semantics.

- **C1:** The [math guide](https://raw.githubusercontent.com/moment/luxon/master/docs/math.md) distinguishes calendar-unit adjustment from epoch-millisecond arithmetic, explains why a day and 24 hours diverge across DST, and describes multi-unit ordering. It also explicitly excludes leap-second support.
- **C2:** The [repository overview](https://github.com/moment/luxon) identifies immutable `DateTime`, `Duration`, and `Interval` types with parsing, formatting, and native `Intl`/zone support. The arithmetic guide explains the internal conceptual split behind those interfaces, making this a useful study of a compact application-facing model.

### 16. [CarbonPHP/carbon](https://github.com/CarbonPHP/carbon)

**PHP; extended mutable/immutable date APIs, intervals, and calendar arithmetic.** Study how a broad library adds policies around a language's existing date classes. The [repository migration notice](https://github.com/CarbonPHP/carbon) identifies this destination and says the old `briannesbitt/Carbon` repository is also kept synchronized. They are one project and are counted once.

- **C1:** [`Traits/Units.php`](https://raw.githubusercontent.com/CarbonPHP/carbon/master/src/Carbon/Traits/Units.php) implements month/year overflow policy, original-day preservation, weekday arithmetic with configurable weekends, and different mutation behavior for mutable and immutable values. These policies materially affect recurring-date calculations.
- **C2:** The same source accepts ordinary units, intervals, converter objects, and closures through a shared arithmetic surface. Its dispatch and trait organization provide more substantive study material than a thin `DateTime` alias, while the repository demonstrates broader formatting, comparison, and clock-control use cases.

### 17. [bitwalker/timex](https://github.com/bitwalker/timex)

**Elixir; date/time manipulation and timezone support on the BEAM.** Study protocol-based interoperability and a library's accommodation of temporal types added to its language's standard library. The README explains its delegation to Elixir's Calendar APIs where possible.

- **C1:** The [`AmbiguousDateTime` guide](https://timex.hexdocs.pm/Timex.AmbiguousDateTime.html) distinguishes gaps from overlaps and documents the `before`/`after` alternatives for repeated local times, including historical transitions beyond ordinary modern DST.
- **C2:** [`Timex.Protocol`](https://raw.githubusercontent.com/bitwalker/timex/main/lib/protocol.ex) defines common conversion and shifting operations for dates, naive datetimes, and datetimes, including Erlang tuple representations. Ambiguous results remain part of the return contract rather than being erased by the abstraction.

## Vectorized and scientific time

### 18. [r-lib/clock](https://github.com/r-lib/clock)

**R/C++; vector-oriented calendar and date/time manipulation.** Study how explicit invalid-value policy can be reconciled with R's vectors and existing date classes. Although it builds on Hinnant's C++ date library, its vector types and resolution policies constitute substantial independent API work.

- **C1:** The [motivation/design vignette](https://clock.r-lib.org/articles/motivations.html) works through invalid month days, nonexistent times, and ambiguous times. It distinguishes rolling to a valid moment from preserving time-of-day, showing why the latter can reorder a sorted input vector.
- **C2:** The [repository](https://github.com/r-lib/clock) describes a high-level API for `Date`/`POSIXct` and a separate family of durations, time points, zoned times, and calendars built using R record types. The vignette explains named resolution policies and strict mode, so callers can make assumptions explicit without reimplementing the algorithms.

### 19. [astropy/astropy](https://github.com/astropy/astropy)

**Python with numerical-library support; specifically the `astropy.time` subsystem.** The whole astronomy monorepo is counted once. Study scientific time where representation precision and physical time scales matter as much as civil calendars.

- **C1:** The [`astropy.time` guide](https://docs.astropy.org/en/stable/time/index.html) describes a two-part floating-point Julian-date representation and compensated arithmetic. It also explains why subtracting UTC times produces a TAI-based delta: leap seconds prevent a universal fixed-length UTC day.
- **C2:** `Time` and `TimeDelta` separate output formats from time scales and support scalar/array operations and unit-aware quantities.
- **C3:** The guide's caching section explains that scale/format transformations can be expensive for arrays. Results are cached, relevant setting changes invalidate caches, and transformed cached objects are made non-writeable to preserve consistency. Study that mechanism rather than treating the documentation's example timings as universal performance measurements.

## Calendar systems, historical dates, and holidays

### 20. [unicode-org/icu4x](https://github.com/unicode-org/icu4x)

**Rust; specifically calendar, calendrical-calculation, and date/time-formatting components.** This internationalization monorepo is counted once. Study how diverse calendar semantics fit behind a common date interface without pretending all calendars share ISO's fields and eras.

- **C1:** The [`Calendar` implementation contract](https://raw.githubusercontent.com/unicode-org/icu4x/main/components/calendar/src/calendar.rs) includes calendar-compatibility requirements before comparing internal dates, range guarantees for Rata Die conversion, and validation of eras, months, and days.
- **C2:** That contract separates calendar-specific internal representations from common date construction, arithmetic, and conversion operations. It is currently sealed/unstable for external implementations, a relevant limitation when studying extensibility.
- **C4:** The [changelog](https://raw.githubusercontent.com/unicode-org/icu4x/main/CHANGELOG.md) records 2024 negative-year/calendar arithmetic fixes and continuity testing, followed by later calendar refactoring and comparisons with Hong Kong Observatory and Korean KASI data. This is concrete evidence of sustained complexity management and external-reference testing.

### 21. [hebcal/hebcal-es6](https://github.com/hebcal/hebcal-es6)

**TypeScript; Jewish holidays, readings, and location-dependent observances.** Study a domain calendar whose correctness depends on multiple interacting calendar classifications and regional customs. The repository's `@hebcal/core` API also explains which lower-level date functions now reside in the separate `@hebcal/hdate` package; that dependency is not counted as another repository here.

- **C1:** [`sedra.ts`](https://raw.githubusercontent.com/hebcal/hebcal-es6/main/src/sedra.ts) derives Torah-reading schedules from leap-year status, the weekday of Rosh Hashana, variable month lengths, and Israel-versus-Diaspora rules. It validates unsupported doubled-reading combinations and impossible schedule keys.
- **C2:** The [repository guide](https://github.com/hebcal/hebcal-es6) exposes calendar generation alongside standalone holiday, reading, and location-oriented functions. The schedule implementation separates classification, lookup results, and cached yearly schedules, providing useful reusable boundaries within a specialized domain.

### 22. [kshetline/tubular_time](https://github.com/kshetline/tubular_time)

**TypeScript; civil, historical, and astronomical date/time calculations.** Study the interaction of timezone discontinuities with calendar discontinuities, including configurable Julian/Gregorian adoption dates.

- **C1:** [`calendar.ts`](https://raw.githubusercontent.com/kshetline/tubular_time/master/src/calendar.ts) contains distinct Gregorian/Julian day-number conversions, explicit calendar-selection handling, and normalization of fields. The [repository documentation](https://github.com/kshetline/tubular_time) works through skipped dates, unusual day lengths, leap seconds, and UTC/TAI-related values.
- **C2:** The documented `Calendar` base handles date arithmetic and the switchover rule independently of a stored instant, while `DateTime` adds values and `Timezone` adds transition data. This lets historical date calculations, timezone conversion, and presentation share a foundation without forcing every operation to be an instant conversion.

### 23. [rickar/cal](https://github.com/rickar/cal)

**Go; holiday and business-calendar computations.** Study the difference between a calendar date, an actual holiday, and an observed non-working date. This adds business-rule composition to the report's lower-level temporal models.

- **C1:** [`v2/holiday.go`](https://raw.githubusercontent.com/rickar/cal/master/v2/holiday.go) combines start/end years, exception years, calculated offsets, and weekday-based observance shifts. It returns actual and observed dates separately and implements Easter-related arithmetic rather than reducing every holiday to a fixed month/day.
- **C2:** The [repository's v2 design explanation](https://github.com/rickar/cal) separates `Calendar` from `BusinessCalendar`, assigns observation policy to individual holidays, and permits custom workday and working-hour functions. Country definitions are separately importable. These are reusable boundaries for business scheduling, not merely a list of holiday dates.

## Recurrence and calendar interchange

### 24. [dateutil/dateutil](https://github.com/dateutil/dateutil)

**Python; datetime extensions, with recurrence as the main study entry.** Study lazy recurrence generation and the difference between composing occurrence sets and simply adding a duration repeatedly.

- **C1:** The [`rrule` documentation](https://dateutil.readthedocs.io/en/stable/rrule.html) explains the recurrence semantics of invalid month days and nonexistent local times: such candidates are omitted rather than silently coerced. Month-end examples expose the consequence for sequence membership.
- **C2:** [`rrule.py`](https://raw.githubusercontent.com/dateutil/dateutil/master/src/dateutil/rrule.py) implements recurrence sets combining inclusion/exclusion rules and explicit dates. These operations support reusable scheduling logic independent of a specific calendar application.
- **C3:** The implementation includes optional cached iteration, cache invalidation when a set changes, and heap-based merging of occurrence generators. This gives a concrete way to study demand-driven expansion and repeated-query costs without materializing every possible future event.

### 25. [libical/libical](https://github.com/libical/libical)

**C/C++; iCalendar protocol objects, parsing, and recurrence.** Study standards-derived recurrence semantics in a library intended to serve multiple calendar clients and servers. The inspected source is on the repository's `4.0` development branch, not a claim that every deployed release has that implementation.

- **C1:** The opening design commentary in [`icalrecur.c`](https://raw.githubusercontent.com/libical/libical/4.0/src/libical/icalrecur.c) describes validating rules, taking missing fields from `DTSTART`, expanding yearly candidates, and applying contracting `BY*` restrictions. Their order and interaction determine the actual occurrence set.
- **C2:** The [repository](https://github.com/libical/libical) provides protocol data structures and parsing; the recurrence code adds an iterator whose working state is distinct from the immutable rule. Optional non-Gregorian recurrence support delegates calendar conversion to ICU4C. It is a useful example of keeping a complex algorithm behind a reusable incremental interface.

### 26. [ical4j/ical4j](https://github.com/ical4j/ical4j)

**Java; iCalendar parsing, data models, and recurrence.** Study how a protocol library composes with `java.time` while guarding against pathological or unproductive recurrence searches.

- **C1:** [`Recur.java`](https://raw.githubusercontent.com/ical4j/ical4j/develop/src/main/java/net/fortuna/ical4j/model/Recur.java) validates recurrence-part ranges, accounts for `COUNT` and `UNTIL`, and limits repeated increments that produce no candidates. The limit is configurable, including an unlimited setting, so it is a policy boundary rather than a universal termination proof.
- **C2:** The recurrence type is generic over `Temporal` and offers both bounded date collections and a stream backed by a recurrence spliterator. The [repository overview](https://github.com/ical4j/ical4j) supplies the surrounding component/property model, parser, and compatibility options.
- **C3:** The same implementation skips ahead toward the search start only when `COUNT` permits it and supports incremental streaming. This is a concrete example of an optimization constrained by recurrence semantics.

## Search coverage and limitations

Discovery used more than six distinct live query formulations, covering: general date/time APIs; TZif readers and ambiguous local times; embedded C/C++ implementations; Java/.NET chronology models; JavaScript Temporal and functional APIs; Python recurrence and scientific precision; Ruby/Elixir/PHP integration; R/Julia temporal types; non-Gregorian and historical calendars; iCalendar protocol engines; and business-day/holiday rules. Follow-up searches across additional language communities and business-calendar implementations mostly returned overlapping architectural families. The final business-calendar pass added `rickar/cal` because it contributed both Go coverage and a distinct actual-versus-observed holiday model.

Every retained canonical GitHub repository page was opened. Each entry also had at least one distinct primary implementation or documentation source opened and read; raw source retrieval was used when GitHub's rendered file reader failed. No candidate code was executed, repositories were not cloned, and dependencies were not installed. One GitHub API release lookup hit a rate limit; the public Time4J releases page supplied the missing release information. Source browsing also caught date-fns' move into `pkgs/core` and Carbon's organization migration.

Selection deliberately excludes calendar UI widgets, full scheduling applications, general job runners, tutorial/awesome lists, and data-only timezone packages. Related implementations such as Moment/Day.js, additional Temporal implementations, workday catalogs, Perl/Haskell/Dart libraries, and standard-library subsystems are not exhaustively enumerated. This is a selection across implementation families, not a finding that omitted projects fail the criteria. Astropy and ICU4X are restricted to the named subsystems, and shared foundations or mirrors are not counted twice.

Maintenance status is stated only where primary material supports it: Joda-Time is explicitly identified as a legacy project with limited ongoing work, and Carbon's migration is documented. The report does not infer active maintenance from stars or recent pushes. Development-branch source and versioned documentation may describe different release snapshots; the links show which was examined. Numerical precision, historical zone data, future political rules, and regional holiday conventions have different validity limits, so inclusion should not be read as a promise of universal accuracy.
