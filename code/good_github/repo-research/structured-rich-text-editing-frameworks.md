# Structured rich-text editing frameworks

Research date: **2026-10-09**

This selection covers 25 repositories that implement reusable editing models, transformations, schemas, extension systems, or native rich-text composition. It includes browser engines, substantial toolkits built on other engines, block editors, and native frameworks. HTML-oriented editors qualify where their internal structure and editing semantics provide substantive engineering material. General code editors, document viewers, and collaboration algorithms without an editing framework are outside the scope.

Each repository's canonical GitHub location and additional primary material were opened. The implementation and documentation links within the entries are recommended reading entry points. Criteria are engineering judgments grounded in those sources, not certifications of correctness or claims that every subsystem is exemplary. An unarchived repository is not automatically described as actively maintained.

**Criteria legend**

- **C1 — Difficult correctness:** document invariants, concurrent changes, selection and Unicode semantics, adversarial input, or failure handling.
- **C2 — Reusable abstractions:** substantial models, schemas, transformations, and extension mechanisms supporting multiple applications.
- **C3 — Performance with structure:** concrete mechanisms addressing editing costs while retaining understandable architectural boundaries.
- **C4 — Sustained evolution:** multi-year evidence of compatibility work, regression handling, testing, or complexity management; age alone is insufficient.

## Browser editing engines and document models

### [ianstormtaylor/slate](https://github.com/ianstormtaylor/slate)

**Language/role:** TypeScript; a customizable nested document model and editing framework, commonly integrated with React.

Study how an extensible editor preserves a small set of universal structural invariants while allowing application-specific schemas. Its normalization design exposes the tradeoff between convenient automatic repair and the possibility of nonterminating custom repair rules.

- **C1:** Elements must contain a text descendant so selection positions remain representable; inline nodes require padding in particular positions; adjacent equivalent text nodes are merged. Custom normalization runs in multiple passes, and the guide explicitly discusses infinite loops and temporarily suppressing normalization during compound transformations. See [normalization constraints and repair rules](https://docs.slatejs.org/concepts/11-normalizing).
- **C2:** The same normalization hook permits domain-specific restrictions through editor overrides while delegating remaining cases to the original implementation. This is a reusable schema mechanism rather than a fixed toolbar vocabulary; the linked guide demonstrates adding constraints without replacing the document engine.

### [facebook/lexical](https://github.com/facebook/lexical)

**Language/role:** TypeScript; an extensible editor engine with node classes, immutable committed state, and framework integrations.

The useful study boundary is the transition from mutable pending state to an immutable snapshot and then to the DOM. It makes update scheduling, state ownership, and reconciliation explicit.

- **C1:** Reads and writes occur in defined synchronous contexts; mutation outside an update is rejected. The distinction between pending and committed state also matters when immediately serializing content. See [Editor State](https://lexical.dev/docs/concepts/editor-state).
- **C2:** The node tree and selection belong to editor state rather than being recovered from arbitrary DOM; node APIs and transforms support application-defined content and behavior within that model.
- **C3:** Transforms run before reconciliation, iterating dirty leaves and elements toward a fixed point. The reconciler can skip clean subtrees, and the documentation explains why starting another update from an update listener adds unnecessary reconciliation. See [node transforms and dirty-node processing](https://lexical.dev/docs/concepts/transforms).

### [slab/quill](https://github.com/slab/quill)

**Language/role:** TypeScript; rich-text editor organized around the Parchment document abstraction and Delta operations.

Quill is particularly instructive for connecting semantic editor objects to DOM nodes while keeping a canonical representation. Parchment and Delta are considered part of this study, not separately counted repositories.

- **C1:** Parchment's structural constraints require container children, represent an empty block with a break, and optimize redundant markup. Equivalent formatting should not accumulate arbitrary wrapper structures. The [Parchment guide](https://quilljs.com/docs/guides/cloning-medium-with-parchment) explains these canonicalization rules and their consequences for custom formats.
- **C2:** Custom inline, block, and embedded content is expressed through Blot subclasses and attributes. The same guide builds several content types using creation, format extraction, and inherited behavior, making the object model a useful example of extensibility at the model/DOM boundary.

### [ckeditor/ckeditor5](https://github.com/ckeditor/ckeditor5)

**Language/role:** TypeScript and JavaScript; editor framework monorepo. Focus on the editing engine, schema, conversion, and transaction machinery.

Study the separation between a semantic model, an editing view, and a data view. This is a large architecture in which conversion and selection behavior are first-class components rather than serialization afterthoughts.

- **C1:** Tree operations, operational transformation, batches for undo, and live positions must agree despite different concepts of node index, offset, and path. Selection attributes and markers introduce further state that has to move consistently with edits. These interactions are explained in the [editing-engine architecture](https://ckeditor.com/docs/ckeditor5/latest/framework/architecture/editing-engine.html).
- **C2:** Schema rules constrain the model, while separate upcast and downcast conversion pipelines connect it to data and editing representations. Writers and change blocks provide a common mutation interface for independent editing features. The architecture guide is the best initial entry point before following individual engine packages.

### [microsoft/roosterjs](https://github.com/microsoft/roosterjs)

**Language/role:** TypeScript; browser editor with a content-model layer between the DOM and formatting operations.

The repository separates content-model types, DOM conversion, core editor behavior, formatting APIs, and plugins. This makes it useful for studying incremental replacement of DOM-centric editing with a reusable intermediate model.

- **C1:** The [formatContentModel implementation](https://github.com/microsoft/roosterjs/blob/master/packages/roosterjs-content-model-core/lib/coreApi/formatContentModel/formatContentModel.ts) coordinates nested undo snapshots, focus-sensitive selection restoration, pending caret formatting, and change notifications. Its nested-operation flag is cleared with `finally`, showing concrete attention to failure paths.
- **C2:** The same formatting pipeline accepts model-level formatting callbacks while core services handle snapshots, rendering, selection, and cache lifetime. The repository's package architecture provides reusable conversion and formatting layers rather than requiring each plugin to manipulate browser state independently.

### [basecamp/trix](https://github.com/basecamp/trix)

**Language/role:** JavaScript; document-model editor exposed through web components.

Trix treats browser editing as input to its own document operations and renders the resulting model. Its smaller document vocabulary is useful for understanding complete model ownership without beginning with a large schema ecosystem.

- **C1:** The [Document implementation](https://github.com/basecamp/trix/blob/main/src/trix/models/document.js) handles deletion across block boundaries, preservation or removal of block breaks, and reconciliation of block attributes. Range arithmetic and newline behavior are integral to editing semantics.
- **C2:** Documents are composed from blocks, text, and pieces, with operations producing new document values. Combined with the repository's editor API and attachment model, this provides a reusable layer for commands and embedded content separate from the custom-element UI. Start with `document.js` and follow its model collaborators.

### [tinymce/tinymce](https://github.com/tinymce/tinymce)

**Language/role:** TypeScript; HTML-oriented editor framework. Focus on `modules/tinymce`, particularly schema-aware parsing and sanitization.

TinyMCE provides a contrasting architecture to JSON-tree editors: browser-compatible HTML, internal editor markers, and input sanitization must coexist. Its maintenance record also exposes the long tail of editing behavior.

- **C1:** [Sanitization.ts](https://github.com/tinymce/tinymce/blob/main/modules/tinymce/src/core/main/ts/html/Sanitization.ts) combines DOMPurify hooks with editor schema decisions about allowed elements, attributes, namespaces, and URLs. It must distinguish content to remove or unwrap while preserving permitted internal state. This is substantive adversarial-input handling, not a claim that every integration is safe by default.
- **C4:** The [changelog](https://github.com/tinymce/tinymce/blob/main/modules/tinymce/CHANGELOG.md) spans releases from 2014 through 2026 and records browser compatibility, selection and paste regressions, API transitions, and sanitizer fixes. It provides direct evidence of managing accumulated behavior across generations of the editor.

### [wikimedia/VisualEditor](https://github.com/wikimedia/VisualEditor)

**Language/role:** JavaScript; standalone rich HTML editing engine. **Official substantive GitHub mirror** of Wikimedia's Gerrit repository, as identified on the repository page.

Study the paired representations of a document: linear content suitable for range operations and a derived spanning tree suitable for structural navigation. The model is unusually explicit about intermediate states visible to observers.

- **C1:** Transactions must collectively preserve tree validity even when individual linear splices do not. `TreeModifier` applies the corresponding tree changes while maintaining a valid tree for event listeners. Reversible transactions and rebasing further constrain the implementation. See [data-model internals](https://www.mediawiki.org/wiki/VisualEditor/Internals/DM).
- **C3:** The linear array supports slicing and range replacement, while the spanning tree supplies parent/child navigation and structural indexing. The documented split is a concrete design response to different editing access patterns, not a numerical speed claim. The same internals guide explains both representations and their synchronization.

### [substance/substance](https://github.com/substance/substance)

**Language/role:** JavaScript; structured document and annotation framework for publishing-oriented editors.

Substance is worth studying for documents whose annotations and relationships are richer than a sequence of formatted paragraphs. The model and its transformation machinery are substantial independent implementations.

- **C1:** [TextOperation.js](https://github.com/substance/substance/blob/master/model/TextOperation.js) implements application, inversion, conflict detection, and pairwise transformation. It explicitly handles overlapping deletions and insertions inside deleted ranges, including configurable conflict rejection. These policies reveal the semantics behind collaborative edit handling; they are not evidence of a universal convergence guarantee.
- **C2:** [Document.js](https://github.com/substance/substance/blob/master/model/Document.js) instantiates schema-defined nodes and maintains indexes for types, property annotations, container annotations, and relationships. Importing dependent nodes and constructing selections belong to the same reusable document layer, supporting domain-specific authoring applications.

## Extension frameworks and block-oriented toolkits

These projects are retained for substantial editing abstractions of their own. Tiptap, Remirror, Milkdown, and BlockNote share ProseMirror ancestry; Plate builds on Slate. They should not be interpreted as independent implementations of every underlying algorithm.

### [ueberdosis/tiptap](https://github.com/ueberdosis/tiptap)

**Language/role:** TypeScript; headless editor and extension framework over ProseMirror.

Study how an application-facing command system packages transaction semantics and extensible node/mark behavior. Its contribution is a substantial integration and extension layer around the lower-level engine.

- **C1:** A command chain combines changes into one transaction. Custom commands must use the supplied chain, and commands that manipulate transactions directly must honor the `dispatch` contract so `.can()` remains a nonmutating feasibility check. See [commands and chaining](https://tiptap.dev/docs/editor/api/commands).
- **C2:** Extensions add named commands that can be composed, tested for applicability, and selected through fallback command sequences. Together with the headless editor and node/mark extensions, this gives applications a reusable vocabulary without prescribing their UI. The command guide demonstrates the extension boundary directly.

### [remirror/remirror](https://github.com/remirror/remirror)

**Language/role:** TypeScript; editor framework combining ProseMirror extensions, lifecycle management, and React integrations.

Remirror is especially useful for studying the mismatch between synchronous editor transactions and asynchronously controlled application state.

- **C1:** In a controlled React editor, separate commands can each read stale state and cause an earlier change to be lost. Remirror's [controlled-editor guide](https://www.remirror.io/docs/controlled-editor/) explains why chained commands share a transaction and why some commands cannot participate in such chains.
- **C2:** Node, mark, and plain extensions aggregate schema, commands, keymaps, input rules, and lifecycle hooks. The [extension architecture](https://www.remirror.io/docs/concepts/extension/) distinguishes static schema options from dynamically changeable options and describes creation, state-update, and destruction hooks. This is substantive configuration and resource-lifetime management above the underlying engine.

### [udecode/plate](https://github.com/udecode/plate)

**Language/role:** TypeScript; Slate-based plugin framework and rich-text UI ecosystem. The canonical repository remains under `udecode`.

Study the conversion of common structural editing behavior into plugin configuration. Its useful contribution is not merely a collection of rendered controls.

- **C1:** [Plugin rules](https://platejs.org/docs/plugin-rules) govern breaking, deleting, merging, normalization, and selection. The table example preserves empty cell structure when content is merged out, while link normalization can remove empty links. This demonstrates why a generic deletion rule is insufficient across node types.
- **C2:** The [plugin model](https://platejs.org/docs/plugin) combines node classification, rendering, handlers, injected properties, deserialization, and configuration. Applications can assemble behavior by node type and override specific rules rather than duplicating the entire editor pipeline. This entry follows the documented Slate-based architecture.

### [Milkdown/milkdown](https://github.com/Milkdown/milkdown)

**Language/role:** TypeScript; Markdown-oriented editor framework integrating ProseMirror, Remark, and plugins.

The distinctive study target is translation between a Markdown syntax tree and a schema-constrained editable tree. The `packages/transformer` subsystem exposes the boundary clearly.

- **C1:** [Parser state](https://github.com/Milkdown/milkdown/blob/main/packages/transformer/src/parser/state.ts) tracks open nodes and marks, creates nodes through schema validation, and merges adjacent text only when mark sets agree. Correct nesting and mark scope are necessary to avoid changing formatting during conversion; this is a code-grounded assessment, not a claim of lossless conversion for arbitrary Markdown.
- **C2:** Parsing is dispatched through schema-provided matching functions and runners. A reusable state/stack mechanism supports multiple syntax constructs while plugins supply their mappings, making the transformer more general than a fixed Markdown-to-HTML renderer.

### [TypeCellOS/BlockNote](https://github.com/TypeCellOS/BlockNote)

**Language/role:** TypeScript; block-oriented editing framework over Tiptap/ProseMirror, with a reusable core and React UI.

BlockNote adds a typed application model for blocks, inline content, and styles. Its core API also has to reconcile application positions with different underlying collaboration mechanisms.

- **C1:** [positionMapping.ts](https://github.com/TypeCellOS/BlockNote/blob/main/packages/core/src/api/positionMapping.ts) selects between ordinary transaction mapping and Yjs-aware mapping. The source explains why Yjs synchronization disrupts normal ProseMirror mapping and exposes left/right bias when tracking positions. This is a concrete collaboration integration problem beyond presentation.
- **C2:** [Custom schemas](https://www.blocknotejs.org/docs/features/custom-schemas) extend or replace block, inline-content, and style specifications while carrying those choices into inferred editor types. Study the schema facade together with position tracking to see the benefits and obligations of a higher-level editing API.

### [codex-team/editor.js](https://github.com/codex-team/editor.js)

**Language/role:** TypeScript; block editor whose tools own typed, serializable content and rendering behavior.

Editor.js is a useful contrast to one large text tree: independent tools manage different block kinds under a common editor lifecycle.

- **C1:** The [Tools API](https://editorjs.io/tools-api/) specifies validation, paste handling, sanitization rules, merge behavior, and read-only support. Tools must preserve their own data contracts when content arrives through paste, conversion, or merging; configurable sanitization is evidence of input-boundary design, not a blanket safety guarantee.
- **C2:** Rendering, saving, cleanup, paste patterns, and import/export conversion are reusable tool interfaces. These allow a single editor host to coordinate paragraphs, media, and domain-specific blocks without hardcoding each block's implementation. The Tools API is the principal architectural entry point.

### [WordPress/gutenberg](https://github.com/WordPress/gutenberg)

**Language/role:** JavaScript/TypeScript, with PHP elsewhere in the monorepo; focus on the reusable `@wordpress/rich-text` package and its role inside block editing.

This entry counts the monorepo once and does not treat all WordPress functionality as rich-text infrastructure. The rich-text package offers an interesting representation between strings and full document trees.

- **C1:** A rich-text value contains text, per-character format arrays, embedded replacements, and selection offsets. Insertions, removals, splits, joins, and HTML conversion must keep these coordinated. The [rich-text package reference](https://developer.wordpress.org/block-editor/reference-guides/packages/packages-rich-text/) documents this representation and warns against constructing values manually.
- **C2:** String-like transformation functions return new rich-text values, while format registration supplies extensible formatting behavior. This creates a reusable editing layer that blocks can share without each implementing selection-aware formatting and serialization. Start with the representation section and transformation APIs in that reference.

## Native and cross-platform frameworks

### [superlistapp/super_editor](https://github.com/superlistapp/super_editor)

**Language/role:** Dart/Flutter; document editor, composition state, and editing infrastructure. Focus on the `super_editor` subsystem within the monorepo.

The request/command/reaction architecture is a useful example of making editing policy inspectable and replaceable outside a browser DOM.

- **C1:** [The core Editor](https://github.com/superlistapp/super_editor/blob/main/super_editor/lib/src/core/editor.dart) groups commands into transactions, runs reactions before final notifications, orders notifications to editable resources, and maintains undo/redo history. Nested command execution and history merging make the boundaries observable and consequential.
- **C2:** Requests are mapped to commands by handlers; commands produce change events; reactions may derive further edits. An editable context supplies resources such as the document and composer. Applications can substitute behavior at these stages rather than intercepting an opaque widget's keystrokes.

### [AppFlowy-IO/appflowy-editor](https://github.com/AppFlowy-IO/appflowy-editor)

**Language/role:** Dart/Flutter; standalone structured editor extracted as a reusable AppFlowy component.

Study the combination of hierarchical block paths and Delta-based inline content, with transactions carrying both document changes and selection changes.

- **C1:** [Transaction implementation](https://github.com/AppFlowy-IO/appflowy-editor/blob/main/lib/src/core/transform/transaction.dart) composes consecutive text operations, composes their inverses in the opposite order, transforms operation paths, and carries before/after selections. Changing a node's type deliberately replaces type-specific attributes to prevent stale state from leaking across block types.
- **C2:** The project's [architecture article](https://appflowy.com/blog/how-we-built-a-highly-customizable-rich-text-editor-for-flutter) explains generic nodes, selections, transactions, and pluggable node widget builders. Read it as the design explanation alongside current transaction source; the reusable separation is between document semantics and Flutter rendering, not merely a set of styled widgets.

### [singerdmx/flutter-quill](https://github.com/singerdmx/flutter-quill)

**Language/role:** Dart/Flutter; native rich-text editor using the Quill Delta representation, rather than a browser-editor wrapper.

Its history implementation is particularly valuable for understanding local undo when the document also receives changes from other sources.

- **C1:** [history.dart](https://github.com/singerdmx/flutter-quill/blob/master/lib/src/document/history.dart) constructs inverse Deltas, composes nearby edits, suppresses recording during undo/redo, and transforms history stacks through incoming changes in user-only mode. These operations expose the distinction between reverting a local intention and reverting an obsolete document snapshot.
- **C2:** The Delta document/history layer is separated from the controller, editor, toolbar, and custom embed builders described in the repository. This supports native applications with different controls and embedded content. The history source is a strong starting point before tracing document composition and controller calls; it does not by itself imply a complete collaboration service.

### [fleather-editor/fleather](https://github.com/fleather-editor/fleather)

**Language/role:** Dart/Flutter; native editor with a separate Parchment document package. It evolved from Zefyr/Notus; the ancestor is not counted again.

Fleather's Parchment is a Dart document implementation, distinct from Quill's TypeScript Parchment. Study its ordered editing rules and the explicit consequences of precedence.

- **C1:** [heuristics.dart](https://github.com/fleather-editor/fleather/blob/master/packages/parchment/lib/src/heuristics.dart) dispatches insertion, formatting, and deletion to ordered rule lists. Rules force block embeds onto separate lines and preserve line styles across splitting or merging; the first matching rule wins, so order is part of correctness.
- **C2:** Document heuristics return Deltas independently of the Flutter editing surface. The separate model and configurable rules support reusable editing semantics, while the [migration guide](https://github.com/fleather-editor/fleather/blob/master/MIGRATION.md) documents changes to controller, codec, and Delta-package interfaces. The repository describes its format as suitable for operational transformation, not as providing built-in collaboration.

### [rajdeep/proton](https://github.com/rajdeep/proton)

**Language/role:** Swift/UIKit; rich-text framework with commands, text processors, and attachments capable of hosting arbitrary views and nested editors.

Proton is useful for studying rich content embedded in a native text system: a view attachment has layout, selection, and ownership consequences beyond the attributed string itself. The repository explicitly warns that its pre-1.0 API may change.

- **C1:** [EditorViewTests.swift](https://github.com/rajdeep/proton/blob/main/Proton/Tests/Editor/EditorViewTests.swift) checks selection validity after replacement, invalid attachment ranges, clearing an attachment's container on deletion, and preserving surrounding newlines. These are concrete lifecycle and position invariants.
- **C2:** The repository's commands, ordered text processors, and view-backed attachments support distinct editing behaviors and nested content. [Attachment update snapshot tests](https://github.com/rajdeep/proton/blob/main/Proton/Tests/Attachments/AttachmentUpdateSnapshotTests.swift) exercise the abstraction through attachment resizing and view changes, providing a useful path into its layout responsibilities.

### [FXMisc/RichTextFX](https://github.com/FXMisc/RichTextFX)

**Language/role:** Java/JavaFX; styled-text framework supporting custom segment types as well as text. Its general document model is relevant even though code editors are a prominent use case.

The distinctive material is the parameterization of paragraph style, segment type, and segment style, paired with persistent document operations.

- **C2:** [ReadOnlyStyledDocument.java](https://github.com/FXMisc/RichTextFX/blob/master/richtextfx/src/main/java/org/fxmisc/richtext/model/ReadOnlyStyledDocument.java) is generic in all three dimensions. Together with segment operations, this permits non-string segments and application-defined styles without replacing document composition and navigation.
- **C3:** The implementation stores paragraphs in a finger tree with composable summaries of paragraph and character counts. Position lookup, split, concatenation, and leaf updates use this structure rather than flattening the entire document for every operation. This is a source-grounded architectural performance mechanism; no benchmark or asymptotic bound is asserted here.

### [MohamedRejeb/compose-rich-editor](https://github.com/MohamedRejeb/compose-rich-editor)

**Language/role:** Kotlin; rich-text state and editing components for Jetpack Compose and Compose Multiplatform.

This is a useful native counterpart to browser transaction engines: it must translate text-field and input-method edits into a formatted paragraph/span model while retaining rich-text history.

- **C1:** [EditPipeline.kt](https://github.com/MohamedRejeb/compose-rich-editor/blob/main/richeditor-compose/src/commonMain/kotlin/com/mohamedrejeb/richeditor/model/EditPipeline.kt) sorts changes in original coordinates, adjusts offsets using actual document-length changes, captures replaced styles, and distinguishes typing, deletion, and other history events. It also trims whole-text rewrites on the web to avoid needlessly losing formatting.
- **C2:** The pipeline operates on a reusable rich-text state and paragraph/span structure, integrated with the repository's HTML/Markdown conversion and shared Compose components. Its explicit edit boundary is useful for studying how platform text input can feed a common model without reducing formatting to a plain string.

### [element-hq/matrix-rich-text-editor](https://github.com/element-hq/matrix-rich-text-editor)

**Language/role:** Rust composer core with web, Kotlin, and Swift bindings; structured message composition for Matrix clients.

This is the official successor location identified by the archived `matrix-org` repository. The predecessor and successor are counted once, despite GitHub recording fork ancestry.

- **C1:** [delete_text.rs](https://github.com/element-hq/matrix-rich-text-editor/blob/main/crates/wysiwyg/src/composer_model/delete_text.rs) uses safe selections and grapheme-aware deletion. It also expands deletion around noneditable mentions and handles list-specific behavior, demonstrating that user-visible deletion cannot be implemented as decrementing a string offset.
- **C2:** A reusable Rust `ComposerModel`, generic Unicode-string handling, and structured composer updates support bindings for multiple UI platforms. The shared core centralizes editing semantics while integrations handle platform interaction. Start with the deletion implementation to see why sharing only markup conversion would be insufficient.

## Historical implementation study

### [facebookarchive/draft-js](https://github.com/facebookarchive/draft-js)

**Language/role:** JavaScript/Flow; React rich-text framework. **Archived on 2023-02-06**; included for historical architecture study, not as a maintained adoption recommendation.

Draft.js remains instructive for the interaction between immutable editing state and React's controlled-component model.

- **C1:** The [EditorState race-condition guide](https://draftjs.org/docs/advanced-topics-editorstate-race-conditions/) explains how multiple event handlers using stale state can overwrite a paste or another edit. It recommends basing transformations on the latest state supplied to editor callbacks. The failure is concrete and reproducible, rather than a generic claim that immutable data prevents races.
- **C2:** The repository separates `EditorState`, content, selection, modifiers, decorators, and entity-based rich content. These are reusable modeling boundaries for formatted editing; the race-condition guide shows why their integration with application state is as important as the individual immutable values.

## Search coverage, exclusions, and limitations

Discovery used distinct live searches for schema/transaction editors; operational-transformation architectures; extension frameworks over ProseMirror and Slate; block and Markdown editors; Flutter/Dart document engines; Swift view attachments; Java styled documents; Kotlin Compose editing; Rust shared composer cores; and publishing/annotation systems. Follow-up searches targeted normalization, parser state, controlled-state races, undo transformations, sanitization, tests, and release history. Later queries increasingly returned already-inspected projects, thin wrappers, generic CRDT libraries, or code editors, yielding diminishing returns for this category.

Canonical repository pages or GitHub API responses were checked for all 25 entries. Every entry also rests on opened documentation, source, or tests beyond its README. Repositories were not cloned or executed, and dependencies were not installed. Performance criteria describe visible mechanisms rather than measured comparisons; correctness criteria identify difficult contracts and concrete handling, not a complete audit. C4 is assigned only where the inspected history demonstrates sustained evolution, not from a creation date or recent push.

An important omission is ProseMirror's core GitHub repositories: [prosemirror-model](https://github.com/ProseMirror/prosemirror-model) states that development moved to another host and was archived on 2026-04-01. No continuing official GitHub mirror was established in this research, so the moved core was excluded under the GitHub-location requirement. Independently substantive frameworks built on it remain eligible. VisualEditor, in contrast, explicitly identifies its substantive GitHub repository as an official mirror.

General-purpose CRDT/OT libraries such as Yjs, Automerge, and Loro were excluded without an editing framework of their own in scope. Code-only editors, renderers, application-only note tools, tutorials, wrapper forks, and duplicate engine subpackages were also excluded. The Dart implementations are retained for native document and editing machinery rather than counted merely for reproducing a browser API. Fleather's ancestor and Matrix's predecessor were not counted separately.

The selection spans TypeScript/JavaScript, Dart, Swift, Java, Kotlin, and Rust, but remains naturally weighted toward browser and Flutter ecosystems. It is a guide to architectural study, not a ranking, an exhaustive census, or an endorsement of present-day support guarantees. Branch-based source links and documentation may evolve after the research date; historical and mirror status are called out where established.
