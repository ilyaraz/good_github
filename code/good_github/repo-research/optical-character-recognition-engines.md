# Optical character recognition engines

Research date: **2026-10-09**.

This selection covers 25 GitHub repositories that implement substantial OCR recognition, training, decoding, or complete detection-and-recognition pipelines. It includes printed and scene text, handwriting, historical documents, mathematical notation, and generative document transcription. Line recognizers are identified separately from complete page engines. Historical implementations are included for their engineering value, with their status stated explicitly; this is a code-study selection guide, not an accuracy ranking or a claim that every component is exemplary.

**Criteria legend:** **C1** — difficult correctness, including numerical semantics, alignment, geometry, concurrency, and failure handling. **C2** — substantial reusable abstractions supporting different models, data, applications, or execution environments. **C3** — concrete performance constraints addressed through inspectable architecture. **C4** — sustained evolution accompanied by compatibility work, testing, or complexity management. Each entry justifies at least two criteria. Criterion assessments are engineering judgments grounded in the linked primary sources.

## General OCR engines and model toolkits

### 1. [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)

**Language/role:** C++; document OCR library and command-line engine, with legacy character recognition and LSTM line recognition. Study the boundary between a large recognition system and an embeddable API, especially ownership, initialization, language state, and decoding.

- **C1:** The API documents the exceptions to instance-level thread independence, parameter resets when changing languages, and image ownership. Its recoded-character beam search must reconcile compact character encodings, blank/repeated labels, dictionary scores, and character positions. These are concrete concurrency and sequence-decoding obligations. Entry points: [public API contracts](https://github.com/tesseract-ocr/tesseract/blob/main/include/tesseract/baseapi.h) and [recoded beam search](https://github.com/tesseract-ocr/tesseract/blob/main/src/lstm/recodebeam.cpp).
- **C2:** The API separates engine state from page/result iteration and output rendering, making the same recognizer usable in applications beyond its CLI.
- **C4:** The repository documents its long development history and the coexistence of the newer LSTM engine with a selectable legacy engine and compatible trained-data requirements. This is explicit compatibility management, rather than an age inferred from repository creation.

### 2. [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

**Language/role:** Primarily Python, with C++ deployment code; training and deployment toolkit. The relevant subsystems here are `ppocr` and OCR inference, counted once within the broader document-AI repository.

- **C2:** `BaseModel` builds transforms, backbones, necks, and heads from configuration, propagates channel dimensions between them, and optionally exposes intermediate features. Study how one construction scheme supports detection, recognition, classification, and training variants. Entry point: [model composition](https://github.com/PaddlePaddle/PaddleOCR/blob/main/ppocr/modeling/architectures/base_model.py).
- **C3:** Recognition inference sorts crops by aspect ratio before batching, chooses padding dimensions from the batch, and preserves model-specific preprocessing and decoding paths. This exposes the interaction between variable-length text, wasted padding, and heterogeneous recognition architectures. Entry point: [recognition inference](https://github.com/PaddlePaddle/PaddleOCR/blob/main/tools/infer/predict_rec.py).

### 3. [JaidedAI/EasyOCR](https://github.com/JaidedAI/EasyOCR)

**Language/role:** Python/PyTorch; multilingual detector-and-recognizer engine. Study the practical recognition layer between neural logits and script-aware text results.

- **C1:** Recognition masks excluded character classes, renormalizes the resulting probabilities, distinguishes blank outputs, and offers greedy, beam, and word-beam decoding. Confidence calculation must remain meaningful for empty and nonempty predictions. These details are visible in [recognition implementation](https://github.com/JaidedAI/EasyOCR/blob/master/easyocr/recognition.py).
- **C2:** The same implementation loads different recognition generations or user-selected model modules behind a common model/converter interface; the repository also exposes custom recognition training rather than only a fixed pretrained service.
- **C3:** The source includes normalized/padded batch collation, CPU quantization, and a second recognition pass for low-confidence crops after contrast adjustment. It is useful for studying when selective extra computation is preferable to applying expensive preprocessing universally.

### 4. [mindee/doctr](https://github.com/mindee/doctr)

**Language/role:** Python/PyTorch; document text recognition library. The repository remains at this canonical URL; its description credits ongoing development and maintenance to t2k. Study geometric bookkeeping across independently replaceable predictors.

- **C1:** Page straightening changes the image coordinate system. The OCR predictor records original shapes and inverse transforms, supports remapping results, validates page dimensions, and handles empty page lists. This is particularly relevant when OCR coordinates drive annotations or redaction. Entry point: [OCR predictor](https://github.com/mindee/doctr/blob/main/doctr/models/predictor/pytorch.py).
- **C2:** Detection and recognition predictors are separate objects composed into a document-producing predictor; optional orientation, language, layout, and table stages fit around that core. The source explicitly rejects a table predictor without its required layout predictor.
- **C3:** Straight-page assumptions avoid orientation work, and segmentation maps are materialized only when needed. The options expose a readable accuracy/latency tradeoff rather than an unexplained speed claim.

### 5. [open-mmlab/mmocr](https://github.com/open-mmlab/mmocr)

**Language/role:** Python/PyTorch; OCR research and application framework. Study reusable recognition construction and the exact interpretation of training targets. Repository metadata inspected during research showed its latest push in November 2024; current maintenance is not assumed.

- **C2:** The registry-built recognizer separates preprocessing, backbone, encoder, and decoder, while exposing distinct loss, prediction, and raw-forward operations. This makes architecture comparisons possible without rewriting the surrounding training/inference contract. Entry point: [encoder-decoder recognizer](https://github.com/open-mmlab/mmocr/blob/main/mmocr/models/textrecog/recognizers/encoder_decoder_recognizer.py).
- **C1:** CTC loss construction ties the blank index to the dictionary, converts logits to log probabilities, manages padded versus flattened targets and valid image ratios, and explicitly discusses infinite loss when inputs are too short for the target. Entry point: [CTC loss module](https://github.com/open-mmlab/mmocr/blob/main/mmocr/models/textrecog/module_losses/ctc_module_loss.py).

### 6. [faustomorales/keras-ocr](https://github.com/faustomorales/keras-ocr)

**Language/role:** Python/TensorFlow/Keras; CRAFT detection plus trainable CRNN recognition. It packages earlier model implementations, but contains substantial model construction, training, geometry, and data-generation code. Study the connection between a convenient pipeline and lower-level trainable components.

- **C2:** Recognition construction produces backbone, inference, training, and decoded-prediction models, with configurable alphabet and architecture parameters. It supports replacing the classification head for a different character inventory. Entry point: [recognizer and model builder](https://github.com/faustomorales/keras-ocr/blob/master/keras_ocr/recognition.py).
- **C1:** Training uses explicit label/input lengths for CTC; decoding pads variable-length outputs with a sentinel. The enclosing pipeline resizes and pads pages, then transforms detected boxes back to original coordinates. Entry point: [pipeline geometry](https://github.com/faustomorales/keras-ocr/blob/master/keras_ocr/pipeline.py).

## Inference-focused and native runtimes

### 7. [RapidAI/RapidOCR](https://github.com/RapidAI/RapidOCR)

**Language/role:** Python core with deployment integrations for other languages; portable OCR inference using several neural runtimes. It reuses OCR model families, including PaddleOCR models, but contributes substantial backend and pre/postprocessing infrastructure.

- **C2:** A common inference-session interface hides ONNX Runtime, OpenVINO, Paddle, PyTorch, TensorRT, and MNN selection, while model resolution accounts for runtime, task, language, version, and model tier. Invalid combinations receive explicit errors. Entry point: [session abstraction](https://github.com/RapidAI/RapidOCR/blob/main/python/rapidocr/inference_engine/base.py).
- **C3:** The recognizer groups crops by width/height ratio, batches normalized images, and restores original result order after inference. Character dictionaries and right-to-left output handling remain outside the backend. Study how runtime portability coexists with OCR-specific batching. Entry point: [text recognizer](https://github.com/RapidAI/RapidOCR/blob/main/python/rapidocr/ch_ppocr_rec/main.py).

### 8. [robertknight/ocrs](https://github.com/robertknight/ocrs)

**Language/role:** Rust; OCR library and CLI using RTen inference, with WebAssembly support. The README explicitly calls it an early preview and describes the shipped language support as Latin-alphabet recognition.

- **C2:** `OcrEngine` separates input preparation, detection, layout analysis, and recognition, with configurable models, alphabet, decoding method, and allowed characters. Internal model abstraction also permits dummy inference implementations in tests. Entry point: [engine API](https://github.com/robertknight/ocrs/blob/main/ocrs/src/lib.rs).
- **C1:** Recognition constructs polygons that follow curved text lines, clips sampling to valid image coordinates, and maps decoded characters back into spatial text objects.
- **C3:** The source explicitly bounds resized line width to balance long-line distortion against computation, and uses parallel processing and width-aware recognition machinery. Entry point: [recognition and crop preparation](https://github.com/robertknight/ocrs/blob/main/ocrs/src/recognition.rs).

## Historical documents, handwriting, and foundational implementations

### 9. [mittagessen/kraken](https://github.com/mittagessen/kraken)

**Language/role:** Python/PyTorch; trainable page analysis and recognition for historical and non-Latin material. Study how recognition, reading order, document geometry, and model lifecycle interact.

- **C1:** The CTC decoder accepts individual or batched outputs, requires explicit sequence lengths for multi-item batches, collapses repeated labels, removes blanks, and preserves time spans and confidence information. Entry point: [CTC decoding](https://github.com/mittagessen/kraken/blob/main/kraken/lib/ctc_decoder.py).
- **C2:** Trainable segmentation, reading order, and recognition are separately configurable stages, with multiple document serialization formats and script directions documented by the repository. The upgrade guide distinguishes restoring complete training state from loading weights for a new run, and explains conversion from training checkpoints into distributable weights. Study these separate training and deployment contracts through the [6.x-to-7.x migration guide](https://github.com/mittagessen/kraken/blob/main/docs/user_guide/migration_6_0.rst).

### 10. [Calamari-OCR/calamari](https://github.com/Calamari-OCR/calamari)

**Language/role:** Python/TensorFlow; trainable line recognition with ensemble voting. It has OCRopy/Kraken ancestry but its own model, training, prediction, checkpoint, and voting implementation. It requires line images or external page segmentation.

- **C1:** Confidence voting aligns differing predicted sequences, resolves length disagreements, combines character alternatives, and merges character spans. Crucially, it votes on characters rather than assuming that different models share numeric label IDs. Entry point: [confidence voter](https://github.com/Calamari-OCR/calamari/blob/master/calamari_ocr/ocr/voting/confidence_voter.py).
- **C2:** Single- and multi-model predictors reconstruct scenarios from checkpoints and compose data processing with replaceable voting. Output-to-input transforms preserve spatial interpretation across preprocessing. Entry point: [predictor construction](https://github.com/Calamari-OCR/calamari/blob/master/calamari_ocr/ocr/predict/predictor.py).
- **C3:** Multi-model voting explicitly disables nested parallel postprocessing because the voter already runs in separate threads—a useful example of controlling parallelism at component boundaries.

### 11. [DCGM/pero-ocr](https://github.com/DCGM/pero-ocr)

**Language/role:** Python; complete page OCR with line transcription and optional language-model refinement. Study the probabilistic decoder and its integration into an editable page representation.

- **C1:** The decoder validates character-set uniqueness and blank-symbol placement, checks log-probability normalization, and uses log-domain operations to merge competing CTC prefixes without double counting. Language-model hidden states must follow surviving hypotheses. Entry point: [decoders](https://github.com/DCGM/pero-ocr/blob/master/pero_ocr/decoding/decoders.py).
- **C2:** Configurable factories assemble layout analysis, line cropping, recognition, and decoding around `PageLayout`. This supports different OCR models and document processing arrangements. Entry point: [page pipeline](https://github.com/DCGM/pero-ocr/blob/master/pero_ocr/document_ocr/page_parser.py).
- **C3:** Page decoding can skip sufficiently confident lines and optionally carry language-model state between lines. The code exposes the cost of refinement rather than treating it as a compulsory universal pass.

### 12. [jpuigcerver/Laia](https://github.com/jpuigcerver/Laia)

**Language/role:** Lua/Torch7; handwriting recognition training, decoding, and forced alignment. **Historical:** the inspected default-branch commit feed ends in July 2018. This is the original Lua implementation, not its later PyLaia successor.

- **C1:** `CTCTrainer` exposes gradient clipping, NaN/infinity checks, loss normalization, and adversarial/weight regularization, with initialization invalidated when dependent components change. Study the numerical and state invariants of a complete training loop. Entry point: [CTC trainer](https://github.com/jpuigcerver/Laia/blob/master/laia/CTCTrainer.lua).
- **C2:** Models, optimizers, training/validation batchers, distorters, and regularizers are replaceable collaborators rather than hardcoded parts of one experiment.
- **C3:** Its width batcher orders variable-width line images and clears cached batches after reordering, providing an inspectable mechanism for reducing padding and managing cached state. Entry point: [width-aware batching](https://github.com/jpuigcerver/Laia/blob/master/laia/WidthBatcher.lua).

### 13. [ocropus-archive/DUP-ocropy](https://github.com/ocropus-archive/DUP-ocropy)

**Language/role:** Python/NumPy/SciPy; foundational OCRopus document-analysis and line-recognition implementation. **Archived historical repository:** this is the canonical destination of the old `ocropus/ocropy` URL, not an additional independent engine. Its README explicitly describes a collection of document-analysis programs rather than a turnkey product.

- **C1:** The network implementation exposes forward/backward sequence calculations, CTC alignment, numerical checks, and clipped updates instead of delegating everything to a modern training framework. Entry point: [LSTM and sequence networks](https://github.com/ocropus-archive/DUP-ocropy/blob/master/ocrolib/lstm.py).
- **C2:** A common network protocol supports stacked, reversed, and parallel compositions. The separate line normalizer measures a centerline, dewarps the image, and scales it while checking that the measured and supplied shapes agree. Study this separation between optical normalization and sequence recognition. Entry point: [line normalization](https://github.com/ocropus-archive/DUP-ocropy/blob/master/ocrolib/lineest.py).

### 14. [tmbdev/clstm](https://github.com/tmbdev/clstm)

**Language/role:** C++/Eigen with Python bindings; compact OCR line-recognition and training engine. **Historical:** the README says maintenance mode; the inspected default-branch feed ends in October 2019. It follows OCRopy's numerical approach but is a separate C++ implementation, not merely a binding.

- **C1:** CTC alignment computes forward/backward quantities in log space, floors probabilities and normalization denominators, and checks dimensional compatibility. This makes numerical semantics unusually accessible. Entry point: [CTC implementation](https://github.com/tmbdev/clstm/blob/master/ctc.cc).
- **C2:** `INetwork` gives layers common sequence input/output ports, subnetworks, parameter/state traversal, codecs, and persistence hooks. OCR drivers reuse these abstractions for trainable image-to-text transformations. Entry point: [network interfaces](https://github.com/tmbdev/clstm/blob/master/clstm.h).

### 15. [uliss/quneiform](https://github.com/uliss/quneiform)

**Language/role:** C/C++; experimental refactoring fork of the Cuneiform OCR engine, with a Qt GUI. **Historical:** the inspected default-branch feed ends in December 2012. Its separate recognition-server, API, and testing work justify treating it as a substantive fork; no second Cuneiform copy is counted.

- **C1:** Process-based recognition transfers images/options/results through shared memory, tracks recognition states, handles allocation failures and worker exit codes, and imposes worker timeouts. Study containment of failures in a legacy engine; some manual-layout operations are explicitly unimplemented. Entry point: [process recognition server](https://github.com/uliss/quneiform/blob/master/src/puma/processrecognitionserver.cpp).
- **C2:** The C interface separates recognition options, formatting options, page ownership, local versus process-based recognition, and multiple export destinations. These are reusable integration boundaries around a large legacy subsystem. Entry point: [C API](https://github.com/uliss/quneiform/blob/master/api/c/c_api.h).

## Script-specific, formula, and scene-text recognizers

### 16. [breezedeus/CnOCR](https://github.com/breezedeus/CnOCR)

**Language/role:** Python/PyTorch; Chinese/English OCR with additional model integrations. GitHub records fork ancestry from `diaomin/crnn-mxnet-chinese-text-recognition`; the documented rewrite and subsequent model/runtime development establish substantial independent evolution.

- **C2:** Encoder/decoder managers construct DenseNet/MobileNet-style visual encoders and recurrent or other decoding configurations while tracking output dimensions. The repository includes training and native recognition models as well as adapters. Entry point: [recognition-model construction](https://github.com/breezedeus/CnOCR/blob/master/cnocr/models/ocr_model.py).
- **C4:** Release notes span 2019–2026 and explicitly cover incompatible model generations, the MXNet-to-PyTorch rewrite, multi-instance initialization fixes, batching additions, and torch/torchvision compatibility repairs. This is unusually useful evidence for studying ecosystem migration without confusing a new backend with unchanged compatibility. Entry point: [release history](https://github.com/breezedeus/CnOCR/blob/master/docs/RELEASE.md).

### 17. [kha-white/manga-ocr](https://github.com/kha-white/manga-ocr)

**Language/role:** Python/Transformers; Japanese region recognition, including multiline manga text. Retained for its development/training and synthetic-data subsystem, not merely the small inference front end. It does not provide full-page text detection by itself.

- **C1:** Synthetic examples must keep visible text, font coverage, and training transcripts consistent. The generator selects characters supported by the selected font, treats kanji and ASCII runs differently, and injects furigana while retaining a separate ground-truth transcription. Entry point: [synthetic example generator](https://github.com/kha-white/manga-ocr/blob/master/manga_ocr_dev/synthetic_data_generator/generator.py).
- **C2:** The training factory composes configurable vision encoders and text decoders, adjusts cross-attention and decoder depth, and aligns tokenizer special tokens with the generated model configuration. Study how a specialized recognition domain is built on reusable model and data interfaces. Entry point: [model/processor factory](https://github.com/kha-white/manga-ocr/blob/master/manga_ocr_dev/training/get_model.py).

### 18. [kotaro-kinoshita/yomitoku](https://github.com/kotaro-kinoshita/yomitoku)

**Language/role:** Python/PyTorch/ONNX; Japanese document OCR and layout analysis. The relevant OCR subsystem combines text detection with a PARSeq-derived recognizer; its own models, normalization, geometry, and deployment logic make it more than a generic model wrapper.

- **C1:** Recognition distinguishes models trained with NFKC normalization from those needing explicit character replacement tables, and has confidence-controlled orientation fallback. These choices can change the actual transcription of Japanese and composite glyphs. Entry point: [text recognizer](https://github.com/kotaro-kinoshita/yomitoku/blob/main/src/yomitoku/text_recognizer.py).
- **C3:** Width bucketing, dynamic-width inference, CPU batch concurrency, and source downscaling address inference cost. The implementation explicitly disables dynamic widths for fixed-shape ONNX exports, exposing a real backend constraint.
- **C2:** Detection and recognition configurations feed a common OCR result schema carrying text, geometry, direction, and separate confidence values. Entry point: [OCR composition](https://github.com/kotaro-kinoshita/yomitoku/blob/main/src/yomitoku/ocr.py).

### 19. [lukas-blecher/LaTeX-OCR](https://github.com/lukas-blecher/LaTeX-OCR)

**Language/role:** Python/PyTorch; pix2tex mathematical-formula image recognition. This is equation transcription to LaTeX, not general page OCR. Study variable-size image handling at the junction of convolutional and transformer models.

- **C1:** The hybrid encoder derives positional-embedding indices from actual image dimensions and enforces patch-size compatibility with the convolutional backbone. Incorrect relationships here silently corrupt image-token geometry or break tensor shapes. Entry point: [hybrid encoder](https://github.com/lukas-blecher/LaTeX-OCR/blob/main/pix2tex/models/hybrid.py).
- **C2:** A callable `LatexOCR` interface coordinates configuration, tokenizer, checkpoint, image resizer, and model; the repository also contains training, formula rendering, and dataset preparation. Its resize/pad routine makes minimum and maximum input dimensions explicit. Entry point: [recognition interface](https://github.com/lukas-blecher/LaTeX-OCR/blob/main/pix2tex/cli.py).

### 20. [baudm/parseq](https://github.com/baudm/parseq)

**Language/role:** Python/PyTorch; scene-text recognition model and training/comparison framework. A cropped-text recognizer rather than a page detector. Repository metadata showed its latest push in May 2024; treat it as a research reference without assuming current dependency support.

- **C1:** Training permutations and attention masks must preserve the semantics of beginning/end tokens and padded sequences. At inference, causal and cloze masks support different decoding paths without exposing forbidden context. Entry points: [permutation training](https://github.com/baudm/parseq/blob/main/strhub/models/parseq/system.py) and [recognition model](https://github.com/baudm/parseq/blob/main/strhub/models/parseq/model.py).
- **C3:** The model supports autoregressive or non-autoregressive decoding and optional iterative refinement. Autoregressive decoding uses a single position query at each step and stops the batch once every item has emitted an end token. This gives concrete, localized mechanisms for studying latency versus contextual refinement.

### 21. [NMAC427/SwiftOCR](https://github.com/NMAC427/SwiftOCR)

**Language/role:** Swift; native recognition of short alphanumeric strings. **Explicitly deprecated and unmaintained**, according to the repository. Retained as an implementation study of a small optical pipeline, not as a deployment recommendation.

- **C1:** Connected-component extraction uses union-find labels, component geometry, merging thresholds, and splitting heuristics for touching characters. The character inventory must preserve the order used to train the neural network. Entry point: [segmentation and recognition](https://github.com/NMAC427/SwiftOCR/blob/master/framework/SwiftOCR/SwiftOCR.swift).
- **C3:** GPUImage filters perform preprocessing, while recognition is dispatched asynchronously; the stages are visible in one compact native implementation. This is evidence of performance-conscious structure, not an endorsement of the README's historical comparative benchmark.
- **C2:** Separate training code generates examples with configurable fonts and trains against a held-out generated set. It provides a concrete route to adapting the constrained recognizer. Entry point: [training subsystem](https://github.com/NMAC427/SwiftOCR/blob/master/framework/SwiftOCR/SwiftOCRTraining.swift).

## Generative OCR and large-scale document transcription

### 22. [datalab-to/surya](https://github.com/datalab-to/surya)

**Language/role:** Python; OCR and document-analysis models with an inference backend layer. The inspected branch uses generative full-page/block recognition; older descriptions of Surya's architecture should not be assumed to describe this version.

- **C1:** Recognition checks blank text regions, detects repetitive generation, and documents escalating-temperature regeneration before falling back to block recognition. Cropping clamps coordinates and handles degenerate boxes. Study explicit mitigation of generative OCR failure modes. Entry point: [recognition orchestration](https://github.com/datalab-to/surya/blob/master/surya/recognition/__init__.py).
- **C2:** Backends share server lifecycle, batch-generation, and capacity interfaces. A server handle distinguishes a process started by the library from an existing service, so shutdown ownership remains explicit. Entry point: [backend contract](https://github.com/datalab-to/surya/blob/master/surya/inference/backends/base.py).
- **C3:** Backend-reported capacity informs aggregate in-flight concurrency, connecting deployment topology to batch throughput rather than hiding it behind a single prediction call.

### 23. [allenai/olmocr](https://github.com/allenai/olmocr)

**Language/role:** Python; trainable generative OCR toolkit and document-transcription pipeline for dataset construction. It includes training and evaluation alongside orchestration, so it is not just an external OCR-service client.

- **C1:** The page pipeline distinguishes connection failures from invalid recognition, retries rotation corrections sequentially, adapts other retries to server queue state, and cancels redundant attempts after success. Study how stochastic output and infrastructure failure require different recovery policies. Entry point: [page-processing pipeline](https://github.com/allenai/olmocr/blob/main/olmocr/pipeline.py).
- **C2:** The work queue separates scheduling from local/S3 storage through a backend interface with completion markers and expiring worker locks. These expose restart and coordination semantics; they do not by themselves prove exactly-once execution. Entry point: [work queue](https://github.com/allenai/olmocr/blob/main/olmocr/work_queue.py).
- **C3:** Independent semaphores bound PDF rendering and inference requests, while retry scheduling observes server load. This is a useful large-corpus counterpart to the smaller line-recognition engines above.

### 24. [Ucas-HaoranWei/GOT-OCR2.0](https://github.com/Ucas-HaoranWei/GOT-OCR2.0)

**Language/role:** Python/PyTorch; unified generative OCR research implementation with training code. The relevant implementation is under `GOT-OCR-2.0-master/GOT`, including the visual encoder, Qwen-based decoder integration, and crop-aware inference.

- **C1:** The model replaces image-token spans with visual features and explicitly verifies matching start/end markers and the location of the closing marker relative to the feature count. These checks reveal essential multimodal sequence invariants. Entry point: [model integration](https://github.com/Ucas-HaoranWei/GOT-OCR2.0/blob/main/GOT-OCR-2.0-master/GOT/model/GOT_ocr_2_0.py).
- **C3:** Dynamic preprocessing chooses an aspect-ratio-aware grid subject to crop-count bounds and can append a thumbnail. The mechanism trades visual detail against the number of image patches presented to the decoder. Entry point: [dynamic crop inference](https://github.com/Ucas-HaoranWei/GOT-OCR2.0/blob/main/GOT-OCR-2.0-master/GOT/demo/run_ocr_2.0_crop.py).

### 25. [deepseek-ai/DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR)

**Language/role:** Python/PyTorch; OCR-oriented visual compression model with a substantive vLLM implementation. Counted once, including its encoder, image processor, and inference adapters. Study the interface between document resolution, visual-token accounting, and language-model serving.

- **C1:** The vLLM adapter calculates the number of image tokens, replaces prompt markers accordingly, validates image inputs, and merges visual embeddings with token embeddings. Processor and model must agree on these counts and layouts. Entry point: [multimodal model adapter](https://github.com/deepseek-ai/DeepSeek-OCR/blob/main/DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py).
- **C3:** The image processor chooses bounded grids using document aspect ratio; configurable base resolution and crops change the visual-token workload. The separate processing/model layers make this resource tradeoff inspectable. Entry point: [image tiling and processing](https://github.com/deepseek-ai/DeepSeek-OCR/blob/main/DeepSeek-OCR-master/DeepSeek-OCR-vllm/process/image_process.py). No comparative throughput claim is inferred from the project's advertised results.

## Search coverage, exclusions, and limitations

Discovery used more than six distinct formulations, including general OCR architecture; multilingual detector/recognizer toolkits; Rust and lightweight C++/ONNX/NCNN runtimes; historical-document and handwriting engines; Japanese, Chinese, and mathematical OCR; Swift/native implementations; scene-text transformer recognition; generative/VLM OCR; Java/C# implementations versus bindings; and classical GOCR/Ocrad/Cuneiform projects. Follow-up searches pursued less prominent implementations and current canonical locations. Late queries mostly returned application shells, duplicated model ports, or additional deployments of already-covered families; the substantive late additions were CLSTM and Quneiform.

Every retained repository's canonical GitHub identity was checked through its repository page or the GitHub API. At least one additional implementation or technical-documentation source was opened and read for every entry; identical README copies were not counted as independent evidence. Source links use branches verified during research. GitHub's unauthenticated API rate limit was reached partway through the investigation; subsequent verification used public repository pages, source files, and commit feeds. No candidate code was executed, no dependencies were installed, and no large repositories were cloned.

Important scope decisions:

- OCRmyPDF-style PDF processing, OCR desktop interfaces, hosted-service SDKs, model-only collections, and simple language bindings were excluded as adjacent layers rather than independent recognition engines. A detection-only model also does not automatically qualify as an OCR engine.
- [PyLaia's former GitHub repository](https://github.com/jpuigcerver/PyLaia) explicitly redirects development/maintenance to Teklia's GitLab fork. No official current substantive GitHub mirror was established, so it is excluded; the original Lua Laia is independently included and labeled historical.
- [GOCR's official distribution page](https://jocr.sourceforge.net/download.html) and [GNU Ocrad's project site](https://www.gnu.org/software/ocrad/) surfaced during classical-engine searches, but an official substantive GitHub mirror was not established. Unofficial copies were not used to manufacture additional entries.
- `chineseocr_lite` and several derivative native deployments were inspected or surfaced in searches but were not added alongside every related model port. RapidOCR and the other retained runtimes give stronger complementary coverage of deployment abstractions. Shared model ancestry is disclosed where relevant; it does not mean those projects are independent accuracy baselines.

The coverage is strongest for Python neural engines, with C++, Rust, Lua, and Swift providing contrasting implementation styles. There is less verified coverage of classical feature-based engines because of the GitHub-only boundary. Repository status checks establish archived/deprecated labels and observed activity, not a promise of support. Performance criteria refer to inspected mechanisms; no independent speed or recognition-quality benchmark was run. Pretrained-weight availability, licensing, and domain accuracy require separate evaluation for deployment.
