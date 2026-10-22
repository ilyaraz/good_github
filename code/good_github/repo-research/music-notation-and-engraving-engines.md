# Music notation and engraving engines

Research date: **2026-10-09** (America/Los_Angeles).

This report selects **20 GitHub repositories** that implement substantial musical layout, engraving, or notation-editor infrastructure. It covers native and browser engines, ABC and MusicXML processing, tablature, Gregorian and Byzantine chant, and several instructive historical designs. Application monorepos are included only for their identified notation subsystems. Format specifications, font collections, score collections, optical recognition, and thin bindings are outside the selection.

The criteria are engineering-study criteria, not a ranking of output quality or a recommendation to adopt every dependency:

- **C1 — Correctness:** difficult invariants, numerical semantics, interacting layout constraints, malformed inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable models, interfaces, or processing stages supporting different use cases.
- **C3 — Performance:** concrete mechanisms addressing interactive or large-score workloads within an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility, regression testing, or deliberate complexity management.

Each entry states at least two supported criteria. Architectural assessments are grounded in the linked implementation or design material; they do not imply that every component is exemplary. Historical status is stated explicitly. A last-push date is only an observation from GitHub metadata, never sufficient evidence for C4.

## Native engraving libraries and full-score typesetters

### 1. [lilypond/lilypond](https://github.com/lilypond/lilypond)

**Language/role:** C++ and Scheme; programmable batch music typesetter. **Official project mirror:** this GitHub repository identifies itself as a mirror; development and issue handling take place on GitLab, with the official repository also identified at GNU Savannah.

Study how a notation language becomes timed events and then graphical objects, with musical policy partly implemented in Scheme. The [architecture guide](https://lilypond.org/doc/v2.24/Documentation/contributor/overview-of-lilypond-architecture) separates parsing, iteration through musical time, and translation through `Engraver` and `Performer` classes.

- **C1:** [Optimal page breaking](https://github.com/lilypond/lilypond/blob/master/lily/optimal-page-breaking.cc) searches line configurations and page-spacing costs while handling forced page counts, conflicting systems-per-page settings, and invalid counts. This is a useful example of global constraints overriding locally attractive line breaks.
- **C2:** The iterator/context/translator split and Scheme extension mechanism support different notation behaviors and graphical versus MIDI output without making the parser responsible for all presentation decisions.
- **C4:** [Release notes](https://github.com/lilypond/lilypond/releases) document development since the October 2022 stable branch, continued 2.24 score compatibility, and Guile/Ghostscript adaptations. The [regression-testing chapter](https://github.com/lilypond/lilypond/blob/master/Documentation/en/contributor/regressions.itexi) explains visual comparisons between versions and tests added for features and fixes.

**Start with:** the architecture guide, then `optimal-page-breaking.cc`.

### 2. [musescore/MuseScore](https://github.com/musescore/MuseScore)

**Language/role:** C++ with Qt-facing application code; interactive scorewriter. The relevant monorepo subsystem is `src/engraving`, particularly its score DOM and rendering passes.

Study the negotiation between rhythmic spacing, geometric collisions, and the dimensions of an editable page. This engine exposes the uncomfortable cases that simplified renderers omit: cross-staff stems, lyrics near barlines, invisible elements, and space that is insufficient to satisfy every constraint.

- **C1:** [Horizontal spacing](https://github.com/musescore/MuseScore/blob/main/src/engraving/rendering/score/horizontalspacing.cpp) combines minimum geometric distances with spring stretching. It handles cross-staff collisions and has an explicit final fallback allowing collisions when squeezing cannot make the system fit. Correctness here includes defined behavior for infeasible layouts.
- **C2:** [Score layout dispatch](https://github.com/musescore/MuseScore/blob/main/src/engraving/rendering/score/scorelayout.cpp) uses a common `LayoutContext`, normalizes requested tick ranges, handles empty scores, and delegates to page, horizontal, or vertical layout implementations. The same score model serves multiple presentation modes.

**Start with:** `horizontalspacing.cpp` and `scorelayout.cpp`. The entire application is counted once.

### 3. [rism-digital/verovio](https://github.com/rism-digital/verovio)

**Language/role:** C++; MEI-centered engraving library with SVG output, format importers, and multiple language bindings.

Study a document-tree engine that organizes engraving as successive traversals. Its repository describes MusicXML, Humdrum, ABC, and other import paths, but the especially useful engineering material is how the layout passes preserve their ordering dependencies.

- **C1:** [Page layout](https://github.com/rism-digital/verovio/blob/develop/src/page.cpp) first measures bounding boxes, adjusts colliding layers, places augmentation dots, then revisits layer collisions with dots included. Accidentals, grace notes, clef changes, lyrics, tuplets, and overflow receive distinct passes. Reordering these operations would change their input assumptions.
- **C2:** The same implementation combines a document model, visitor-like functors, and a `BBoxDeviceContext` that measures through the drawing interface. This separates musical transformations from output-device operations and supports native and bound-library use.
- **C3:** The page implementation records completed layout and offers restoration of cached horizontal layout, providing concrete reuse mechanisms rather than only a speed claim.

**Start with:** `src/page.cpp` and the [MEI round-trip test driver](https://github.com/rism-digital/verovio/blob/develop/doc/test-suite-roundtrip.py), which reloads and compares structured XML output.

### 4. [grame-cncm/guidolib](https://github.com/grame-cncm/guidolib)

**Language/role:** C++; GUIDO notation language and embeddable score-layout engine.

Study the boundary between abstract musical representation, graphical representation, and platform graphics. The repository contains the engine, language support, platform integrations, and regression infrastructure; it is not merely a viewer around another engraver.

- **C1:** [Space-force functions](https://github.com/grame-cncm/guidolib/blob/dev/src/engine/graphic/GRSpaceForceFunction.cpp) maintain ordered force entries as springs are added or removed, update associated extents, and treat zero-force springs specially. This makes numerical spacing invariants and degeneracies unusually explicit.
- **C2:** The [graphics-device design note](https://github.com/grame-cncm/guidolib/blob/dev/doc/graphicdevices.txt) explains replacing Windows device handles with the pure-virtual `VGDevice` abstraction. Clients supply drawing implementations, while font-independent music-symbol identifiers remain distinct from ordinary text characters.

**Start with:** `doc/graphicdevices.txt`, then `GRSpaceForceFunction.cpp`. The latter includes legacy and disabled paths, so it is a study of accumulated engineering decisions, not uniformly clean modern C++.

### 5. [lenmus/lomse](https://github.com/lenmus/lomse)

**Language/role:** C++; embeddable score rendering, editing, and playback library. Its documentation describes it as a work in progress before version 1.0; GitHub metadata showed its last push in 2024.

Study how an engraving library can leave window ownership to its host application while retaining rich document and interaction semantics. Scores can coexist with other document elements and be rendered through different view arrangements.

- **C1:** The [Gourlay spacing implementation](https://github.com/lenmus/lomse/blob/master/src/graphic_model/layouters/lomse_spacing_algorithm_gourlay.cpp) represents time slices, minimum spacing rods, springs, and column spacing functions. System justification refines an approximate force when needed, and line penalties measure the departure from preferred spacing.
- **C2:** The [rendering overview](https://github.com/lenmus/lomse/blob/master/docs/api/mainpages/render-overview.h) documents `Document`, `View`, `Interactor`, and `Presenter`, including ownership and multiple views of one document. The host supplies display/buffer integration; the library supplies score layout and interaction.

**Start with:** the rendering overview and `lomse_spacing_algorithm_gourlay.cpp`.

### 6. [andigamesandmusic/belle](https://github.com/andigamesandmusic/belle)

**Language/role:** C++; graph-based music engraving and vector-graphics library. **Snapshot caveat:** the inspected repository has a single published commit; its README describes a much longer prior development history, which is not treated as C4 evidence.

Belle offers a substantially different model: musical events occupy connected “islands,” rendered graphics become reusable stamps, and musical concepts are represented through MICA data. Its README also candidly describes the engraver as unfinished.

- **C1:** [Spring-network solving](https://github.com/andigamesandmusic/belle/blob/main/include/belle-springs.h) fixes endpoint anchors, constructs a coefficient matrix, bounds spring coefficients, and applies numerical stabilization. The [spacing layer](https://github.com/andigamesandmusic/belle/blob/main/include/belle-spacing.h) derives rhythm-sensitive springs and explicitly falls back when the solver fails.
- **C2:** Graph relations, musical concept data, vector stamps, and device-independent output provide reusable layers for interactive applications and printed scores. The spacing code operates on music nodes and instants rather than hard-coding a single sequence of bars.

**Start with:** `belle-spacing.h` and `belle-springs.h`.

## Browser and interactive rendering systems

### 7. [vexflow/vexflow](https://github.com/vexflow/vexflow)

**Language/role:** TypeScript; reusable notation primitives and layout for Canvas and SVG, in browsers and Node.js.

Study the engine beneath many higher-level browser score systems. This entry covers the VexFlow 5+ lineage. The [project history note](https://github.com/vexflow/vexflow/blob/main/VEXFLOW.md) explicitly distinguishes it from `0xfe/vexflow`, which hosts the earlier 4.x lineage; those are not counted twice here.

- **C1:** The [formatter](https://github.com/vexflow/vexflow/blob/main/src/formatter.ts) aligns voices through rational-valued ticks, assigns minimum widths from notes and modifiers, then distributes available space. Its implementation also estimates spacing deviations and handles rest alignment. Shared musical time and glyph geometry must remain consistent across staves.
- **C2:** The repository exposes both individual stave/note/context primitives and higher-level `Factory`, `EasyScore`, and system construction. The formatter accepts multiple voice and note types rather than requiring a particular interchange format or editor.

**Start with:** `src/formatter.ts` and `VEXFLOW.md` for the implementation and lineage boundaries.

### 8. [opensheetmusicdisplay/opensheetmusicdisplay](https://github.com/opensheetmusicdisplay/opensheetmusicdisplay)

**Language/role:** TypeScript; MusicXML-to-browser score layout built on VexFlow. It contributes substantial score-level layout and semantic processing, so it is more than a thin rendering wrapper.

Study what a full-score layer must add above low-level engraving primitives: graphical score construction, expression placement, system coordination, and geometry suitable for interaction.

- **C1:** [MusicSheetCalculator](https://github.com/opensheetmusicdisplay/opensheetmusicdisplay/blob/develop/src/MusicalScore/Graphical/MusicSheetCalculator.ts) places lyrics and chord symbols against staff skyline/bottom-line geometry, including handling labels whose visible bounds differ from their margins.
- **C2:** Semantic and graphical score representations are separated, with injectable graphical-symbol, text-measurement, and transposition services and explicit engraving rules.
- **C3:** The [batch skyline calculator](https://github.com/opensheetmusicdisplay/opensheetmusicdisplay/blob/develop/src/MusicalScore/Graphical/SkyBottomLineBatchCalculator.ts) groups compatible work and selects a WebGL backend with a plain-backend fallback. The score calculator also caches stable interior-system skyline results during lazy rendering.

**Start with:** `MusicSheetCalculator.ts` and `SkyBottomLineBatchCalculator.ts`.

### 9. [paulrosen/abcjs](https://github.com/paulrosen/abcjs)

**Language/role:** JavaScript; ABC parsing, SVG engraving, and browser interaction.

Study a compact, documented rendering pipeline whose intermediate elements retain a relationship to the parsed music. The [engraver architecture document](https://github.com/paulrosen/abcjs/blob/main/src/write/README.md) separates element creation, layout, and drawing, with interaction information attached along the way.

- **C1:** [Staff-group layout](https://github.com/paulrosen/abcjs/blob/main/src/write/layout/staff-group.js) synchronizes voices at common durations, explicitly tolerates floating-point inexactness, shifts already placed voices when another needs more room, and accounts for spacing already consumed by other voices. Zero-duration items are ordered before notes through a separate duration-index adjustment.
- **C2:** “Absolute” elements group items that move together, while “relative” elements represent their constituent glyphs. Horizontal and vertical layout complete before the drawing pass, making musical grouping and SVG emission separate responsibilities.

**Start with:** `src/write/README.md` and `src/write/layout/staff-group.js`.

### 10. [CoderLine/alphaTab](https://github.com/CoderLine/alphaTab)

**Language/role:** TypeScript-centered cross-platform notation and guitar-tablature library. The relevant monorepo subsystem is `packages/alphatab/src/rendering`.

Study the coordination of different notation styles, rendering backends, layout modes, and interactive geometry. The current source tree includes standard, tablature, slash, and numbered-notation bar renderers.

- **C2:** [ScoreRenderer](https://github.com/CoderLine/alphaTab/blob/develop/packages/alphatab/src/rendering/ScoreRenderer.ts) obtains separate canvas and layout implementations through factories. [ScoreLayout](https://github.com/CoderLine/alphaTab/blob/develop/packages/alphatab/src/rendering/layout/ScoreLayout.ts) provides the common layout-engine boundary and bar-renderer lookup infrastructure.
- **C3:** Rendering supports lazy partial requests and an optimized resize path. Partial updates preserve the bounds of unaffected bars. Completion events are deliberately emitted after profiling scopes close because listeners may immediately initiate another render—an instructive interaction between performance instrumentation and reentrancy.

**Start with:** `ScoreRenderer.ts` and `rendering/layout/ScoreLayout.ts`. These are implementation mechanisms, not independently measured latency guarantees.

### 11. [Smoosic/Smoosic](https://github.com/Smoosic/Smoosic)

**Language/role:** TypeScript; browser notation editor and reusable library, using its own VexFlow branch. This is the current organizational repository identified by the old personal repository's migration notice.

Study the work between an editable musical-object model and a glyph engine: measure-column estimates, page/system layout, editing state, and deferred rendering. Its VexFlow fork is not counted as another independent project.

- **C2:** The [layout formatter](https://github.com/Smoosic/Smoosic/blob/main/src/render/sui/formatter.ts) groups measures by score column, computes common widths across staves, estimates vertical extents, and applies page/layout settings above the underlying glyph renderer. This is substantial score-level abstraction supporting application and library use.
- **C3:** [Render-state management](https://github.com/Smoosic/Smoosic/blob/main/src/render/sui/renderState.ts) distinguishes complete rendering from replacing changed measures. It maintains a replacement queue, guards overlapping redraw work, waits for idle time before full layout, and provides promises for a sufficiently rendered state.

**Start with:** `formatter.ts` and `renderState.ts`. The older `AaronDavidNewman/Smoosic` repository is deliberately excluded from the count.

### 12. [jocelyn-stericker/satie](https://github.com/jocelyn-stericker/satie)

**Language/role:** TypeScript and React; MusicXML engraving and patch-based editing with SVG output. **Historical:** the former `jnetterf/satie` URL resolves to this owner; GitHub metadata reports a last push in 2017.

Study an unusually explicit model of incremental engraving. Its value is the validation and invalidation design, not an assumption that its old frontend dependencies are suitable for a new deployment.

- **C1:** The [engine design document](https://github.com/jocelyn-stericker/satie/blob/master/src/engine/README.md) specifies unvalidated, validated, and rendered states. Models must not mutate based on unrelated contents of their current line; line-dependent information belongs in layouts. Moving a measure between lines has different invalidation consequences from editing its contents.
- **C2:** Musical models, layouts, contextual attributes, MusicXML import, and React/SVG views have separate roles; the engine handles merging voices and cross-staff notation above individual models.
- **C3:** Validated layouts are memoized. The document connects invalidation scope to the cost of updating affected lines, giving a concrete performance rationale for the model/layout boundary.

**Start with:** the engine design document and the [engine source directory](https://github.com/jocelyn-stericker/satie/tree/master/src/engine).

## Chant and tradition-specific engraving

### 13. [gregorio-project/gregorio](https://github.com/gregorio-project/gregorio)

**Language/role:** C, TeX, and Lua; GABC-to-GregorioTeX pipeline for Gregorian chant publications.

Study a specialized engraver that cooperates with a general typesetting system. Musical syllables, chant glyphs, text shaping, and TeX line breaking must agree despite being implemented in different layers.

- **C1:** [Syllable processing](https://github.com/gregorio-project/gregorio/blob/develop/tex/gregoriotex-syllable.lua) stores separate minimum text and note distances, traverses discretionary-node alternatives, reshapes text for ligatures and kerning, and adjusts inter-syllable glue. These operations couple linguistic and musical geometry.
- **C2:** The C converter emits a TeX-facing representation, while Lua/TeX supplies document integration and detailed layout controls, supporting individual scores and larger books without embedding a complete document editor.
- **C4:** The [changelog](https://github.com/gregorio-project/gregorio/blob/develop/CHANGELOG.md) spans releases from the 2010s through 2026 and records TeX Live integration, compatibility defaults, package conflicts, compiler portability, and spacing fixes. It also explicitly warns that 6.2.0 was not released to CTAN and is incompatible with CTAN's 6.1.0; consumers should read that qualification.

**Start with:** `gregoriotex-syllable.lua` and `CHANGELOG.md`.

### 14. [frmatthew/exsurge](https://github.com/frmatthew/exsurge)

**Language/role:** JavaScript; GABC-based square-note chant renderer. **Historical:** GitHub metadata reports a last push in 2017; the README describes its tests and API reference as unfinished.

Study direct browser chant engraving independent of Gregorio's TeX pipeline. The public API separates `ChantContext`, `ChantScore`, layout, line arrangement, and drawable creation.

- **C1:** [Chant-line implementation](https://github.com/frmatthew/exsurge/blob/master/src/Exsurge.Chant.ChantLine.js) accumulates notation bounds, includes clefs and custodes, aligns multiple lyric tracks by their largest height/baseline requirements, and incorporates braces and initials into line geometry. Chant-specific boundary symbols affect available space and vertical extents.
- **C2:** The [source modules](https://github.com/frmatthew/exsurge/tree/master/src) separate GABC handling, neumes, markings, signs, text, drawing, and core geometry. This supports embedding chant in web applications without requiring the surrounding score editor or a TeX installation.

**Start with:** `Exsurge.Chant.ChantLine.js` and the module directory. Retained for substantive specialized layout code, with no C4 claim.

### 15. [neanes/neanes](https://github.com/neanes/neanes)

**Language/role:** TypeScript and Vue/Electron; Byzantine chant scorewriter with its own layout service.

Study the adaptation of paragraph optimization to a different musical tradition. This is especially useful for understanding why Western staff notation is not a universal score model.

- **C1:** The [line-breaking design](https://github.com/neanes/neanes/blob/master/notes/knuth_plass.md) encodes neumes, lyric collisions, melismas, martyrias, and prohibited breaks using boxes, glue, and penalties. The [implementation](https://github.com/neanes/neanes/blob/master/src/services/LayoutService.ts) preserves space for transferred barlines and carries lyric overhang across boundaries; it distinguishes soft penalties from absolute break prohibitions.
- **C3:** The design uses dynamic programming to choose breakpoints, while the implementation caches text widths, neume widths, and ink bounds and bounds adjustment-ratio search. Those are concrete responses to the cost of repeated layout in an interactive scorewriter.

**Start with:** `notes/knuth_plass.md` and `LayoutService.ts`. The separately inspected [layout tests](https://github.com/neanes/neanes/blob/master/src/services/LayoutService.test.ts) include adjacent-melisma, penalty-cap, prohibited-break, and Greek-hyphen cases; tests were read, not executed.

## ABC batch engraving and lead-sheet composition

### 16. [lewdlime/abcm2ps](https://github.com/lewdlime/abcm2ps)

**Language/role:** C; ABC-to-PostScript/SVG batch engraver. **Archived and end of life:** the repository explicitly names abc2svg as its successor. The older `leesavide/abcm2ps` URL redirects here.

Study a traditional procedural implementation with substantial multi-voice engraving logic. Its original use case—independent voices on multiple organ keyboards and pedal staff—helps explain why its data model is richer than a single melody renderer.

- **C1:** [Music layout](https://github.com/lewdlime/abcm2ps/blob/master/music.c) computes symbol widths across rhythmic sequences, manages floating voices and clefs, sets stems in multi-voice contexts, and adjusts rests when voices share a staff. Musical state and geometry interact across both tune and line boundaries.
- **C2:** The [shared representation](https://github.com/lewdlime/abcm2ps/blob/master/abcm2ps.h) defines symbols, voices, systems, formatting, and tablature structures used across parsing, layout, and output modules. This supports multiple staves, voice arrangements, and PostScript/SVG output rather than one fixed notation template.

**Start with:** `music.c` and `abcm2ps.h`. Retained as an archival algorithmic study, not a maintained dependency recommendation.

### 17. [ChordPro/chordpro](https://github.com/ChordPro/chordpro)

**Language/role:** Perl; reference ChordPro implementation and lead-sheet/songbook typesetter. Its category fit is chord/lyric notation and page composition; embedded staff notation is delegated to external engines.

Study how a text-oriented musical format becomes printable pages when chord positions, text markup, font metrics, diagrams, and wrapping must remain coordinated.

- **C1:** [PDF song layout](https://github.com/ChordPro/chordpro/blob/master/lib/ChordPro/Output/PDF/Song.pm) keeps chord and lyric baselines distinct, calculates font-dependent placement, propagates markup across fragments, and returns remaining text for continuation. Chords above, below, inline, or in a separate column change the layout constraints.
- **C2:** Parsed song/songbook data feeds separate output modules, and the [delegate interface](https://www.chordpro.org/chordpro/chordpro-configuration-delegates/) converts embedded ABC or LilyPond sections into images through configurable handlers. This allows a lead-sheet engine to compose richer musical documents without implementing every notation grammar itself.

**Start with:** `Output/PDF/Song.pm` and the delegate documentation. The bundled/delegated ABC engine is not counted as a separate repository.

## Desktop editors with substantial layout subsystems

### 18. [helge17/tuxguitar](https://github.com/helge17/tuxguitar)

**Language/role:** Java; multitrack tablature editor and player. The relevant subsystem is the shared `common/TuxGuitar-lib` graphics code, connected to desktop editor controls.

Study how standard notation and guitar tablature share a musical model while offering different presentation and interaction needs. The repository also contains multiple UI-toolkit and export modules, but this entry focuses on layout rather than playback backends.

- **C2:** [TGLayout](https://github.com/helge17/tuxguitar/blob/master/common/TuxGuitar-lib/src/main/java/app/tuxguitar/graphics/control/TGLayout.java) provides common layout, painting, resources, score/tab display modes, and measure-update behavior. The desktop [Tablature controller](https://github.com/helge17/tuxguitar/blob/master/desktop/TuxGuitar/src/app/tuxguitar/app/view/component/tab/Tablature.java) connects that layer to horizontal/vertical views, carets, selections, and abstract painters.
- **C3:** `updateMeasureNumbers` collects changed measure headers and registered dependants, removes duplicates, sorts them, and updates the selected measures rather than always rebuilding the song. Resource disposal is coordinated separately by the controller. This makes dependency-aware incremental layout directly inspectable.

**Start with:** `TGLayout.java` and `Tablature.java`. The monorepo counts once.

### 19. [Xenoage/Zong](https://github.com/Xenoage/Zong)

**Language/role:** Java and Kotlin; music notation framework/editor with independent layout and renderer modules. **Historical:** GitHub metadata reports a last push in 2018. The default `kotlin` branch documents an unfinished Java-to-Kotlin conversion.

Study a strongly staged layout architecture, while treating buildability of this transitional branch as unverified. Its README points to visual reports based on the Unofficial MusicXML Test Suite, but that alone is not used to award C4.

- **C1:** [ScoreLayouter](https://github.com/Xenoage/Zong/blob/kotlin/layout/src/com/xenoage/zong/musiclayout/layouter/ScoreLayouter.java) deliberately postpones beam spacing until both horizontal and vertical positions are fixed, because beam slants depend on final geometry. Continued elements are carried from one frame into the next, and layout exceptions yield an error layout.
- **C2:** Notation calculation, measure-column spacing, frame/system breaking, horizontal filling, vertical filling, beam placement, and stamping are separate responsibilities. Target-specific `SystemFiller` and `FrameFiller` strategies illustrate reusable layout policy.

**Start with:** `ScoreLayouter.java` and the [music-layout subsystem](https://github.com/Xenoage/Zong/tree/kotlin/layout/src/com/xenoage/zong/musiclayout).

### 20. [robert-strandh/Gsharp](https://github.com/robert-strandh/Gsharp)

**Language/role:** Common Lisp; interactive score editor with custom engraving and redisplay. **Historical:** GitHub metadata reports a last push in 2021; some design documents explicitly describe unimplemented features.

Study the tension between globally good pagination and locally responsive editing. Its value includes a mathematical design discussion alongside the implementation, rather than only API documentation.

- **C1:** The [line-breaking design](https://github.com/robert-strandh/Gsharp/blob/master/Doc/linebreak.tex) explains why page-count constraints and material far ahead in the score can change earlier breaks. It formalizes rhythmic spacing and separates musical measures, lines, and pages rather than treating layout as a greedy walk.
- **C3:** The same document develops incremental dynamic programming around modified segments, aiming to keep unavoidable global work inexpensive while restricting costly recomputation. These are design arguments, not verified throughput measurements.
- **C2:** The [model document](https://github.com/robert-strandh/Gsharp/blob/master/Doc/model.tex) distinguishes buffers, segments, temporally overlapping layers, and note clusters. Its explicit implementation caveats make it useful for comparing the intended abstraction with the realized editor.

**Start with:** `Doc/linebreak.tex` and `Doc/model.tex`.

## Search coverage and limitations

Discovery used more than six distinct live-search formulations, including general engraving architecture; C++ GUIDO/Lomse-style libraries; TypeScript/VexFlow/ABC rendering; Rust, Go, and Haskell implementations; Gregorian chant; guitar tablature; Java/Kotlin MusicXML layout; Common Lisp score editing; graph-based engraving; ChordPro/ABC integration; and Carnatic, numbered, and Byzantine notation. Later general and language-specific searches increasingly returned bindings, applications around already identified engines, tutorials, or duplicate lineages. The Byzantine search added Neanes and materially widened tradition coverage.

Every retained canonical GitHub repository was opened directly or checked through the GitHub API. Each was also checked against separate primary architecture, implementation, or testing material; raw copies of the root README were not counted as independent evidence. GitHub API rate limiting was worked around by reading public repository pages and individual source files. The linked branch paths were verified during research and may evolve afterward.

Important selection boundaries:

- **Moved projects:** [moinejf/abc2svg](https://github.com/moinejf/abc2svg) explicitly says it moved to ChiselApp; no substantive official GitHub mirror was established, so it is excluded. LilyPond remains because its project GitHub mirror contains the actual source. Smoosic's old personal repository was replaced with its organizational repository.
- **Related lineages:** VexFlow's earlier repository and Smoosic's VexFlow fork are not additional entries. OSMD and Smoosic qualify through their own substantial score-level layout and editing infrastructure.
- **Adjacent domains:** music-theory/composition toolkits, MusicXML/MEI schemas, SMuFL font specifications, recognition systems, score archives, and thin Verovio bindings were not counted as engraving engines. Search results for editor integrations did not substitute for independent layout implementations.
- **Smaller candidates:** Carnot's repository, parser, and SVG renderer were inspected. Its alpha Carnatic renderer is relevant, but was left outside the main selection in favor of codebases with broader implementation material. Jianpu and Rust results included wrappers and small applications; language or tradition diversity was not treated as sufficient qualification on its own.
- **Historical material:** abcm2ps is archived/end of life; Satie, Exsurge, Zong, and Gsharp are historical study candidates; Belle is a published snapshot. Their inclusion rests on concrete architecture or algorithms, not an assumption of ongoing maintenance. Lomse's pre-1.0 documentation and older observed push are also noted.

No candidate code was run, dependencies installed, repositories cloned, or external services modified. Tests and performance mechanisms were inspected but not executed or benchmarked. This is a source-based selection guide, with stronger coverage of Western staff notation and chant than of every global notation tradition.
