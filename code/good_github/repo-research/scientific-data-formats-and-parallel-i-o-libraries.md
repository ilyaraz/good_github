# Scientific data formats and parallel I/O libraries

Research date: 2026-10-09

This report selects 24 GitHub repositories implementing scientific file formats, array storage engines, parallel I/O, and reusable scientific data exchange layers. It covers both cluster filesystems and object storage, and includes domain schemas when their libraries contain substantial storage or serialization machinery. MPICH and SEACAS are counted once each, with the relevant subsystems identified. Bindings are included only where their own semantics and implementation provide substantial material to study.

The criteria are selection judgments grounded in the linked primary sources, not certifications of overall code quality. Repository pages were opened to verify identities; each entry also has an inspected implementation or documentation source beyond its repository README. Performance discussion concerns mechanisms and tradeoffs, not independently measured speedups. Inclusion does not imply a current maintenance or support guarantee.

- **C1 — Difficult correctness:** invariants, concurrency, numerical semantics, malformed inputs, or failure behavior require careful handling.
- **C2 — Reusable abstractions:** substantial interfaces and data models support multiple applications or backends.
- **C3 — Performance with structure:** identifiable architectural mechanisms address real data movement, memory, latency, or throughput constraints.
- **C4 — Sustained evolution:** dated history demonstrates years of development together with compatibility, testing, or complexity management.

## Foundational formats and MPI I/O

### 1. [HDFGroup/hdf5](https://github.com/HDFGroup/hdf5)

**Language/role:** C core, with C++, Fortran, and Java interfaces; hierarchical scientific storage and parallel HDF5.

Study the boundary between persistent file structure and process-local metadata caches. HDF5 is particularly instructive because independent readers, a serial writer, and cooperating MPI ranks require different protocols despite sharing a file format.

- **C1:** The locking design explains how flushing a parent before its referenced child can expose invalid on-disk metadata. Superblock consistency flags, file-open ordering, and SWMR restrictions address these failure modes. SWMR should not be confused with coordinated parallel HDF5 writing. [File-locking design](https://support.hdfgroup.org/documentation/hdf5/latest/_file_lock.html).
- **C3:** Collective metadata reads can replace many separate reads with one rank reading and broadcasting; metadata writes can combine operations using an MPI datatype. The documentation also identifies API calls that make per-operation collective configuration difficult. [Collective metadata I/O](https://support.hdfgroup.org/documentation/hdf5/latest/collective_metadata_io.html).

These two technical notes are useful entry points into cache coherence and metadata aggregation.

### 2. [Unidata/netcdf-c](https://github.com/Unidata/netcdf-c)

**Language/role:** C; netCDF data model, storage backends, and command-line utilities.

Study how one public scientific array API spans classic netCDF, HDF5, remote protocols, PnetCDF, and NCZarr without making every public operation a separate backend primitive.

- **C2:** File creation/opening selects a dispatch table; several public API calls collapse onto a smaller internal operation set. The table records the backend model and its own interface version, making this a concrete example of format polymorphism in C. [Internal dispatch architecture](https://docs.unidata.ucar.edu/netcdf-c/current/md__2home_2vagrant_2Desktop_2netcdf-c_2docs_2dispatch.html).
- **C4:** The release history spans dated releases from 2001 through 2026 and records reader/writer synchronization fixes, HDF5 compatibility choices, backward reading of changed NCZarr metadata, and platform and test adjustments. This supplies evidence of compatibility work rather than age alone. [Release notes](https://github.com/Unidata/netcdf-c/blob/main/RELEASE_NOTES.md).

The dispatch document warns that some signatures may lag the source; use it for architecture, then consult the current definitions.

### 3. [Parallel-NetCDF/PnetCDF](https://github.com/Parallel-NetCDF/PnetCDF)

**Language/role:** C implementation with C, C++, and Fortran interfaces; MPI access to classic netCDF formats.

Study request aggregation when an application produces many small scientific variables. PnetCDF is a separate I/O implementation, rather than a new file format.

- **C1:** Ordinary nonblocking requests retain dependence on the user's buffers until completion; buffered writes instead copy into library-managed storage. The FAQ also distinguishes collective participation requirements and data consistency operations. [Buffer and collective semantics](https://parallel-netcdf.github.io/doc/faq.html).
- **C3:** Posting a nonblocking request registers it without performing I/O or communication. Wait operations aggregate the queued requests, recovering larger transfers and cross-variable locality that separate calls lose. [Aggregation design and examples](https://parallel-netcdf.github.io/wiki/CombiningOperations.html).

The contrast between request posting, buffer ownership, and actual progress makes this a good companion to a general asynchronous I/O library.

### 4. [ornladios/ADIOS2](https://github.com/ornladios/ADIOS2)

**Language/role:** C++ core with multiple language interfaces; scientific file I/O, streaming, and in situ/in transit transport.

Study the `ADIOS`, `IO`, `Variable`, `Attribute`, and `Engine` object boundaries. Engine implementations serve different transports while preserving a common application vocabulary.

- **C2:** `IO` constructs an implementation of the abstract engine interface; variables describe global, local, and joined data layouts independently of the selected engine. File and streaming operations share the same components. [Component architecture](https://adios2.readthedocs.io/en/latest/components/components.html).
- **C1:** Step acquisition, deferred versus synchronous operations, and collective open/close behavior form explicit contracts. The guide also documents subtle global-array cases: uncovered regions leave destination memory untouched, while overlapping blocks do not specify which writer's value wins. These are meaningful semantic boundaries to trace through the engines. [Shapes and engine semantics](https://adios2.readthedocs.io/en/latest/components/components.html).

The component guide is the primary entry point; engine-specific guarantees must be checked before generalizing from one backend.

### 5. [NCAR/ParallelIO](https://github.com/NCAR/ParallelIO)

**Language/role:** C and Fortran; high-level netCDF-oriented parallel I/O for distributed simulations.

Study the separation between application decomposition and the processes that actually access storage. PIO supports both I/O ranks that also compute and dedicated I/O ranks shared by computation components.

- **C2:** Its asynchronous initialization creates computation and I/O communicators and an I/O service loop. The documented message sequence sends an operation identifier followed by its arguments, executes the backend operation, then returns results when required. [I/O-system initialization and protocol](https://ncar.github.io/ParallelIO/group___p_i_o__init__c.html).
- **C3:** Rearrangement exposes point-to-point versus collective communication, handshakes, nonblocking sends, and bounds on pending requests. These controls make buffering and communication pressure visible architectural choices. [Rearranger options](https://ncar.github.io/ParallelIO/group___p_i_o__rearr__options.html).

The inspected generated API documentation identifies itself as PIO 2.5.4; treat its limitations as version-specific.

### 6. [pmodels/mpich](https://github.com/pmodels/mpich)

**Language/role:** Primarily C; the relevant subsystem is **ROMIO**, under `src/mpi/romio`, rather than the entire MPI implementation.

Study the lower-level I/O substrate beneath many scientific format libraries. ROMIO connects MPI file operations to filesystem-specific behavior through ADIO, an internal abstract device layer.

- **C2:** The ROMIO source subtree separates public MPI-I/O routines, the ADIO layer, filesystem implementations, documentation, and tests. ADIO isolates filesystem adaptation from the portable MPI-I/O implementation. [ROMIO source and internal design overview](https://github.com/pmodels/mpich/tree/main/src/mpi/romio).
- **C3:** The same overview describes aggregation controls, data-sieving hints, deferred opens, and handling direct-I/O alignment restrictions. These provide concrete mechanisms for studying how scattered application accesses become viable storage operations. [ROMIO implementation overview](https://github.com/pmodels/mpich/tree/main/src/mpi/romio).

The embedded ROMIO README contains historical release material, including a 2008 version heading. It is useful architectural context, not evidence that those historical defaults describe every current filesystem driver.

## Chunked arrays and transactional storage

### 7. [zarr-developers/zarr-python](https://github.com/zarr-developers/zarr-python)

**Language/role:** Python; chunked, compressed multidimensional arrays and hierarchical metadata.

Study an array API whose storage units are separately addressable objects. This makes storage granularity, codec work, and request concurrency central concerns rather than details hidden behind a single file handle.

- **C2:** The implementation combines NumPy-compatible array types, groups, configurable encodings, and stores ranging from memory and local files to object storage. These are reusable boundaries across analysis workflows. [Repository overview](https://github.com/zarr-developers/zarr-python).
- **C3:** The performance guide distinguishes the independently readable chunk from the efficiently writable shard. Grouping chunks reduces object count but changes write granularity; memory layout, empty-chunk handling, and concurrency settings add further tradeoffs. [Performance and sharding guide](https://zarr.readthedocs.io/en/stable/user-guide/performance/).

The performance guide is the best entry point for connecting application access patterns to storage layout. The repository's related subpackages are counted within this one entry.

### 8. [zarrs/zarrs](https://github.com/zarrs/zarrs)

**Language/role:** Rust; an independent Zarr implementation and extensible codec pipeline.

Study how Rust traits express different transformations without collapsing array-to-array, array-to-byte, and byte-to-byte operations into an untyped filter interface.

- **C2:** Codec traits expose configuration, representation bounds, full and partial operations, and capability declarations. This allows new encodings to participate in array operations through a shared interface. [Codec extension architecture](https://book.zarrs.dev/extensions/codec.html).
- **C3:** The implementation balances parallel work across chunks and inside codecs. Reusable partial decoders can cache a fully decoded chunk when a codec cannot decode a subset; cache locking and the distinction between asynchronous concurrency and task parallelism are documented explicitly. [Reading and concurrency design](https://book.zarrs.dev/arrays/array_read.html).

These entry points are especially useful for studying how extension interfaces carry performance information, not merely encode/decode function pointers.

### 9. [saalfeldlab/n5](https://github.com/saalfeldlab/n5)

**Language/role:** Java; hierarchical chunked tensor storage, originating in scientific imaging.

Study a comparatively small storage model with explicit metadata and block operations. The repository contains the filesystem backend and an API used by additional backend projects.

- **C1:** The filesystem specification defines sparse missing chunks, smaller edge chunks, integer-sized block headers, endianness, and size limits. Correctness depends on interpreting these together rather than treating every block as a full dense tile. [Filesystem format specification](https://github.com/saalfeldlab/n5#file-system-specification).
- **C2:** `N5Reader` separates metadata, dataset attributes, chunk access, block access, and existence checks. Its documentation distinguishes a chunk from the coarsest block in a sharded dataset and explains that an existence check does not validate contents. [N5Reader interface](https://github.com/saalfeldlab/n5/blob/master/src/main/java/org/janelia/saalfeldlab/n5/N5Reader.java).

The format section and reader interface are complementary entry points into on-disk invariants and backend-independent behavior.

### 10. [google/tensorstore](https://github.com/google/tensorstore)

**Language/role:** C++ and Python; composable access to large arrays across formats and storage systems.

Study the combination of a formal indexing model with explicit asynchronous storage and transaction semantics.

- **C1:** Isolated transactions hide pending modifications until commit; atomic isolated transactions additionally require all modifications to commit atomically and fail without changes when that guarantee cannot be provided. This distinction prevents assuming every transaction has the same atomicity. [Transaction contract](https://google.github.io/tensorstore/python/api/tensorstore.Transaction.html).
- **C2:** A normalized index transform combines domains with constant, affine single-dimension, or index-array mappings. It represents compositions of indexing operations, including cases that can be composed without copying index arrays. [Index-space design](https://google.github.io/tensorstore/index_space.html).

These two entry points expose both semantic layers: what coordinates a view denotes, and when modifications become visible.

### 11. [TileDB-Inc/TileDB](https://github.com/TileDB-Inc/TileDB)

**Language/role:** C++ with a C API; dense and sparse multidimensional array storage engine.

Study bounded-memory array query execution and the separation of logical query processing from backend I/O.

- **C2:** The architectural model separates array schemas, domains, dimensions, fragment metadata, queries, filters, and the virtual filesystem. This supplies reusable machinery for both dense and sparse arrays. [Architecture guide](https://github.com/TileDB-Inc/TileDB/wiki/Architecture).
- **C3:** Sparse reads use bounding rectangles to find relevant tiles. When user buffers cannot hold a result, subarray partitioning and incomplete-query state support incremental retrieval. The guide also separates compute and I/O pools and describes tile and read-ahead caches. [Read path and storage management](https://github.com/TileDB-Inc/TileDB/wiki/Architecture).

This wiki is explicitly a historical architecture overview and contains unfinished sections. The populated read-path sections support the selection; they should not be treated as an exhaustive map of current class ownership.

### 12. [earth-mover/icechunk](https://github.com/earth-mover/icechunk)

**Language/role:** Rust with Python bindings; transactional storage for Zarr-style scientific arrays.

Study how a chunked scientific dataset gains snapshots and coordinated updates without becoming a conventional database server.

- **C1:** Writers persist chunks and manifests before the new snapshot, then publish it through a conditional atomic update of repository metadata. Competing commits can fail and require conflict resolution and retry. [Storage specification, version 2.1](https://icechunk.io/en/latest/reference/spec-v2-1/).
- **C2:** The workspace separates format serialization, storage traits, backend implementations, shared types, and transaction/version-control logic. The format supports chunk data stored inline, in owned objects, or through virtual references. [Crate architecture](https://github.com/earth-mover/icechunk#crate-structure) and [read-path specification](https://icechunk.io/en/latest/reference/spec-v2-1/).

The specification is the most useful entry point for tracing publication order and the distinction between data identity and physical location. No C4 claim is needed for this newer architectural family.

## Simulation schemas, meshes, and data exchange

### 13. [CGNS/CGNS](https://github.com/CGNS/CGNS)

**Language/role:** C with Fortran interfaces; CFD data representation and parallel storage access.

Study the boundary between a domain schema and the lower-level storage library. CGNS gives coordinates, connectivity, zones, and solution fields domain meaning above HDF5 arrays.

- **C2:** The parallel interface provides specialized operations for coordinates, elements, fields, and general arrays while using the ordinary mid-level library for other schema operations. The documented sequence separates dataset creation from distributed data writes. [Parallel CGNS architecture](https://cgns.org/cgns-archives/CGNS_docs_current/pcgns/general.html).
- **C1:** Parallel access carries communicator and collective-participation contracts. The routine reference also distinguishes shaped memory arrays from selected file regions and explicitly marks removed queue interfaces as deprecated. [Parallel routine contracts](https://cgns.org/cgns-archives/CGNS_docs_current/pcgns/library.html).

Both entry points are in the official documentation archive; the architecture overview is dated 2013. They are historical implementation guidance, and deprecated queued output is not presented as a current feature.

### 14. [sandialabs/seacas](https://github.com/sandialabs/seacas)

**Language/role:** C, C++, and Fortran suite; relevant subsystems are **Exodus** and **IOSS** for finite-element data I/O.

Study how an engineering mesh and transient fields map onto interchangeable database implementations. The monorepo is counted once, rather than counting Exodus and IOSS separately.

- **C2:** IOSS separates regions and grouping entities from fields, properties, and the `DatabaseIO` hierarchy. That design permits additional database implementations while preserving the simulation-facing model. [IOSS design document](https://sandialabs.github.io/seacas-docs/IOSystem.pdf).
- **C1:** The design defines ordered model-definition, model-data, transient-definition, and transient-data phases. States must close before transitioning; opening output is delayed so restart input is not accidentally overwritten. These are concrete lifecycle invariants, not merely file-format choices. [IOSS state and database lifecycle](https://sandialabs.github.io/seacas-docs/IOSystem.pdf).

The design PDF is dated 2010; the [official documentation index](https://sandialabs.github.io/seacas-docs/sphinx/html/) continues to link it as developer guidance. Use it for the model and consult current source for implementation details.

### 15. [LLNL/Silo](https://github.com/LLNL/Silo)

**Language/role:** Primarily C, with Python and Fortran interfaces; mesh and field storage with multi-file parallel organization.

Study a useful alternative to requiring every data write to use a collective storage API. Silo's serial library can participate in parallel output through explicit file ownership and cross-file mesh references.

- **C2:** Multi-block meshes and variables assemble individual pieces through named references, including references into other files. This keeps the logical scientific object separate from its physical file partitioning. [Multi-block data model](https://silo.readthedocs.io/latest/parallel.html).
- **C1/C3:** PMPIO divides ranks into groups and passes a baton controlling access to each group's file. Handoff closes the file before the next rank proceeds. Groups can progress independently, balancing concurrency against file count without allowing simultaneous uncoordinated writers to one serial file. [PMPIO protocol](https://silo.readthedocs.io/latest/parallel.html).

The multi-block and PMPIO sections provide a compact study of parallel organization above a serial storage library.

### 16. [LLNL/conduit](https://github.com/LLNL/conduit)

**Language/role:** C++ with C, Fortran, and Python interfaces; scientific data exchange, including **Relay I/O and Relay MPI**.

Study schema-carrying hierarchical data as the common payload between simulation memory, communication, and storage backends.

- **C2:** Relay builds I/O and communication on the same `Node` model. Serial I/O, MPI communication, and collective I/O are separated into libraries so serial clients do not acquire unnecessary MPI linkage. [Relay architecture](https://llnl-conduit.readthedocs.io/en/latest/relay.html).
- **C3:** Known-schema communication can pass compact contiguous buffers directly to MPI. Noncontiguous data is compacted temporarily; generic communication also transports the schema. The documented receive paths preserve existing output layouts when possible, making allocation and copying policy inspectable. [Relay MPI implementation strategy](https://llnl-conduit.readthedocs.io/en/latest/relay_mpi.html).

The documentation labels Relay APIs as work in progress. The two guides make the abstraction/performance tradeoff more concrete than the project's broad interoperability goal alone.

### 17. [openPMD/openPMD-api](https://github.com/openPMD/openPMD-api)

**Language/role:** C++ and Python; scientific metadata schema and I/O across HDF5, ADIOS2, and JSON backends.

Study how a domain-neutral scientific schema is enforced above several storage engines while leaving expensive transfers deferred.

- **C2:** The API represents series, iterations, meshes, and particles above backend-specific files and transports, supporting serial and MPI workflows. This is substantive schema and lifecycle machinery rather than a generated binding. [Repository data-model overview](https://github.com/openPMD/openPMD-api).
- **C1:** The workflow guide defines exactly what a flush point means for user buffers: pending writes must include pre-flush changes but exclude later changes, and requested reads must populate their buffers by completion. Attributes follow a different immediate/copying policy. [Deferred data contract](https://openpmd-api.readthedocs.io/en/0.17.0/usage/workflow.html).

The versioned workflow guide is the principal entry point for understanding ownership and visibility across the schema/backend boundary.

### 18. [pdidev/pdi](https://github.com/pdidev/pdi)

**Language/role:** C++ implementation with C, Fortran, and Python interfaces; declarative coupling of simulations to I/O and other data handlers.

Study an architecture that exposes application buffers and events while placing the choice and composition of handlers in configuration.

- **C1:** Each process-local data-store entry carries a buffer reference, a type/layout description, and access synchronization. Multiple readers are allowed while writes require exclusive access; transferring a reference does not copy the application data. [Core data-store concepts](https://pdi.dev/main/Concepts.html).
- **C2:** A separate event subsystem handles control transfer, while the YAML specification orchestrates plugins. HDF5, netCDF, MPI, Python, and other handlers can be combined around the same exposed data. Events are synchronous by default, with other behavior implemented by plugins. [Control and configuration architecture](https://pdi.dev/main/Concepts.html).

The core-concepts document is a concise entry point into typed shared-buffer ownership and event-driven scientific I/O composition.

## Native object interfaces and specialized formats

### 19. [h5py/h5py](https://github.com/h5py/h5py)

**Language/role:** Python and Cython; Python object and array semantics over HDF5.

Study the implementation work needed to make disk-backed datasets resemble NumPy arrays while preserving HDF5's different lifetime, selection, and concurrency rules.

- **C2:** Dataset proxies translate slicing into hyperslabs, implement broadcasting through repeated selections, expose compound fields, and compose resizing and filter behavior. This handwritten semantic layer is why the repository merits a separate entry from HDF5. [Dataset interface and implementation behavior](https://docs.h5py.org/en/stable/high/dataset.html).
- **C1:** Calls into HDF5 are protected by an interpreter-wide reentrant lock. The guide explicitly separates thread-safe use from parallel execution, including why disabling Python's GIL does not remove that lock. [Threading design](https://docs.h5py.org/en/stable/threads.html).

The dataset guide also documents important semantic surprises: indexing twice can modify only a temporary array, and shrinking datasets discards data rather than reshaping it like NumPy.

### 20. [JuliaIO/JLD2.jl](https://github.com/JuliaIO/JLD2.jl)

**Language/role:** Julia; native object serialization using an HDF5-compatible format implementation.

Study preservation of Julia object structure above binary datatypes and object references, implemented without simply forwarding every operation to the HDF5 C library.

- **C1:** Internals distinguish in-memory read representations from file datatypes, validate expected attribute types, reuse committed datatype definitions, and use object-header offsets to resolve reference cycles. These are concrete object-identity and representation invariants. [Internals and design](https://juliaio.github.io/JLD2.jl/stable/internals/).
- **C2:** Custom serialization hooks allow a type's storage representation and reconstructed type to differ. The same internals expose groups, datasets, compressed reads, and alternative I/O implementations, including memory mapping subject to eligibility rules. [Serialization and I/O interfaces](https://juliaio.github.io/JLD2.jl/stable/internals/).

The internals reference is the main entry point. HDF5 format compatibility should not be read as a promise that every foreign program understands arbitrary Julia object semantics.

### 21. [asdf-format/asdf](https://github.com/asdf-format/asdf)

**Language/role:** Python; Advanced Scientific Data Format, combining structured metadata with binary arrays.

Study extensible serialization of scientific objects while keeping their schema and representation explicit. This is the astronomy-associated Advanced Scientific Data Format, not the similarly named Adaptable Seismic Data Format.

- **C2:** Converter interfaces map custom objects to tagged YAML nodes and back, select among tag versions, delegate to other converters, and connect custom types to binary block storage. [Converter architecture](https://www.asdf-format.org/projects/asdf/en/latest/asdf/extending/converters.html).
- **C1:** Reference cycles require staged reconstruction: a converter can yield an incomplete object before resolving its back-reference. Lazy trees add another distinction because child objects need not be materialized when their parent is converted. [Cycles and lazy conversion](https://www.asdf-format.org/projects/asdf/en/latest/asdf/extending/converters.html).

The converter guide provides a concrete path into graph identity, deferred decoding, and schema extensibility beyond a simple dictionary serializer.

### 22. [HEASARC/cfitsio](https://github.com/HEASARC/cfitsio)

**Language/role:** C with Fortran-callable interfaces; FITS file access for astronomy.

Study an established binary scientific format implementation whose workload includes both tiny header operations and large image/table transfers.

- **C2:** FITS images, header data units, and tables share a reusable file interface. The official reference manual exposes both high-level operations and specialized routines, allowing applications to avoid reproducing binary layout handling. [CFITSIO reference guide](https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/).
- **C3:** The I/O layer caches FITS-sized blocks, finds existing cached blocks before reading, reuses buffers, and writes dirty contents back before eviction. This makes small metadata and table accesses practical through a distinct buffering layer. [How CFITSIO manages data I/O](https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node124.html).

These are useful entry points for studying the interaction between a rigid record format and application access patterns. The repository also documents deterministic comparison against reference outputs for its test program; no benchmark was run here.

### 23. [ecmwf/eccodes](https://github.com/ecmwf/eccodes)

**Language/role:** C++ implementation with C and Fortran interfaces; GRIB and BUFR encoding/decoding for meteorological data.

Study numerical encoding alongside evolving domain definitions. A seemingly simple array of weather values requires scale factors, reference values, packed widths, and edition-specific interpretation.

- **C1:** The simple-packing implementation computes binary and decimal scales, handles constant fields, finds a representable reference value, and reports ranges that cannot fit the selected precision. These are numerical semantics visible directly in code. [DataSimplePacking implementation](https://github.com/ecmwf/eccodes/blob/develop/src/eccodes/accessor/DataSimplePacking.cc).
- **C4:** The dated change history documents years of definition and encoding fixes, changes in unit/parameter interpretation, deprecation notices, and migration from manually implemented virtual tables to C++ inheritance. This is evidence of managing both compatibility and implementation complexity. [Official change history](https://confluence.ecmwf.int/spaces/ECC/pages/45757989/History%2Bof%2BChanges).

The packing source and change history together show why correctness in a scientific format includes meaning and precision, not just byte-level round trips.

### 24. [tbeu/matio](https://github.com/tbeu/matio)

**Language/role:** C; MATLAB MAT-file reading and writing independent of MATLAB's shared libraries.

Study a reusable binary interchange implementation supporting nested scientific objects rather than only flat numeric arrays.

- **C1:** The level-5 implementation recursively sizes structures and cells, accounts for alignment padding, handles sparse and complex representations, and propagates errors from size arithmetic. This exposes the allocation and representation invariants that make binary serialization difficult. [MAT level-5 implementation](https://github.com/tbeu/matio/blob/master/src/mat5.c).
- **C2:** A shared variable representation covers numeric, sparse, character, cell, and structure data. Format support can incorporate zlib for compressed level-5 data and HDF5 for newer MAT files without requiring MATLAB at runtime. [Repository architecture and dependencies](https://github.com/tbeu/matio) and [representation handling](https://github.com/tbeu/matio/blob/master/src/mat5.c).

The `mat5.c` source is the principal reading entry point; the selection concerns its format implementation, not a claim that every malformed-input path has been audited.

## Coverage, search process, and limits

Discovery used more than six distinct live query formulations, including:

- Parallel scientific I/O around HDF5, netCDF, PnetCDF, and ADIOS2.
- Dedicated I/O ranks, PIO rearrangers, MPI-I/O, and aggregation.
- PDI, PIDX, and SIONlib as less prominent parallel-I/O approaches.
- Scientific array stores around Zarr, TensorStore, and TileDB.
- Rust and Julia implementations, including Zarrs and JLD2, and Java N5.
- Snapshot, manifest, conditional-update, and transaction architecture in Icechunk.
- Astronomy formats and implementations, including FITS and ASDF.
- Mesh and simulation schemas around CGNS, Exodus/IOSS, Silo, Conduit, and openPMD.
- Meteorological encoding and MATLAB interchange through ecCodes and matio.

Follow-up searches targeted primary design notes, numerical packing code, reference cycles, buffer lifetimes, compatibility history, and source interfaces. Later broad language/format queries mostly returned alternative implementations, wrappers, adjacent processing tools, or candidates requiring substantially more validation; the retained set already covered the major distinct architectures found. Repository stars were not used as quality evidence.

This is a selection guide, not a census. Generic databases, general-purpose columnar formats, compression-only libraries, visualization applications, format-specification-only repositories, and generated wrappers were outside the chosen scope. Related language bindings and Zarr/N5 adapters were not counted as separate projects without a distinct implementation reason. MPICH and SEACAS are deliberately scoped to their I/O subsystems.

PIDX was discovered and its canonical GitHub page was opened, but its wiki/source-tree fetches did not expose enough additional implementation material in this session to support a retained entry. SIONlib documentation was discovered, but a qualifying official GitHub repository was not established. These are research limitations, not negative quality judgments. No unofficial mirror or fork is intentionally presented as an independent project.

Several sources are historical: the ROMIO embedded overview, PIO 2.5.4 API pages, the CGNS documentation archive, IOSS's 2010 design document, and TileDB's architecture wiki. Their age is identified where relevant; architectural inference from them does not establish current defaults or active maintenance. C4 is asserted only where dated evolution and specific compatibility or complexity-management work were inspected. No candidate code was executed, dependencies installed, large repositories cloned, or external services modified.
