# Computer vision and image analysis libraries

Research date: **2026-10-09**

This selection covers 25 GitHub repositories implementing reusable image processing, quantitative image analysis, visual recognition, and image-based geometry. It includes general toolkits, scientific image infrastructure, native implementations in several languages, accelerated execution systems, and focused detection libraries. For broader monorepos, the relevant subsystem is identified. Pure image codecs, editors, model-weight collections, thin language bindings, and application-only reconstruction systems are outside the main scope.

The criteria below are engineering judgments grounded in the linked primary material. They identify promising code to study, not a claim that every component is exemplary, defect-free, or currently maintained at the same pace. Documentation versions are identified where material differences matter; a reachable repository is not by itself evidence of active maintenance.

- **C1 — Difficult correctness:** nontrivial invariants, numerical semantics, concurrency, adversarial inputs, or failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or components serving multiple algorithms and use cases.
- **C3 — Performance with structure:** concrete approaches to memory, throughput, latency, or computational cost, exposed through understandable architecture.
- **C4 — Sustained evolution:** evidence across years of compatibility work, testing, migration, or complexity management; repository age alone is insufficient.

## General computer vision toolkits

### [opencv/opencv](https://github.com/opencv/opencv)

**C++ with Python and Java interfaces; general computer vision.** Study the core image representation underlying image processing and geometric vision, particularly how an apparently simple image object represents ownership, views, channels, and non-contiguous memory. The repository's default branch observed during research was `5.x`; the entry point below deliberately documents the established 4.13 API rather than assuming identical behavior across major versions.

**C1:** `cv::Mat` makes strides, submatrices, reference-counted storage, explicit cloning, and external-buffer construction part of its contract. Correct code must distinguish a shared header from a deep copy and handle non-contiguous regions. **C2:** the same multidimensional container represents images, volumes, tensors, and other numerical objects. **C3:** header-only region selection, buffer reuse through `create`, and parallel element traversal offer concrete ways to avoid copying and allocate work. Start with the [Mat reference and detailed data-layout description](https://docs.opencv.org/4.13.0/d3/d63/classcv_1_1Mat.html).

### [lessthanoptimal/BoofCV](https://github.com/lessthanoptimal/BoofCV)

**Java; image processing, calibration, tracking, and structure from motion.** A useful independently implemented alternative to C++-centric vision toolkits. Study typed image families and the relationship between camera models, coordinate systems, and calibration algorithms.

**C2:** gray, planar, and interleaved representations have explicit types; generic operations coexist with type-specific pixel access. The [quick-start API guide](https://boofcv.org/index.php?title=Tutorial_Quick_Start) explains how planar images compose bands and how unsigned byte storage is exposed through integer accessors. **C1:** calibration supports different projection models rather than pretending that all cameras share pinhole assumptions. The [calibration guide](https://boofcv.org/index.php?title=Tutorial_Camera_Calibration) explains normalized versus spherical coordinates, distortion, and why a low residual can still accompany a biased calibration dataset. These are useful examples of algorithmic correctness depending on acquisition geometry as well as implementation.

### [davisking/dlib](https://github.com/davisking/dlib)

**C++ with Python interfaces; study the image-processing subsystem of a broader machine-learning toolkit.** Its generic image interface is a compact example of structural adaptation: algorithms can accept an image container by implementing a small contract rather than inheriting a universal image class.

**C2:** seven free functions plus `image_traits` and pixel traits describe dimensions, resizing, storage, stride, and swapping. This separates image algorithms from a particular owning container. **C1:** the contract specifies zero-sized images, null data pointers, row-major storage with padding, and legal resize dimensions; the accompanying image-view implementation turns these representation rules into concrete access behavior. The [generic image interface and implementation](https://dlib.net/dlib/image_processing/generic_image.h.html) is the strongest starting point. The engineering lesson is how explicit preconditions and storage contracts allow reusable native image algorithms without erasing pixel types.

### [scikit-image/scikit-image](https://github.com/scikit-image/scikit-image)

**Python and compiled numerical kernels; scientific image processing.** Study the consequences of making NumPy arrays the common image representation while retaining image-specific intensity semantics.

**C1:** changing dtype is not equivalent to preserving an image's meaning: the library distinguishes conversion, intensity rescaling, clipping, and `preserve_range`. Its [dtype guide](https://scikit-image.org/docs/stable/user_guide/data_types.html) explains precision loss and why automatic stretching can turn background noise into apparent signal. **C2:** these conventions let filters, transforms, morphology, and analysis functions compose around ordinary arrays. **C4:** the dated release archive spans many years; the [0.19 release notes](https://scikit-image.org/docs/stable/release_notes/release_0.19.html) document backported clipping and histogram fixes, restoration of accidental channel-behavior changes, test adaptation, and NumPy/Pillow compatibility. This is concrete evidence of managing numerical behavior and ecosystem change rather than merely adding algorithms.

## Multidimensional and quantitative image analysis

### [DIPlib/diplib](https://github.com/DIPlib/diplib)

**C++, with MATLAB and Python interfaces; quantitative image analysis.** Study its deliberate choice of runtime image typing over exposing every pixel type and dimension as a user-facing template parameter.

**C2:** framework functions perform type dispatch, dimensional traversal, input checking, and output creation so individual algorithms can implement line processing. **C1:** writable intermediate state is separated by thread, and the documented constness policy distinguishes image metadata from shared pixel storage. **C3:** in-place outputs coexist with convenient returning wrappers; filters estimate work before starting threads, addressing excessive overhead on small images. The [design decisions](https://diplib.org/diplib-docs/design.html) explain these tradeoffs, including limitations of the empirically chosen threading threshold. The [library overview](https://diplib.org/diplib-docs/) provides a second entry into the image model and algorithm modules. The core and its interfaces count as one repository.

### [InsightSoftwareConsortium/ITK](https://github.com/InsightSoftwareConsortium/ITK)

**C++ and Python; scientific image segmentation, filtering, and registration.** Study region negotiation in a demand-driven processing pipeline rather than only individual medical-imaging algorithms.

**C1:** `RequestedRegion`, `BufferedRegion`, and `LargestPossibleRegion` obey an explicit containment invariant. Metadata propagation, requested-region negotiation, and data generation occur in separate passes; invalid requests can raise an error. **C2:** `DataObject` and `ProcessObject` allow specialized data types to participate even when they do not support image regions. **C3:** region requests and modification times determine when upstream data must be regenerated and support processing images in pieces. The [DataObject architecture reference](https://docs.itk.org/projects/doxygen/en/latest/classitk_1_1DataObject.html) is unusually useful for understanding these contracts; the [streaming example](https://examples.itk.org/src/core/common/streamapipeline/documentation) connects them to a monitored pipeline.

### [ukoethe/vigra](https://github.com/ukoethe/vigra)

**C++ with Python bindings; generic image analysis.** Study ownership and algorithm reuse through multidimensional array views. Its longstanding documentation is especially useful as a design reference; this selection makes no claim about a current release cadence.

**C2:** `MultiArray` owns memory while `MultiArrayView` exposes the same data through subarrays, slices, and transformed indexing. Most algorithms accept views, allowing them to operate on differently arranged storage. **C1:** scan order and coordinate order are explicit, and matching element counts do not guarantee matching shapes. The documentation contrasts unchecked paired iteration with arithmetic that detects shape mismatch. **C3:** slicing and transposition can change the index-to-memory mapping without copying pixels. Start with the [multidimensional array tutorial](https://ukoethe.github.io/vigra/doc-release/vigra/MultiDimensionalArrayTutorial.html); the [tutorial map](https://ukoethe.github.io/vigra/doc-release/vigra/Tutorial.html) leads to convolution, feature accumulators, and segmentation.

### [imglib/imglib2](https://github.com/imglib/imglib2)

**Java; generic multidimensional image representation and access.** This repository supplies core infrastructure, not every algorithm in the wider ImgLib2 ecosystem. Study the separation between an image's data domain and the mechanism used to visit samples.

**C2:** [Accessibles](https://imglib2.net/imglib2/accessibles) model coordinate-to-value mappings, encompassing stored images, views, interpolated images, and sparse samples. `RandomAccess` and `Cursor` offer separate navigation capabilities rather than forcing one traversal model on every container. **C1:** [accessor documentation](https://imglib2.net/imglib2/accessors) explicitly warns that returned pixel objects may be reused proxies: moving an accessor can invalidate the apparent reference, and preserving access requires the appropriate copy operation. This is a substantive object-lifetime and mutation contract despite Java's managed memory. The interface hierarchy shows how dimensionality and value type can vary independently.

### [luispedro/mahotas](https://github.com/luispedro/mahotas)

**Python and C++; image analysis and feature extraction.** Study the seam between a convenient NumPy API and numerical feature definitions that differ across publications and implementations.

**C1:** the [Haralick implementation](https://raw.githubusercontent.com/luispedro/mahotas/master/mahotas/features/texture.py) handles zero-probability entropy terms, checks image dimensionality and integer inputs, exposes a switch for reproducing a published formula error, and distinguishes two interpretations of a variance feature. Background exclusion can fail when a direction has no valid neighboring pairs. **C2:** direction-specific co-occurrence matrices feed a common feature computation, with 2D/3D support and aggregation options; the broader [feature guide](https://mahotas.readthedocs.io/en/latest/features.html) places this beside LBP, moments, and local descriptors. The source should take precedence over older prose: it includes optional computation of the fourteenth Haralick feature, while the feature guide still describes only thirteen.

## Native implementations in additional language ecosystems

### [image-rs/imageproc](https://github.com/image-rs/imageproc)

**Rust; image-processing algorithms built on the Rust image ecosystem.** Study a relatively approachable implementation of geometric transformations with generic pixel types.

**C1:** projective transforms have explicit multiplication order, stored inverses, invertibility failure through `Option`, and separately defined border and interpolation behavior. Control-point estimation uses a numerical solve rather than assuming arbitrary correspondences determine a valid transform. **C2:** generic warping accepts either a projection object or a mapping function and can write into a supplied output image. **C3:** the implementation classifies translation, affine, and projective transformations, allowing specialized mapping paths instead of paying for the most general calculation everywhere. Read the [geometric transformation API](https://docs.rs/imageproc/latest/imageproc/geometric_transformations/index.html) alongside its [Rust implementation](https://docs.rs/imageproc/latest/src/imageproc/geometric_transformations.rs.html).

### [JuliaImages/ImageFiltering.jl](https://github.com/JuliaImages/ImageFiltering.jl)

**Julia; multidimensional filtering and stencil operations.** This is a substantive component of JuliaImages rather than an umbrella package that merely re-exports dependencies.

**C1:** kernel origins use indices, correlation is distinguished from convolution, and padding changes the mathematical operation. Region-limited computation without padding transfers explicit responsibilities to the caller; IIR filtering can differ from filtering the full array. **C2:** multidimensional arrays, factored kernels, output types, border policies, and algorithm choices are independently configurable. **C3:** separable kernels reduce work, while FIR versus FFT selection depends on image and kernel size; resource dispatch can select an execution implementation. The [filtering guide](https://juliaimages.org/ImageFiltering.jl/stable/filters/) explains these choices with executable API examples and boundary semantics, making it a strong study of numerical interfaces expressed through multiple dispatch.

### [image-js/image-js](https://github.com/image-js/image-js)

**TypeScript/JavaScript; image processing and quantitative region analysis.** A useful browser/Node ecosystem counterpoint to native scientific stacks. Study the conversion from pixels into masks, labeled regions, and reusable shape measurements.

**C2:** the [ROI analysis guide](https://docs.image-js.org/docs/tutorials/roi-analysis/) composes thresholding or watershed segmentation with ROI maps, region extraction, masks, and properties such as surface, holes, fill ratio, and roundness. The abstraction supports both particle measurements and object discrimination. **C1:** the same guide treats touching objects and regions cut by the image border as substantive measurement failure modes: a merged component changes shape statistics, while a truncated component does not represent the whole object. Its border removal and alternative segmentation paths expose those assumptions. This is evidence of nontrivial analysis semantics, not proof that the tutorial's heuristic thresholds generalize to arbitrary data.

## Memory-efficient and accelerated image execution

### [libvips/libvips](https://github.com/libvips/libvips)

**C with additional interfaces; demand-driven image processing.** Study how a library executes a chain of operations without materializing every intermediate image.

**C3:** images can be represented by functions that produce requested rectangular regions; operations connect these producers into a pipeline, reducing intermediate storage and repeated allocation. **C1:** the execution contract gives each generation sequence private state, makes start/stop mutually exclusive, and prohibits concurrent use of a state by multiple generators. Operations avoid mutating their input images. **C2:** regions, partial images, operations, and sinks form reusable execution abstractions across filters and file sources. The [evaluation architecture](https://www.libvips.org/API/current/how-it-works.html) explains these mechanisms, as well as SIMD dispatch and format-dependent streaming limitations. No universal speed multiplier is inferred from the project's performance discussion.

### [DanBloomberg/leptonica](https://github.com/DanBloomberg/leptonica)

**C; image processing and image analysis, including document-oriented operations.** Study a native image representation with unusually explicit documentation of buffer ownership and resource transfer.

**C1:** `pixSetData`, cloning, copying, destruction, and transfer have different lifetime effects. In particular, assigning an image buffer does not automatically dispose of the old one, and transferring from a multiply referenced image cannot simply steal its storage. **C2:** `Pix` provides common storage and metadata contracts for many measurement and transformation operations. **C3:** transfer and custom allocation interfaces address large-buffer costs without forcing every operation to deep-copy an image. The [pix1.c implementation and ownership commentary](https://raw.githubusercontent.com/DanBloomberg/leptonica/master/src/pix1.c) explain both the rationale and the hazards. This is a good study of a disciplined C API where correct ownership is an explicit caller concern.

### [halide/Halide](https://github.com/halide/Halide)

**C++ compiler and embedded DSL, with Python interfaces; image and array pipelines.** Included for its image-processing execution model, rather than as a general-purpose compiler recommendation.

**C2:** `Func`, expression graphs, image parameters, and schedules separate what a pipeline computes from how its stages execute. **C3:** wrapper functions permit consumer-specific computation and staging of loads without rewriting the algorithm. The [wrapper-function tutorial](https://halide-lang.org/docs/tutorial/lesson_19_wrapper_funcs.html) shows the resulting loop nests and how `Func::in` rewrites selected producer-consumer relationships. This provides an unusually inspectable route from a reusable abstraction to memory locality and scheduling decisions. The main repository also identifies JIT and ahead-of-time compilation paths and CPU/GPU targets. The study target is the pipeline and scheduling architecture; no numerical speed comparison is assumed.

### [ermig1979/Simd](https://github.com/ermig1979/Simd)

**C++ with a C API; SIMD implementations of image-processing primitives.** Study how one API can retain scalar and multiple instruction-set implementations without obscuring validation and performance measurement.

**C1:** the documented automatic test mode compares implementations of the same function, including scalar versus SIMD paths. This directly addresses a common source of low-level numerical and boundary inconsistencies. **C3:** runtime implementation selection, architecture-specific optimization, performance statistics, and tests parameterized by image dimensions and channels connect optimization to a repeatable framework. **C2:** the C interface and C++ image views support use outside a single vision application, including conversion to OpenCV representations. The [project's architecture, API integration, and test-framework documentation](https://ermig1979.github.io/Simd/help/index.html) is the verified entry point. Its test claims are project documentation, not independently measured coverage.

### [CVCUDA/CV-CUDA](https://github.com/CVCUDA/CV-CUDA)

**C++/CUDA with Python bindings; GPU image-processing operators.** Study the layers connecting public operator APIs, private kernels, bindings, correctness references, and benchmarks.

**C1:** the [operator implementation guide](https://cvcuda.github.io/CV-CUDA/advanced/make_operator.html) explains a concrete multi-GPU failure: constructor-time allocation may belong to a different device than a later invocation. Its per-device resource abstraction allocates lazily and restores the appropriate device for destruction. The guide also distinguishes numerical reference tests from Python API tests and negative-input checks. **C2:** tensors and variable-shape image batches support common operator interfaces. **C3:** [the operator overview](https://cvcuda.github.io/CV-CUDA/) documents GPU-resident interoperability and fused operations such as resize/crop/convert/reformat. These are concrete mechanisms for reducing pipeline overhead. The repository documents NVIDIA/CUDA platform constraints; this is not a portable CPU backend.

## Differentiable vision and recognition infrastructure

### [kornia/kornia](https://github.com/kornia/kornia)

**Python/PyTorch; differentiable image processing and geometric vision.** Study how classical image transforms become composable tensor operations while retaining explicit geometry conventions.

**C1:** the [geometric transformation reference](https://kornia.readthedocs.io/en/latest/geometry.transform.html) distinguishes source-to-destination pixel homographies from destination-to-source normalized mappings, documents `align_corners`, and specifies padding and empty-output behavior. Mixing these conventions can produce plausible-looking but incorrect results. **C2:** batched image and transformation tensors provide reusable interfaces for 2D and 3D warping within learned pipelines, with common camera and geometry components around them. The API's explicit shapes, transform direction, and sampling rules are the main study target. Differentiability is part of the repository's stated design, but this report does not claim that every discrete operator has useful gradients everywhere.

### [pytorch/vision](https://github.com/pytorch/vision)

**Python and C++/CUDA; Torchvision transforms, datasets, operators, and models.** Focus on the transforms subsystem rather than treating its pretrained model inventory as the quality evidence.

**C2:** transforms v2 dispatch across images, videos, bounding boxes, masks, and keypoints, including nested input structures and batches. **C1:** an augmentation must update image data and annotations consistently while respecting dtype-dependent value ranges and box coordinate conventions. **C3:** the [transforms guide](https://docs.pytorch.org/vision/stable/transforms.html) explains tensor versus PIL execution, dtype choices, resizing modes, and performance considerations. It also documents the transition from the March 2023 v2 introduction and compatibility caveats. This is useful architecture for sharing one transformation description across classification, detection, segmentation, and video tasks without losing the meaning of each data object.

### [facebookresearch/detectron2](https://github.com/facebookresearch/detectron2)

**Python with native operators; detection, segmentation, and visual-recognition framework.** Study the data structures that let many recognition models share batching and annotation code.

**C2:** `Boxes`, `Instances`, `Keypoints`, and `ImageList` expose domain operations such as clipping, joint indexing, device transfer, and batching images of different sizes. **C1:** instance fields must have consistent lengths; indexing must preserve correspondence among fields. Image batching pads tensors while retaining original sizes, and tensor slicing may share storage. Keypoint visibility and box modes carry additional semantic constraints. The [structures reference](https://detectron2.readthedocs.io/en/latest/modules/structures.html) documents these contracts and links implementations. These are substantial reusable invariants, not merely convenience wrappers around a model. The documentation reports version 0.6; its availability should not be interpreted as evidence of a recent tagged release.

### [open-mmlab/mmcv](https://github.com/open-mmlab/mmcv)

**Python and native vision operators; shared OpenMMLab vision infrastructure.** Focus on data transformations and image operators. Avoid attributing the wider ecosystem's model implementations, or MMEngine's training machinery, to this repository.

**C2:** `BaseTransform`, registries, and dictionary-to-dictionary composition separate dataset description from loading, augmentation, and formatting. **C1:** the [data transformation design](https://mmcv.readthedocs.io/en/latest/understand_mmcv/data_transform.html) explicitly distinguishes `(width, height)` configuration arguments from `(height, width)` metadata. `TransformBroadcaster` and `cache_randomness` share random choices across paired images; `avoid_cache_randomness` rejects incompatible transforms when shared parameters are requested. These contracts prevent related inputs from receiving inconsistent augmentations. **C3:** dataset construction records paths and sample metadata rather than eagerly loading every image, placing expensive preparation into the per-sample pipeline. The guide provides both base-class code and composition examples.

## Features, fiducials, and image-based geometry

### [vlfeat/vlfeat](https://github.com/vlfeat/vlfeat)

**C with MATLAB interfaces; classical visual features and statistical vision algorithms. Historical study target.** The official site still lists 0.9.21, released in 2018, as its latest version. That is a reason to study the implementation on its merits, not to assume contemporary platform support.

**C1:** the [SIFT implementation guide](https://www.vlfeat.org/api/sift.html) explains scale-space construction, rejection of unstable edge and low-contrast responses, ambiguous orientations, and descriptor conventions. **C2:** reusable filter objects support processing multiple images, and detection can be separated from descriptor computation at custom keypoints. **C4:** the [official release news](https://www.vlfeat.org/index.html) records 2015 and 2018 maintenance releases, including MatConvNet argument compatibility and macOS binary fixes. This supports historical compatibility work across years, not an active-maintenance claim. It is particularly useful for reading an implementation together with its mathematical explanation.

### [openMVG/openMVG](https://github.com/openMVG/openMVG)

**C++; reusable multiple-view geometry and structure-from-motion components.** Study the libraries underneath its command-line reconstruction pipeline, especially the boundary between a minimal solver and robust estimation.

**C2:** the `Kernel` concept combines observations, a solver, and an error metric. Solver contracts include minimum sample counts and the maximum number of candidate models, allowing different geometric estimators to share robust-estimation machinery. **C1:** homographies, fundamental and essential matrices, triangulation, and camera resection have different constraints and residuals; robust fitting must score candidate models against imperfect correspondences. The [multiview documentation](https://openmvg.readthedocs.io/en/latest/openMVG/multiview/multiview/) explains both the geometry and the interface. The repository further describes separately composable image, feature, camera, matching, and reconstruction libraries. This is a library selection, not a separate entry for each bundled executable.

### [isl-org/Open3D](https://github.com/isl-org/Open3D)

**C++ and Python; study RGB-D integration and reconstruction within a broader 3D library.** Its category fit here is the transformation of depth/color images and camera trajectories into a reconstructed scene, rather than unrelated visualization facilities.

**C1:** integration couples calibrated camera transforms, depth truncation, voxel resolution, and signed-distance accumulation. The [RGB-D integration guide](https://www.open3d.org/docs/release/tutorial/pipelines/rgbd_integration.html) explains that smaller voxels can increase sensitivity to depth noise and shows the camera-pose inversion used by the pipeline. **C2:** RGB-D images, camera intrinsics, volume integration, and surface extraction are separate reusable components. **C3:** `ScalableTSDFVolume` uses hierarchical hashing to support larger scenes than a uniformly allocated volume. This is an explicit data-structure response to memory scale, with a documented path from inputs to marching-cubes output.

### [AprilRobotics/apriltag](https://github.com/AprilRobotics/apriltag)

**C; visual fiducial detection and pose estimation.** A focused library with enough algorithmic depth to complement the general toolkits. Study the interaction between marker families, detection stages, camera geometry, and resource ownership.

**C1:** the [pose implementation](https://raw.githubusercontent.com/AprilRobotics/apriltag/master/apriltag_pose.c) contains orthogonal iteration, SVD-based rotation updates, determinant handling, and an explicitly approximate polynomial-root routine. These are useful numerical choices to examine, including their limitations. **C2:** detector instances accept tag families and expose detections and pose inputs independently of image acquisition. **C3:** the [repository's tuning and integration guide](https://github.com/AprilRobotics/apriltag#tuning-the-detector-parameters) explains the tradeoff between decimation, speed, and detection distance, plus thread-count controls and stage-by-stage debug images. No advertised speed ratio is adopted here. The library and generated tag-family files count as one project.

## Coverage and search notes

Discovery used more than six distinct live-search formulations, followed by repository-page verification and additional primary-source reading for every retained entry. Search angles included:

- General C++/Python computer vision toolkits and image representation architecture.
- Java, Rust, Julia, and JavaScript/TypeScript native image-analysis implementations.
- Multidimensional microscopy/scientific image analysis, generic arrays, and streaming region pipelines.
- Demand-driven image evaluation, buffer ownership, SIMD testing, GPU operators, and compiler scheduling.
- Differentiable geometry, augmentation consistency, detection structures, and shared recognition infrastructure.
- Local descriptors, robust multiview estimation, RGB-D reconstruction, and fiducial pose estimation.

Later queries increasingly returned already-covered architectures, thin wrappers, examples, or adjacent application frameworks. A final language-oriented pass added image-js rather than another similar C++ toolkit. Searches also surfaced libCVD and Accord.NET; they were not retained for additional full verification in this selection. Their omission is not a negative quality assessment. CImg, PCL, standalone reconstruction applications, and broader medical-imaging applications are likewise not comprehensively surveyed here. OpenCV add-on modules and interfaces to selected libraries were not counted as independent projects.

Every linked repository heading was opened at its canonical GitHub page. Additional sources were opened and read, including actual implementations for Mahotas, Leptonica, imageproc, dlib, and AprilTag and architecture/API material for the other entries. Search snippets alone were not used as final verification. A few initially attempted documentation routes were unavailable; retained citations use successfully retrieved alternatives. The report does not depend on an unofficial mirror or count a fork as a separate implementation.

This was read-only source research: no candidate repository was cloned, built, installed, or benchmarked. C3 judgments concern documented mechanisms, not independently measured performance; tests discussed here were inspected through primary documentation or source, not executed. VLFeat is explicitly historical. For the other projects, inclusion establishes category fit and engineering substance, not a blanket promise about release cadence, support, security, or uniform code quality. The selection spans several communities but remains weighted toward C++ and Python because those ecosystems supplied the deepest primary evidence in this search.
