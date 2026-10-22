# Computer-aided manufacturing and toolpath generation systems

Research date: **2026-10-09**. This selection covers 20 GitHub repositories implementing machining geometry, CAM applications, PCB isolation routing, laser job preparation, and additive manufacturing toolpaths. Additive systems are included when they compute deposition paths or scan vectors; generic CAD, firmware, G-code senders, and visualization-only tools are outside the selection. FreeCAD and GridSpace are counted once each, with their relevant subsystems identified below.

The criteria are engineering assessments grounded in the linked implementation and documentation, not certifications of output correctness or uniform code quality. Sources were inspected without building or running candidate software. Source links follow the indicated branches and may change after this research date.

- **C1 — Correctness:** difficult geometry, numerical semantics, state invariants, concurrency, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable models, interfaces, or algorithms supporting different operations and machines.
- **C3 — Performance:** concrete computational or machine-time constraints addressed through an understandable architecture.
- **C4 — Evolution:** sustained development accompanied by compatibility work, testing, or explicit complexity management; age alone does not qualify.

## Machining kernels and reusable geometry

### 1. [aewallin/opencamlib](https://github.com/aewallin/opencamlib)

**Language/role:** C++ machining kernel with Python and JavaScript bindings. Study the separation of cutter geometry from drop-cutter and push-cutter algorithms used to produce three-dimensional milling paths.

- **C1:** The cutter interface decomposes contact into triangle vertices, edges, and facets. Drop operations raise the cutter location to avoid cutting the model, while push operations accumulate intervals where the cutter would gouge it. These are explicit geometric contracts, not merely mesh visualization. **C2:** The same template-method interface supports different cutter shapes and offset cutters. Start with [`millingcutter.hpp`](https://github.com/aewallin/opencamlib/blob/master/src/cutters/millingcutter.hpp).
- **C3:** [`batchdropcutter.cpp`](https://github.com/aewallin/opencamlib/blob/master/src/dropcutter/batchdropcutter.cpp) makes the optimization progression unusually readable: exhaustive triangle testing, XY KD-tree candidate selection, overlap/height rejection, and OpenMP work sharing. This is a useful place to study how a geometric kernel exposes and reduces its expensive primitive operations.

### 2. [aewallin/openvoronoi](https://github.com/aewallin/openvoronoi)

**Language/role:** C++ with Python bindings; incremental Voronoi geometry motivated by CNC offset generation. Particularly useful for studying topology-preserving geometric algorithms beneath a CAM application.

- **C1:** [`checker.cpp`](https://github.com/aewallin/openvoronoi/blob/master/src/checker.cpp) checks vertex degree against vertex type and supplies face-connectivity and vertex-state checks. It also exposes limitations: the face-count-versus-generator-count check is a stub. The presence of checkers is evidence of difficult invariants, not a claim that all invariants are enforced.
- **C2:** [`offset.hpp`](https://github.com/aewallin/openvoronoi/blob/master/src/offset.hpp) defines closed offset loops containing line or circular-arc elements. Filtering the diagram controls inside/outside generation separately from walking offsets. This gives reusable topology, filtering, and curve-output layers rather than a single hard-coded pocketing script.

### 3. [Heeks/libarea](https://github.com/Heeks/libarea)

**Language/role:** C++ library and Python module for planar profiling and pocketing. A legacy Heeks-family implementation, included for its compact treatment of islands, offsets, and linked pocket curves; current active maintenance is not asserted.

- **C1:** [`AreaPocket.cpp`](https://github.com/Heeks/libarea/blob/master/AreaPocket.cpp) builds a curve tree, repeatedly offsets regions, detects when island offsets stop remaining inside a region, subtracts them, and links inner curves through chosen points. Connectivity changes as offsets meet are the central difficulty.
- **C2:** [`Area.h`](https://github.com/Heeks/libarea/blob/master/Area.h) separates area booleans, offsets, arc fitting, region splitting, and pocket-toolpath generation. Pocket parameters cover tool radius, stock allowance, stepover, direction, and multiple fill modes. Engineers can study both the reusable API and its older design tradeoffs, including global accuracy, unit, progress, and cancellation state.

### 4. [dubstar-04/LibLathe](https://github.com/dubstar-04/LibLathe)

**Language/role:** Python operation layer with C++ geometry in the inspected `main` branch; CNC turning paths and G-code. Adds lathe-specific concerns that are largely absent from milling-centric libraries.

- **C1:** [`rough.py`](https://github.com/dubstar-04/LibLathe/blob/main/liblathe/op/rough.py) removes unsuitable turning features, offsets the remaining profile for stock allowance, sorts intersections along roughing passes, inserts lead moves, and rejects a generated path when it intersects the internal part offset. The explicit tolerances and implementation TODOs are useful review material.
- **C2:** Operations consume shared points, segments, segment groups, stock, and tool geometry before a separate path object emits G-code. [`segmentgroup.cpp`](https://github.com/dubstar-04/LibLathe/blob/main/liblathe/base/segmentgroup.cpp) provides bounds, intersections, offsets, and defeaturing; its offset implementation uses a quadtree followed by point simplification. This is a substantive geometry/operation boundary, rather than a formatter around an external CAM engine.

## Desktop machining applications

### 5. [FreeCAD/FreeCAD](https://github.com/FreeCAD/FreeCAD)

**Language/role:** C++ and Python; specifically the **CAM workbench**, under `src/Mod/CAM`. Study how manufacturing operations live inside a parametric CAD document.

- **C2:** The [CAM workbench guide](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/CAM_Workbench.md) describes jobs containing stock, tools, ordered operations, and dressups. Operations produce an internal machine-independent command dialect, with controller dialects and output units handled during postprocessing. That separation supports operation reuse across machines.
- **C1:** [`linking.py`](https://github.com/FreeCAD/FreeCAD/blob/main/src/Mod/CAM/Path/Base/Generator/linking.py) generates connecting moves by trying candidate clearance heights and checking a wire, cutter diameter, or tool shape against supplied solids. It rejects negative retract offsets and reports failure when no collision-free connection is found. The corresponding [linking tests](https://github.com/FreeCAD/FreeCAD/blob/main/src/Mod/CAM/CAMTests/TestLinkingGenerator.py) exercise blocked gaps, tolerances, and null geometry. This is a local generator capability, not a claim of automatic whole-machine or fixture collision certification.

### 6. [SebKuzminsky/pycam](https://github.com/SebKuzminsky/pycam)

**Language/role:** Python three-axis CAM application and scripted toolpath pipeline. An older codebase: GitHub metadata showed the latest push in January 2024, so ongoing active development is not assumed. Its relatively direct algorithms remain valuable for study.

- **C1:** [`PathGenerators/__init__.py`](https://github.com/SebKuzminsky/pycam/blob/master/pycam/PathGenerators/__init__.py) restricts collision candidates by the cutter's bounds, finds a permitted contact height, returns an explicit failure value above the allowed Z range, and recursively inserts samples when midpoint heights are not collinear.
- **C2:** Cutter objects, models, motion grids, and emitted motion steps are separate inputs/outputs. **C3:** [`DropCutter.py`](https://github.com/SebKuzminsky/pycam/blob/master/pycam/PathGenerators/DropCutter.py) distributes grid lines through a multiprocessing-compatible worker, reports progress, honors cancellation, and converts unavailable heights into safety moves. It shows how numerical sampling, parallel execution, and application responsiveness meet in a small module.

### 7. [vilemduha/blendercam](https://github.com/vilemduha/blendercam)

**Language/role:** Python; the **Fabex** CAM extension, formerly BlenderCAM. Useful for studying manufacturing operations integrated with a general-purpose scene and mesh environment.

- **C2:** [`toolpath.py`](https://github.com/vilemduha/blendercam/blob/master/fabex/toolpath.py) dispatches distinct machining strategies, manages operation sources and cache invalidation flags, checks machine feed limits, and separates toolpath generation from G-code export. It distinguishes ordinary three-axis, four-axis, and indexed orientation workflows; the indexed handling should not be mistaken for general simultaneous five-axis machining.
- **C1:** [`strategies/parallel.py`](https://github.com/vilemduha/blendercam/blob/master/fabex/strategies/parallel.py) composes a sampling pattern, depth layers, sampled chunks, chunk ordering, ramping, and holding bridges. These stages must preserve both surface constraints and intentional uncut material. The [testing guide](https://github.com/vilemduha/blendercam/blob/master/docs/testing.md) documents operation-based regression comparisons between generated and reference G-code, providing a concrete way to examine behavior across changes.

### 8. [Heeks/heekscnc](https://github.com/Heeks/heekscnc)

**Language/role:** C++ CAD integration plus Python toolpath and postprocessor code. A legacy CAM add-on for HeeksCAD, distinct from both `heekscnc-old` and Dan Heeks's separately named experimental PyCAM. The inspected build documentation still targets an older wxWidgets stack; treat it as historical engineering material.

- **C1:** [`area_funcs.py`](https://github.com/Heeks/heekscnc/blob/master/area_funcs.py) combines depth passes, pocket offsets, climb/conventional direction, ramp or helix entry, and clearance moves. Its keep-tool-down test constructs the swept planar footprint of a connecting move and subtracts the permitted area before deciding whether retraction is needed.
- **C2:** [`nc/nc.py`](https://github.com/Heeks/heekscnc/blob/master/nc/nc.py) defines a controller-independent creator interface covering coordinate modes, tools, feeds, arcs, workplanes, and cycles. Studying this alongside the pocket code reveals the boundary between geometric strategy and machine-language generation. Its separate use of libarea and OpenCAMLib is documented in the repository README.

## Browser CAM and planar/PCB workflows

### 9. [GridSpace/grid-apps](https://github.com/GridSpace/grid-apps)

**Language/role:** Primarily JavaScript; specifically **Kiri:Moto**, including `src/kiri/mode/cam`. The monorepo also contains other applications, which are not additional entries here.

- **C1:** [`prepare.js`](https://github.com/GridSpace/grid-apps/blob/master/src/kiri/mode/cam/work/prepare.js) sequences safe-height moves around operation/rotary-angle changes, checks travel against pocket boundaries, and changes below-stock descent into cutting motion where required. It also manages tool/feed state and work/widget coordinate conversion. This is a useful integration point for studying how otherwise valid cuts become a coherent machining program.
- **C3:** [`topo3.js`](https://github.com/GridSpace/grid-apps/blob/master/src/kiri/mode/cam/work/topo3.js) shards terrain rasterization, shares/caches mesh vertices with worker “minions,” and merges results for contour clipping. This provides inspectable performance structure for browser-based surface machining. The [release history](https://github.com/GridSpace/grid-apps/releases) also records concrete memory, geometry-tolerance, and CAM routing fixes; no numerical speedup is assumed here.

### 10. [tbfleming/jscut](https://github.com/tbfleming/jscut)

**Language/role:** JavaScript with C++ support; a browser CAM predecessor. **Historical:** its README explicitly names LaserWeb4 as its successor and says new features are no longer added. The relevant branch is `gh-pages`, not the stale `master` branch.

- **C1:** [`js/Cam.js`](https://github.com/tbfleming/jscut/blob/gh-pages/js/Cam.js) clips candidate connecting segments against allowed regions before merging paths. It records whether closing a path is safe without retracting, then uses that fact during G-code generation. Pocketing repeatedly offsets by cutter diameter and overlap, making geometric and traversal assumptions visible.
- **C2:** [`api/js/cam.js`](https://github.com/tbfleming/jscut/blob/gh-pages/api/js/cam.js) separates geometry combination, preview geometry, CAM paths, SVG conversion, and G-code output. Operations and tools are normalized independently, including unit conversion and inside/outside margins. Its compact embeddable API is the main reason to retain it alongside its more capable successor.

### 11. [multigcs/viaconstructor](https://github.com/multigcs/viaconstructor)

**Language/role:** Python desktop/headless CAM for DXF, SVG, HPGL, and other planar inputs. A smaller application with substantial geometry and machine-output logic.

- **C1:** [`calc.py`](https://github.com/multigcs/viaconstructor/blob/main/viaconstructor/calc.py) determines nesting among closed objects and uses containment parity to choose automatic inside/outside cutter offsets. It separately tracks inner objects and excludes tab/break geometry from that relationship construction.
- **C2:** [`machine_cmd.py`](https://github.com/multigcs/viaconstructor/blob/main/viaconstructor/machine_cmd.py) defines a postprocessor interface for moves, arcs, tools, units, coolant, and spindle state, then translates machining polylines through it. The same module selects pending paths by nesting level, tool, inside-out pocket constraints, endpoint distance, and whether reversal is allowed. This makes it a useful study of small-application architecture where geometric ordering and output dialects remain distinguishable.

### 12. [pcb2gcode/pcb2gcode](https://github.com/pcb2gcode/pcb2gcode)

**Language/role:** C++ command-line CAM for Gerber isolation milling, board routing, and drilling. Particularly strong material for constrained graph optimization rather than only polygon offsets.

- **C1:** [`eulerian_paths.cpp`](https://github.com/pcb2gcode/pcb2gcode/blob/master/src/eulerian_paths.cpp) handles a mixture of reversible and directed milling paths. It converts directions, accounts for self-loops, reasons about vertex in/out balance, and stitches residual loops using a Hierholzer-style traversal. Direction constraints make this more involved than a generic nearest-neighbor tour.
- **C3:** [`path_finding.cpp`](https://github.com/pcb2gcode/pcb2gcode/blob/master/src/path_finding.cpp) first tries a direct permitted connection, then uses A* with a maximum path length, cached surface queries, and a bounded search that can give up. It exposes the tradeoff between reducing physical travel/retractions and spending more computation finding permitted connections.

## Laser manufacturing preparation

### 13. [LaserWeb/LaserWeb4](https://github.com/LaserWeb/LaserWeb4)

**Language/role:** JavaScript web application for laser and milling CAM. The source branch is `dev-es6`; its binaries repository is packaging, not a separate codebase selected here.

- **C1:** [`cam-gcode-mill.js`](https://github.com/LaserWeb/LaserWeb4/blob/dev-es6/src/lib/cam-gcode-mill.js) splits paths at holding tabs, limits each depth pass, retracts for unsafe closures, and computes ramp feed from the required plunge time and available path length. It maintains explicit current/finished/next Z state while emitting commands.
- **C3:** The [G-code settings documentation](https://github.com/LaserWeb/LaserWeb4/wiki/3.3-Settings-Gcode) exposes generation concurrency and a curve-linearization factor as user-adjustable computation/precision tradeoffs. Together with the distinct operation-to-path and path-to-G-code functions, this is a concrete example of CAM performance choices surfacing in an application rather than remaining hidden implementation constants.

### 14. [meerk40t/meerk40t](https://github.com/meerk40t/meerk40t)

**Language/role:** Python laser design, planning, and device framework. **Maintenance mode:** the repository explicitly reports limited maintainer bandwidth; automated weekly builds are experimental snapshots, not evidence of production readiness.

- **C2:** [`core/cutplan.py`](https://github.com/meerk40t/meerk40t/blob/main/meerk40t/core/cutplan.py) describes and implements a pipeline from copied operations through scene-to-device preprocessing, validation, cutcode conversion, optimization, and spooling. Validation and optimization stages can enqueue further commands, and plan construction remains separate from final spool work.
- **C1:** The same implementation distinguishes containment-based inner-first constraints from travel optimization. It can optimize between grouped pieces while retaining required inner-before-outer cuts, or process containment hierarchies individually. This is a useful case study in preserving manufacturing semantics while reordering work. The repository's driver framework supplies the wider context for sharing that planner across different laser controllers.

### 15. [t-oster/VisiCut](https://github.com/t-oster/VisiCut)

**Language/role:** Java laser-job preparation application; uses LibLaserCut for device-level behavior. Study the mapping from artwork and material/process settings into machine jobs, rather than treating it as only a sender.

- **C2:** [`VisicutModel.java`](https://github.com/t-oster/VisiCut/blob/master/src/main/java/de/thomas_oster/visicut/VisicutModel.java) builds jobs from portable-file parts, graphic filters, laser profiles, material/focus settings, and device capabilities. The prepared job is reused for sending, saving, and time estimation.
- **C1:** [`VectorProfile.java`](https://github.com/t-oster/VisiCut/blob/master/src/main/java/de/thomas_oster/visicut/model/VectorProfile.java) transforms object coordinates into device pixels and delegates selectable vector ordering to the optimizer. It deliberately disables reordering for script-generated shapes, preserving the script's intended sequence. That exception illustrates why a manufacturing planner cannot apply a generic path optimizer indiscriminately.

## Additive manufacturing and explicit deposition paths

### 16. [Ultimaker/CuraEngine](https://github.com/Ultimaker/CuraEngine)

**Language/role:** C++ model-to-G-code engine, independently usable behind a front end. Selected instead of counting the Cura UI as another toolpath implementation.

- **C2:** The [pipeline documentation](https://ultimaker.github.io/CuraEngine/docs/pipeline.html) separates mesh slicing, feature areas, `LayerPlan` movement generation, thermal-command insertion, and G-code export. Temperature commands depend on estimated future path time, so geometric planning and process state have an explicit interface.
- **C3:** The same document describes producer/consumer overlap between stages to reduce memory overhead and support multithreaded processing. [Generating Paths](https://ultimaker.github.io/CuraEngine/docs/generating_paths.html) explains why printing order is determined before emitting paths, reducing storage while respecting mesh, layer, extruder, and feature ordering. It also describes shared infill machinery used for support, skin, and ironing. These documents are architectural entry points, not promises that every current strategy uses an identical algorithm.

### 17. [prusa3d/PrusaSlicer](https://github.com/prusa3d/PrusaSlicer)

**Language/role:** C++ FDM and mSLA preparation system. It is a substantive Slic3r descendant, not an independent origin; related Bambu/Orca/SuperSlicer forks are not counted again in this selection.

- **C1:** In the inspected default-branch [`Print.cpp`](https://github.com/prusa3d/PrusaSlicer/blob/master/src/libslic3r/src/libslic3r/Print.cpp), updating a print temporarily transforms instances into bed coordinates with scope-guarded restoration, validates extruder candidates and slicing inputs, distinguishes invalid/empty/changed states, and invalidates previews accordingly. This is rich material on correctness at the CAD/configuration/slicer boundary.
- **C4:** The [May 2019 2.0.0 release](https://github.com/prusa3d/PrusaSlicer/releases/tag/version_2.0.0) records project round-trip, localization, and regression fixes; the [2026 release history](https://github.com/prusa3d/PrusaSlicer/releases) documents the 3.0 alpha transition, separate configuration storage, legacy 3MF compatibility fixes, and worker failure handling. This is sustained complexity and compatibility management, not just a long commit history. The cited source layout follows the 3.0 development line, not the 2.9 stable layout.

### 18. [ORNLSlicer/ORNLSlicer](https://github.com/ORNLSlicer/ORNLSlicer)

**Language/role:** C++/Qt slicing and toolpath framework for additive processes including FDM and directed energy deposition. **Canonical rename:** the repository formerly called `Slicer-2` now identifies itself as ORNLSlicer.

- **C2:** The [slicing-pipeline architecture](https://github.com/ORNLSlicer/ORNLSlicer/blob/develop/docs/architecture/slicing-pipeline.md) separates parts, computable steps, islands, regions, paths, segments, and machine writers. It carefully documents exceptions: cylindrical layers own paths directly and image slicing does not use the ordinary toolpath hierarchy.
- **C3:** Dirty steps are queued onto worker threads, while preprocessing, cross-part ordering, postprocessing, and output have separate responsibilities. **C1:** The architecture specifies coordinate restoration, copied effective settings, cancellation, and mode-specific restrictions, including the cylindrical writer constraint. These are valuable explicit invariants for extending a multithreaded research slicer. The [rename release](https://github.com/ORNLSlicer/ORNLSlicer/releases) provides the migration context.

### 19. [drlukeparry/pyslm](https://github.com/drlukeparry/pyslm)

**Language/role:** Python library for metal additive manufacturing, especially laser powder-bed scan-vector generation. A distinct process family from extrusion-oriented desktop slicers.

- **C1:** [`hatching.py`](https://github.com/drlukeparry/pyslm/blob/master/pyslm/hatching/hatching.py) handles contour offsets and clipping of open hatch vectors against closed boundaries. It explicitly sets clipping scale, fill semantics, and preservation of auxiliary coordinates; its documentation distinguishes maintained input order from any additional ordering required by a scan strategy.
- **C2:** The same module defines reusable base hatchers and region abstractions supporting multiple scan strategies, with layer/model data rather than G-code text as the central interface. The repository also documents mesh slicing, supports, and analysis around these abstractions. A material limitation is that commercial machine build-file translators are not all distributed as part of the open library; do not equate scan-vector generation with universal machine export.

### 20. [FullControlXYZ/fullcontrol](https://github.com/FullControlXYZ/fullcontrol)

**Language/role:** Python framework for explicitly designing deposition paths and process changes, rather than deriving every path from a sliced solid. Useful for procedural and nonstandard printing workflows.

- **C2:** [`steps2gcode.py`](https://github.com/FullControlXYZ/fullcontrol/blob/master/fullcontrol/gcode/steps2gcode.py) interprets a heterogeneous list of step objects through their `gcode(state)` methods. The interpreter supports steps that expand the remaining program, while common state carries the point, printer, extruder, and extrusion geometry.
- **C1:** [`extrusion_classes.py`](https://github.com/FullControlXYZ/fullcontrol/blob/master/fullcontrol/gcode/extrusion_classes.py) turns path length and bead area into deposited volume, converts volume to filament-length or volumetric E units, and tracks relative versus absolute extrusion references. Mode changes reset the appropriate reference and emit matching commands. These stateful numerical semantics are the main engineering interest; explicit path design leaves geometric printability decisions with the designer.

## Search coverage and limitations

Discovery used more than six distinct query families: general CAM/drop-cutter kernels; FreeCAD/PyCAM machining; Blender/Heeks integration; browser SVG-to-CNC systems; Gerber isolation milling; laser path planning; turning libraries; extrusion slicer architecture; metal powder-bed and directed-energy toolpaths; explicit procedural deposition; and newer Rust, Go, C#, and multiaxis candidates. Follow-up searches checked official hosting and project lineage. Later cross-language and multiaxis queries increasingly returned small prototypes, wrappers, duplicate families, or claims without comparably strong inspected implementation evidence, so the selection stopped at 20 rather than filling a quota.

Every retained canonical GitHub repository was opened or checked through GitHub's API. Each has additional primary implementation or architecture evidence beyond its README. API rate limiting partway through the work was handled with public repository pages and individual raw source files. No dependencies were installed, candidate code executed, repositories cloned, or external services modified.

Important boundaries and omissions:

- **Hosting:** [FlatCAM's official download page](https://flatcam.org/download) points to Bitbucket, and [DXF2GCODE's official project wiki](https://sourceforge.net/p/dxf2gcode/wiki/Home/) points to its SourceForge project/source workflow. GitHub copies appeared in search, but an official substantive mirror was not established, so neither was retained.
- **Family overlap:** FreeCAD's entire monorepo and GridSpace's applications each count once. OpenCAMLib, OpenVoronoi, and libarea have separate implementations and responsibilities even when used by the same applications. PrusaSlicer's ancestry and jscut's succession are explicitly identified rather than presented as independent reinventions.
- **Industrial breadth:** Coverage is strongest for three-axis/2.5D milling, planar laser/PCB work, and additive paths. Simultaneous five-axis machining, full mill-turn synchronization, and industrial postprocessor verification are underrepresented; indexed operations are not counted as evidence of those capabilities.
- **Evidence limits:** Selection does not establish throughput, machine safety, universal format compatibility, or uniformly exemplary code. Historical applications are retained for concrete implementation value. Inference is limited to what an engineer can learn from the inspected structure; maintenance and performance claims are not inferred from stars or repository age.
