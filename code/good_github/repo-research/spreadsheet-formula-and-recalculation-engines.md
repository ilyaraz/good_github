# Spreadsheet formula and recalculation engines

Research date: **2026-10-09**

This selection covers 21 GitHub repositories implementing spreadsheet expression evaluation, dependency tracking, recalculation, or compilation of spreadsheet calculations into executable programs. It includes standalone runtimes and identifiable calculation subsystems within larger applications and file libraries. Merely reading or writing formula strings, returning previously cached Excel results, or automating an installed spreadsheet application is outside scope. The criteria describe worthwhile engineering to study, not a guarantee of complete Excel compatibility or uniformly exemplary code.

**Criteria legend:** **C1** — difficult correctness involving invariants, concurrency, numerical semantics, adversarial inputs, or failure modes. **C2** — substantial reusable abstractions supporting multiple use cases. **C3** — real performance constraints addressed through an understandable architecture. **C4** — sustained evolution with concrete compatibility, testing, or complexity-management evidence. Each entry explicitly justifies at least two criteria. Links within entries are starting points into inspected primary material.

## Standalone and embeddable runtimes

### 1. [handsontable/hyperformula](https://github.com/handsontable/hyperformula)

**Language/role:** TypeScript; headless spreadsheet parser, evaluator, and mutable workbook engine.

Study how a calculation graph becomes a reusable application component with named expressions, structural edits, custom functions, and browser/server integration. Its especially instructive design decision is representing ranges as graph nodes that can reuse smaller ranges.

- **C1:** Evaluation must respect precedents, while edits and range expressions preserve dependency relationships. The [dependency-graph guide](https://hyperformula.handsontable.com/docs/guide/dependency-graph.html) explains these ordering and representation rules.
- **C3:** The same guide explains why expanding successively larger cumulative ranges creates quadratically many edges, and how composing range nodes and reusing associative aggregates avoids that representation cost.
- **C4:** The [changelog](https://github.com/handsontable/hyperformula/blob/master/CHANGELOG.md) records compatibility and deprecation work across 2021–2026, including structural-edit failures, explicit breaking changes, and fixes for statistical precision on large-offset data. This is stronger evidence than repository age alone.

### 2. [ironcalc/IronCalc](https://github.com/ironcalc/IronCalc)

**Language/role:** Rust, with language bindings; spreadsheet engine and XLSX integration. The project describes itself as work in progress.

Study a recalculation algorithm in which dynamic arrays can discover ordering requirements during execution. The [evaluation implementation](https://github.com/ironcalc/IronCalc/blob/main/base/src/evaluation.rs) begins with unusually useful algorithm documentation and then implements the associated state machine.

- **C1:** A spill can invalidate what an earlier formula observed. The engine records those observations, restarts with newly learned anchor ordering, distinguishes stale spill contents from current values, and detects circular ordering requirements. This addresses correctness beyond ordinary static topological sorting.
- **C3:** Evaluation bounds recursion, unwinds without committing partial results, and replays pending work to handle long dependency chains without exhausting the native or WebAssembly stack. It retains learned anchor order across evaluations to avoid repeating discovery work.
- **C2:** The repository separates the calculation core, workbook/file handling, and bindings, making the same engine useful outside its web interface.

### 3. [PSU3D0/formualizer](https://github.com/PSU3D0/formualizer)

**Language/role:** Rust with Python and WebAssembly bindings; embeddable workbook calculation and mutation runtime.

Study the interaction between columnar storage and spreadsheet dependencies. The [evaluation-crate guide](https://github.com/PSU3D0/formualizer/blob/main/crates/formualizer-eval/README.md) describes Arrow-backed values, spill overlays, dependency scheduling, and optional parallel execution.

- **C1:** The [range-dependency tests](https://github.com/PSU3D0/formualizer/blob/main/crates/formualizer-eval/src/engine/tests/range_dependencies.rs) exercise invalidation after changing an interior cell, verify that unrelated changes do not dirty a formula, and update dependencies when a formula's referenced range changes.
- **C2:** Resolver, range-resolver, and function-provider interfaces separate evaluation from application-owned storage and extension functions; a higher-level workbook crate wraps those lower-level facilities.
- **C3:** Arrow storage and compact range/dependency representations explicitly target range-heavy workloads and repeated recalculation. The repository's timing comparisons are not reproduced here as independently verified performance results.

The architecture documents include drafts; those should be distinguished from implemented behavior and executable tests.

### 4. [kohei-us/ixion](https://github.com/kohei-us/ixion)

**Language/role:** C++; general-purpose formula interpreter, dependency tracker, and spreadsheet model backend. **Official substantive GitHub mirror; development is hosted on GitLab.**

Study the boundary between discovering affected formulas and executing a correctly ordered calculation batch.

- **C1:** [Formula calculation](https://github.com/kohei-us/ixion/blob/master/src/libixion/formula_calc.cpp) resets calculation status and checks circular dependencies before interpreting cells. Serial and threaded execution use the same prepared batch; calculation-begin/end notifications are managed by a scope object.
- **C3:** The [dirty-cell tracker](https://github.com/kohei-us/ixion/blob/master/src/libixion/dirty_cell_tracker.cpp) uses per-sheet spatial indexes for affected ranges, explicitly includes volatile formulas, and records relationships for sorting the dirty subset. This combines selective work discovery with dependency-aware parallel execution.
- **C2:** The model context and formula APIs support embedding the calculation backend without adopting a spreadsheet UI.

### 5. [vogtb/f7](https://github.com/vogtb/f7)

**Language/role:** TypeScript and Java, with ANTLR grammars; formula execution library. **Historical source release**, not presented by its author as a ready-to-adopt production package.

This less prominent codebase is useful for studying the layers between a generated parser and hand-written spreadsheet semantics. The selection concerns those implementation layers, rather than generated parser output.

- **C1:** The [spreadsheet executor](https://github.com/vogtb/f7/blob/main/src/main/js/execution/Executor.ts) tracks the computation stack to detect circular references and keeps computation markers separate from cell data. Named ranges and relative grid lookups require evaluation context.
- **C2:** The [code executor](https://github.com/vogtb/f7/blob/main/src/main/js/execution/CodeExecutor.ts) separates typed AST visitation from injected lookup functions and the formula caller. This makes the distinction between expression evaluation and workbook access explicit.

The README candidly identifies inefficient range queries, memory-management limitations, and incomplete integration. No C3 or C4 claim is made for this repository.

## Workbook graph compilers and generated calculation programs

### 6. [vinci1it2000/formulas](https://github.com/vinci1it2000/formulas)

**Language/role:** Python; Excel formula interpreter and workbook-to-executable-model compiler.

Study how spreadsheet cells become a dataflow dispatcher with explicit inputs and outputs. The [ExcelModel implementation](https://github.com/vinci1it2000/formulas/blob/master/formulas/excel/__init__.py) contains model completion, range assembly, calculation, comparison, and compilation.

- **C1:** Model finalization handles references and assembled ranges, with an explicit circular-resolution path. `solve_circular` examines cycles and inserts circular-error values or rewrites relevant graph connections; it does not simply assume every workbook is acyclic.
- **C2:** A workbook can become a callable model with selected input/output cells, be reconstructed from dictionaries, or be evaluated through its dispatcher. The same abstractions serve whole-workbook processing and extracted calculations.
- **C3:** `compile` shrinks the dispatcher around requested inputs and outputs and extracts the relevant workflow, showing how reusable calculation services can avoid retaining every workbook computation.

Its circular-handling implementation should be studied on its own terms, rather than assumed to reproduce all Excel iterative-calculation settings.

### 7. [dgorissen/pycel](https://github.com/dgorissen/pycel)

**Language/role:** Python; spreadsheet-to-Python compiler with a dependency graph and lazy evaluation.

Study a compact graph-based alternative to maintaining an interactive grid. The [ExcelCompiler](https://github.com/dgorissen/pycel/blob/master/src/pycel/excelcompiler.py) combines workbook import, graph construction, serialization, and evaluation.

- **C1:** The compiler reads workbook iterative-calculation settings, including iteration limits and tolerance, and selects different cell/evaluation machinery for cyclic and non-cyclic models. This exposes the distinction between rejecting a cycle and evaluating an intentionally iterative model.
- **C2:** Workbook wrappers, plugin function modules, compiled cell maps, and serialized models let the calculation graph be reused independently of Excel and inspected with graph tools.
- **C3:** Cached values and lazy evaluation limit repeated computation when querying compiled outputs.

The repository documents incomplete function coverage and a particular limitation of reference-producing functions: an `OFFSET` target outside the compiled graph can fail. Treat its historical benchmark examples as examples, not general performance guarantees.

### 8. [bradbase/xlcalculator](https://github.com/bradbase/xlcalculator)

**Language/role:** Python; workbook model compiler and AST evaluator. The project identifies itself as a modernization of Koala; it is included separately for its evaluator/context and typed-function design.

- **C1:** The [evaluator](https://github.com/bradbase/xlcalculator/blob/master/xlcalculator/evaluator.py) distinguishes blank cells from stored values, resolves defined names, evaluates range dependencies, and includes cycle checks in the evaluation context. The README also discusses differences between Python numeric behavior and Excel, rather than asserting perfect numerical equivalence.
- **C2:** Model storage, evaluator contexts, AST evaluation, and the function namespace are separate abstractions. Function registration and argument-validation decorators allow new functions to participate in spreadsheet-style coercion.

Study the [project's extension and testing guidance](https://github.com/bradbase/xlcalculator/blob/master/README.rst), which asks contributors to test both the Python function and its behavior against Excel. Array-formula support and precision limitations are explicitly documented; these constraints matter when choosing representative workloads.

### 9. [vallettea/koala](https://github.com/vallettea/koala)

**Language/role:** Python; earlier Excel-to-dependency-network engine, distributed as Koala2.

Study an explicit mutable calculation graph for repeated what-if evaluation. The [Spreadsheet implementation](https://github.com/vallettea/koala/blob/master/koala/Spreadsheet.py) exposes graph generation, pruning, value replacement, invalidation, and evaluation in one navigable core.

- **C1:** Setting an intermediate cell can fix its value and suppress its formula; freeing it restores evaluation. Dependents must be reset correctly, and input-dependent reference functions need additional pointer-reset tracking. These are meaningful cache-validity problems, not just expression parsing.
- **C2:** Named ranges, graph serialization, construction without a workbook file, and selected input/output interfaces make the model usable for simulation and service integration.
- **C3:** Graph generation can restrict outputs, pruning removes calculations unaffected by designated inputs, and evaluation reuses values until dependencies change.

The README calls the implementation early-stage. Inclusion recognizes the substantive graph design and its relationship to later Python evaluators, without implying current maintenance or universal workbook compatibility.

### 10. [tamc/excel_to_code](https://github.com/tamc/excel_to_code)

**Language/role:** Ruby compiler generating C or Ruby calculation programs; an older alternative to a permanently resident spreadsheet interpreter.

Study compilation as a deployment strategy for spreadsheet models. The [project structure](https://github.com/tamc/excel_to_code/blob/master/docs/structure_of_this_project.md) separates extraction, formula/reference processing, rewriting, simplification, and target-language generation.

- **C2:** A shared sequence of intermediate transformations feeds separate C and Ruby backends, while supported spreadsheet functions are implemented as reusable runtime operations. The generated calculation can be embedded in other programs.
- **C3:** Generated outputs are evaluated on demand and cached, as explained in [the calculation protocol](https://github.com/tamc/excel_to_code/blob/master/docs/how_does_the_calculation_work.md). Shared dependencies need not be recalculated for each output; pruning and simplification reduce the emitted model.
- **C1:** That protocol makes cache invalidation an explicit caller obligation: reset, set inputs, then read outputs. The README also specifies compile-time restrictions on dynamic references and warns that generated C is not thread-safe and can differ in rounding semantics.

## Calculation subsystems in spreadsheet file libraries

### 11. [apache/poi](https://github.com/apache/poi)

**Language/role:** Java; formula evaluation shared by spreadsheet-format implementations. **Official GitHub mirror of Apache's GitBox repository.** The relevant subsystem is `poi/.../ss/formula`, not the entire document-processing monorepo.

- **C1:** The [WorkbookEvaluator](https://github.com/apache/poi/blob/trunk/poi/src/main/java/org/apache/poi/ss/formula/WorkbookEvaluator.java) makes intermediate-result cache validity explicit and coordinates evaluation across collaborating workbooks. Workbook edits require notification or cache invalidation to avoid stale answers.
- **C2:** `EvaluationWorkbook`, operation contexts, user-defined-function lookup, and collaborating-workbook environments separate expression execution from concrete workbook storage. This permits common evaluation machinery across spreadsheet formats.
- **C3:** Intermediate-result caching avoids repeating dependent calculations. The [evaluation guide](https://poi.apache.org/components/spreadsheet/eval.html) explains the practical memory constraint for streaming SXSSF workbooks: referenced cells must still be available, so full evaluation is often incompatible with a narrow streaming window.

This is a particularly useful selection for studying how a file API's lifecycle constrains a calculation engine.

### 12. [ClosedXML/ClosedXML](https://github.com/ClosedXML/ClosedXML)

**Language/role:** C#; XLSX library with an internal calculation engine.

Study the combination of range-based dirty tracking and an adaptive calculation chain. The [formula-calculation design document](https://github.com/ClosedXML/ClosedXML/blob/develop/docs/concepts/formula-calculation.rst) distinguishes a cell's current value from its potentially stale cached value.

- **C1:** Dirty state propagates transitively through an R-tree of precedent areas. Changes to sheets and defined names can invalidate formulas as well as ordinary cell edits; cycles in the calculation chain raise an exception.
- **C3:** The chain reuses previous evaluation order. When evaluation encounters a dirty precedent, the supporting formula is moved ahead of the current formula, improving later passes. Spatial overlap searches avoid representing a large range solely as individually enumerated cell edges.
- **C2:** The [XLCalcEngine implementation](https://github.com/ClosedXML/ClosedXML/blob/develop/ClosedXML/Excel/CalcEngine/XLCalcEngine.cs) separates formula parsing, calculation visitation, dependency tracking, and chain management behind workbook/sheet listeners.

### 13. [EPPlusSoftware/EPPlus](https://github.com/EPPlusSoftware/EPPlus)

**Language/role:** C#; spreadsheet library with a reverse-Polish-notation calculation engine. **Source-available licensing distinction:** the inspected branch uses PolyForm Noncommercial terms, with commercial licensing offered separately.

Study execution at workbook, worksheet, range, named-range, and individual-formula scopes through the [RPN execution implementation](https://github.com/EPPlusSoftware/EPPlus/blob/develop8/src/EPPlus/FormulaParsing/DependencyChain/RpnFormulaExecution.cs).

- **C1:** Circular-reference detection checks both the formula stack and collisions with array-formula ranges. The engine distinguishes allowed circular references from exceptions and treats cancellation as a condition that must propagate, rather than be converted silently to a formula error.
- **C2:** The same execution machinery accepts several calculation scopes and uses calculation options to control dependency following, expression caching, and cycle policy.
- **C3:** The optimized dependency chain, expression caches, and accessed-range bookkeeping address repeated evaluation and reference traversal. The code offers useful examples of the interaction between cached expressions and mutable workbook state.

The [repository introduction](https://github.com/EPPlusSoftware/EPPlus/blob/develop8/Readme.md) is the licensing and product-context entry point; public source access should not be confused with unrestricted commercial reuse.

### 14. [qax-os/excelize](https://github.com/qax-os/excelize)

**Language/role:** Go; spreadsheet file library with a native `CalcCellValue` evaluator. The canonical repository owner differs from the `github.com/xuri/excelize/v2` Go import path.

Study an evaluator integrated directly into a document library. The [calculation source](https://github.com/qax-os/excelize/blob/master/calc.go) contains typed arguments, references, coercion, token evaluation, and spreadsheet functions.

- **C1:** Formula arguments distinguish numbers, strings, lists, matrices, and errors. Calculation contexts track iteration counts and configured limits; invalid tokens and failed numeric conversions produce explicit errors. These details expose where Go semantics need translation into spreadsheet semantics.
- **C2:** `formulaArg`, cell/range references, the calculation context, and the common function-dispatch mechanism provide reusable machinery across many function families and workbook cells.
- **C3:** `CalcCellValue` has separate caches for raw and formatted results, while the infix evaluator uses explicit operand/operator/function stacks. Inspecting these structures is useful for understanding both evaluation cost and the distinction between calculation and presentation.

This entry concerns native evaluation, not the library's separate streaming file-I/O facilities.

### 15. [PHPOffice/PhpSpreadsheet](https://github.com/PHPOffice/PhpSpreadsheet)

**Language/role:** PHP; multi-format spreadsheet library with a built-in calculation engine.

- **C1:** The [Calculation implementation](https://github.com/PHPOffice/PhpSpreadsheet/blob/master/src/PhpSpreadsheet/Calculation/Calculation.php) maintains a cyclic-reference stack, iteration controls, cell context, and formula-error state. Spill-reference handling and the boundary between PHP values and spreadsheet values add semantic complexity.
- **C2:** Calculation can attach to a particular spreadsheet or operate as a standalone engine. Parsing, function execution, logging, branch pruning, and workbook access are identifiable responsibilities within the subsystem.
- **C3:** The [calculation-engine guide](https://github.com/PHPOffice/PhpSpreadsheet/blob/master/docs/topics/calculation-engine.md) documents result caching and explicit disable/flush operations, making the cost and correctness implications of repeated evaluation visible.

Study this code alongside its documented limitations, including array-argument coverage and operator/type-coercion differences. The guide's distinction between `getValue()` and `getCalculatedValue()` also makes it easy to establish that this library actually evaluates formulas.

## Spreadsheet application cores

### 16. [dream-num/univer](https://github.com/dream-num/univer)

**Language/role:** TypeScript; office SDK monorepo. The relevant components are `packages/engine-formula` and its spreadsheet integration, counted together once.

Study how formula calculation becomes a service within a larger extensible application, including formulas owned by features rather than only ordinary cells.

- **C1:** The [dependency generator](https://github.com/dream-num/univer/blob/dev/packages/engine-formula/src/engine/dependency/formula-dependency.ts) builds execution lists, clears invalid dependency state, and detects cycles using an explicit traversal stack and node colors. Workbook disposal also removes associated cached ASTs.
- **C2:** Injected dependency, configuration, interpreter, and runtime services separate dependency discovery from execution state. The [runtime service](https://github.com/dream-num/univer/blob/dev/packages/engine-formula/src/services/runtime.service.ts) tracks array results, feature ranges, function state, and calculation progress through explicit interfaces.
- **C3:** Spatial dependency indexes, flattened-range caches, and AST caches address repeated range and dependency queries. This is a useful contrast to small evaluators that repeatedly scan every cell or range.

### 17. [LibreOffice/core](https://github.com/LibreOffice/core)

**Language/role:** Primarily C++; full office-suite monorepo. **Official read-only GitHub mirror.** The selected subsystem is Calc's `sc/` formula-cell and interpreter machinery.

Study production-scale interaction between mutable document state, dependency discovery, and parallel formula groups. The [formula-cell implementation](https://github.com/LibreOffice/core/blob/master/sc/source/core/data/formulacell.cxx), especially `InterpretFormulaGroupThreading`, provides a concrete entry point.

- **C1:** Dependencies must be ready before a formula group can run concurrently. A failed speculative dependency probe can leave a precedent dirty, requiring another check. During threaded execution, the implementation guards document mutation, manages token reference-counting policy, drops token caches, and merges thread contexts back in the main thread.
- **C3:** Formula groups are distributed through a thread pool with per-thread interpreter contexts. Eligibility checks and fallback paths make this more instructive than an isolated parallel map over cells.

The monorepo's breadth is a navigation cost; start with the selected implementation instead of treating all office-suite components as part of this category.

### 18. [GNOME/gnumeric](https://github.com/GNOME/gnumeric)

**Language/role:** C; numerical spreadsheet application. **Official read-only GitHub mirror of the GNOME GitLab project.**

Study dependency management as a subsystem shared by cells, names, and other dependent objects. The [dependency implementation](https://github.com/GNOME/gnumeric/blob/master/src/dependent.c) contains class-based dependent operations, dynamic dependencies, dirty flags, and range indexing.

- **C1:** Dynamic references need registrations that can change after evaluation; marking one dependent dirty is explicitly distinct from recursively queuing affected computations. Those distinctions are central to avoiding missed or excessive recalculation.
- **C3:** Row buckets grow with row number, allowing range-dependency indexing to scale without treating every possible worksheet row as an equally sized allocation. The implementation connects this representation directly to affected-dependent lookup.

The [NEWS file](https://github.com/GNOME/gnumeric/blob/master/NEWS) is a useful second entry point for numerical and compatibility work: inspected releases discuss GEOMEAN accuracy, blank criteria, Excel-compatible function behavior, and test-suite improvements. These entries support studying ongoing semantic refinement, without assuming every function is numerically interchangeable with Excel.

### 19. [ONLYOFFICE/sdkjs](https://github.com/ONLYOFFICE/sdkjs)

**Language/role:** JavaScript; shared editor SDK. The relevant subsystem is the spreadsheet engine under `cell/model/FormulaObjects`, counted once within this monorepo.

Study formula semantics that must survive interactive edits and shared-formula changes. The [parser and formula-object implementation](https://github.com/ONLYOFFICE/sdkjs/blob/master/cell/model/FormulaObjects/parserFormula.js) is a large but substantive entry point.

- **C1:** Changing a shared formula's reference area removes and rebuilds dependencies and records the change for undo. Notification handlers distinguish dirtying from other structural events. Range intersection, array conversion, and error propagation are explicit evaluation concerns.
- **C2:** A hierarchy of number, error, array, reference, area, and function objects supplies common operations to the spreadsheet function library. Helpers for one- and two-argument calculations centralize scalar/range/array handling rather than leaving every function to reinvent it.

This is tightly integrated editor-engine code, not a small standalone parser package. Its value is in seeing calculation, reference rewriting, and application mutation meet.

### 20. [DanBricklin/socialcalc](https://github.com/DanBricklin/socialcalc)

**Language/role:** JavaScript with surrounding Perl utilities; original SocialCalc implementation. **Historical project**, included for its substantive browser recalculation design, not as a claim of present maintenance.

- **C1:** The [core scheduler](https://github.com/DanBricklin/socialcalc/blob/master/socialcalc-3.js) tracks calculation ordering, detects circular references, and preserves resumable traversal state. The [formula library](https://github.com/DanBricklin/socialcalc/blob/master/formula1.js) coordinates external-sheet caches with waiting/loading/recalculation states.
- **C3:** Recalculation is a state machine split into time slices using timers, with explicit ordering, calculation, and waiting phases. It yields control during long work and resumes after sheet loading, addressing browser responsiveness without requiring worker threads.

Study this as an architectural ancestor with a different concurrency model from modern threaded engines. The report does not separately count EtherCalc or downstream SocialCalc variants as additional independent engines.

### 21. [andmarti1424/sc-im](https://github.com/andmarti1424/sc-im)

**Language/role:** C with Yacc grammar and optional Lua integration; terminal spreadsheet derived from `sc`, with substantive separate evolution.

Study recalculation embedded in a compact interactive application. The [dependency graph](https://github.com/andmarti1424/sc-im/blob/main/src/graph.c) documents forward edges to precedents and reverse edges to dependents; the [expression interpreter](https://github.com/andmarti1424/sc-im/blob/main/src/interp.c) is the companion semantic layer.

- **C1:** Edits must preserve both directions of dependency relationships. Bottom-up evaluation only processes a formula when its precedents have been visited; separate visitation state supports dependency traversal and evaluation.
- **C3:** `EvalRange` finds dependents of changed cells and reevaluates them, while `EvalAll` provides a full graph traversal. This creates a concrete study of selective recalculation in an interactive terminal application.

The bottom-up implementation can rescan the vertex list; inclusion is not a claim of optimal asymptotic complexity. The earlier `sc` implementation is not counted separately.

## Coverage, search process, and limitations

Discovery used live web searches with more than six distinct formulations: general dependency-graph/incremental-recalculation engines; Rust/C++ spreadsheet runtimes; Python Excel evaluators and compilers; Java/.NET formula evaluation; JavaScript/browser engines; Go/PHP calculation libraries; LibreOffice/Gnumeric parallel and range-based calculation; terminal/Python-native spreadsheets; Ruby-to-C compilation; and academic Funcalc/Haskell approaches. Follow-up searches and repository traversal located less prominent implementations such as F7 and `excel_to_code`. Later searches increasingly returned already identified engines, small demonstrations, commercial bindings, or papers without a verifiable public engine repository.

Every retained canonical repository URL was checked through its GitHub page or public GitHub API. Relevant implementation files, design/API documentation, or tests were then opened separately. GitHub's unauthenticated API limit was reached during tree inspection; public directory pages and raw source files supplied the remaining evidence. No candidate code was executed, dependencies installed, or repositories cloned.

Important boundaries and exclusions:

- Formula-preserving readers/writers, cached-value readers, Excel/LibreOffice automation wrappers, function-name lists, and tutorial-only recalculation exercises were excluded. General expression evaluators without spreadsheet reference/workbook semantics were also outside scope.
- `fast-formula-parser` was investigated, but its README now directs users to the SheetXL successor. It was not added as another presumed-maintained independent engine. Pyspread was investigated, but its current README points to GitLab and the inspected GitHub copy's official-mirror status was not established.
- Academic Corecalc/Funcalc material informed discovery, but a publicly readable canonical GitHub engine repository was not verified; a spreadsheet corpus repository was not substituted for the engine.
- Official substantive mirrors are identified individually. F7 and the original SocialCalc are explicitly historical; lack of an archive flag is not treated as proof of active maintenance. Other entries make no blanket maintenance guarantee.
- Koala and xlcalculator are related, but expose sufficiently different graph/model/evaluator organization to merit comparison; that lineage is stated. Monorepos and their internal packages are counted only once.
- Performance criteria refer to inspected mechanisms, not independently reproduced speed rankings. Compatibility remains workload-dependent. Inferences about what an engineer can learn are editorial judgments grounded in the linked implementation, not audits of every component.

The result is deliberately a selection guide across 21 distinct repositories, spanning TypeScript/JavaScript, Rust, C/C++, Python, Java, C#, Go, PHP, and Ruby. It is not an exhaustive catalog or a claim that all listed projects are suitable for new deployments.
