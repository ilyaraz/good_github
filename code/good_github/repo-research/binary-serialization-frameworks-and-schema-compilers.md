# Binary serialization frameworks and schema compilers

Research date: **2026-10-09**

This report selects **29 GitHub repositories** covering binary interchange formats, schema-to-code compilers, object graph serializers, and composable binary codecs. It includes both large cross-language systems and smaller implementations with distinctive engineering constraints. For projects that also provide RPC, JSON, or other facilities, the discussion focuses on their binary serialization and schema machinery. Each repository was opened and checked against additional primary documentation or source material.

The criteria identify worthwhile engineering study, not a blanket endorsement of every component or a deployment recommendation. Descriptions of mechanisms are grounded in the linked sources; judgments about what engineers can learn from them are this report's inferences. No comparative benchmark results are asserted.

## Criteria legend

- **C1 — Correctness:** difficult invariants, numerical semantics, concurrency, adversarial inputs, or failure handling.
- **C2 — Abstractions:** substantial reusable interfaces or representations supporting multiple use cases.
- **C3 — Performance and structure:** concrete resource constraints addressed through understandable architectural choices.
- **C4 — Evolution:** evidence across years of compatibility work, testing, or complexity management; age alone does not qualify.

## Cross-language formats and schema ecosystems

### 1. [protocolbuffers/protobuf](https://github.com/protocolbuffers/protobuf)

**Language/role:** C++ compiler (`protoc`) and multiple language runtimes; schema-driven tagged binary messages.

Study the boundary between a common wire contract, generated language APIs, and runtime behavior. The relevant monorepo subsystems are the compiler and message runtimes, rather than downstream RPC frameworks.

- **C1:** Correct decoding includes accepting both packed and unpacked repeated fields, concatenating repeated packed payloads, replacing duplicate scalar fields, and recursively merging duplicate message fields. These are observable compatibility semantics, not merely parser implementation choices. The [encoding guide](https://protobuf.dev/programming-guides/encoding/) gives explicit examples.
- **C2:** A shared schema language and compiler feed multiple language runtimes; field numbers and wire types allow readers to process a common representation independently of source-language object layout. Start with the [repository's compiler/runtime overview](https://github.com/protocolbuffers/protobuf#overview) and the encoding guide.

### 2. [google/flatbuffers](https://github.com/google/flatbuffers)

**Language/role:** C++ schema compiler with multilingual runtimes; generated accessors over serialized buffers.

Useful for studying how a wire layout becomes an access API, and how compact immutable structs differ from extensible tables.

- **C1:** Struct alignment is defined independently of the host compiler. Table access follows signed vtable offsets and handles absent or out-of-range fields by returning defaults. These rules must agree across platforms and schema versions.
- **C3:** Shared vtables avoid repeated layout metadata, inline structs reduce indirection, and reverse buffer construction reduces builder bookkeeping. The [internals guide](https://flatbuffers.dev/internals/) explains these decisions and walks through generated code, making it the principal entry point.

### 3. [capnproto/capnproto](https://github.com/capnproto/capnproto)

**Language/role:** C++ core, schema compiler, serialization runtime, and RPC system; the serialization subsystem is the focus here.

Study direct traversal of a segmented wire representation and the security consequences of avoiding an eager parse into a separate object graph.

- **C1:** Readers must validate pointer bounds and account for traversal to resist cyclic or overlapping-pointer amplification. The [encoding specification's security section](https://capnproto.org/encoding.html#security-considerations) describes the required checks.
- **C3:** Pointer checks occur when accessors dereference data, preserving the design's avoidance of an upfront message scan. The same [encoding specification](https://capnproto.org/encoding.html) explains struct/list pointers, segments, and layout evolution. This is a concrete performance–validation tradeoff, not an assertion that validation is free.

### 4. [apache/avro](https://github.com/apache/avro)

**Language/role:** Multilingual serialization system, with Java and other implementations; schemas, binary encoders, container files, and schema resolution.

Study a format that omits field names and type tags from ordinary binary records and instead makes the writer's schema part of the decoding contract.

- **C1:** Reader/writer resolution recursively matches records, arrays, maps, and unions; it specifies numeric promotions, missing-field defaults, and error cases. Defaults are reader behavior, which matters when reasoning about schema changes.
- **C2:** The schema model supports generic data processing, generated representations, container storage, and protocol messages. Canonical schema forms separate meaningful structure from irrelevant textual differences. The primary entry point is the [Avro 1.12.0 specification](https://avro.apache.org/docs/1.12.0/specification/), especially binary encoding and schema resolution. This is a versioned reference, not a claim that 1.12.0 is the latest release.

### 5. [apache/thrift](https://github.com/apache/thrift)

**Language/role:** C++ IDL compiler and multilingual libraries; generated types and binary/compact serialization protocols within an RPC stack.

The educational subsystem is the compiler–protocol–transport boundary: generated structures can use different encodings without embedding network mechanics in every serializer.

- **C2:** Protocols map typed values to bytes, transports handle byte movement, and generated processors connect service calls to those interfaces. The [concepts guide](https://thrift.apache.org/docs/concepts) explains these layers.
- **C3:** Compact encoding uses field-ID deltas, varints, and boolean values folded into field headers. These optimizations remain expressed through the protocol abstraction. Read the [compact protocol specification](https://github.com/apache/thrift/blob/master/doc/specs/thrift-compact-protocol.md) alongside the concepts guide.

### 6. [aeron-io/simple-binary-encoding](https://github.com/aeron-io/simple-binary-encoding)

**Language/role:** Java schema tooling and generated codecs for several languages; Simple Binary Encoding for latency-sensitive messages. The former `real-logic` URL redirects to this canonical repository.

Study a design in which predictable memory access and allocation behavior shape the schema and generated API.

- **C2:** Schemas generate reusable typed codecs, with message-template identity and an extension mechanism for optional fields. Structural changes that are not compatible extensions require a new message type.
- **C3:** Flyweights access the underlying transfer buffer directly; forward streaming access, native type mappings, and explicit alignment address latency variance and copying. The [design principles](https://github.com/aeron-io/simple-binary-encoding/wiki/Design-Principles) also state the limitations: values retained after processing need copying, and oversized messages need external fragmentation. The [repository overview](https://github.com/aeron-io/simple-binary-encoding#simple-binary-encoding-sbe) describes generator targets.

### 7. [6over3/bebop](https://github.com/6over3/bebop)

**Language/role:** C# compiler with multilingual generated code and runtimes; `.bop` schemas and binary records.

Study the deliberate distinction between fixed-layout structs and evolving messages, plus the connection between generated code and runtime schema reflection.

- **C1:** Struct fields are concatenated and are not intended for additive/deprecated-field evolution. Messages carry indexed fields and an overall length; an older reader encountering an unknown field can skip the remainder of that message. The [wire format](https://docs.bebop.sh/reference/wire-format/) makes this precise.
- **C2:** The compiler can emit a binary schema representation that runtimes use for dynamic encoding and decoding, supporting inspection tools without the original source schema. See the [binary schema design](https://docs.bebop.sh/reference/binary-schema/).

The separate `bebop-next` repository describes staging work for a compiler rewrite; it is not counted as another independent framework here.

### 8. [microsoft/bond](https://github.com/microsoft/bond)

**Language/role:** Haskell schema compiler with C++, C#, and other runtimes; schematized data transformations and binary protocols. **Historical, archived project: Microsoft states that open-source development ended March 31, 2025, including security fixes.**

Still valuable as a study of operations on partially materialized data.

- **C2:** `bonded<T>` can represent an object, a serialized payload, or compatible typed views; `bonded<void>` works with runtime schema information. This unifies several data-processing paths behind one abstraction.
- **C3:** Lazy deserialization defers construction of selected nested objects. Transcoding can visit serialized fields and write a target protocol without first building the full user object. Read the [C++ guide's bonded/lazy/transcoding sections](https://github.com/microsoft/bond/blob/master/doc/src/bond_cpp.md); the [project-end notice](https://github.com/microsoft/bond#bond-project-has-ended) supplies the maintenance qualification.

## Explicit binary layouts, constrained schemas, and embedded generation

### 9. [vlm/asn1c](https://github.com/vlm/asn1c)

**Language/role:** C implementation of an ASN.1 compiler and generated codec support for several encoding rules, including BER, DER, PER, and OER.

Study a compiler whose semantic normalization and constraint analysis are as consequential as its syntax parser. Its stages parse an ASN.1 tree, fix/check it, then emit target code.

- **C1:** Subtype constraints, recursive definitions, wide integer representations, and encoding-rule differences make correctness difficult. The [compiler manual](https://github.com/vlm/asn1c/blob/master/doc/man/asn1c.man.md) exposes separate stages and constraint-generation controls.
- **C4:** The [ChangeLog](https://github.com/vlm/asn1c/blob/master/ChangeLog) records work across 2004–2017 and beyond: regression cases for recursive references, constraint overflow handling, PER corrections, portability fixes, and backward-compatible type options. This supports a sustained complexity-management claim without assuming a current support cadence.

### 10. [ndsev/zserio](https://github.com/ndsev/zserio)

**Language/role:** Java schema compiler and extensions; code generation and runtimes for C++, Java, and Python.

Especially useful for studying bit-level layouts with dependent lengths, alignment, offsets, and compressed arrays.

- **C1:** Layout features interact: optional-field alignment changes whether padding exists, and offset fields cannot be delta-packed because doing so would invalidate offset semantics.
- **C2:** The language provides compound types, parameters, arrays, and templates; compiler extensions implement a Java interface, allowing additional generators or analysis tools.
- **C3:** Packed arrays apply delta compression to eligible elements, while explicit alignment exposes a space/access tradeoff. Read the [language overview](https://github.com/ndsev/zserio/blob/master/doc/ZserioLanguageOverview.md) and the [extension architecture](https://github.com/ndsev/zserio#extensions).

### 11. [kaitai-io/kaitai_struct_compiler](https://github.com/kaitai-io/kaitai_struct_compiler)

**Language/role:** Scala compiler for declarative `.ksy` binary format descriptions; multiple parsing backends and documented Java/Python serialization support since 0.11.

Study how a parser-oriented schema becomes a bidirectional contract for editing or constructing existing binary formats.

- **C1:** Generated `_check()` methods enforce consistency between object values and schema constraints before writing; some checks depend on stream position and must occur during `_write()`. Incorrect lengths can corrupt the interpretation of every subsequent field.
- **C2:** A shared declarative description supports nested types, parameters, lengths, offsets, and bit-sized fields. The [serialization guide](https://doc.kaitai.io/serialization.html) explains both the generated API and its constraints. The entry is the compiler, not the separate collection of format definitions; write support should not be inferred for every parsing target.

### 12. [nordicsemi/zcbor](https://github.com/nordicsemi/zcbor)

**Language/role:** C/C++-compatible CBOR runtime and Python CDDL-to-C generator, aimed at constrained systems.

Study generated validation as a small state machine over a shared low-level codec.

- **C1:** State tracks payload bounds and container counts. Backup states permit rollback when optional values, alternatives, or variable repetitions fail to match; a failed candidate must not leave the next candidate at the wrong position.
- **C2:** Generated per-type functions compose the same runtime primitives, while public wrappers expose chosen schema entry types. The [architecture document](https://github.com/nordicsemi/zcbor/blob/main/ARCHITECTURE.md) explains this split.
- **C3:** Small call signatures and selective inlining/removal of unused generated functions address code size. The [project guide](https://github.com/nordicsemi/zcbor#code-generation) also documents a material limitation: its C canonical-encoding support does not enforce every canonical rule, including map-key ordering.

### 13. [nanopb/nanopb](https://github.com/nanopb/nanopb)

**Language/role:** ANSI C Protocol Buffers runtime and Python generator; bounded-memory embedded use.

Study how one wire format can support very different memory ownership and I/O models.

- **C1:** Stream callbacks must honor full-length I/O, failure returns, and substream boundaries. Maximum field sizes and counts constrain generated storage; unbounded fields can use callbacks. These contracts are detailed in [basic concepts](https://jpa.kapsi.fi/nanopb/docs/concepts.html).
- **C3:** Schema options turn variable-size fields into fixed arrays, while callback streams let applications handle data without materializing an entire message.
- **C4:** The [changelog](https://github.com/nanopb/nanopb/blob/master/CHANGELOG.txt) documents generator and test improvements across years, fixes backported to older branches, and later error-cleanup and recursion-limit work. This is concrete evolution evidence, not a claim that old releases share current fixes.

## Independent Protocol Buffers implementations

### 14. [tokio-rs/prost](https://github.com/tokio-rs/prost)

**Language/role:** Rust runtime, derive macros, and build-time code generation for Protocol Buffers.

This is a substantive Rust implementation, not a generated binding around the C++ runtime. Study how ordinary Rust data types, generated derives, and a small wire-level runtime divide responsibility.

- **C1:** `DecodeContext` carries recursion budget into nested decodes; each child receives a new context, keeping sibling traversal from incorrectly consuming the parent's depth budget. The [encoding implementation](https://github.com/tokio-rs/prost/blob/master/prost/src/encoding.rs) contains the checks and failure path. A feature can disable the limit, so it is not unconditional.
- **C2:** `prost-build`, `prost-derive`, and the runtime separate schema compilation, type-level integration, and wire operations. Serialization uses `bytes::Buf`/`BufMut`; existing annotated Rust types can also participate. See the [project overview](https://github.com/tokio-rs/prost#prost).

### 15. [tomas-abrahamsson/gpb](https://github.com/tomas-abrahamsson/gpb)

**Language/role:** Erlang Protocol Buffers compiler generating encoders, decoders, verifiers, and introspection APIs.

Study how code generation adapts a wire format to BEAM memory behavior and Erlang's data representations.

- **C1:** Optional generated verifiers check values before encoding; unknown-field preservation and omitted-field defaults have explicitly documented semantics, including loss of presence information under some options.
- **C2:** Record/map representations, translation hooks, generated introspection, and target-OTP controls support varied integrations. Generated codecs do not require gpb at runtime.
- **C3:** `copy_bytes` can choose when to copy sub-binaries so a small retained field does not keep an entire input message alive. The [compiler API guide](https://gpb.hexdocs.pm/gpb_compile.html) explains the memory tradeoff and option interactions; the [repository guide](https://github.com/tomas-abrahamsson/gpb) provides the overall generation model.

## Rust-native representations

### 16. [rkyv/rkyv](https://github.com/rkyv/rkyv)

**Language/role:** Rust archival serialization and direct access to archived values.

Study the distinction between an ordinary Rust object and its relocatable archived representation, rather than treating serialized bytes as an ordinary in-memory struct.

- **C1:** Safe access to untrusted archives requires validating their representation. The `bytecheck` feature derives `CheckBytes`; checked access validates before returning an archived reference. The [validation chapter](https://rkyv.org/validation.html) also explains custom validation contexts.
- **C2:** Relative pointers and the separate `Archive`, `Serialize`, and `Deserialize` traits form the core; corresponding unsized traits let more complex types build on that machinery. The [architecture chapter](https://rkyv.org/architecture.html) is a compact entry into the design.

### 17. [jamesmunns/postcard](https://github.com/jamesmunns/postcard)

**Language/role:** Rust, `no_std`-oriented binary format integrated with Serde.

Study a compact format whose schema is supplied by agreement between endpoints, usually through common Rust types.

- **C1:** Varint decoding has type-dependent maximum lengths and value bounds. The format accepts some nonminimal encodings while rejecting overflow and overlong representations; cross-pointer-width values work only within the smaller platform's range. The [wire specification](https://postcard.jamesmunns.com/wire-format) gives explicit accepted/rejected examples.
- **C2:** Mapping the Serde data model supports common scalar, collection, enum, and struct representations without an external IDL. The [repository](https://github.com/jamesmunns/postcard) describes the constrained-environment role.

Wire-format stability from 1.0 does **not** provide automatic schema evolution: the specification explicitly leaves compatibility between application schema revisions to users.

### 18. [near/borsh-rs](https://github.com/near/borsh-rs)

**Language/role:** Rust implementation and derive macros for Binary Object Representation Serializer for Hashing.

Study serialization intended to make byte representation suitable for hashing, where two implementations disagreeing about ordering or numeric handling can have consequences beyond interoperability.

- **C1:** The [Borsh specification](https://github.com/near/borsh#specification) defines little-endian integers, ordered serialization of unordered containers, field-order encoding, and NaN rejection. These are important determinism obligations; the specification's intent should not be read as an audit of every decoder path.
- **C2:** Serialization/deserialization traits and derive macros support application types, while a separate `BorshSchema` derive exposes schema information. The [Rust repository's documentation entry points](https://github.com/near/borsh-rs#docs-shortcuts) show these interfaces. The separate format/specification repository is cited as evidence and is not counted as another implementation.

## MessagePack and CBOR implementations

### 19. [msgpack/msgpack-c](https://github.com/msgpack/msgpack-c)

**Language/role:** C and C++ MessagePack implementations; one repository with separate `c_master` and `cpp_master` branches. The C++ unpacker is the study focus.

Study incremental decoding and the ownership boundary between decoded object views and backing allocation zones.

- **C1:** `msgpack::object` copies are shallow. An `object_handle` owns the associated zone, so keeping only the object after destroying its handle can leave dangling references.
- **C3:** Streaming unpacking can reference payload storage instead of copying it; zones and buffer reference counting manage lifetimes. The reference policy can be customized to control peak memory. The [C++ unpacker guide](https://github.com/msgpack/msgpack-c/wiki/v2_0_cpp_unpacker) explains both the API and these ownership/performance mechanisms. The [repository landing page](https://github.com/msgpack/msgpack-c) points to the two implementation branches.

### 20. [tinylib/msgp](https://github.com/tinylib/msgp)

**Language/role:** Go source-to-source MessagePack generator and runtime library.

Study an approach where Go type declarations themselves serve as the schema, with generated byte-slice and streaming paths.

- **C2:** Generated types implement sizing, marshaling, unmarshaling, and stream encoding/decoding interfaces. Extension support allows specialized types to join the same model. The [generator guide](https://github.com/tinylib/msgp/wiki/Using-the-Code-Generator) documents the generated interface sets and test/benchmark generation.
- **C3:** Separate slice-oriented and buffered stream APIs support different allocation and message-size tradeoffs; sizing and buffer reuse can avoid heap allocation in suitably designed callers. The [implementation overview](https://github.com/tinylib/msgp#use) also explains the file-based type-discovery boundary, an important limitation for generator users.

### 21. [MessagePack-CSharp/MessagePack-CSharp](https://github.com/MessagePack-CSharp/MessagePack-CSharp)

**Language/role:** C#/.NET MessagePack serializers, formatters, resolvers, analyzers, and source generation.

Study how typed serializer lookup and generated code coexist with deployment environments that prohibit runtime code emission.

- **C1:** The [security implementation](https://github.com/MessagePack-CSharp/MessagePack-CSharp/blob/master/src/MessagePack/MessagePackSecurity.cs) explicitly increments object-graph depth and fails at the configured maximum. Custom formatters must participate correctly in this protocol.
- **C2:** `IFormatterResolver` selects typed formatters and permits composition of custom behavior with built-in handling.
- **C3:** Source-generated formatters/resolvers support AOT deployments, while runtime generation is available in supported environments. The [main extension and AOT documentation](https://github.com/MessagePack-CSharp/MessagePack-CSharp#aot-code-generation) explains the lookup and generation paths. No headline speed multiplier is adopted here.

### 22. [fxamacker/cbor](https://github.com/fxamacker/cbor)

**Language/role:** Go CBOR and CBOR Sequence codec, including deterministic-encoding options and configurable decoding policies.

Study a reusable codec whose input-policy choices are explicit and whose configuration can be shared safely.

- **C1:** Decoding policy covers nested-depth/container limits, invalid UTF-8, duplicate map keys, and the distinction between well-formedness and validity. Duplicate-key rejection can leave a partially filled destination, which callers must handle deliberately. Inspect [decode.go](https://github.com/fxamacker/cbor/blob/master/decode.go).
- **C2:** Immutable encoding/decoding modes, type/tag registration, and struct mapping make the implementation adaptable to protocols with different CBOR subsets. Modes are documented as safe for concurrent reuse in the [custom-mode guide](https://github.com/fxamacker/cbor#custom-modes).

## Object graphs and language-specific semantics

### 23. [EsotericSoftware/kryo](https://github.com/EsotericSoftware/kryo)

**Language/role:** Java object-graph serialization and copying, with pluggable serializers and reference resolvers.

Study the interaction between schema changes and object identity, where simply skipping an unknown field can be incorrect.

- **C1:** `CompatibleFieldSerializer` attempts to read unknown field data so later references remain meaningful. Its source explains that skipping referenced data can invalidate subsequent reference resolution. This is an unusually concrete compatibility failure mode.
- **C2:** Custom serializers and interchangeable `ReferenceResolver` implementations separate object encoding from identity bookkeeping. Reference tracking can also be selected by type. Read the [reference architecture](https://github.com/EsotericSoftware/kryo#references) and [CompatibleFieldSerializer implementation](https://github.com/EsotericSoftware/kryo/blob/master/src/com/esotericsoftware/kryo/serializers/CompatibleFieldSerializer.java).

Default serializers have differing evolution guarantees; a general claim of backward compatibility would be misleading.

### 24. [apache/fory](https://github.com/apache/fory)

**Language/role:** Multilingual framework with binary object serialization, schema IDL/compiler, and row representations. This entry concerns the binary object and schema subsystems, not the monorepo's JSON serializer.

Study the mapping between idiomatic language objects and a shared representation of references, nullability, and concrete type identity.

- **C1:** Reference metadata distinguishes null, previously seen objects, untracked values, and newly tracked objects. Reference slots must be reserved in the right order during decoding. Rust/C++ smart-pointer semantics also differ from languages with implicit object references.
- **C2:** Native-language and cross-language modes address different type-system needs, while schema IDL provides explicit shared contracts and generated domain objects. The [cross-language wire specification](https://github.com/apache/fory/blob/main/docs/specification/xlang_serialization_spec.md) details reference/type metadata; the [repository's schema section](https://github.com/apache/fory#schema-idl) describes the compiler path.

### 25. [USCiLab/cereal](https://github.com/USCiLab/cereal)

**Language/role:** Header-only C++ serialization library with binary and other archive types; binary archives and smart-pointer support are the relevant parts.

Study archive-independent serialization functions and object construction under C++ ownership rules.

- **C1:** Restoring shared ownership, weak references, polymorphic objects, and types without default constructors requires careful allocation and exception handling. `enable_shared_from_this` adds state that must survive user construction.
- **C2:** The archive interface and `LoadAndConstruct` customization let application types participate without requiring a single construction strategy. The [pointer design guide](https://uscilab.github.io/cereal/pointers.html) explains mechanisms and limitations: raw pointers/references and the aliasing `shared_ptr` constructor are not supported. The [repository overview](https://github.com/USCiLab/cereal) establishes the binary archive role.

### 26. [Sereal/Sereal](https://github.com/Sereal/Sereal)

**Language/role:** Perl/XS-centered binary format and implementations for additional languages; dynamic values and object graphs in one monorepo.

Study distinctions often hidden by JSON-like models: aliasing, shared references, weak references, byte strings, and object reconstruction hooks.

- **C1:** The protocol separately represents references, aliases, and weakened references. `COPY` cannot recursively refer to arbitrary other `COPY` structures; object-class references also have constraints. These rules make identity and decoder traversal nontrivial.
- **C2:** The tagged representation supports compound dynamic values and custom object freeze/thaw behavior. The [protocol specification](https://github.com/Sereal/Sereal/blob/main/sereal_spec.pod) is the main entry point; the [project objectives](https://github.com/Sereal/Sereal#objectives) explain the shared/weak-reference motivation. The specification also documents Perl string and object semantics that do not uniformly round-trip through every other language.

## Composable binary codecs

### 27. [construct/construct](https://github.com/construct/construct)

**Language/role:** Python declarative framework for symmetric binary parsing and building.

Study executable format descriptions assembled from reusable fields, containers, adapters, and context-dependent values, rather than a fixed universal wire format.

- **C1:** Bit/byte composition has explicit invariants: bit structures must total a whole number of bytes, nested bit-stream conversions are restricted, and seeking/lazy constructs can invalidate restreamed offsets. The [bit/byte design guide](https://construct.readthedocs.io/en/latest/bitwise.html) states these boundaries candidly.
- **C2:** A common construct abstraction supports parsing, building, sizing, and compilation, with internal methods for subclass implementers. The [core implementation](https://github.com/construct/construct/blob/master/construct/core.py) exposes the public/internal API split and contextual error propagation.

### 28. [scodec/scodec](https://github.com/scodec/scodec)

**Language/role:** Scala functional binary codec combinators, with type-directed composition and derivation.

Study how binary consumption, validation, and domain mapping can be represented algebraically.

- **C1:** Decoding returns a value together with unconsumed bits or an explicit error carrying context. Partial domain mappings use error-aware combinators; encoder size bounds expose lower and upper limits on emitted bits.
- **C2:** `Decoder`, `Encoder`, and `Codec` compose through mapping and dependent sequencing, allowing later fields to depend on earlier decoded values. Read the [core algebra guide](https://scodec.org/guide/Core%2BAlgebra.html) alongside the [current repository introduction](https://github.com/scodec/scodec#introduction). The guide is useful for the design, but its examples should be read with the chosen major version in mind; the repository distinguishes 1.x and 2.x.

### 29. [haskell/binary](https://github.com/haskell/binary)

**Language/role:** Haskell binary serialization via the `Binary` class, `Get`/`Put` abstractions, and ByteStrings.

Study how a pure interface supports incremental input without conflating “needs another chunk” with malformed or truncated data.

- **C1:** The decoder's `Partial`, `Done`, and `Fail` states carry continuation, remaining bytes, and consumed offsets. End-of-input is explicit; the implementation carefully adjusts offsets for unused input. Inspect [Data.Binary.Get](https://github.com/haskell/binary/blob/master/src/Data/Binary/Get.hs).
- **C2:** High-level `Binary` instances and generic derivation coexist with reusable low-level `Get` and `Put` operations and builders. The [repository guide](https://github.com/haskell/binary#using-binary) connects these layers. This entry is the implementation repository, counted once despite its several public modules.

## Coverage, exclusions, and limitations

Discovery used more than six distinct live search formulations, including: cross-language IDL/compiler architecture; direct-buffer and Rust archival formats; low-latency SBE/Bond/Bebop designs; ASN.1 and bit-level schema tools; embedded Protocol Buffers; Java/C++ object graphs; MessagePack and CBOR implementations; Go source generators; canonical hashing formats; CDDL-to-C generation; Scala codec algebras; Erlang compiler behavior; and Haskell binary libraries. Follow-up searches and primary-source reads checked compiler stages, wire specifications, ownership rules, validation, and release/change history.

The list extends beyond the approximate 15–25 guide because the later searches added distinct CDDL, BEAM, functional-codec, and Perl object-identity designs. Further searches increasingly returned comparable implementations, bindings, wrappers, benchmarks, and new projects whose architectural coverage overlapped the selection. This is not an exhaustive inventory of every qualifying library.

Important selection boundaries:

- **Bincode was excluded:** its [archived GitHub landing page](https://github.com/bincode-org/bincode) contains a migration notice to SourceHut and no substantive implementation tree in the inspected default branch. It was not treated as a current GitHub codebase or replaced by an unofficial fork.
- **Bond is explicitly historical.** The [official project-end notice](https://github.com/microsoft/bond#bond-project-has-ended) is materially different from merely slow release activity.
- **The Bebop staging rewrite was not double-counted.** [bebop-next](https://github.com/6over3/bebop-next) describes itself as staging development; its capabilities were not attributed to the retained Bebop codebase.
- Independent implementations of a shared format were retained only when they expose different engineering lessons: bounded C storage, Rust derives and recursion control, BEAM sub-binary retention, C++ zone ownership, Go generation, or .NET formatter/AOT architecture. Other plausible candidates, including protobuf-c, additional C++ serializers, and additional Haskell CBOR libraries, were left out to limit repetition; exclusion does not imply poor quality.
- Format-only specifications, generated wrappers, tutorial projects, lists of links, RPC-only frameworks, and predominantly analytical storage formats were not standalone entries. Format specifications were used as evidence for retained implementations where appropriate.

Every retained canonical repository URL was opened, and each entry has additional primary evidence beyond its landing README, including substantive design, implementation, or wire-format material. Branch moves and repository redirects discovered during research were reflected in the links. Versioned and older documentation is identified where it affects interpretation. Except for explicit status statements, inclusion does not imply a checked maintenance or security-support commitment. No repositories were cloned, dependencies installed, candidate code executed, or performance/security audits performed. C4 is claimed selectively where dated evolution and concrete compatibility/testing work were actually inspected.
