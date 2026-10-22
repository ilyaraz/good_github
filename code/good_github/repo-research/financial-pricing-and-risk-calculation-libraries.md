# Financial pricing and risk calculation libraries

Research date: **2026-10-09**

This selection covers libraries that implement financial-instrument valuation, derivatives sensitivities, curve calibration, exposure simulation, hedging risk, or portfolio loss measures. It spans full analytics frameworks and smaller numerical engines. Trading execution systems, market-data clients, accounting tools, and generic optimization libraries are outside the scope unless their financial calculation subsystem is itself substantial. The 20 repositories below are study candidates, not a certification of numerical accuracy or production suitability.

Criteria used:

- **C1 — Difficult correctness:** numerical stability, financial conventions, state invariants, stochastic estimation, or explicit failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components that serve multiple instruments, models, measures, or workflows.
- **C3 — Performance and structure:** concrete treatment of computational or memory costs with an architecture that can be understood and inspected.
- **C4 — Sustained evolution:** evidence across years of testing, compatibility work, or deliberate management of complexity; repository age alone does not qualify.

Repository headings link to verified GitHub repositories. The implementation, test, and documentation links in each entry are suggested reading paths and evidence for the stated criteria. Maintenance claims are limited to what the inspected primary material establishes. Branch links describe the inspected source and may change after this date.

## Broad pricing and risk frameworks

### 1. [lballabio/QuantLib](https://github.com/lballabio/QuantLib)

**C++ — general quantitative-finance library.** Study the boundary between a financial instrument, the market-dependent calculation lifecycle, and an interchangeable pricing engine. This is particularly useful for understanding how an extensive product library shares valuation infrastructure.

- **C1:** `Instrument` makes expiration a distinct state transition, requires consistent expired results, rejects a missing engine or unavailable NPV, and validates engine arguments before calculation. These are meaningful safeguards against stale or incomplete valuation results. The [instrument implementation](https://github.com/lballabio/QuantLib/blob/master/ql/instrument.hpp) also documents observability testing.
- **C2:** The same interface separates argument construction, engine execution, and result extraction, including error estimates and additional results. Concrete products can reuse the engine protocol or supply their own calculation implementation. The inspected [release notes](https://github.com/lballabio/QuantLib/blob/master/News.md) additionally show explicit replacement APIs and staged deprecations, useful context when studying this abstraction's compatibility costs.

### 2. [OpenSourceRisk/Engine](https://github.com/OpenSourceRisk/Engine)

**C++ — Open Source Risk Engine, including QuantExt, OREData, and OREAnalytics.** Counted once as a monorepo. It extends QuantLib with its own trade/data and portfolio-risk machinery; it is not merely a second copy of QuantLib. Start with the transition from individual prices to simulated exposure data used by risk and valuation-adjustment calculations.

- **C1:** The [valuation engine](https://github.com/OpenSourceRisk/Engine/blob/master/OREAnalytics/orea/engine/valuationengine.cpp) checks date-grid and cube dimensions, manages model recalibration, and uses a scope-bound resetter to restore simulated market and fixing state. These details make scenario valuation a state-management problem as well as a numerical one.
- **C2:** A portfolio, simulation market, model builders, valuation calculators, and output cubes are separate collaborators. The [NPVCube interface](https://github.com/OpenSourceRisk/Engine/blob/master/OREAnalytics/orea/cube/npvcube.hpp) abstracts trade/date/sample/depth storage and explicitly specifies initialization and write-order invariants. Engineers can study reusable risk infrastructure independently of a particular pricing model.

### 3. [OpenGamma/Strata](https://github.com/OpenGamma/Strata)

**Java — financial analytics and market-risk framework.** The relevant monorepo components are product, market, pricer, measure, and calculation modules. Study how trade definitions and market-data preparation feed independently reusable pricing functions.

- **C1:** The [swap product pricer](https://github.com/OpenGamma/Strata/blob/main/modules/pricer/src/main/java/com/opengamma/strata/pricer/swap/DiscountingSwapProductPricer.java) distinguishes present value, forecast value, accrued interest, par rate, and sensitivities. It explicitly handles leg currencies and conversion rather than collapsing all amounts into an untyped scalar.
- **C2:** The [calculation-flow guide](https://strata.opengamma.io/calculation_flow/) separates calculation rules, market-data requirements, scenario construction, execution, and reporting. Individual stages can be run and persisted separately; trade-by-measure results can contain scenario arrays.
- **C3:** That flow builds required market data and scenarios before execution, both to expose data failures early and to enable vector-based scenario calculations. This is concrete architectural support for large repeated valuation workloads, without requiring a numerical speed claim.

### 4. [finmath/finmath-lib](https://github.com/finmath/finmath-lib)

**Java — mathematical-finance models, simulation, calibration, and sensitivities.** A strong choice for studying stochastic computation as an algebra rather than embedding raw simulation arrays throughout every product.

- **C2:** The [RandomVariable interface](https://github.com/finmath/finmath-lib/blob/main/src/main/java/net/finmath/stochastic/RandomVariable.java) specifies immutable arithmetic, filtration time, deterministic versus pathwise representation, statistics, and conditional expectation. Its contract deliberately avoids exposing a fixed internal data model, allowing product logic to work with different numerical representations.
- **C1:** The [adjoint-differentiation implementation](https://github.com/finmath/finmath-lib/blob/main/src/main/java/net/finmath/montecarlo/automaticdifferentiation/backward/RandomVariableDifferentiableAAD.java) treats conditional expectations and indicator functions specially and manages unique graph-node identities, including deserialization. These are subtler requirements than differentiating ordinary scalar arithmetic.
- **C3:** The same operator graph discards argument values when their derivatives do not need them—for example, addition and averaging—and retains only necessary multiplication/division operands. It is a concrete study in reducing the memory cost of simulation sensitivities.

### 5. [amaggiulli/QLNet](https://github.com/amaggiulli/QLNet)

**C# — native .NET implementation derived from QuantLib.** This is an explicitly related codebase, retained because it has a substantial C# implementation and its own framework integration and evolution, rather than being generated bindings. Compare how QuantLib's valuation design is expressed through .NET interfaces, nullable results, and event callbacks.

- **C1:** The [Instrument implementation](https://github.com/amaggiulli/QLNet/blob/develop/src/QLNet/Instruments/Instrument.cs) unregisters and registers update callbacks when engines change, invalidates lazy calculations, validates arguments, and rejects missing results. This makes lifecycle correctness visible in relatively compact code.
- **C2:** `IPricingEngine` arguments/results and the instrument's virtual calculation hooks support multiple product families while keeping engine replacement explicit. The [project release notes](https://github.com/amaggiulli/QLNet/blob/develop/News.txt) document .NET 8 integration, callable-bond changes, new overnight-index support, and calendar/schedule fixes—evidence that the port has its own substantive maintenance concerns. No claim of independent numerical ancestry is intended.

### 6. [domokane/FinancePy](https://github.com/domokane/FinancePy)

**Python with Numba — product-oriented derivatives and fixed-income analytics.** Study the separation of market curves, mathematical models, product conventions, and date utilities, plus the decision to keep computational kernels readable in Python.

- **C1:** The [Hull–White tree implementation](https://github.com/domokane/FinancePy/blob/master/financepy/models/hw_tree.py) combines term-structure discounting, short-rate lattice construction, exercise conventions, and callable/puttable bond or swaption rollback. It includes explicit treatment of small mean-reversion parameters and distinct European valuation approaches.
- **C3:** The same file isolates array-oriented tree construction and rollback kernels behind cached Numba compilation. This gives a concrete example of separating an accessible product API from expensive numerical loops; no C++-equivalent speed is assumed here.
- **C4:** The [changelog](https://github.com/domokane/FinancePy/blob/master/CHANGELOG.md) records releases from 2022 through 2026, numerical corrections, unit/regression-test changes, and repairs to examples after API reorganizations. Its documented renamings also show that sustained evolution does not imply an unchanging API.

### 7. [avhz/RustQuant](https://github.com/avhz/RustQuant)

**Rust — quantitative-finance workspace.** Counted once; the relevant components are instruments, stochastic processes, dates, and numerical support. The repository describes itself as a personal project rather than professional financial software. Its value here is the inspectable Rust design and algorithms, not an inferred production track record.

- **C2:** The [MonteCarloPricer trait and implementation macro](https://github.com/avhz/RustQuant/blob/main/crates/RustQuant_instruments/src/monte_carlo_pricer.rs) compose `Payoff`, a stochastic process, and simulation configuration. The same infrastructure distinguishes path-dependent and terminal-only payoffs across several option types.
- **C1:** The [Heston backend](https://github.com/avhz/RustQuant/blob/main/crates/RustQuant_instruments/src/backends/heston.rs) exposes complex-valued characteristic-function calculations, numerical integration, date-to-year-fraction conversion, and embedded reference-price assertions. It is useful for reviewing numerical assumptions and test tolerances; the source also explicitly fixes the volatility-risk premium to zero.

## Curves, interest-rate models, and cash-flow conventions

### 8. [attack68/rateslib](https://github.com/attack68/rateslib)

**Python and Rust — fixed-income valuation, curve solving, FX, and risk sensitivities.** **Source-available, not open source:** the repository states noncommercial/commercial dual licensing. Study the interaction between calibrated market quotes, curve parameters, and first- and second-order risk rather than treating automatic differentiation as an isolated utility.

- **C1:** The [solver](https://github.com/attack68/rateslib/blob/main/python/rateslib/solver.py) tracks associated object state and prevents calculations when curves have changed without recalibration. It distinguishes this from FX mutations that produce a warning. The gradient machinery also handles an empty solver container and uses Jacobian pseudoinverses in calibration sensitivities.
- **C2:** The solver connects curves, volatility objects, FX objects, instruments, and prerequisite solvers through one calibration/risk layer. The [Python package tree](https://github.com/attack68/rateslib/tree/main/python/rateslib) shows reusable periods, legs, scheduling, curves, dual numbers, mutability, and instrument components. This is especially useful for studying cross-curve and cross-currency sensitivity dependencies.

### 9. [marc-henrard/muRisQ-ir-models](https://github.com/marc-henrard/muRisQ-ir-models)

**Java — research implementations of interest-rate derivative models, built partly on Strata.** Retained for its separate model and pricer implementations, not as a Strata fork. Study how research models are expressed using an existing product and market-data vocabulary.

- **C1:** The [two-factor rational swaption tests](https://github.com/marc-henrard/muRisQ-ir-models/blob/master/src/test/java/marc/henrard/murisq/pricer/swaption/RationalTwoFactorSwaptionPhysicalProductSemiExplicitNiPricerTest.java) compare semi-explicit and numerical-integration prices, check payer/receiver parity, and test reductions to a one-factor model over expiry, tenor, and moneyness combinations. These are meaningful independent consistency checks.
- **C2:** The [semi-explicit pricer](https://github.com/marc-henrard/muRisQ-ir-models/blob/master/src/main/java/marc/henrard/murisq/pricer/swaption/RationalTwoFactorSwaptionPhysicalProductSemiExplicitPricer.java) consumes resolved products, a rates provider, and model parameters, while delegating model formulas separately. That structure allows alternative model/pricer combinations without rebuilding contract conventions.
- **C3:** Its documented reduction to at most one-dimensional integration provides a concrete computational alternative to the fuller numerical-integration implementation used in the tests.

### 10. [wolffsiemssen/json_risk](https://github.com/wolffsiemssen/json_risk)

**JavaScript — JSON-defined financial pricing and risk library.** This entry covers the calculation library, not the separate risk-system application. Study how a portable instrument schema and market-parameter representation can support both browser and server calculations.

- **C1:** The [schedule-generation guide](https://www.jsonrisk.de/01_Documentation/05_Schedule_generation.html) explains independent interest, fixing, and repayment schedules and their merger into cash flows. It explicitly covers split accrual periods, long/short stubs, forward/backward generation, and invalid combinations when the effective date is absent.
- **C2:** The [parameter guide](https://www.jsonrisk.de/01_Documentation/04_Parameters.html) defines reusable scalars, curves, volatility surfaces, calendars, and scenario rules. Curves expose interpolation, extrapolation, compounding, and ordered-axis requirements, while tags connect scenarios to parameters. These are substantive data contracts, not just JSON serialization around a single formula.

## Specialized derivatives numerics

### 11. [quants-net/PyFENG](https://github.com/quants-net/PyFENG)

**Python/NumPy — financial-engineering reference models.** The repository explicitly targets academic use. Study how analytic, stochastic-volatility, Monte Carlo, and other option models can share an interface while retaining model-specific numerical techniques.

- **C2:** [OptABC](https://github.com/quants-net/PyFENG/blob/main/pyfeng/opt_abc.py) supplies common forward/discount handling, numerical Greeks, implied-volatility inversion, and volatility-smile operations around a model-specific `price` method. It also handles broadcasting and preserves the original model while solving on a copy.
- **C1:** The [Heston tests](https://github.com/quants-net/PyFENG/blob/main/tests/test_heston.py) compare analytic and simulated moments, benchmark implied volatilities, and forward-price errors across alternative Monte Carlo schemes. They explicitly note catastrophic cancellation in an infinite-sum calculation, making this a useful example of tests informed by numerical failure modes.

### 12. [jherekhealy/AQFED.jl](https://github.com/jherekhealy/AQFED.jl)

**Julia — numerical library accompanying _Applied Quantitative Finance for Equity Derivatives_.** Although associated with a book, it contains reusable implementations across implied volatility, American exercise, cash dividends, baskets, and other models rather than only lesson notebooks. A good choice for close study of option-pricing numerics.

- **C1:** The [Householder implied-volatility solver](https://github.com/jherekhealy/AQFED.jl/blob/master/src/black/iv_solver_householder.jl) normalizes prices, rejects out-of-domain values, uses type-dependent machine precision, and evaluates a logarithmic objective with scaled complementary-error functions. Its stopping conditions and derivative ratios expose numerical decisions hidden by a simple formula API.
- **C3:** The [Black-module guide](https://github.com/jherekhealy/AQFED.jl/blob/master/src/black/README.md) compares different inversion algorithms, demonstrates higher-precision arithmetic, and shows precompiled reverse-differentiation tapes for repeated Greek calculations. This provides a reproducible path for investigating accuracy/cost tradeoffs without accepting any benchmark number as universal.

### 13. [vollib/py_lets_be_rational](https://github.com/vollib/py_lets_be_rational)

**Python with optional Numba — direct implementation of Peter Jäckel's Black implied-volatility algorithm.** A historical Python port: its README still describes Python 2.7 and old Numba installation requirements. It is retained as numerical source to study, without a claim of current maintenance. The original C wrapper and the broader Vollib wrappers are not counted separately.

- **C1:** The [numerical implementation](https://github.com/vollib/py_lets_be_rational/blob/master/py_lets_be_rational/lets_be_rational.py) combines rational initial guesses, Householder iteration, bracketing fallbacks, small-parameter and asymptotic expansions, and intrinsic/maximum-price checks. This is a compact but demanding example of making a familiar financial inversion work across floating-point regimes.
- **C3:** The implementation separates reusable numerical helpers and decorates selected kernels for compilation, including cached and no-GIL variants. The [optional JIT adapter](https://github.com/vollib/py_lets_be_rational/blob/master/py_lets_be_rational/numba_helper.py) preserves an ordinary Python fallback. The engineering point is the explicit acceleration boundary, not an unverified speedup claim.

### 14. [marcdemers/py_vollib_vectorized](https://github.com/marcdemers/py_vollib_vectorized)

**Python/Numba — batch option prices, implied volatilities, and Greeks.** This shares Vollib/Let's Be Rational ancestry with the preceding entry. It is included for its substantive batch kernels and array-facing API, not as an independent pricing model. Importing the package also patches corresponding `py_vollib` functions, an integration behavior documented by the repository.

- **C1:** The [public implied-volatility layer](https://github.com/marcdemers/py_vollib_vectorized/blob/main/py_vollib_vectorized/implied_volatility.py) broadcasts inputs, handles discount-factor underflow, checks intrinsic and maximum-price bounds, exposes error policy, and marks invalid results as NaN. This demonstrates the additional failure semantics required by bulk calculation.
- **C3:** The [compiled inversion kernels](https://github.com/marcdemers/py_vollib_vectorized/blob/main/py_vollib_vectorized/_iv_models.py) run contract loops and transformed-root iterations under the JIT boundary while reusing lower-level numerical functions. Study this implementation alongside the scalar library to distinguish array/API overhead from the inversion algorithm itself.

## Simulation, differentiable pricing, and contract composition

### 15. [google/tf-quant-finance](https://github.com/google/tf-quant-finance)

**Python/TensorFlow — tensor-oriented numerical finance.** **Archived and no longer maintained according to the repository's explicit notice.** Retained as a historical architecture reference for hardware-accelerated and differentiable pricing, not as a current support recommendation.

- **C1:** The [implied-volatility solver](https://github.com/google/tf-quant-finance/blob/master/tf_quant_finance/black_scholes/implied_vol_newton_root.py) supports normal and lognormal underlyings, broadcast shapes, optional argument validation, tolerances, and per-element convergence/failure results. The [tests](https://github.com/google/tf-quant-finance/blob/master/tf_quant_finance/black_scholes/implied_vol_newton_root_test.py) exercise graph and eager execution, negative Bachelier underlyings, discounting, and invalid arguments.
- **C2:** The repository documents three layers: foundational numerics, intermediate stochastic/PDE methods, and finance-specific pricing/calibration. The solver's reuse of shared root-search and normalization components illustrates that separation in actual code.
- **C3:** Independent contracts are represented as tensor cells with broadcasting, allowing numerical work to fit TensorFlow's execution and hardware-acceleration model. This is architectural evidence of performance intent, not a claim that every calculation benefits from a GPU.

### 16. [pfnet-research/pfhedge](https://github.com/pfnet-research/pfhedge)

**Python/PyTorch — derivative hedging and risk-based pricing under transaction costs.** Study the boundary between financial P&L semantics and interchangeable learned or analytic hedging policies. This is a calculation framework rather than a trading-execution bot.

- **C1:** The [financial tensor functions](https://github.com/pfnet-research/pfhedge/blob/main/pfhedge/nn/functional.py) calculate gains using the previous hedge position, subtract derivative liabilities and transaction costs, and validate tensor dimensions. The entropic-risk function uses `logsumexp`; the P&L function explicitly rejects unsupported final-cost deduction rather than silently applying it.
- **C2:** The [Hedger module](https://github.com/pfnet-research/pfhedge/blob/main/pfhedge/nn/modules/hedger.py) composes input features, a PyTorch model, derivative instruments, an optimizer, and a hedge-loss criterion. Its shared simulation, P&L, fitting, and pricing interface supports comparison of neural, Black–Scholes, and transaction-cost-aware policies.

### 17. [rcalxrc08/FinancialMonteCarlo.jl](https://github.com/rcalxrc08/FinancialMonteCarlo.jl)

**Julia — Monte Carlo valuation of equity derivatives.** Study multiple dispatch across processes, payoffs, curves, simulation methods, and execution modes. The README describes partial parallel-backend support and warns that automatic differentiation is not reliable for every payoff or derivative order; those limitations should travel with any reuse.

- **C1:** The [American-option engine](https://github.com/rcalxrc08/FinancialMonteCarlo.jl/blob/master/src/options/engines/general_american_engine.jl) regresses continuation values on in-the-money paths, compares them with exercise values, and tracks exercise times for discounting. Its explicit polynomial design matrix and normal-equation solve make regression conditioning and exercise-time semantics available for review.
- **C2:** That engine operates on abstract matrices, payoff types, zero-rate curves, and Monte Carlo configuration, allowing the same exercise logic to work with different simulation components.
- **C3:** The [threaded pricer](https://github.com/rcalxrc08/FinancialMonteCarlo.jl/blob/master/src/multi_threading.jl) splits simulations into batches with assigned seeds and aggregates batch prices. It also exposes practical design questions: the implementation uses integer division for paths per batch, so arbitrary requested path counts should not be assumed to be preserved exactly.

### 18. [JuliaComputing/Miletus.jl](https://github.com/JuliaComputing/Miletus.jl)

**Julia — compositional financial contracts and valuation models.** A distinctive alternative to a large inheritance hierarchy of named products: study contracts as a small algebra whose expressions can be interpreted by different valuation models.

- **C2:** The [contract definitions](https://github.com/JuliaComputing/Miletus.jl/blob/master/src/contracts.jl) provide typed composition through scaling, giving, acquiring both/either contracts, conditions, and exercise-time operators. European and American products can be expressed through these reusable primitives.
- **C1:** The [binomial model implementations](https://github.com/JuliaComputing/Miletus.jl/blob/master/src/models/binomial.jl) distinguish fixed-time acquisition from exercise before maturity, require agreement between model and contract maturity, and perform discounted backward induction with an exercise-versus-continuation maximum where appropriate. The code makes the financial meaning of contract operators visible in the numerical interpreter.

## Portfolio loss measures and risk attribution

### 19. [braverock/PerformanceAnalytics](https://github.com/braverock/PerformanceAnalytics)

**R — return-based portfolio risk and performance analytics.** This is the development repository identified by the project's own release history; the older `R-Finance` copy and CRAN mirror are not additional entries. Focus on the risk estimators and attribution functions rather than only the plotting layer.

- **C1:** The [VaR implementation and embedded documentation](https://github.com/braverock/PerformanceAnalytics/blob/master/R/VaR.R) distinguish estimation methods, univariate/component/marginal portfolio semantics, higher moments, cleaning, standard errors, and loss-sign conventions. The `invert` default explicitly preserves historical behavior, illustrating how mathematical and practitioner conventions can conflict at an API boundary.
- **C2:** One interface handles several return-series representations, supplied moments, portfolio weights, and estimation methods, making the estimator reusable for individual assets and portfolio decomposition.
- **C4:** The [release history](https://github.com/braverock/PerformanceAnalytics/blob/master/NEWS.md) describes work across multiple years, including 2017 higher-moment changes, 2018 standard-error work, and later testing and compatibility efforts. It also documents consolidating portfolio-return functions and subsequent edge-case corrections, providing stronger evolution evidence than an old creation date.

### 20. [dcajasn/Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib)

**Python, NumPy, SciPy, and CVXPY — portfolio risk measures and risk-aware allocation.** Counted once; the relevant subsystem is `riskfolio/src/RiskFunctions.py`, alongside the broader allocation framework. Study the gap between writing a mathematical risk definition and implementing a usable numerical estimator and attribution API.

- **C1:** [RiskFunctions](https://github.com/dcajasn/Riskfolio-Lib/blob/master/riskfolio/src/RiskFunctions.py) checks return-array dimensions and nonfinite values; historical CVaR handles the tail sample boundary explicitly. EVaR first attempts a constrained SciPy optimization, then an exponential-cone formulation with compatible solver fallbacks, and raises if no result can be obtained.
- **C2:** The same module exposes standalone tail, moment, downside, and drawdown measures, plus `Risk_Contribution`, which dispatches by risk measure and computes asset contributions from weight perturbations. The reusable measure vocabulary connects risk reporting and attribution with the project's portfolio-construction use cases; the selection does not imply that all measures or solver choices have identical robustness.

## Search coverage and limitations

Discovery used more than six distinct live-web formulations, including broad derivatives pricing/XVA, Java Strata/finmath, Python fixed-income curves, Rust pricing, Julia financial-contract and Monte Carlo libraries, JavaScript JSON Risk, C# pricing, R/Python portfolio risk, implied-volatility kernels, and additional credit-risk and energy-pricing searches. Searches for PyFENG, AQFED, and Vollib-family implementations expanded the selection beyond the best-known institutional frameworks. Later credit/energy and language-specific searches largely yielded narrow demos, service clients, general energy optimization, or overlapping implementations rather than stronger additions.

Every retained canonical GitHub repository was opened, and at least one additional primary implementation or substantive documentation source was read. Additional source inspection covered regression tests, numerical kernels, API contracts, and release notes. GitHub's unauthenticated API was rate-limited during research; verification therefore used repository HTML, public raw source files, and project documentation. No candidate repository was cloned, installed, or executed, and tests were inspected rather than run.

The selection excludes generated/API-only wrappers, standalone tutorial notebooks, awesome-lists, trading bots, generic mathematical libraries, and unverified claims of institutional quality. Related implementations are labeled: ORE extends QuantLib, QLNet is a separate C# implementation derived from QuantLib, muRisQ builds on Strata, and the two retained Vollib-family projects share numerical ancestry but expose different substantive implementation layers. No unofficial mirror is offered as a separate project. Rateslib's source-available license and TensorFlow Quant Finance's archive notice are explicit exceptions to any assumption that this is a list of actively maintained open-source packages.

Coverage is strongest for rates, equity/FX derivatives, exposure simulation, and return-based portfolio risk. It is thinner for standalone credit-portfolio and commodity-specialist engines. Criteria judgments and suggested study value are grounded engineering inferences from the cited material, not benchmark results, a comprehensive security audit, or evidence that every component is uniformly exemplary.
