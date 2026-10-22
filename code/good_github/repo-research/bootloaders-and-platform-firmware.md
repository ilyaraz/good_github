# Bootloaders and platform firmware

Research date: 2026-10-09.

This report selects 27 GitHub codebases covering hardware initialization, firmware runtime services, operating-system loading, network boot, and recoverable embedded firmware updates. It spans x86, Arm application and microcontroller profiles, RISC-V, POWER/PowerPC, and Open Firmware environments, with C, assembly, C++, Rust, Go, and Forth implementations. Linux-based boot environments and two broader frameworks are included only for their identified bootloader subsystems. This is a guide to engineering material worth studying, not a security audit or a claim that every component is exemplary.

Criteria legend:

- **C1 — Correctness:** demanding invariants, concurrency, numerical or binary semantics, adversarial inputs, or recovery from failure.
- **C2 — Abstractions:** substantial reusable interfaces and components supporting different platforms or applications.
- **C3 — Performance:** concrete latency, memory, storage, or throughput constraints addressed through understandable architecture.
- **C4 — Evolution:** sustained development supported by evidence of compatibility work, testing, or complexity management, rather than age alone.

## Hardware initialization and embedded boot foundations

### 1. [u-boot/u-boot](https://github.com/u-boot/u-boot)

**Language/role:** C and assembly; configurable boot firmware for embedded systems. The GitHub repository accompanies upstream development hosted on the U-Boot project's Git service.

Study how a bootloader supports many boards without putting each peripheral's implementation into board-specific startup code.

- **C1:** The driver model defines an ordered bind, platform-data conversion, and probe lifecycle; device sequence numbers must remain unique within a class and stable over the device's lifetime. The documentation also identifies sandbox tests for lifecycle, ordering, allocation, and bus behavior. These are concrete invariants behind apparently simple device lookup operations. [Driver-model design](https://docs.u-boot.org/en/latest/develop/driver-model/design.html).
- **C2:** Drivers, device instances, and *uclasses* separate hardware implementations from common interfaces. Bus-owned child data and device-tree-derived configuration allow the same peripheral driver to serve different SoCs and boards. The same [design document](https://docs.u-boot.org/en/latest/develop/driver-model/design.html) is the recommended entry point.

### 2. [barebox/barebox](https://github.com/barebox/barebox)

**Language/role:** C and assembly; embedded bootloader. **Official GitHub mirror**, explicitly identified as such by the repository.

Study the boundary between boot-selection policy and persistent state, especially for unattended devices with multiple system images.

- **C1:** Bootchooser decrements attempt counters, chooses eligible targets by priority, and requires an explicit success indication before restoring attempts. Its documentation discusses recovery when every target fails and the tradeoff of freezing counters. It explicitly warns that the fallback NV-variable backend is not power-failure safe. [Bootchooser algorithm and failure scenarios](https://www.barebox.org/doc/latest/user/bootchooser.html).
- **C2:** Boot targets are abstract objects with configurable boot actions, priorities, and attempt counts; storage backends are separate from the selection algorithm. This supports different redundant-system layouts without rewriting the policy engine. The [same guide](https://www.barebox.org/doc/latest/user/bootchooser.html) provides worked integrations.

### 3. [coreboot/coreboot](https://github.com/coreboot/coreboot)

**Language/role:** Primarily C and assembly; platform initialization followed by a payload. **Official read-only mirror** of the coreboot review repository.

Study staged execution when ordinary RAM does not yet exist, and how hardware initialization hands a precisely described machine to another firmware component.

- **C1:** Bootblock, verification, ROM, post-CAR, and RAM stages have different memory assumptions. The post-CAR transition must dismantle cache-as-RAM before normal DRAM execution; verification hooks authenticate files before loading them when verified boot is enabled. [Architecture and stage responsibilities](https://doc.coreboot.org/getting_started/architecture.html).
- **C3:** Separately built stages allow different compression choices; relocatable stages can be cached in CBMEM to accelerate S3 resume. This exposes the relationship between flash footprint, decompression, and resume latency without relying on unsupported benchmark claims. [Stage loading and caching](https://doc.coreboot.org/getting_started/architecture.html).

### 4. [tianocore/edk2](https://github.com/tianocore/edk2)

**Language/role:** Primarily C, with assembly and build tooling; reusable UEFI/PI firmware implementation. The relevant study area is **MdeModulePkg's DXE core**, rather than every package in this large repository.

Study a dependency-driven driver runtime implemented inside firmware.

- **C1:** The DXE dispatcher maintains distinct discovered and scheduled lists, processes firmware volumes once, and resolves before/after dependencies before dispatch. Locks protect dispatcher state, and failed dependency-section extraction can defer processing. [Dispatcher implementation](https://github.com/tianocore/edk2/blob/master/MdeModulePkg/Core/Dxe/Dispatcher/Dispatcher.c).
- **C2:** Firmware-volume protocols and dependency expressions let independently packaged drivers become eligible as services appear. This is a substantial reusable execution model rather than a hardcoded sequence of board initialization calls. Start with the explanatory algorithm and state declarations in [Dispatcher.c](https://github.com/tianocore/edk2/blob/master/MdeModulePkg/Core/Dxe/Dispatcher/Dispatcher.c).

### 5. [slimbootloader/slimbootloader](https://github.com/slimbootloader/slimbootloader)

**Language/role:** C, assembly, and Python tooling; Intel-oriented platform boot firmware using EDK II libraries. It is a separate staged implementation, not an additional copy of EDK II.

Study how narrowly defined boot phases and payload interfaces make platform initialization tractable.

- **C1:** Stage 1B migrates loader state and the stack from temporary RAM to DRAM before invoking temporary-memory teardown. With verified boot enabled, each stage verifies its successor; failure either enters the configured recovery path or halts. [Boot flow](https://slimbootloader.github.io/developer-guides/boot-flow.html).
- **C2:** Stage handoff structures, a common loader-global-data accessor, payload HOBs, and board initialization hooks separate common flow from platform details. The [boot-flow guide](https://slimbootloader.github.io/developer-guides/boot-flow.html) describes these interfaces and their ordering.

### 6. [oreboot/oreboot](https://github.com/oreboot/oreboot)

**Language/role:** Rust and assembly; early platform firmware targeting LinuxBoot payloads. **A substantive Rust reimplementation descended from coreboot**, retained separately because its implementation and integration model differ.

Study firmware organization in Rust before an operating system or normal heap environment is available.

- **C1:** Early code operates from SRAM or execute-in-place storage until DRAM initialization completes. The RISC-V handoff must also establish exception delegation, platform SBI services, privilege transition, and device-tree placement. [Boot-flow design](https://github.com/oreboot/oreboot/blob/main/Documentation/boot-flow.md).
- **C2:** Board-defined DTFS layouts describe stored images, while RustSBI traits provide the common service interface and oreboot supplies SoC-specific mechanisms such as timers. The [boot-flow document](https://github.com/oreboot/oreboot/blob/main/Documentation/boot-flow.md) connects those layers to the LinuxBoot payload. Platform coverage should be evaluated per board; coreboot ancestry does not imply coreboot-equivalent support.

### 7. [AsahiLinux/m1n1](https://github.com/AsahiLinux/m1n1)

**Language/role:** C, assembly, Rust components, and Python host tools; Apple Silicon bootloader and hardware experimentation environment.

Study the adaptation between Apple's boot environment and the Linux Arm64 boot contract.

- **C1:** The kernel handoff constructs device-tree properties for initrd placement, reserves its memory, handles framebuffer formats, and transfers boot randomness with explicit failure handling. These operations reconcile two different platform descriptions and must agree with the memory the kernel may use. [Kernel boot preparation](https://github.com/AsahiLinux/m1n1/blob/main/src/kboot.c).
- **C2:** Payload loading, device-tree selection, stage-one/stage-two chainloading, and a host-controlled proxy support normal boot and hardware investigation through the same environment. [m1n1 user guide](https://asahilinux.org/docs/sw/m1n1-user-guide/). The bootloader subsystem is the focus here; the hypervisor is additional study material.

### 8. [usbarmory/armory-boot](https://github.com/usbarmory/armory-boot)

**Language/role:** Go on TamaGo; primary bootloader for USB armory Mk II, plus reusable boot and download packages.

Study a compact bare-metal Go loader with an authenticated configuration boundary.

- **C1:** Configuration loading rejects incompatible kernel/unikernel selections and malformed parameter arrays. When a public key is configured, it verifies the configuration signature before using its image hashes and clears loaded image buffers on failure. Authentication is conditional on that configured key. [Configuration loader](https://raw.githubusercontent.com/usbarmory/armory-boot/master/config/config.go).
- **C2:** Separate `config`, `disk`, `exec`, and `sdp` packages distinguish configuration, ext4-backed media access, Linux/ELF handoff, and NXP serial download. The repository documents these reusable packages; [config.go](https://raw.githubusercontent.com/usbarmory/armory-boot/master/config/config.go) is a practical starting point for tracing their interaction.

### 9. [littlekernel/lk](https://github.com/littlekernel/lk)

**Language/role:** C and assembly; small SMP-capable kernel used as a bootloader foundation, including Android-device bootloaders. Included for its **firmware execution substrate**, not as a claim that every downstream Android loader is in this repository.

Study what changes when boot firmware needs scheduling, blocking operations, and multiple CPUs.

- **C1:** Run-queue insertion asserts thread state, queue non-membership, disabled interrupts, and possession of the thread spinlock. CPU wakeups distinguish pinned from unpinned threads. [Thread implementation](https://github.com/littlekernel/lk/blob/master/kernel/thread.c).
- **C2:** The same thread API, wait queues, architecture hooks, and platform interfaces support many processor families and firmware applications. [thread.c](https://github.com/littlekernel/lk/blob/master/kernel/thread.c) exposes the reusable scheduling layer beneath the repository's modular platform and application structure.

## Secure and server platform runtime firmware

### 10. [ARM-software/arm-trusted-firmware](https://github.com/ARM-software/arm-trusted-firmware)

**Language/role:** C and assembly; Trusted Firmware-A secure boot stages and EL3 runtime services. **Official read-only GitHub mirror**.

Study a boot chain that remains part of the machine's runtime privilege and power-management architecture.

- **C1:** Cold boot elects or selects a primary CPU and keeps secondary CPUs in a safe state until initialization permits release. Image stages cross secure/non-secure memory and exception-level boundaries with specified entry contracts. [Firmware design](https://github.com/ARM-software/arm-trusted-firmware/blob/master/docs/design/firmware-design.rst).
- **C2:** PSCI runtime services, interrupt-management infrastructure, translation-table support, and documented BL31 entry requirements allow platform ports and alternative earlier boot stages to share the runtime implementation. [Firmware design and handoff interfaces](https://github.com/ARM-software/arm-trusted-firmware/blob/master/docs/design/firmware-design.rst).

### 11. [riscv-software-src/opensbi](https://github.com/riscv-software-src/opensbi)

**Language/role:** C and RISC-V assembly; machine-mode implementation of the Supervisor Binary Interface.

Study a firmware ABI that lets kernels avoid embedding each board's privileged hardware mechanisms.

- **C1:** Domains constrain hart membership, cross-hart operations, and memory access. Memory regions have alignment and nesting rules, and overlapping regions must resolve access permissions consistently with physical memory protection. [Domain design](https://github.com/riscv-software-src/opensbi/blob/master/docs/domain_support.md).
- **C2:** Platform-independent `libsbi.a` is separated from platform-specific operations and firmware compositions. The [repository's architectural introduction](https://github.com/riscv-software-src/opensbi/blob/master/README.md) explains the library boundary; the domain document shows how hardware partitioning is represented above it. The README also records the compatibility consequences of introducing hart-state management.

### 12. [rustsbi/rustsbi](https://github.com/rustsbi/rustsbi)

**Language/role:** Rust; SBI implementation libraries and the Prototyper firmware in one repository.

Study how privileged firmware contracts become traits implemented by platform code rather than an inseparable board-specific binary.

- **C1:** The hart-state-management interface distinguishes pending, started, stopped, suspended, and resuming states. Starting another hart is asynchronous; success semantics and privilege/PMP setup remain obligations of the implementation. [Hsm trait and state contract](https://docs.rs/rustsbi/latest/rustsbi/trait.Hsm.html).
- **C2:** Extension traits expose common SBI behavior while implementations supply hardware mechanisms, usable in machine-mode firmware or hypervisor contexts. The [Hsm API](https://docs.rs/rustsbi/latest/rustsbi/trait.Hsm.html), including optional implementations, is an accessible entry point. These contracts identify what to review; Rust alone does not prove a platform implementation obeys them.

### 13. [TrustedFirmware-M/trusted-firmware-m](https://github.com/TrustedFirmware-M/trusted-firmware-m)

**Language/role:** Primarily C; secure processing environment for microcontroller-class platforms. **Official read-only mirror**. The selected subsystem is the **Secure Partition Manager**, beyond TF-M's bootloader integration.

Study isolation and service dispatch on systems without a conventional process MMU.

- **C1:** Secure/non-secure boundaries require separate execution contexts and stacks. IPC partitions serialize service requests through messages; direct secure-function calls have different constraints on concurrent clients and memory access. [SPM implementation design](https://tf-m.docs.trustedfirmware.org/en/latest/design_docs/services/secure_partition_manager.html).
- **C2:** Service IDs, handles, client APIs, partition APIs, and the non-secure agent provide a common framework across IPC and secure-function models. **C3:** The documentation explicitly contrasts IPC isolation and scheduling cost with the smaller secure-function model for constrained devices. [Runtime models and isolation design](https://tf-m.docs.trustedfirmware.org/en/latest/design_docs/services/secure_partition_manager.html).

### 14. [open-power/hostboot](https://github.com/open-power/hostboot)

**Language/role:** C++, C, and assembly; POWER processor, interconnect, and memory initialization, with supporting runtime services.

Study firmware large enough to need its own microkernel, user-space services, and synchronization infrastructure. **Branch caveat:** the repository's default-page README says its `master` branch is deprecated; use named release branches. The implementation inspected here is `release-fw1120`.

- **C1:** Futex waiting compares the expected value under a lock before queuing a blocked task. Wake/requeue paths manipulate scheduler state and explicitly discuss races involving released tasks and the destination futex. [Release-branch futex implementation](https://github.com/open-power/hostboot/blob/release-fw1120/src/kernel/futexmgr.C).
- **C2:** The repository separates its bootloader, microkernel, user-space drivers, initialization services, and imported hardware procedures. Its task/scheduler/futex interfaces are reusable mechanisms for that firmware workload, as demonstrated by [FutexManager](https://github.com/open-power/hostboot/blob/release-fw1120/src/kernel/futexmgr.C).

### 15. [open-power/skiboot](https://github.com/open-power/skiboot)

**Language/role:** C and POWER assembly; OPAL boot and runtime firmware, normally loaded after Hostboot.

Study the boundary between hardware initialization and firmware services that an already-running OS invokes.

- **C1:** All hardware threads enter a shared entry point; atomic master-thread selection prevents simultaneous initialization from corrupting state. Hostboot-supplied data is converted into the device tree exported to the OS. [Implementation overview](https://github.com/open-power/skiboot/blob/master/doc/overview.rst).
- **C3:** OPAL calls are designed not to block, to avoid injecting execution jitter into the OS. Firmware maintains per-CPU stacks; compressed payloads trade decompression against flash space and bytes read during boot. [OS interface and binary layout](https://github.com/open-power/skiboot/blob/master/doc/overview.rst). The performance reasoning is architectural, not a universal latency guarantee.

## PC firmware interfaces and operating-system loaders

### 16. [coreboot/seabios](https://github.com/coreboot/seabios)

**Language/role:** C and x86 assembly; legacy BIOS implementation. **Official read-only mirror** of the SeaBIOS Git repository.

Study compatibility with execution modes and calling conventions that modern application code rarely encounters.

- **C1:** Cross-mode calls save and restore segment registers, descriptor-table state, A20 state, and interrupt-related state. The code checks execution mode and stack assumptions around transitions. [Stack and mode-transition implementation](https://github.com/coreboot/seabios/blob/master/src/stacks.c).
- **C2:** Common far-call, software-interrupt, stack-hop, and internal-thread helpers centralize mechanisms used by BIOS services and hardware initialization. [stacks.c](https://github.com/coreboot/seabios/blob/master/src/stacks.c) is a concentrated entry point for studying this abstraction layer; the repository also documents its QEMU build/test path.

### 17. [openbios/openbios](https://github.com/openbios/openbios)

**Language/role:** Forth and C, with architecture-specific code; portable IEEE 1275 Open Firmware implementation. This is useful for understanding legacy firmware interfaces and emulated-machine boot environments, without assuming that legacy interface support means the repository is archived.

Study how an interpreter, a device model, and an OS-facing firmware ABI fit together.

- **C1:** The client bridge checks argument counts, translates arguments onto the Forth stack, handles `call-method`/`interpret` exceptions specially, and restores stack depth on return. It records compatibility behavior for clients requesting fewer return values. [Client-interface implementation](https://github.com/openbios/openbios/blob/master/libopenbios/client.c).
- **C2:** A portable Forth engine and dictionary underlie user, device, and client interfaces; the hosted form supports development outside a target ROM. The [client bridge](https://github.com/openbios/openbios/blob/master/libopenbios/client.c) shows how the reusable language machinery becomes an operating-system service interface.

### 18. [rhboot/shim](https://github.com/rhboot/shim)

**Language/role:** Primarily C; first-stage UEFI loader and trust intermediary.

Study how boot authentication must accommodate distribution-specific keys and the later revocation of vulnerable components.

- **C1:** SBAT's signed component metadata and generation-based revocation address the distinction between an authentic binary and an acceptable security generation. Its design examines failure and compatibility consequences across a multi-component boot chain. [SBAT design](https://github.com/rhboot/shim/blob/main/SBAT.md).
- **C2:** Signature indirection and component/vendor metadata form a reusable trust and revocation scheme across separately distributed loaders. **C3:** The design is explicitly motivated by limited UEFI revocation storage and the growth of per-image hash lists. [SBAT background and generation model](https://github.com/rhboot/shim/blob/main/SBAT.md). This is a design study, not a claim that any arbitrary signed chain is safe.

### 19. [acidanthera/OpenCorePkg](https://github.com/acidanthera/OpenCorePkg)

**Language/role:** Primarily C; UEFI bootloader and shared support libraries, with a strong Apple/macOS interoperability focus.

Study firmware compatibility work organized into reusable libraries rather than a collection of unstructured platform patches.

- **C1:** `OcGuardLib` adapts a UBSan runtime to the UEFI/EDK II environment, including the firmware calling convention and reporting of undefined arithmetic, alignment, and type behavior. [UBSan integration](https://github.com/acidanthera/OpenCorePkg/blob/master/Library/OcGuardLib/Ubsan.c).
- **C2:** The repository provides common image loading, configuration, cryptographic, ACPI, SMBIOS, and UEFI-variable facilities shared with other Acidanthera projects.
- **C4:** Its [changelog](https://github.com/acidanthera/OpenCorePkg/blob/master/Changelog.md) records a long sequence of compatibility fixes, from older macOS/kext and 2019 EDK II integrations through newer EDK II migrations, hibernation fixes, configuration validation, and secure-boot restoration. This is concrete evolution evidence, not a star-count argument.

### 20. [Limine-Bootloader/Limine](https://github.com/Limine-Bootloader/Limine)

**Language/role:** C and assembly; multiprotocol bootloader and reference implementation of the Limine boot protocol, spanning several 64-bit architecture families and x86 BIOS support.

Study an explicit kernel/loader contract, including the lifetime and ownership of information passed at entry.

- **C1:** The inspected v12 usage documentation defines the conditions for enforcing configuration and payload hashes under UEFI Secure Boot. A signed loader without an enrolled configuration hash does not enable that enforcement. Measured-boot failure handling also avoids returning to the menu after partially extending measurements. [Usage and trust policy](https://github.com/limine-bootloader/limine/blob/v12.x/USAGE.md).
- **C2:** Feature requests and responses provide extensible handoff structures for memory maps, modules, processors, and firmware tables, with documented pointer conventions and reclaimable-memory lifetime. [Official protocol specification](https://github.com/limine-bootloader/limine-protocol/blob/trunk/PROTOCOL.md). The specification repository is an entry point, not a separately counted implementation.

## Network boot and Linux-based boot environments

### 21. [ipxe/ipxe](https://github.com/ipxe/ipxe)

**Language/role:** C and architecture-specific assembly; network boot firmware supporting NIC-ROM replacement and chainloading.

Study protocol composition and object lifetime in a constrained, asynchronous boot environment.

- **C1:** Interface shutdown blocks further operations before notifying the peer, transfers the destination through a temporary interface, and manages references while disconnecting. Multi-interface shutdown nullifies interfaces first to prevent callback loops. [Object-interface implementation](https://github.com/ipxe/ipxe/blob/master/src/core/interface.c).
- **C2:** Reference-counted interfaces, operation lookup, and pass-through dispatch supply a common mechanism beneath different transports and boot services. [interface.c](https://github.com/ipxe/ipxe/blob/master/src/core/interface.c) makes these abstractions inspectable independently of the HTTP, SAN, or device-specific implementations using them.

### 22. [open-power/petitboot](https://github.com/open-power/petitboot)

**Language/role:** C; Linux/kexec-based bootloader, including POWER/OPAL and Arm64/ACPI platforms.

Study the architectural benefit of using an existing kernel for device access while keeping boot policy in a smaller user-space program.

- **C1:** Boot actions and configuration changes are centralized in the discovery server; UI clients request actions. The design ties this boundary to password restrictions and user permissions, and explicitly avoids silently changing the kernel command line. [Design constraints](https://github.com/open-power/petitboot/blob/master/doc/dev/design.rst).
- **C2:** `pb-discover`, multiple UI clients, event-reporting utilities, boot hooks, and plugin interfaces separate discovery, policy, and presentation. Utility differences and platform quirks are abstracted to support different systems and existing configuration formats. [Component architecture](https://github.com/open-power/petitboot/blob/master/doc/components.rst). The older twin UI is documented as incomplete relative to the ncurses client.

### 23. [u-root/u-root](https://github.com/u-root/u-root)

**Language/role:** Go with small assembly components; LinuxBoot userland and kexec bootloaders. The relevant monorepo areas are **`cmds/boot` and `pkg/boot`**, not its entire collection of Unix utilities.

Study a bootloader implemented as a Linux user-space application with explicit low-level kernel handoff code.

- **C1:** The Linux loader must bridge kexec's entry state to the new kernel's required addressing mode and `boot_params` register argument. Its small assembly “purgatory” exists specifically to satisfy that contract. [Linux loader architecture/API](https://pkg.go.dev/github.com/u-root/u-root/pkg/boot/linux).
- **C2:** Boot packages and command implementations can be composed into firmware initramfs images, supporting Linux and multiboot targets. The same [loader package documentation](https://pkg.go.dev/github.com/u-root/u-root/pkg/boot/linux) explains the reusable boundary between constructing load segments and entering the new kernel. Documentation was inspected at the rendered v0.16.0 package; this is not a latest-release claim.

## Microcontroller boot, update recovery, and mask ROM

### 24. [mcu-tools/mcuboot](https://github.com/mcu-tools/mcuboot)

**Language/role:** C boot core, Python image tooling, and simulator support; OS-independent secure boot and update infrastructure for microcontrollers.

Study persistent state machines where a reset may occur between individual flash operations.

- **C1:** Image trailers encode test, permanent, revert, and interrupted-swap states. New-swap state tables have an explicit evaluation order; resumed swaps recover their operation from persisted swap information. Validation and failure outcomes are part of the boot algorithm. [Design document](https://github.com/mcu-tools/mcuboot/blob/main/docs/design.md).
- **C2:** Flash-area IDs, independently erasable areas, common image/TLV formats, and OS porting layers decouple boot policy from platform flash access. **C3:** The design explains scratch-size versus erase-wear tradeoffs and alternatives such as offset swaps and direct execution. [Flash layout and upgrade strategies](https://github.com/mcu-tools/mcuboot/blob/main/docs/design.md). The safety properties differ by configured strategy.

### 25. [wolfSSL/wolfBoot](https://github.com/wolfSSL/wolfBoot)

**Language/role:** C; portable secure bootloader, signing tools, and application-side update API.

Study authentication, update confirmation, and rollback behind a small hardware-abstraction boundary.

- **C1:** Application updates verify the candidate, swap partitions, enter a testing state, and require explicit confirmation; interrupted swaps resume. A crucial documented exception is bootloader self-update, whose erase/rewrite operation is not interruption safe. [Firmware-update procedure](https://github.com/wolfSSL/wolfBoot/blob/master/docs/firmware_update.md).
- **C2:** A small flash/clock HAL and application-facing library separate the boot policy from OS and MCU integration.
- **C4:** Dated [release notes](https://github.com/wolfSSL/wolfBoot#release-notes) trace evolution from 2018 through later hardware support and security work, including manifest-parser bounds fixes and tests, non-regression coverage, and flash-write compatibility changes. This history makes it useful to study how initially simple update logic accumulates hardware exceptions.

### 26. [embassy-rs/embassy](https://github.com/embassy-rs/embassy)

**Language/role:** Rust; broader embedded framework, counted once for **`embassy-boot` and its nRF, STM32, and RP platform integrations**.

Study a firmware-update library that can be shared between the bootloader and an asynchronous application.

- **C1:** The boot layout separates active, DFU, and persistent-state partitions, imposes page-alignment/size constraints, and requires spare DFU capacity. Trial boot and rollback depend on that state surviving reset. [Boot architecture and API](https://docs.embassy.dev/embassy-boot/git/default/index.html).
- **C2:** `BootLoader` operates over `embedded_storage` flash implementations, while firmware-updater and state APIs keep applications from directly manipulating internal boot state. Networking is deliberately supplied outside the boot core, and hardware integrations live in separate crates. [Library boundaries and platform crates](https://docs.embassy.dev/embassy-boot/git/default/index.html). Signature verification requires the documented feature and API choices; it is not implied merely by using the library.

### 27. [raspberrypi/pico-bootrom-rp2350](https://github.com/raspberrypi/pico-bootrom-rp2350)

**Language/role:** C and Arm/RISC-V assembly; published RP2350 mask-ROM source. **Reference release:** the repository identifies the inspected source as the A4 ROM version, rather than a generally field-updatable bootloader.

Study a hardware-fixed boot environment with two instruction-set families and a very tight code-space budget.

- **C1:** Non-secure buffer validation combines address-range checks, privilege-sensitive SAU/MPU checks, special treatment of USB RAM, redundant comparisons, and control-flow checks intended to resist instruction-skipping faults. [Validation implementation](https://github.com/raspberrypi/pico-bootrom-rp2350/blob/master/src/main/arm/arm8_validate_ns_buffer.S).
- **C3:** The repository explains its separate Arm main, non-secure, RISC-V, and secure-gateway images. Reusing the non-secure Arm image through RISC-V emulation and placing gateways around fixed hardware address attributes expose concrete code-density and layout tradeoffs. Its README warns that compiler variation can exceed the available ROM space. The repository overview and [validation assembly](https://github.com/raspberrypi/pico-bootrom-rp2350/blob/master/src/main/arm/arm8_validate_ns_buffer.S) are complementary entry points.

## Coverage, search process, and limitations

Discovery used more than twenty distinct live search formulations, followed by opening GitHub repository pages and reading implementation files, project-authored API documentation, design documents, or release history for every retained entry. Search angles included embedded driver models and verified boot; coreboot/UEFI staging; Arm trusted and management firmware; RISC-V SBI and Rust firmware; POWER boot/runtime firmware; network boot and Secure Boot; MCU swap recovery; Apple Silicon handoff; mask ROM; bare-metal Go; Forth/Open Firmware; and small bootloader kernels. Later searches mostly returned already-covered projects, vendor forks, examples, or broader embedded frameworks; LK and Embassy were retained because their boot-related abstractions added distinct material.

The GitHub headings identify distinct repositories, not separate builds of one implementation. Official mirrors are marked where the repository states that relationship. oreboot is retained as a substantive separate implementation; EDK II-derived libraries alone were not grounds to count additional platform ports. Hostboot's deprecated default branch and the RP2350 reference-release scope are explicitly flagged. No general claim of active maintenance is inferred from a recent push or crawl date.

Important exclusions and limits:

- [ARM-software/SCP-firmware](https://github.com/ARM-software/SCP-firmware) explicitly identifies itself as an archived, no-longer-used repository. [aik/SLOF](https://github.com/aik/SLOF) says its official repository moved to GitLab. Neither was retained as a current GitHub project; this search did not establish a qualifying official GitHub mirror of their new upstreams.
- GNU GRUB searches led to its official project source instructions outside GitHub; an arbitrary GitHub mirror or distribution fork was not substituted. This is a GitHub-scoped selection, not an exhaustive map of boot software.
- Binary-only firmware distributions, flashing utilities, boot-theme/configuration collections, tutorials, board-only forks, and general-purpose RTOS/application firmware were excluded. Historical vendor Open Firmware snapshots were considered less useful additions than the inspected OpenBIOS implementation for this selection.
- Some web fetches returned cache errors or access failures; selected public GitHub API reads supplied the missing source material. The supplementary API archive-status sweep later hit a rate limit, so it is not presented as a complete maintenance audit. Every retained canonical repository page had already been opened through the web reader.
- No candidate code was cloned, built, executed, or installed, and no hardware behavior was tested. Criteria labels are grounded engineering judgments from the cited material, not independently measured reliability or performance results. Branch-based links and live documentation can change; board support, configuration, release choice, and deployed trust policy still need separate evaluation.
