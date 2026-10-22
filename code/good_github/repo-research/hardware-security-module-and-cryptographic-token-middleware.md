# Hardware security module and cryptographic token middleware

Research date: 2026-10-09.

This report selects 27 GitHub repositories implementing the software between applications and cryptographic tokens: PKCS#11 providers and consumers, smart-card transport, HSM device libraries, software tokens, policy proxies, and hardware security service abstractions. Software tokens and simulators are included because they implement the same stateful interfaces and support interoperability work; they do not thereby provide hardware isolation. Embedded and cloud projects are included where a concrete token middleware subsystem exists. The selection emphasizes implementation study, not deployment endorsements or a claim that every component is uniformly exemplary.

Criteria legend:

- **C1 — Correctness:** difficult invariants, concurrency, adversarial inputs, protocol semantics, or failure recovery.
- **C2 — Abstraction:** substantial reusable interfaces or components serving multiple applications or backends.
- **C3 — Performance:** concrete resource or latency constraints addressed through an understandable design; no benchmark superiority is implied.
- **C4 — Evolution:** documented development over years accompanied by compatibility work, testing, or complexity management.

The criteria assignments are engineering judgments grounded in the linked material. Repository identities, default branches, archive status, and source paths were checked through the GitHub API. Each entry also draws on opened documentation or implementation files. Source links track branches and may change after this research date.

## Module coordination, application integration, and transport

### 1. [OpenSC/OpenSC](https://github.com/OpenSC/OpenSC)

**Language/role:** C; multi-vendor smart-card middleware, PKCS#11 module, Windows minidriver, and token tools.

Study the boundary between a shared token/session model and card-specific behavior. **C1:** the session implementation checks conflicts between read-only sessions and Security Officer login, coordinates changes under the PKCS#11 lock, logs out when the last session closes, and invalidates sessions after card removal or replacement. These are concrete lifecycle invariants that ordinary cryptographic primitive libraries do not face. **C2:** the common session layer delegates through a card framework, while the repository exposes standard application interfaces across many card families. [Session implementation](https://github.com/OpenSC/OpenSC/blob/master/src/pkcs11/pkcs11-session.c).

The [NEWS file](https://github.com/OpenSC/OpenSC/blob/master/NEWS) is a useful second entry point: it records card compatibility changes, fuzz-discovered parsing errors, reconnection fixes, and expansion of tests against software tokens. It also makes clear why studying this code requires attention to historical compatibility rather than assuming uniform card behavior.

### 2. [p11-glue/p11-kit](https://github.com/p11-glue/p11-kit)

**Language/role:** C; PKCS#11 module discovery, coordinated loading, proxying, and forwarding.

Study a library solving ownership conflicts among independent consumers in the same process. **C1:** managed modules reference-count initialization and finalization so one consumer cannot shut down another's module; `C_CloseAllSessions` is scoped to the caller's sessions. The design explicitly addresses concurrent calls. **C2:** each consumer receives a wrapped module interface, allowing coordination without requiring all callers to share application-specific code. [Managed-module design](https://github.com/p11-glue/p11-kit/blob/master/doc/manual/p11-kit-sharing.xml).

The [remoting documentation](https://github.com/p11-glue/p11-kit/blob/master/doc/manual/p11-kit-remoting.xml) explains the complementary client/server design: expose selected token URIs through a Unix socket and forward that interface to remote applications. This is a particularly useful repository for understanding where module lifetime, process isolation, and token location can be abstracted independently.

### 3. [OpenSC/libp11](https://github.com/OpenSC/libp11)

**Language/role:** C; higher-level PKCS#11 access library, OpenSSL provider, and legacy engine.

Study the reconciliation of OpenSSL's application model with constrained, stateful PKCS#11 sessions. **C1:** the slot code drains in-use sessions before changing read/write mode, coordinates transitions with mutexes and condition variables, and discards sessions invalidated by the underlying module. **C3:** a reusable session pool avoids repeatedly opening sessions while explicitly handling unavailable sessions and mode transitions. The transition reservation also accounts for process forks. [Slot and session-pool implementation](https://github.com/OpenSC/libp11/blob/master/src/p11_slot.c).

The [session-pool stress test](https://github.com/OpenSC/libp11/blob/master/tests/session-pool-stress.c) runs signing, key generation, and session-mode changes concurrently. It is a useful companion to the implementation because it tests interacting behaviors rather than merely successful single-threaded signing.

### 4. [openssl-projects/pkcs11-provider](https://github.com/openssl-projects/pkcs11-provider)

**Language/role:** C; PKCS#11 integration with OpenSSL's provider interface.

Study the semantic mismatch between OpenSSL operation contexts and token capabilities. **C1:** the provider documents why duplicating an in-progress OpenSSL context requires token operation-state support, and supplies explicit workarounds for modules lacking that support, session callbacks, or particular attributes. **C2:** URI-based key selection and provider operation dispatch adapt different hardware and software modules to ordinary OpenSSL consumers. **C3:** configurable session caching is bounded by the token's reported capacity, while session-key caching can avoid repeated decryption or remote retrieval. [Provider configuration and behavior](https://github.com/openssl-projects/pkcs11-provider/blob/main/docs/provider-pkcs11.7.md).

Read [session.c](https://github.com/openssl-projects/pkcs11-provider/blob/main/src/session.c) alongside the manual to trace the pool, login, and synchronization machinery. This is the verified canonical repository; older references using the `latchset` owner should not be counted as another project.

### 5. [OpenSC/pkcs11-helper](https://github.com/OpenSC/pkcs11-helper)

**Language/role:** C; application-oriented access to existing token certificates and private-key operations.

Study middleware that absorbs removable-device and authentication lifecycle problems for its callers. **C1:** session validation checks provider availability and handle validity; session management tracks references, mutexes, and PIN-cache expiration. [Session implementation](https://github.com/OpenSC/pkcs11-helper/blob/master/lib/pkcs11h-session.c). **C2:** the API separates providers, tokens, certificates, data objects, and crypto integration, allowing applications to select certificates and handle reinsertion without reproducing those mechanisms. [API overview](https://github.com/OpenSC/pkcs11-helper/blob/master/doc/api/main.dox).

**C4:** the [ChangeLog](https://github.com/OpenSC/pkcs11-helper/blob/master/ChangeLog) documents development from 2006 through 2025, including fork recovery, provider quirks, OpenSSL/LibreSSL compatibility, and property APIs introduced specifically to extend behavior without breaking the API. The library's focus is consuming existing keys, rather than comprehensive token provisioning.

### 6. [LudovicRousseau/PCSC](https://github.com/LudovicRousseau/PCSC)

**Language/role:** C; pcsc-lite smart-card resource manager and client library.

This is the transport/resource layer beneath much token middleware, rather than a PKCS#11 implementation itself. **C2:** its source documents a daemon, client library, IPC message layer, request service, and server-side card operations behind the common SCard interface. **C1:** transaction processing must reconcile reader sharing, outstanding locks, card removal/reset events, power state, and invalid handles; for example, ending a transaction cannot reset a card owned by another transaction. [Architecture comments and transaction implementation](https://github.com/LudovicRousseau/PCSC/blob/master/src/winscard.c).

The [ChangeLog](https://github.com/LudovicRousseau/PCSC/blob/master/ChangeLog) offers a compatibility-oriented reading route through this lower layer. The study value is in coordinating real devices and multiple clients while maintaining familiar API semantics.

### 7. [caml-pkcs11/caml-crush](https://github.com/caml-pkcs11/caml-crush)

**Language/role:** OCaml and C; PKCS#11 RPC proxy and policy filter. **Historical study candidate:** GitHub's recorded last push was 2022-05-07; this report does not assert current maintenance.

**C1:** the filter addresses API-level hazards involving object visibility, permitted mechanisms, administrative operations, and unsafe combinations of key attributes. Its documentation also acknowledges semantic differences introduced by local caches. **C2:** separate frontend, rule parser, filter engine, extension hooks, and backend isolate filtering policy from RPC and native bindings. [Filter architecture and rules](https://github.com/caml-pkcs11/caml-crush/blob/master/doc/FILTER.md).

The [scenario-test documentation](https://github.com/caml-pkcs11/caml-crush/blob/master/src/tests/ocaml/HOW_TO_PERFORM_TESTS.md) describes tests for sticky sensitive/extractable attributes and wrap/decrypt combinations, plus a small language for composing operation sequences. The [former ANSSI repository](https://github.com/ANSSI-FR/caml-crush) explicitly directs readers here and now serves archives only; it is not counted separately.

## Token implementations and emulation

### 8. [softhsm/SoftHSMv2](https://github.com/softhsm/SoftHSMv2)

**Language/role:** C++; software implementation of a PKCS#11 token.

Study a full token API without needing a physical device. **C1:** initialization validates mutex callbacks and threading flags; object-template handling checks sizes, required attributes, and key classes; fork handling can reset process-local state. **C2:** the main implementation assembles separate crypto factories, object stores, slot managers, session managers, and handle managers. The repository supports OpenSSL/Botan backends and alternative persistent stores. [Main implementation](https://github.com/softhsm/SoftHSMv2/blob/main/src/lib/SoftHSM.cpp).

**C4:** the [NEWS history](https://github.com/softhsm/SoftHSMv2/blob/main/NEWS) records 2018–2026 changes, including crypto backend upgrades, a session close/open race, object-search races, database transaction issues, attribute immutability, and CI improvements. This makes it valuable for studying standards conformance as a continuing engineering task.

### 9. [opencryptoki/opencryptoki](https://github.com/opencryptoki/opencryptoki)

**Language/role:** C; Linux/AIX PKCS#11 framework supporting IBM hardware tokens and software tokens.

Study how a common API, policy machinery, and token-specific libraries coexist. **C2:** a shared mechanism table and function-pointer interface give token libraries and tools one representation of supported mechanisms. **C3:** generated numeric/string indexes use compressed jump tables, while sharing the table through the API library avoids duplicating it in every token library. [Developer architecture notes](https://github.com/opencryptoki/opencryptoki/blob/master/doc/README.devel).

**C1:** [token-store documentation](https://github.com/opencryptoki/opencryptoki/blob/master/doc/README.token_data) describes corruption detection, unique object filenames, format migration, and the dependency between restored token metadata and PIN state. The legacy TPM material concerns TPM 1.2; the repository identifies that token as deprecated. It should not be confused with the separate TPM 2.0 implementation below.

### 10. [tpm2-software/tpm2-pkcs11](https://github.com/tpm2-software/tpm2-pkcs11)

**Language/role:** C and Python; TPM 2.0-backed PKCS#11 module and provisioning tools.

Study the mapping of PKCS#11's token/login model onto a TPM hierarchy. **C2:** persistent primary keys, per-token login objects, an AES wrapping key, and SQLite metadata bridge token objects to TPM-protected operations. **C1:** the login flow unseals the wrapping key using SO/USER authorization and protects object authorization values; correctness spans hardware state and host metadata. [Architecture](https://github.com/tpm2-software/tpm2-pkcs11/blob/master/docs/ARCHITECTURE.md).

The [database upgrade design](https://github.com/tpm2-software/tpm2-pkcs11/blob/master/docs/DB_UPGRADE.md) adds a second concrete C1 example: cooperative file locking prevents competing schema upgrades, migration works on a backup, and rename/recovery rules preserve the original database. The same document identifies a historical host-endianness/type-size compatibility issue.

### 11. [latchset/kryoptic](https://github.com/latchset/kryoptic)

**Language/role:** Rust; PKCS#11 software token with OpenSSL-backed cryptography.

Study the separation of token semantics from storage and encrypted attribute representation. **C1:** the storage design derives per-object encryption keys, authenticates attribute types as associated data, and versions the encryption-key representation. Its ASN.1 parameter structures make algorithm and format choices explicit. [Storage encryption design](https://github.com/latchset/kryoptic/blob/main/doc/storage-encryption.md).

**C2:** the `Storage` and `StorageDBInfo` traits cover object persistence, attribute search/update, token metadata, authentication, and backend construction. SQLite and NSS database support sit behind those contracts. [Storage interfaces](https://github.com/latchset/kryoptic/blob/main/src/storage/mod.rs). This is a useful Rust counterpart to older C/C++ software tokens, especially for comparing typed component boundaries with an externally imposed C ABI. The design evidence is not a claim of independently audited security.

### 12. [wolfSSL/wolfPKCS11](https://github.com/wolfSSL/wolfPKCS11)

**Language/role:** C; configurable PKCS#11 implementation using wolfCrypt, including optional TPM-backed storage/operations.

Study an implementation designed to fit different host and embedded storage arrangements. **C2:** a small storage interface separates typed token/object records from open, close, read, write, and remove operations; builds can replace the default storage implementation. [Storage contract](https://github.com/wolfSSL/wolfPKCS11/blob/master/wolfpkcs11/store.h).

**C1:** release notes describe concrete fixes for extractability checks during wrapping, object lifetime after destruction, length handling, login enforcement, and operation-active state. **C4:** the same history runs from 2021 through 2026 and records TPM additions, interoperability tests, negative tests, and explicit compatibility switches for corrected attribute defaults. [Configuration and release notes](https://github.com/wolfSSL/wolfPKCS11/blob/master/README.md). Those switches are instructive examples of the tension between specification corrections and existing stored tokens.

### 13. [harrison314/BouncyHsm](https://github.com/harrison314/BouncyHsm)

**Language/role:** C# and native C; HSM/smart-card simulator with PKCS#11, REST, and web interfaces.

**Development/test scope:** the repository explicitly says it does not protect stored keys or network traffic and is not intended for production data. Its value is controllable token behavior.

**C1:** the login handler models application/session ownership, unplugged tokens, context-specific authentication, and cancellation of a simulated protected authentication path. [Login handler](https://github.com/harrison314/BouncyHsm/blob/main/src/Src/BouncyHsm.Core/Services/P11Handlers/LoginHandler.cs). **C2:** ordered mechanism profiles can add/remove algorithms, constrain key sizes and operation flags, and restrict curves to emulate different devices. [Profile model](https://github.com/harrison314/BouncyHsm/blob/main/Doc/Profiles.md).

Study how the service makes difficult authentication states reproducible, together with the documented [standard deviations](https://github.com/harrison314/BouncyHsm/blob/main/Doc/Restrictions.md), including network-error translation and nested-template limits.

## Device, embedded, and cloud adapters

### 14. [Yubico/yubihsm-shell](https://github.com/Yubico/yubihsm-shell)

**Language/role:** C; `libyubihsm`, YubiHSM PKCS#11 module, and management tools in one repository.

Study a vertical slice from standard token calls to an authenticated device protocol. **C2:** the PKCS#11 layer translates requests/results through `libyubihsm`, with HTTP connector and direct USB options. It also documents where PKCS#11 attributes cannot map directly to device capabilities and how objects inherit authentication-key domains. [PKCS#11 integration design](https://github.com/Yubico/yubihsm-shell/blob/master/pkcs11/README.adoc).

**C1:** the device library validates framing and lengths, checks response MACs, manages encrypted session state, and can recreate configured sessions after specific authentication/session failures. [Protocol implementation](https://github.com/Yubico/yubihsm-shell/blob/master/lib/yubihsm.c). The monorepo is counted once; its shell, library, and provider are complementary layers rather than separate selections.

### 15. [Yubico/yubico-piv-tool](https://github.com/Yubico/yubico-piv-tool)

**Language/role:** C; PIV device library, command-line tooling, and YKCS11 module.

Focus on `lib/` and `ykcs11/`, not just the executable. **C2:** YKCS11 maps fixed PIV key slots, certificates, public keys, and object labels into a general PKCS#11 interface; its documentation identifies which public operations run through OpenSSL and which functions depend on device support. [Mapping and supported semantics](https://github.com/Yubico/yubico-piv-tool/blob/master/doc/YKCS11/Functions_and_values.adoc).

**C1:** authentication must distinguish SO, USER, and context-specific logins. The implementation restricts context-specific login to signing/decryption contexts, synchronizes slot login state, and handles already-authenticated or conflicting user types. [YKCS11 implementation](https://github.com/Yubico/yubico-piv-tool/blob/master/ykcs11/ykcs11.c). This is a useful case study in exposing a fixed-function card application through a much broader token standard.

### 16. [CardContact/sc-hsm-embedded](https://github.com/CardContact/sc-hsm-embedded)

**Language/role:** C; SmartCard-HSM and STARCOS PKCS#11/CSP-minidriver middleware.

**C2:** the project supports both PC/SC and a CT-API path, with the latter motivated by embedded footprint constraints; the same project serves standard PKCS#11 applications and Windows minidriver consumers. The [project documentation](https://github.com/CardContact/sc-hsm-embedded/blob/master/README) also explains virtual slots for cards with multiple PINs and the compatibility problem this creates for applications that discover slots only at module load.

**C1:** [session management](https://github.com/CardContact/sc-hsm-embedded/blob/master/src/pkcs11/session.c) separates marking sessions unusable on token removal from freeing their memory, and tears down session objects, search state, mechanism parameters, and crypto buffers on closure. Study this smaller implementation to understand the lifecycle costs hidden behind a nominally lightweight middleware interface. The README limits the direct-CCID test coverage to particular readers; broad reader compatibility should not be inferred from that path.

### 17. [Nitrokey/nethsm-pkcs11](https://github.com/Nitrokey/nethsm-pkcs11)

**Language/role:** Rust; PKCS#11 module translating operations to a network NetHSM.

Study the added failure and resource boundaries when the token is a remote service. **C1:** session handles map to independently synchronized session objects, and slot-level session removal must reconcile the manager's handle map with session state. **C2:** separate login, enumeration, encryption, decryption, signing, and object/database components sit behind the PKCS#11 session facade. [Backend session implementation](https://github.com/Nitrokey/nethsm-pkcs11/blob/main/pkcs11/src/backend/session.rs).

**C3:** the project uses a thread pool to accelerate queries across all keys and documents multi-instance retry/timeout tests. Its [README](https://github.com/Nitrokey/nethsm-pkcs11/blob/main/README.md) also reports an unresolved thread-pool cleanup issue when the library is unloaded, and describes configuration workarounds. That limitation is material to studying its concurrency design.

### 18. [MicrochipTech/cryptoauthlib](https://github.com/MicrochipTech/cryptoauthlib)

**Language/role:** C; secure-element host library, specifically its `lib/pkcs11/` and `app/pkcs11/` middleware subsystems.

Study how a general object API maps onto physically constrained secure-element slots. **C2:** the provider's configuration describes transport selection, reserved objects, and device slots available for newly created objects, allowing the same middleware to integrate with p11-kit/OpenSSL consumers. [PKCS#11 application guide](https://github.com/MicrochipTech/cryptoauthlib/blob/main/app/pkcs11/README.md).

**C1:** the object-search implementation copies caller-owned templates into bounded caches and associates caches with sessions; ownership, buffer sizes, and concurrent searches therefore become explicit implementation concerns. [Find-template implementation](https://github.com/MicrochipTech/cryptoauthlib/blob/main/lib/pkcs11/pkcs11_find.c). The [release notes](https://github.com/MicrochipTech/cryptoauthlib/blob/main/release_notes.md) explain the move to per-session cache slots and device-specific build/test organization. The whole repository is counted once, rather than treating each chip family as a separate project.

### 19. [GoogleCloudPlatform/kms-integrations](https://github.com/GoogleCloudPlatform/kms-integrations)

**Language/role:** C++; Cloud KMS adapters, particularly the `kmsp11/` Cloud HSM integration.

Study the translation from token-local expectations to cloud resources and IAM. **C2:** configured key rings become tokens, and the adapter maps remote keys into PKCS#11 objects; optional generated certificates accommodate consumers that expect a certificate alongside every private key. Authentication uses cloud credentials rather than ordinary local token PIN semantics. The guide also distinguishes hardware keys from an explicit option permitting software-protected keys. [PKCS#11 user guide](https://github.com/GoogleCloudPlatform/kms-integrations/blob/master/kmsp11/docs/user_guide.md).

**C1:** a session owns an optional ongoing operation guarded by a mutex, making serialization and operation lifetime explicit. [Session contract](https://github.com/GoogleCloudPlatform/kms-integrations/blob/master/kmsp11/session.h). RPC timeouts and key refresh configuration further expose the boundary between a process-local token view and changing remote state. The accompanying CNG provider is part of the same repository, not another entry.

## Application libraries and service abstractions

### 20. [eclipse-keypont/crypto11](https://github.com/eclipse-keypont/crypto11)

**Language/role:** Go; standard Go cryptographic interfaces backed by PKCS#11 keys.

Study how an idiomatic `crypto.Signer` can safely hide a session-oriented native API. **C2:** key objects implement Go signing/decryption interfaces while a context manages token access. **C3:** one session preserves login state while a bounded, dynamically used pool supplies exclusive sessions to operations; wait timeouts and pool statistics expose saturation. The package also explains why per-block symmetric operations are costly. [Package architecture](https://github.com/eclipse-keypont/crypto11/blob/master/crypto11.go).

**C1:** [sessions.go](https://github.com/eclipse-keypont/crypto11/blob/master/sessions.go) protects session acquisition against context closure and replaces sessions after selected fatal token/session errors rather than returning poisoned handles to the pool. This is the current canonical owner, replacing older Thales-owner references; those paths are not separate projects.

### 21. [parallaxsecond/rust-cryptoki](https://github.com/parallaxsecond/rust-cryptoki)

**Language/role:** Rust; idiomatic PKCS#11 library above a separate raw FFI crate.

This selection concerns the substantive `cryptoki` layer, not generated bindings alone. **C1:** `Session` intentionally does not implement `Sync`, while allowing ownership transfer through `Send`; automatic session closure and explicit close state make native-resource lifetime part of the Rust API. [Session type](https://github.com/parallaxsecond/rust-cryptoki/blob/main/cryptoki/src/session/mod.rs). **C2:** the workspace separates raw `cryptoki-sys` bindings from session, mechanism, object, slot, and context abstractions that applications can reuse without manipulating every C structure directly.

The [changelog](https://github.com/parallaxsecond/rust-cryptoki/blob/main/CHANGELOG.md) provides an additional route into API and mechanism evolution. Its history derives from earlier rust-pkcs11 work, but this repository contains a separately developed higher-level implementation and is not presented as a duplicate copy of those bindings.

### 22. [pyauth/python-pkcs11](https://github.com/pyauth/python-pkcs11)

**Language/role:** Python and Cython; higher-level Python PKCS#11 objects and operations.

Study the interaction between lazy iteration and a stateful foreign API. **C1:** the concurrency documentation describes reentrant session locks spanning multi-call operations such as searches and streaming encryption. An unconsumed iterator can leave an operation active; iterator completion is therefore part of the API's correctness contract. [Concurrency design and limitations](https://github.com/pyauth/python-pkcs11/blob/master/docs/concurrency.rst).

**C2:** token filtering by labels, serials, flags, and required mechanisms, alongside slots, sessions, object types, and typed exceptions, provides application-level semantics beyond a literal binding. [API reference source](https://github.com/pyauth/python-pkcs11/blob/master/docs/api.rst). The concurrency document includes runtime assumptions and untested monkeypatching cases, so it should be read as the project's documented model rather than a universal guarantee for all Python runtimes. Older `danni` links resolve to this canonical project.

### 23. [Pkcs11Interop/Pkcs11Interop](https://github.com/Pkcs11Interop/Pkcs11Interop)

**Language/role:** C#; managed .NET access to native PKCS#11 libraries.

Study an unusually concrete cross-platform ABI problem. **C1:** C `unsigned long` has different widths across platforms, while .NET integer widths are fixed; native structure packing also varies. The architecture therefore maintains separate width/alignment variants rather than assuming one marshaling layout works everywhere. **C2:** high-level factories choose the appropriate platform implementation, while low-level APIs retain native control and high-level APIs offer managed collections and streams. [Architecture](https://github.com/Pkcs11Interop/Pkcs11Interop/blob/master/doc/04_ARCHITECTURE.md).

The [interface guide](https://github.com/Pkcs11Interop/Pkcs11Interop/blob/master/doc/05_INTERFACES.md) explains the library → slot → session → object/mechanism relationships. This is a substantive abstraction library despite its wrapper role. GitHub recorded its last push in February 2025; no claim of a recent release cadence is made here.

### 24. [go-piv/piv-go](https://github.com/go-piv/piv-go)

**Language/role:** Go; direct PIV management and private-key operations through PC/SC.

Study a device-oriented alternative to going through PKCS#11. **C1:** the transport chunks APDUs, retrieves additional response fragments, and translates card status words into useful authentication/not-found errors, including an older-device retry-count quirk. [PC/SC and APDU layer](https://github.com/go-piv/piv-go/blob/v2/v2/piv/pcsc.go).

**C2:** the [key implementation](https://github.com/go-piv/piv-go/blob/v2/v2/piv/key.go) adapts PIV keys to Go signing/decryption interfaces and separates key authentication policy from each cryptographic operation. PIN prompts, cached versus per-use authentication, and attestation-derived policy make this more than a transport wrapper. The verified default branch is `v2`, with source under the additional `v2/` directory; the repeated segment in these source URLs is intentional.

### 25. [Yubico/python-yubihsm](https://github.com/Yubico/python-yubihsm)

**Language/role:** Python; native YubiHSM 2 protocol and object API.

Study a separate implementation of the device protocol rather than a generated binding to `libyubihsm`. **C1:** authenticated sessions track a counter and MAC chain, check response session identifiers and MACs before advancing state, validate command framing, and clear stored session-key references on closure. **C2:** the same core exposes typed object references, filtering by domains/capabilities, and session operations independently of transport. [Protocol and session implementation](https://github.com/Yubico/python-yubihsm/blob/main/yubihsm/core.py).

The [project guide](https://github.com/Yubico/python-yubihsm/blob/main/README.adoc) documents HTTP connector and direct USB backends and integration with Python cryptographic key representations. Its device tests require hardware and can reset it; they were inspected as documentation, not executed. The independent protocol implementation justifies retaining this alongside the C SDK.

### 26. [parallaxsecond/parsec](https://github.com/parallaxsecond/parsec)

**Language/role:** Rust; platform security service, especially its PKCS#11 provider and persistent key-information managers.

Study the additional abstraction needed when applications use a shared security service rather than loading a module directly. **C2:** the PKCS#11 provider translates the service's cryptographic operations to dynamically loaded token libraries and separates hardware handles from application-visible key identities. [Provider implementation](https://github.com/parallaxsecond/parsec/blob/main/src/providers/pkcs11/mod.rs).

**C1:** the [key-information manager](https://github.com/parallaxsecond/parsec/blob/main/src/key_info_managers/mod.rs) persists mappings involving application identity, provider information, key names, and attributes behind synchronized storage interfaces. Provider startup reconciles stored metadata with objects actually present on the token. These are consequential identity, persistence, and recovery boundaries. The broader repository also offers TPM and other providers; the retained unit is this service architecture, counted once.

### 27. [Mastercard/pkcs11-tools](https://github.com/Mastercard/pkcs11-tools)

**Language/role:** C; token object-management tools backed by shared parsing, attribute, and cryptographic-operation code.

Study the mechanics of moving and managing keys across heterogeneous PKCS#11 providers. **C2:** a common object/attribute model supports key generation, certificate/CSR operations, wrapping, unwrapping, and rewrapping. The manual documents consistent key identifiers for JVM interoperability and multiple standard/vendor wrapping mechanisms. [Manual](https://github.com/Mastercard/pkcs11-tools/blob/master/docs/MANUAL.md).

**C1:** [unwrapping implementation](https://github.com/Mastercard/pkcs11-tools/blob/master/lib/pkcs11_unwrap.c) combines parsed wrapped-key data with caller overrides, enforces token-versus-session placement, and gives temporary keys used for rewrapping different extractability treatment. Envelope and individual wrapping mechanisms then dispatch through the shared context. This is included as substantive token-management infrastructure, not as a collection of one-off examples.

## Search coverage and limitations

Discovery used more than twenty live search formulations, followed by repository/API verification and reads of selected source files. The main angles were:

- General PKCS#11 middleware and software tokens: OpenSC, SoftHSM, openCryptoki, alternative Rust/C# implementations.
- Module coordination, OpenSSL providers, RPC forwarding, and policy-enforcing proxies.
- TPM-backed tokens and embedded secure-element integrations, including Microchip, FreeRTOS, NXP, and other vendor communities.
- Vendor device stacks: YubiHSM, PIV, SmartCard-HSM/STARCOS, and NetHSM.
- Go, Rust, Python, .NET, and Java bindings, distinguishing substantive ownership/ABI abstractions from thin or generated wrappers.
- Cloud KMS/HSM adapters and shared cryptographic service architectures.

Representative searches included “GitHub PKCS11 middleware OpenSC SoftHSM architecture,” “GitHub PKCS11 Rust kryoptic cryptoki NetHSM middleware,” “GitHub TPM PKCS11 OpenSSL provider p11-kit module remote RPC,” “GitHub smartcard HSM middleware PCSC PIV Nitrokey sc-hsm-embedded,” “GitHub PKCS11 proxy filter OCaml caml crush,” and “GitHub remote Cloud KMS PKCS11 library middleware.” Later searches mostly added alternative vendor implementations or repeated already-covered architecture families. The list extends beyond the rough 25-repository guide because the embedded adapter, cloud adapter, and filtering proxy contribute distinct implementation problems.

Excluded from the final selection were tutorials, installation-only wrappers, awesome lists, pure header/binding generators, duplicate forks, general signing applications, and hardware firmware without a substantial host-middleware focus. Related Java, JavaScript, additional secure-element, and OS-keychain projects surfaced, but are not comprehensively covered. This is a diverse selection rather than a complete ecosystem inventory. Closed vendor SDKs are necessarily underrepresented.

Moved paths were consolidated under canonical owners. The archive-only ANSSI Caml Crush repository was excluded in favor of its documented successor. Caml Crush is explicitly treated as a historical study candidate; Pkcs11Interop's older activity is also disclosed. Other retained repositories were not marked archived at verification time, which is not itself proof of active maintenance. C4 is claimed only where the cited change history supplies substantive evidence beyond dates.

All work was read-only research plus this report. No candidate code, test suite, dependency installer, device operation, or external mutation was executed. Performance criteria reflect documented designs rather than measured throughput, and security-sensitive design descriptions are not independent audits or certification claims.
