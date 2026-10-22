# Medical image processing and registration frameworks

Research date: **2026-10-09**.

This selection covers 21 GitHub repositories implementing reusable medical-image processing, spatial registration, or the application infrastructure that makes those algorithms usable. It includes volumetric CT/MRI, neuroimaging, motion-corrupted MRI reconstruction, and whole-slide pathology; both classical optimization and learned registration are represented. Application monorepos are counted once, with the relevant subsystem identified. These are engineering study candidates, not a claim that every component is exemplary or that registration accuracy transfers between datasets.

Criteria legend:

- **C1 — Correctness:** demanding numerical semantics, coordinate invariants, concurrency, or consequential failure modes.
- **C2 — Abstraction:** substantial reusable interfaces or components supporting multiple algorithms and applications.
- **C3 — Performance:** concrete responses to computation, memory, or throughput constraints within an understandable architecture.
- **C4 — Evolution:** sustained development demonstrated together with compatibility, testing, or complexity management. Age or popularity alone does not qualify.

The criteria judgments below are grounded engineering interpretations of the linked documentation and implementation. Repository availability is verified; ongoing maintenance is not presumed from a live repository or its star count.

## Foundational image-processing libraries

### 1. [InsightSoftwareConsortium/ITK](https://github.com/InsightSoftwareConsortium/ITK)

**Language/role:** C++ with Python interfaces; N-dimensional segmentation, image processing, and registration foundation.

Study how generic programming turns a numerical optimization problem into interchangeable objects while preserving the distinction between image samples and spatial transformations. This is the foundational library behind several separately listed systems, rather than an independent implementation of every algorithm they expose.

- **C1:** Registration couples transform parameterization, interpolation, metric behavior, and optimizer convergence. The technical guide explains why a metric with a broad capture range can have poor final precision, and why initialization and metric choice are part of correctness.
- **C2:** Targets, transforms, metrics, interpolators, and optimizers are separate components, allowing image-to-image and point-set-to-image configurations.
- **C3:** The multiresolution framework estimates alignment on reduced images and propagates the transform to finer levels, addressing expensive metric evaluation and optimization stability together.

**Entry point:** [Registration framework and multiresolution design](https://docs.itk.org/projects/doxygen/en/stable/RegistrationPage.html), which supports all three criteria and links into the class APIs.

### 2. [SimpleITK/SimpleITK](https://github.com/SimpleITK/SimpleITK)

**Language/role:** C++ with multiple language bindings; a simplified image and registration API over ITK.

Study the engineering of a substantial façade around a template-heavy library: runtime image types, ownership semantics, spatial metadata, and a configurable registration object. Its own image semantics make it more than a generated language wrapper.

- **C1:** The image API documents copy-on-write aliasing hazards when underlying ITK objects are modified directly, fully buffered/zero-index requirements, and dimension checks when copying spatial information. [Image class contract](https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1Image.html).
- **C2:** `ImageRegistrationMethod` combines interchangeable transforms, metrics, optimizers, interpolation, and progress observers behind a compact interface. The registration guide explicitly treats mask rejection, random sampling, physical parameter scaling, and floating-point variability from threading. [Registration overview](https://simpleitk.readthedocs.io/en/master/registrationOverview.html).

**Entry points:** The two linked API guides connect ownership invariants to registration configuration and reproducibility.

## Configurable classical registration engines

### 3. [SuperElastix/elastix](https://github.com/SuperElastix/elastix)

**Language/role:** C++; parameter-driven rigid and nonrigid registration built on ITK, with additional registration components.

Study a component system that turns registration experiments into reproducible parameter configurations. Components register with a core that initializes and connects them; each component owns its parameter interpretation and reporting.

- **C2:** Metrics, optimizers, transformation models, and interpolators can be extended without rewriting the core. This is substantive configuration and algorithm infrastructure, despite its reuse of ITK. [Component architecture](https://github.com/SuperElastix/elastix/wiki/What-is-elastix).
- **C3:** The transformix memory analysis separates input/output buffers, B-spline coefficient storage, and additional casts. It explains how coefficient precision and interpolation choice change memory requirements and numerical quality, providing a concrete performance-design exercise. [Memory consumption in transformix](https://github.com/SuperElastix/elastix/wiki/Memory-consumption-in-transformix).

**Entry points:** The architecture and memory documents above. The latter is explicitly an older design note, not a benchmark of the current release.

### 4. [ANTsX/ANTs](https://github.com/ANTsX/ANTs)

**Language/role:** C++ and shell orchestration; registration, normalization, and medical-image analysis tools.

Study how a sophisticated registration engine exposes staged rigid, affine, and symmetric deformable optimization through a composable command-line specification.

- **C1:** The registration walkthrough explains physical-space initialization failures, normalization of multiple metric weights, smoothing of update versus accumulated deformation fields, and discontinuities introduced by masks. These are concrete numerical failure modes, not merely a list of available algorithms.
- **C2:** Each stage specifies its own transformation, metrics, convergence policy, and resolution schedule; multimodal image pairs can contribute different metrics to the same transform.
- **C3:** Sampling fractions, shrink factors, smoothing, and early convergence provide explicit control over costly full-resolution metric evaluation.

**Entry point:** [Anatomy of an antsRegistration call](https://github.com/ANTsX/ANTs/wiki/Anatomy-of-an-antsRegistration-call), including the registration-stage and SyN explanations. The useful study target is the engine and orchestration, not only the convenience scripts.

### 5. [KCL-BMEIS/niftyreg](https://github.com/KCL-BMEIS/niftyreg)

**Language/role:** C/C++, with CUDA/OpenCL routines; rigid, affine, and nonlinear medical registration.

Study an implementation where transformation representations and interchange conventions are first-class concerns. This is the verified current GitHub home; older UCL and SourceForge references are not separate entries.

- **C1:** The format contract distinguishes absolute deformation from displacement, physical coordinates from voxel indices, and Euclidean fields from velocity parameterizations requiring scaling and squaring. It also specifies NIfTI header precedence and padding of B-spline control lattices. [Transformation formats](https://github.com/KCL-BMEIS/niftyreg/wiki/transformations).
- **C2:** A shared family of transform representations supports registration, resampling, composition, inversion, averaging, and Jacobian calculation across separate tools. The same format document explains their interoperability.
- **C3:** The project documents CPU code alongside CUDA/OpenCL routines for computationally intensive registration. [Project overview](https://github.com/KCL-BMEIS/niftyreg/wiki).

**Entry points:** The transformation specification is the strongest architectural starting point; the overview links to executable documentation.

### 6. [BioMedIA/MIRTK](https://github.com/BioMedIA/MIRTK)

**Language/role:** C++; Medical Image Registration ToolKit, successor to IRTK, with extension modules.

Study a general registration controller that accommodates images, point sets, transformation constraints, and multilevel optimization within one energy formulation.

- **C2:** `GenericRegistrationFilter` describes parsed image-similarity terms, point-set distance terms, point-set constraints, and transformation constraints with separate types and weights. This makes mixed geometric and intensity objectives inspectable rather than burying them in one application-specific loop.
- **C3:** The same controller explicitly models resolution-pyramid images and cached displacement fields. Cache records associate a field with its transformation, domain, and input time, exposing the bookkeeping needed to reuse expensive spatial computations safely.

**Entry point:** [GenericRegistrationFilter header](https://raw.githubusercontent.com/BioMedIA/MIRTK/master/Modules/Registration/include/mirtk/GenericRegistrationFilter.h). These claims concern the declared architecture; cache effectiveness was not benchmarked. The published documentation site was inaccessible during this search, so the implementation header supplied the additional primary evidence.

### 7. [pyushkevich/greedy](https://github.com/pyushkevich/greedy)

**Language/role:** C++ with additional interfaces; affine and greedy deformable registration for medical images.

Study a comparatively focused registration engine with unusually explicit descriptions of its computational and numerical controls.

- **C1:** The reference specifies fixed-to-moving displacement semantics, stationary-velocity modes, and the risk that large updates produce non-diffeomorphic fields. Gradient scaling and smoothing are explained as algorithmic behavior, not arbitrary tuning knobs.
- **C3:** Thread count, floating-point precision, and stored warp precision expose distinct CPU, memory, and disk tradeoffs. The documentation warns that single precision is less extensively tested and can affect normalized cross-correlation calculations.
- **C2:** Affine estimation, deformable alignment, transform-chain reslicing, and several similarity metrics share a common command interface.

**Entry point:** [Greedy reference](https://greedy.readthedocs.io/en/latest/reference.html). No numerical speed advantage is inferred from the repository's name or tagline.

## Application and interaction frameworks

### 8. [MITK/MITK](https://github.com/MITK/MITK)

**Language/role:** C++/Qt, with bindings; interactive medical-image processing framework integrating ITK and VTK.

Study the **core geometry and image-data subsystem** within the larger application monorepo. A medical application must keep processing, slice display, and measurements consistent across coordinate systems.

- **C1:** `BaseGeometry` defines intrinsic bounds, an index-to-world affine mapping, origin, and spacing. Image geometries have different corner conventions, and continuous versus integer index conversion is explicit. These contracts explain common half-voxel and coordinate-space mistakes.
- **C2:** The abstract geometry model underlies concrete 3D, plane, sliced, and time geometry types; processing subclasses must initialize geometry during output-information propagation. This is a reusable spatial model for multiple data objects and operations.

**Entry point:** [BaseGeometry API and detailed description](https://docs.mitk.org/latest/classmitk_1_1BaseGeometry.html). The repository introduction establishes the broader ITK/VTK application-framework role; this entry does not separately count its plugins.

### 9. [Slicer/Slicer](https://github.com/Slicer/Slicer)

**Language/role:** C++, Python, and Qt; extensible medical-image computing application and platform.

Study **MRML and its processing/module integration**, not just the graphical viewer. MRML represents image volumes, segmentations, meshes, points, and transform chains as a shared scene that modules can manipulate.

- **C2:** Data, display, and storage nodes separate computational data from visualization and persistence. Node references and event observers let modules coordinate through shared state rather than direct coupling.
- **C1:** The developer guide addresses observer management, scene lifecycle, transform representation, and state restoration. It specifically documents why scene undo is disabled by default, making memory and insufficiently tested behavior visible rather than treating the feature as universally safe.

**Entry point:** [MRML architecture, events, and scene state](https://slicer.readthedocs.io/en/latest/developer_guide/mrml_overview.html). This is one monorepo entry; embedded libraries and extensions are not counted as additional projects here.

## Neuroimaging and specialized reconstruction

### 10. [spm/spm](https://github.com/spm/spm)

**Language/role:** MATLAB with compiled C routines; brain-image processing and statistical analysis suite.

Study the **spatial preprocessing/coregistration subsystem** rather than the unrelated EEG/MEG and statistical portions. The repository identifies itself as the development version; separate SPM release repositories are not additional entries.

- **C1:** `spm_coreg` explicitly converts through image affine matrices and distinguishes physical sampling steps, rotation/translation tolerances, and joint-histogram smoothing. Its comments explain changes intended to smooth the objective and reduce local-minimum problems.
- **C2:** A parameterized coregistration routine accepts image handles, configurable information-theoretic or correlation costs, initial parameters, and sampling schedules. It reuses the suite's volume, transformation, optimization, and display machinery.

**Entry point:** [spm_coreg implementation](https://raw.githubusercontent.com/spm/spm/main/spm_coreg.m). The repository also documents old-format readability and warns that algorithm/template changes mean analyses should remain on one SPM version; compatibility should not be mistaken for identical results.

### 11. [MRtrix3/mrtrix3](https://github.com/MRtrix3/mrtrix3)

**Language/role:** C++ with Python tools; diffusion-MRI processing, computational anatomy, and image operations.

Study the **core image abstraction** that supports the larger command suite. It is useful for understanding how a medical-imaging framework hides storage formats while retaining control over data layout.

- **C2:** The templated `Image` interface exposes dimensions, spacing, transforms, metadata, strides, and value access through a shared buffer abstraction. Algorithms can operate on a common image model rather than per-format arrays.
- **C3:** Direct and indirect I/O paths are explicit. `with_direct_io` can preload data when datatype, scaling, or stride requirements demand it; the low-memory write path avoids extra buffering but has documented format restrictions. These are concrete tradeoffs between convenience, contiguous access, and RAM use.

**Entry point:** [core/image.h](https://raw.githubusercontent.com/MRtrix3/mrtrix3/master/core/image.h), especially direct-I/O conversion and buffer access. The repository's diffusion-MRI role establishes the category fit.

### 12. [dipy/dipy](https://github.com/dipy/dipy)

**Language/role:** Python with compiled numerical components; diffusion and broader medical-image analysis.

Study the **alignment subsystem**, where a Python-facing object model makes physical-space deformation mathematics explicit.

- **C1:** `get_direction_and_spacings` explains why voxel gradients must be rescaled and reoriented into physical coordinates. `DiffeomorphicMap` distinguishes field discretization, domain and codomain grids, prealignment, and forward/backward fields. [imwarp implementation](https://raw.githubusercontent.com/dipy/dipy/master/dipy/align/imwarp.py).
- **C2:** Mapping objects are separate from the registration optimizer and similarity metric, allowing an estimated mapping to be reused for images and inverse transformations. [Symmetric diffeomorphic registration example](https://docs.dipy.org/stable/examples_built/registration/syn_registration_3d.html).

**Entry points:** Start with the mapping contract in `imwarp.py`, then the worked 3D example showing the separation between estimation, application, and persistence. The implementation and comments are study material, not a proof that every numerical edge case is resolved.

### 13. [gift-surg/NiftyMIC](https://github.com/gift-surg/NiftyMIC)

**Language/role:** Python with ITK/SimpleITK-related dependencies; motion correction and super-resolution reconstruction from MRI slice stacks.

Study how slice-to-volume registration becomes part of a larger inverse problem. The pipeline alternates motion estimation and reconstruction instead of treating registration as an isolated preprocessing operation.

- **C1:** The Tikhonov solver explicitly factors the acquisition operator into warping, blurring, and downsampling, with masking and zeroth- or first-order regularization. This exposes the physical model and the augmented least-squares problem being solved.
- **C2:** Stack objects, the shared `Solver` base, configurable loss functions, regularizers, minimizers, and in-plane versus full-3D deconvolution support multiple reconstruction configurations.

**Entry point:** [Tikhonov reconstruction solver](https://raw.githubusercontent.com/gift-surg/NiftyMIC/master/niftymic/reconstruction/tikhonov_solver.py).

**Limitation:** The repository's installation documentation still describes older Python and operating-system combinations. It is retained for substantive research architecture; present-day installation compatibility was not established.

## Medical-image preprocessing for learning

### 14. [Project-MONAI/MONAI](https://github.com/Project-MONAI/MONAI)

**Language/role:** Primarily Python/PyTorch, with compiled components; healthcare-imaging transforms, datasets, inference, and learning infrastructure.

Study the **transform pipeline and lazy resampling subsystem**, where numerical image quality and computational cost constrain execution order.

- **C1:** Spatial transforms must compose in order, retain coordinate metadata, and materialize pending operations before a transform needs actual voxel values.
- **C2:** `Compose`, `LazyTrait`, `LazyTransform`, and explicit pending-operation controls form a reusable execution protocol.
- **C3:** Compatible operations are fused into fewer resampling passes, avoiding repeated interpolation and intermediate allocations. The [lazy-resampling design](https://monai.readthedocs.io/en/1.6.0/lazy_resampling.html) explains all three criteria and labels the feature experimental in that documentation version.
- **C4:** The [changelog](https://raw.githubusercontent.com/Project-MONAI/MONAI/dev/CHANGELOG.md) records releases from 2020 through 2026, dependency support, distributed tests, documented breaking changes, and fixes to affine alignment, transform inversion, and memory leaks.

**Entry points:** The execution-design guide and changelog above connect architecture to sustained compatibility and correctness work.

### 15. [TorchIO-project/torchio](https://github.com/TorchIO-project/torchio)

**Language/role:** Python/PyTorch; loading, preprocessing, augmentation, and patch sampling for 3D medical images.

Study a domain-specific data pipeline that balances volume-level preprocessing with patch-level training. MRI artifact augmentation provides category-specific functionality beyond a generic image loader.

- **C2:** Subjects and subject datasets feed interchangeable uniform, weighted, label-driven, and grid samplers. Grid sampling works with aggregation and explicit border/overlap behavior.
- **C3:** The queue prepares volumes in CPU worker processes, extracts multiple patches per prepared volume, shuffles a bounded patch buffer, and supplies GPU training batches. Queue length and samples per volume expose memory, diversity, and throughput tradeoffs.
- **C1:** Patch overlap, padding/cropping, sampling distributions, and epoch completion across subjects have defined semantics; distributed subject sampling is explicitly accommodated.

**Entry point:** [Patch sampling and Queue design](https://docs.torchio.org/latest/patches/training/). The current canonical owner is TorchIO-project; older `fepegar/torchio` links are not another project.

## Differentiable and learned registration libraries

### 16. [voxelmorph/voxelmorph](https://github.com/voxelmorph/voxelmorph)

**Language/role:** Python; learned deformable registration, with evolving PyTorch code and a separately identified TensorFlow branch.

Study the boundary between predicting a deformation and applying it correctly. This repository contains reusable geometric operations as well as registration-model infrastructure.

- **C1:** The functional implementation documents target-to-source voxel affine semantics, centered versus corner origins, batched shapes, and right-composition with a displacement field. Affine component order and coordinate/displacement conversion are explicit. [Functional geometry implementation](https://raw.githubusercontent.com/voxelmorph/voxelmorph/dev/voxelmorph/functional.py).
- **C2:** Affine construction, displacement conversion, spatial transformation, field integration, resizing, and composition are exposed as reusable operations rather than being inseparable from one trained model. The same source is a concrete entry point.

**Entry point:** The linked functional geometry implementation, starting with affine-to-displacement conversion and composition.

**Status distinction:** The repository README warns that PyTorch interfaces may change and directs users of the stable TensorFlow implementation to `dev-tensorflow`. Read documentation and source from matching versions; old `torch/layers.py` paths did not resolve during verification.

### 17. [DeepRegNet/DeepReg](https://github.com/DeepRegNet/DeepReg)

**Language/role:** Python/TensorFlow 2; a framework for medical-image registration using deep learning.

Study how one framework exposes different deformation representations and levels of supervision without reducing registration to a single neural-network architecture.

- **C1:** The technical tutorial distinguishes directly predicted displacement fields, integrated velocity fields, and affine transforms. It explains why an intensity loss can fail across modalities and why deformation regularization is needed alongside image similarity.
- **C2:** Intensity, anatomical-label, and deformation losses support unsupervised, weakly supervised, and combined training. The framework also accommodates ROI prediction as a related formulation, making the relationship between model outputs and training evidence explicit.

**Entry point:** [Registration models, losses, and supervision](https://github.com/DeepRegNet/DeepReg/blob/main/docs/source/tutorial/registration.md). This supplies substantive algorithm-architecture evidence beyond the repository overview. No current support cadence or cross-version TensorFlow compatibility is inferred from the project description.

### 18. [airlab-unibas/airlab](https://github.com/airlab-unibas/airlab)

**Language/role:** Python/PyTorch; automatic-differentiation laboratory for classical and experimental registration.

Study how automatic differentiation can support optimization of transform parameters directly, without requiring a learned predictor.

- **C1:** The transformation layer defines rotation centers, center-of-mass initialization, unit-displacement conversions, and scaling-and-squaring integration for diffeomorphic transformations. These are precisely the numerical interfaces where seemingly compatible tensors can have incompatible meanings.
- **C2:** Rigid, similarity, affine, B-spline, nonparametric, and Wendland-kernel models share transformation interfaces; registration, loss, and regularizer components are separately organized.

**Entry points:** [Transformation API](https://airlab.readthedocs.io/en/latest/transformation.html) and [building-block index](https://airlab.readthedocs.io/en/latest/).

**Limitation:** Its README explicitly flags CPU convolution memory costs for large images. That historical implementation warning should not be read as a benchmark of current PyTorch or evidence of a current maintenance commitment.

### 19. [BioMedIA/deepali](https://github.com/BioMedIA/deepali)

**Language/role:** Python/PyTorch; image, point-set, and surface registration building blocks.

Study a small, substantive library focused on the coordinate-system boundary between medical images and tensor frameworks, with both directly optimized and predicted transformation parameters.

- **C1:** Its grid model distinguishes world, voxel, normalized-cube, and cube-corner coordinates. The guide documents reversed tensor shape versus image size order, `align_corners` semantics, center-preserving resizing, and rejection of inconsistent origin/center specifications. [Coordinate-space design](https://biomedia.github.io/deepali/reference/core/domain.html).
- **C2:** Core coordinate/tensor functions, data types, losses, neural-network blocks, and spatial transformation models are separated, allowing pieces to be combined with task-specific PyTorch models. [Library organization and API map](https://biomedia.github.io/deepali/).

**Entry points:** The coordinate-space document is especially useful for studying interoperability invariants; the API map shows where that model is reused across images and transformations.

### 20. [uncbiag/mermaid](https://github.com/uncbiag/mermaid)

**Language/role:** Python/PyTorch; differentiable optimization-based registration, emphasizing velocity and momentum formulations.

Study an extensible numerical-model framework rather than only a packaged registration command. Its focus includes stationary velocity and large-deformation diffeomorphic models.

- **C1:** The model-extension guide makes voxel-volume weighting, time integration, regularization energy, and parameter upsampling between scales explicit. It also warns that shooting formulations can require more sophisticated optimization to converge.
- **C2:** Similarity measures, registration networks, forward integrators, losses, and multiscale optimizers have separate extension points. A new similarity measure can be registered once and propagated across registration models.

**Entry points:** [Model-extension architecture](https://mermaid.readthedocs.io/en/latest/notes/howto_own_registration.html) and [numerical/model API map](https://mermaid.readthedocs.io/en/latest/).

**Historical-documentation caveat:** The extension guide itself says it needs updating, and the README's environment example uses Python 3.7. Retain the architectural lessons, but do not assume those examples describe a currently supported installation.

## Whole-slide pathology registration

### 21. [MathOnco/valis](https://github.com/MathOnco/valis)

**Language/role:** Python with image-I/O and processing backends; registration of pathology whole-slide image series.

Study a registration pipeline designed around extremely large images and inconsistent tissue appearance. The repository explains feature-based ordering, serial rigid alignment toward a reference, tissue masks, and higher-resolution nonrigid refinement.

- **C1:** Annotation transfer requires matching aspect ratios and explicit pyramid-level, pixel-unit, and X/Y conventions. Known slice order must be preserved deliberately rather than replaced by appearance-based ordering. [Workflow and coordinate contracts](https://raw.githubusercontent.com/MathOnco/valis/main/docs/examples.rst).
- **C2:** Registrar and slide objects reuse estimated transforms for slide warping, point transfer, region extraction, and multiplexed-image construction.
- **C3:** Alignment can use reduced pyramid levels before higher-resolution refinement; pyvips-based region warping avoids loading an entire slide into memory. The same examples document this execution model and its output-size tradeoffs.

**Entry point:** The linked examples source supplies substantive workflow and implementation explanation. The repository's pipeline description supplies the complementary architecture overview.

## Coverage, search process, and limitations

Discovery used substantially more than six distinct query formulations, including:

- Medical registration toolkits around ITK, ANTs, elastix, NiftyReg, MIRTK, and Plastimatch.
- C++ medical-imaging application frameworks, including MITK and Slicer.
- Python preprocessing and patch pipelines around MONAI and TorchIO.
- Automatic-differentiation registration with AirLab, Mermaid, DeepReg, and deepali.
- Focused deformable-registration engines, including Greedy, and searches for newer GPU-oriented alternatives.
- MATLAB and diffusion/neuroimaging processing, leading to SPM, DIPY, and MRtrix3.
- MRI motion correction and reconstruction, leading to NiftyMIC.
- Rust/Julia registration ecosystems and whole-slide pathology registration, adding VALIS while revealing several thin wrappers and narrowly scoped projects.

Later comparison and alternative-framework queries largely returned already inspected projects; the pathology pass supplied the last clearly distinct addition. Every retained canonical repository page was opened, and each entry has at least one separately read primary technical source. The report relies on implementation files, class contracts, algorithm guides, and the MONAI changelog rather than search snippets or star rankings. Some raw sources were used when GitHub rendering or documentation sites failed.

Thin bindings, packaging-only repositories, tutorials, resource lists, and duplicate forks were excluded. In particular, Julia ANTs bindings, RNiftyReg, and separate elastix language packages were not treated as independent registration engines. SimpleITK remains because its runtime API, image ownership, metadata contracts, and registration façade are a substantial separate engineering subject. The Plastimatch search led to a [packaging repository describing GitLab upstream](https://github.com/ImagingDataCommons/plastimatch-python-distributions); an official substantive GitHub mirror was not established, so it was not retained. No retained repository is represented as an official mirror or archived project without evidence of that status.

Coverage is strongest in C++ and Python, with MATLAB providing another architecture family. The Rust/Julia search did not establish additional candidates with sufficiently inspected reusable implementation evidence for this selection; this is a search limitation, not a judgment that those ecosystems lack suitable software. Older documentation is explicitly identified where it affects interpretation. No candidate was cloned, built, installed, or benchmarked, and no numerical speed or clinical-accuracy ranking is asserted. C4 is deliberately awarded only where a dated evolution record and concrete compatibility/testing work were both inspected.
