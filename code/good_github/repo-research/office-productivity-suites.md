# Office productivity suites

Research date: **2026-10-09**.

This selection covers integrated word-processing, spreadsheet, and presentation suites; frameworks for building those suites; and substantial engines or hosting layers used by them. It contains **15 repositories, not 15 independent products**. In particular, the three ONLYOFFICE implementation repositories belong to one suite, and Univer Workspace builds on Univer. Monorepos are counted once. Historical implementations are separated from contemporary projects, and official GitHub mirrors are identified.

The emphasis is on what an experienced engineer can learn from actual source and design material. Criterion assignments are grounded engineering judgments, not certifications of correctness, security, interoperability, or uniform code quality. The linked implementation and documentation files are suggested reading entry points.

Criteria legend:

- **C1 — Difficult correctness:** invariants, concurrency, numerical or document semantics, adversarial inputs, and failure handling.
- **C2 — Reusable abstractions:** substantial models, interfaces, frameworks, or services supporting multiple applications and use cases.
- **C3 — Performance with structure:** concrete resource or latency constraints addressed through understandable architectural mechanisms.
- **C4 — Sustained evolution:** years of changes accompanied by compatibility work, testing, or explicit management of complexity.

## Integrated desktop suites

### 1. [LibreOffice/core](https://github.com/LibreOffice/core)

**Language/role:** Primarily C++; complete suite, including Writer (`sw`), Calc (`sc`), and Draw/Impress (`sd`). **Official read-only GitHub mirror**; development review takes place on LibreOffice Gerrit.

Study how application-specific document models coexist with a shared component system, rendering toolkit, and document lifecycle. This is an especially useful codebase for understanding why office compatibility involves much more than parsing ZIP and XML files.

- **C1:** Calc's [formula regression tests](https://github.com/LibreOffice/core/blob/master/sc/qa/unit/ucalc_formula.cxx) exercise reference parsing, quoted sheet names, token equality, formula grammar conversion, implicit intersection, and reference updates. These are concrete examples of preserving spreadsheet meaning through edits and transformations.
- **C2:** The repository's [architecture overview](https://github.com/LibreOffice/core#the-important-bits-of-code) distinguishes the VCL rendering/widget layer, UNO framework, shared `sfx2` document/load/save machinery, and individual applications. These are substantial cross-suite abstractions rather than unrelated bundled programs.
- **C3:** The [Calc internals note](https://github.com/LibreOffice/core/blob/master/sc/README.md) specifies a column-oriented binary cache with typed cell blocks for quick serialization. It provides a small, understandable entry into performance-sensitive storage inside a much larger suite.

### 2. [apache/openoffice](https://github.com/apache/openoffice)

**Language/role:** Primarily C++, with Java and scripting support; Apache OpenOffice suite. **Official Apache GitHub repository synchronized with the ASF GitBox source.**

Study the UNO component contracts and the office-wide document APIs. Although it shares ancestry with LibreOffice, it is a separately evolved suite; this entry focuses on its explicit component semantics, not on counting the common ancestry twice as independent invention.

- **C1:** [`XInterface.idl`](https://github.com/apache/openoffice/blob/trunk/main/udkapi/com/sun/star/uno/XInterface.idl) specifies stable interface-query results, object identity across interface views, and balanced reference acquisition/release. The comments explain why these invariants permit runtime caching and how language bindings affect the contract.
- **C2:** [`XDocumentProperties.idl`](https://github.com/apache/openoffice/blob/trunk/main/offapi/com/sun/star/document/XDocumentProperties.idl) exposes shared document metadata, user-defined properties, and loading/saving through storage or media. It is a reusable office API that bridges arbitrary importers, ODF packages, and loaded documents.

These interfaces are useful reading precisely because they state obligations that implementation classes and extensions must preserve; their existence does not prove every implementation satisfies them.

### 3. [KDE/calligra](https://github.com/KDE/calligra)

**Language/role:** C++/Qt/KDE; Words, Sheets, Stage, and related graphics applications. **Official KDE GitHub mirror**; the repository points to KDE Invent as upstream.

Study a suite organized around shared editable shapes and application-specific content models. Its Flake architecture offers a different decomposition from the UNO family.

- **C2:** [`KoShape.h`](https://github.com/KDE/calligra/blob/master/libs/flake/KoShape.h) defines a common shape abstraction with independent data backends, painting, ODF persistence, coordinate transformations, hierarchy notifications, and interaction permissions. The documented model/view separation permits multiple shapes to display the same underlying data.
- **C1:** Sheets' [`DependencyManager.cpp`](https://github.com/KDE/calligra/blob/master/sheets/engine/DependencyManager.cpp) maintains provider/consumer relationships, regenerates dependencies after named-area changes, removes stale circular-dependency flags, and detects recursion while calculating dependency depths. Its use of spatial range indexing alongside dependency maintenance makes spreadsheet invalidation particularly instructive.

Read the comments and incomplete branches critically: the code is evidence of substantial engineering problems and mechanisms, not a claim that every edge case is finished.

### 4. [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice)

**Language/role:** TypeScript/Electron with a Rust spreadsheet sidecar; desktop Docs, Sheets, Slides, and other document tools. Relevant subsystems are its own document engines and transaction handling, beyond the AI interface.

Study how direct UI editing and programmatic operations can share the same mutation path while retaining office-package structure.

- **C1:** Slides' [`applySessionTxn` and `journaledTxn`](https://github.com/genspark-ai/genoffice/blob/main/apps/slides/src/main/slides-main.ts) validate batches, distinguish atomic from per-operation execution, rehearse changes before touching undo history, mark archive-only edits dirty, and resolve slides by durable identity after structural edits. These address concrete rollback, redo preservation, and incorrect-target failure modes.
- **C2:** The [`pptx-engine` API](https://github.com/genspark-ai/genoffice/blob/main/packages/pptx-engine/src/index.ts) separates package parsing, relationships, themes, slide transfer, resource cleanup, identity, and targeted XML modification from the Electron application. It is substantial reusable document machinery, not merely a call to an external office executable.

**Limit:** The inspected [Slides journal design](https://github.com/genspark-ai/genoffice/blob/main/docs/slides-op-journal.md) explicitly describes collaboration groundwork with no network transport yet. Do not mistake same-process sharing for a completed multi-user collaboration system or interpret preservation goals as universal compatibility guarantees.

### 5. [tuna-os/gtk-office-suite](https://github.com/tuna-os/gtk-office-suite)

**Language/role:** Rust/GTK4; Letters, Tables, and Decks. **Explicitly pre-alpha:** the project's own status warns that it is not ready for everyday documents.

Study the separation between testable document engines and GUI projections, and the defensive handling of packaged office formats. Its value here is its implementation structure, not parity with established suites.

- **C1:** [`zip_guard.rs`](https://github.com/tuna-os/gtk-office-suite/blob/main/suite-common-core/src/zip_guard.rs) enforces member-count, individual decompression, and aggregate decompression budgets. It bounds actual reads instead of trusting attacker-controlled uncompressed sizes, reads one byte beyond the limit to detect overflow, and distinguishes oversized from unreadable parts.
- **C2:** The [architecture document](https://github.com/tuna-os/gtk-office-suite/blob/main/docs/ARCHITECTURE.md) separates GTK-free document models, file formats, and undo commands from GUI binaries. Shared crates supply atomic saves, autosave, formatting, style primitives, package limits, and PDF export across the three applications.

The repository also distinguishes model round trips, LibreOffice oracle comparisons, and GUI journeys. Those testing layers are useful to study, but no C4 claim is made for this emerging implementation.

## Collaborative web suites and suite frameworks

### 6. [CollaboraOnline/online.mirror](https://github.com/CollaboraOnline/online.mirror)

**Language/role:** Primarily C++, with JavaScript/TypeScript browser code; Collabora Online and Collabora Office monorepo. **Official read-only mirror of Collabora Gerrit.** Counted once, including its document engine; the older `online` issue-tracking location is not a second source-code entry.

Study the boundary between the web service daemon, isolated document-rendering processes, browser sessions, and remote WOPI storage. The repository explicitly distinguishes `engine`, `wsd`, `kit`, `browser`, C++ tests, and browser integration tests.

- **C1:** [`DocumentBroker.hpp`](https://github.com/CollaboraOnline/online.mirror/blob/main/wsd/DocumentBroker.hpp) documents document lifecycle states and a separate data-state model spanning remote storage, the local file, and the loaded engine. Saving and uploading are distinct operations, so lifecycle transitions must preserve unsaved changes and track which copy is current.
- **C3:** [`TileCache.hpp`](https://github.com/CollaboraOnline/online.mirror/blob/main/wsd/TileCache.hpp) exposes tile subscriptions, cancellation, invalidation, keyframes/deltas, and stale-render handling. Its comments discuss avoiding re-rendering regions a user has already scrolled past: a concrete bandwidth/rendering tradeoff with an inspectable implementation boundary.

### 7. [cryptpad/cryptpad](https://github.com/cryptpad/cryptpad)

**Language/role:** Primarily JavaScript; encrypted collaborative office suite with rich text, sheets, presentations, and additional applications. Some applications integrate external editing engines; the distinct implementation studied here is CryptPad's security and collaboration framework.

- **C1:** The [security architecture](https://docs.cryptpad.org/en/dev_guide/basics.html) combines content sanitization, CSP, and a separate-origin editor sandbox. The engineering challenge is to process another collaborator's content without exposing unrelated account data. This model still depends on receiving trustworthy client code from the host, as the repository explains.
- **C2:** The [application framework](https://docs.cryptpad.org/en/dev_guide/client/framework.html) centralizes document-history loading, ChainPad patches, reconnection, and common collaboration controls behind APIs consumed by application-specific editors.
- **C3:** The [client architecture](https://docs.cryptpad.org/en/dev_guide/client/architecture.html) shares a worker and WebSocket across tabs where supported, with fallback connectors using the same underlying code. It deliberately keeps document decryption outside the shared worker to avoid making one busy document slow every tab.

This is a particularly strong selection for studying how security boundaries constrain reusable UI and resource-sharing designs.

### 8. [dream-num/univer](https://github.com/dream-num/univer)

**Language/role:** TypeScript; embeddable office SDK for sheets, documents, and presentations, with browser and headless usage. The monorepo's shared core is the relevant subsystem.

Study the distinction between user intent, persistent document changes, and ephemeral interface state, and how plugins participate in that model.

- **C2:** [`command.service.ts`](https://github.com/dream-num/univer/blob/dev/packages/core/src/services/command/command.service.ts) distinguishes commands that orchestrate work, operations that change non-persistent UI state, and mutations that change snapshots. It supplies shared registration, dependency access, execution, and multi-command selection rather than duplicating those mechanisms for every editor.
- **C1:** The [command-service tests](https://github.com/dream-num/univer/blob/dev/packages/core/src/services/command/__tests__/command.service.spec.ts) check that synchronous and asynchronous sequences stop on failure or exception and report where execution stopped. Combined with the persistent/ephemeral distinction, this is concrete evidence for studying failure propagation and document-state discipline.

**Boundary:** The repository's capability matrix separates open-source packages from Pro features, including collaboration and some format-exchange capabilities. Do not assume every feature advertised across the Univer product family is implemented in this GitHub tree.

### 9. [dream-num/univer-workspace](https://github.com/dream-num/univer-workspace)

**Language/role:** TypeScript/React/Node.js; deployable multi-application office workspace built on Univer SDKs. This is a product and storage implementation, not another independent rendering engine.

Study how a real suite host adds identity, permissions, document hierarchy, isolated drafts, and recovery around an editing SDK.

- **C1:** The [workspace architecture](https://github.com/dream-num/univer-workspace/blob/main/apps/workspace/docs/architecture.md) gives product metadata, collaboration snapshots/revisions, and blob bytes separate owners. Cross-system writes use durable operations and recovery rather than assuming one SQLite transaction covers everything. WebSocket notifications invalidate cached views; authoritative data is read again through authenticated APIs.
- **C2:** The [client-core package](https://github.com/dream-num/univer-workspace/blob/main/packages/client-core/README.md) provides storage-neutral authentication, document/worktree workflows, bounded asset recovery, atomic local transfers, and a worker-backed content runtime while leaving credentials, sessions, and presentation to the host application. It is an internal reusable package, not a separately published SDK.

No multi-year maturity claim is made. The architecture also identifies which responsibilities remain in upstream SDKs, so those algorithms should not be credited to this repository.

## Substantial suite engines and hosting layers

The following ONLYOFFICE repositories are separate implementation units of the same product family. Its distribution umbrella, desktop pack, Docker images, and generated bundles are not counted as additional suites.

### 10. [ONLYOFFICE/sdkjs](https://github.com/ONLYOFFICE/sdkjs)

**Language/role:** JavaScript; shared client editing implementation used by ONLYOFFICE Docs and Desktop Editors. The source contains word-processing, spreadsheet, presentation, PDF, and shared editor code, not just an integration wrapper.

Study how a suite's undo/history representation intersects with remote changes, object identity, and editor-specific recalculation.

- **C1:** [`CollaborativeEditingBase.js`](https://github.com/ONLYOFFICE/sdkjs/blob/master/common/CollaborativeEditingBase.js) resolves incoming changes through object identifiers and a change factory, reconstructs serialized history records, schedules recalculation, tracks locks, and records changes that must be undone before remote changes can be accepted. These are concrete concurrency and state-ordering concerns.
- **C2:** The same common editing layer supports multiple editors, while the repository's [component map](https://github.com/ONLYOFFICE/sdkjs#-repository-structure-overview) separates shared modules from `word`, `cell`, `slide`, and other document types. The reusable unit is the editing machinery, not merely a consistent toolbar.

The implementation includes both older and newer change-loading paths, making compatibility complexity visible without assuming every path has equal test coverage.

### 11. [ONLYOFFICE/core](https://github.com/ONLYOFFICE/core)

**Language/role:** Primarily C++; conversion and rendering components shared by ONLYOFFICE's desktop and server products. Covers office formats across documents, spreadsheets, and presentations.

Study semantic translation between document models and the shared drawing vocabulary beneath different output formats.

- **C1:** [`DocxConverter.cpp`](https://github.com/ONLYOFFICE/core/blob/master/OdfFile/Writer/Converter/DocxConverter.cpp) handles OOXML-to-ODF conversion using section state, continuous versus page-breaking sections, inherited headers/footers, columns, page layouts, and style contexts. The source explicitly addresses style-name collisions. These are semantic preservation problems, not a mechanical XML rename.
- **C2:** [`IRenderer.h`](https://github.com/ONLYOFFICE/core/blob/master/DesktopEditor/graphics/IRenderer.h) defines a substantial common interface for pages, text, paths, images, brushes, clipping, transforms, and drawing commands. It provides a coherent abstraction to study across the suite's rendering and conversion backends.

This entry represents different code from `sdkjs`: native format/rendering infrastructure rather than browser-side editing and collaboration state.

### 12. [ONLYOFFICE/server](https://github.com/ONLYOFFICE/server)

**Language/role:** JavaScript/Node.js; backend coordination for ONLYOFFICE Docs. Particularly instructive for comparing deployment descriptions with the behavior actually present in the public source.

- **C1:** The current [`taskqueueMemory.js`](https://github.com/ONLYOFFICE/server/blob/master/Common/sources/taskqueueMemory.js) specifies expiration before delivery, delayed dead-letter events, idempotent acknowledgement, receiver removal, and protection against reentrant dispatch. Those distinctions matter when document conversion or response handling fails midway.
- **C3:** Its shared backend admits only one in-flight task per receiver and orders queued tasks by priority with FIFO ordering within equal priorities. This is explicit backpressure around an understandable queue abstraction, not an unsupported throughput claim.

**Material limitation:** The source expressly states that this public/community queue has no persistence, cross-process delivery, or broker reconnect logic. The legacy-named [`taskqueueRabbitMQ.js`](https://github.com/ONLYOFFICE/server/blob/master/Common/sources/taskqueueRabbitMQ.js) currently redirects to that memory implementation. Older README instructions mentioning RabbitMQ and Redis therefore do not establish distributed queue behavior in the inspected code.

### 13. [nextcloud/richdocuments](https://github.com/nextcloud/richdocuments)

**Language/role:** PHP plus JavaScript/TypeScript; Nextcloud Office's substantial WOPI hosting and integration layer. **Requires a separate Collabora server** and is not a second office rendering engine.

Study the point at which storage permissions, public sharing, remote editing, and file replacement meet. This is retained because it implements protocol and lifecycle behavior beyond embedding an editor iframe.

- **C1:** [`WopiController.php`](https://github.com/nextcloud/richdocuments/blob/main/lib/Controller/WopiController.php) derives write capability from document tokens and user locks, rejects timestamp mismatches as conflicts, checks available storage, and distinguishes a locked-file response from a generic server failure so clients can retry appropriately.
- **C2:** The controller provides a common storage-facing contract for different office document types and access modes, including ordinary users, public shares, versions, and federation. Check-file information, content transfer, save-as, and lock operations expose suite services without placing the document engine inside Nextcloud.

The [changelog](https://github.com/nextcloud/richdocuments/blob/main/CHANGELOG.md) is a useful second entry point for protocol changes, database migrations, older PHP/browser compatibility, and successive Nextcloud-version support. These are integration obligations, not evidence that a particular Collabora deployment is configured correctly.

## Historical suites with distinct engineering value

### 14. [neooffice/NeoOffice](https://github.com/neooffice/NeoOffice)

**Language/role:** Primarily C++ with Objective-C++ platform code; native macOS office suite derived from OpenOffice/LibreOffice. **Archived and discontinued**, as the [official project page](https://neooffice.github.io/) explicitly states.

This fork is retained because its macOS integration represents substantial separate work. Study the interaction between a portable office event loop and native modal dialogs, menus, drag/print operations, and platform lifetimes.

- **C1:** [`salinst.mm`](https://github.com/neooffice/NeoOffice/blob/NeoOffice-2021_branch/vcl/java/source/app/salinst.mm) documents and implements event-queue/SolarMutex ordering, avoids native-modal deadlocks, and rechecks shutdown state around event handling. The code ties several measures to specific historical bugs.
- **C4:** The official history describes nearly twenty years of native integration. The [release record](https://github.com/neooffice/NeoOffice/releases) documents continued adaptation to Intel/Apple Silicon, macOS and JDK changes, and VoiceOver pointer-lifetime failures, including fixes that proved insufficient and were revised. This is substantive compatibility and failure-management evidence, not just an old repository creation date.

Use it as a historical platform-integration study, not as a recommendation for current document compatibility.

### 15. [UlricE/SiagOffice](https://github.com/UlricE/SiagOffice)

**Language/role:** C and embedded Scheme, with X11 interfaces; Siag spreadsheet, Pathetic Writer, Egon Animator, and utilities. **Historical source tree:** GitHub metadata reports its last push in 2015; no present-day maintenance claim is made.

Study a smaller suite that achieves extensibility through scripting and external applications rather than a large component runtime.

- **C2:** [`xcommon/plugin.c`](https://github.com/UlricE/SiagOffice/blob/master/xcommon/plugin.c) defines a shared command/reply protocol over two pipes, with loading, saving, printing, window discovery, embedding, and teardown. It documents response requirements and timeout behavior, providing a concrete reusable extension boundary across the suite.
- **C4:** The [ChangeLog](https://github.com/UlricE/SiagOffice/blob/master/ChangeLog) records years of shared-resource refactoring, platform/build fixes, ICCCM clipboard corrections, Excel formatting work, and OpenOffice import support. It also records changes to numeric coercion and inter-sheet references, showing that compatibility and semantics evolved alongside the applications.

The plugin implementation explicitly admits limitations, including unsupported multiline replies. Its historical design is worth reading; it should not be treated as a modern security model for untrusted plugins.

## Search coverage, exclusions, and limitations

Discovery used well over six distinct live-web formulations. Search angles included broad open-source suite comparisons; C++/Qt/KDE architectures; encrypted browser collaboration; WOPI hosting; ONLYOFFICE's implementation split; TypeScript office SDKs; native macOS forks; Scheme/X11 historical suites; Java/NetBeans alternatives; and Rust/local desktop suites. Representative queries included `open source office suite GitHub architecture LibreOffice Calligra ONLYOFFICE`, `GitHub collaborative office suite spreadsheet document slides Univer CryptPad`, `site:github.com office WOPI Collabora richdocuments`, `NeoOffice official source code GitHub`, `Siag Office official source GitHub`, `Joeffice GitHub source repository`, and `open source office suite Rust GitHub Nino`. Targeted source searches then checked component contracts, collaboration changes, conversion code, and plugin implementations.

Every retained canonical repository URL was checked through its GitHub page and/or the public GitHub API. Every entry also has an independently opened implementation, design, test, or changelog source beyond the repository landing-page README. Public GitHub metadata was checked for archive status; recent push timestamps were not used as evidence for C4. Source references follow the branch observed during research and can change later.

The search converged on repeated product families, packaging projects, single-purpose editors, and thin integrations. Word processors, standalone spreadsheet engines, generic note/task/groupware systems, document-generation wrappers, and proprietary suites without substantive public source were excluded. WebODF was investigated but left outside this multi-application scope. Joeffice surfaced in a developer-authored architecture article, but was not retained without equally strong inspected repository evidence. Recent rebrandings and forks were not counted merely for having a different name. ONLYOFFICE distribution repositories and multiple historical copies of the same office code were not used to pad the list.

Some web-rendered GitHub pages timed out, the public API reached a shared rate limit, and Collabora's hosted SDK documentation presented a bot challenge. Readable GitHub mirror source and raw implementation files supplied the evidence used here. No candidate was cloned, built, or executed, and no test results or performance numbers were independently reproduced. The newer Rust and TypeScript selections are supported by concrete code and architecture, with their maturity limits stated; the historical selections provide additional architectural diversity without implying active support.
