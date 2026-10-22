# Hardware debug servers and device programming tools

Research date: **2026-10-09**

This selection covers 27 GitHub repositories implementing hardware debug servers, debug-probe firmware and host libraries, flash programmers, and device provisioning tools. It spans Arm, AVR, MSP430, STM8, RISC-V, ESP devices, FPGA/CPLD programming, and SoC recovery/manufacturing workflows. Broad hardware toolkits appear only where their programming or debugging subsystems provide substantial implementations. Each repository is counted once.

The criteria identify useful engineering study material, not a certification of correctness or a claim that every component is exemplary:

- **C1 — Difficult correctness:** state, concurrency, memory/flash invariants, protocol semantics, or consequential failure handling.
- **C2 — Reusable abstractions:** substantial interfaces or models supporting multiple devices, transports, clients, or workflows.
- **C3 — Performance with structure:** explicit treatment of transfer latency, programming time, bandwidth, memory limits, or execution timing through understandable mechanisms.
- **C4 — Sustained evolution:** multi-year evidence of compatibility work, testing, or complexity management; age or a recent push alone does not qualify.

Repository identities and default branches were checked through GitHub pages or the GitHub API. Linked implementation files were read in addition to repository descriptions. Links generally follow default branches and can change; these are source snapshots, not assurances about a released package. None of the retained repositories was marked archived at inspection. Maintenance caveats and official mirrors are identified below.

## Host debug servers and programming libraries

### 1. [openocd-org/openocd](https://github.com/openocd-org/openocd)

**Language/role:** C with Tcl configuration; multi-target debug server, JTAG/SWD adapter integration, and flash programming. This is the project's **official read-only GitHub mirror**; upstream development uses the project's own infrastructure.

An experienced engineer can study how one server reconciles target operations with adapter-specific transaction engines.

- **C1:** The JTAG API distinguishes the queued TAP state from executed operations and documents callback ordering, buffer lifetime, and failure behavior. In particular, callback execution after an unsuccessful queue flush is not uniformly guaranteed across drivers. These are concrete asynchronous API contracts. Entry point: [JTAG public interface](https://github.com/openocd-org/openocd/blob/master/src/jtag/jtag.h).
- **C2:** The architecture separates the JTAG core from adapter drivers and supports both the normal driver model and a minidriver integration path. Tcl-facing commands sit above these mechanisms. The [JTAG architecture notes](https://github.com/openocd-org/openocd/blob/master/doc/manual/jtag.txt), though incomplete in places, explain the boundary.
- **C3:** The queued interface permits asynchronous adapter implementations and batches operations rather than requiring a host/USB transaction for every scan. The same public interface makes synchronization costs visible.

### 2. [probe-rs/probe-rs](https://github.com/probe-rs/probe-rs)

**Language/role:** Rust; reusable embedded debugging and flashing library with command-line and debugger integrations.

The flash planner is a particularly useful entry into the larger probe/session/core architecture: it translates sparse image data into operations constrained by device geometry.

- **C1:** The builder maintains ordered, non-overlapping data spans and separately represents pages, erase sectors, and fill regions. Fill regions account for bytes affected by erase that were not supplied in the new image. Study the interval handling and layout construction in [flashing/builder.rs](https://github.com/probe-rs/probe-rs/blob/master/probe-rs/src/flashing/builder.rs).
- **C2:** The [flashing module API](https://github.com/probe-rs/probe-rs/blob/master/probe-rs/src/flashing/mod.rs) exposes both file-oriented programming and lower-level staged data followed by commit. Shared layout, algorithm, progress, erase, and verification types let multiple frontends reuse the same machinery instead of embedding their own flash algorithms.

### 3. [pyocd/pyOCD](https://github.com/pyocd/pyOCD)

**Language/role:** Python; Arm debug library, GDB server, and flash programmer.

This is a strong choice for studying how a high-level host implementation makes device-aware programming decisions. The [flash builder](https://github.com/pyocd/pyOCD/blob/main/pyocd/flash/builder.py) exposes both the correctness conditions and its cost model.

- **C1:** It rejects overlapping or out-of-region input, constructs sector/page operations, and supports preservation of unwritten data. It explicitly disables some optimizations and preservation options for regions whose erased sectors cannot be read.
- **C3:** It estimates chip-erase versus sector-erase cost, avoids programming unchanged pages, supports a target CRC analyzer, and enables double buffering where supported. The fast verification option explicitly accepts CRC-based equality, so that mode should not be described as a byte-for-byte proof.

The useful study topic is the interaction between geometry, preservation policy, and transfer cost, rather than Python syntax or the CLI alone.

### 4. [stlink-org/stlink](https://github.com/stlink-org/stlink)

**Language/role:** C; STM32 ST-LINK host library, flash utilities, and the st-util GDB server. Inspected source links use the repository's **testing** default branch.

- **C1:** The [flash loader implementation](https://github.com/stlink-org/stlink/blob/testing/src/stlink-lib/flash_loader.c) selects target-resident loaders for different STM32 families and handles SRAM placement, alignment, fault state, and interrupt masking. Its comments explain why halting the core must precede disabling interrupts; otherwise the loader can inherit the wrong execution conditions.
- **C4:** The [changelog](https://github.com/stlink-org/stlink/blob/testing/CHANGELOG.md) records multi-bank erase and regression work in 2020, STLINK-V3 and STM32H7 reset changes in 2021, and further family, memory-map, and platform compatibility work in the dated 2026 release section.

Study how a shared host library contains family-specific flash behavior without forcing every utility to reproduce it. Unreleased changelog material is not treated as a shipped release.

### 5. [dlbeer/mspdebug](https://github.com/dlbeer/mspdebug)

**Language/role:** C; MSP430 programmer, debugger/GDB proxy, and simulator, with multiple probe and bootloader backends.

- **C1:** The [device interface](https://github.com/dlbeer/mspdebug/blob/master/drivers/device.h) gives breakpoint changes an explicit dirty-state contract: modified breakpoint entries must be marked for reloading before execution resumes. It also distinguishes flash-related operations from devices using FRAM.
- **C2:** That interface defines a device-class table for opening, memory access, erase, registers, execution control, and polling. This is a compact example of a common debugger model over dissimilar transports.
- **C4:** The [ChangeLog](https://github.com/dlbeer/mspdebug/blob/master/ChangeLog) documents unaligned transfers and Intel HEX fixes in 2010, FRAM reset-vector and erase-policy fixes in 2012, and adaptation to TI's 64-bit library API in 2016.

Its value includes accumulated support for older hardware; the historical compatibility record should not be mistaken for a promise of a particular present release cadence.

### 6. [felias-fogg/PyAvrOCD](https://github.com/felias-fogg/PyAvrOCD)

**Language/role:** Python; AVR GDB server covering debugWIRE, JTAG, and UPDI through supported probe arrangements.

This smaller project is unusually instructive about preserving source-level stepping semantics over constrained on-chip debug facilities.

- **C1:** The [breakpoint/execution manager](https://github.com/felias-fogg/PyAvrOCD/blob/main/pyavrocd/breakexec.py) distinguishes active and allocated breakpoints, tracks original instruction words, deals with hardware breakpoint allocation after reset, and handles stepping around interrupts.
- **C3:** The [range-stepping design note](https://github.com/felias-fogg/PyAvrOCD/blob/main/docs/rangestepping-speedup.md) explains why GDB range commands alone do not distinguish step-in from step-over. It combines temporary-breakpoint placement and command history to reduce host round trips while retaining the intended behavior. The execution manager also treats unnecessary flash rewriting as a cost.

The design note is useful because it explains the inference and its reset conditions, rather than merely advertising faster stepping.

### 7. [cnlohr/ch32fun](https://github.com/cnlohr/ch32fun)

**Language/role:** Primarily C; retain the **minichlink host programmer and GDB server subsystem**, not the monorepo's general application examples.

- **C2:** The [minichlink interface](https://github.com/cnlohr/ch32fun/blob/master/minichlink/minichlink.h) defines a function table with low-level debug-register operations and higher-level memory/programming operations that can be supplied or derived. Its contracts distinguish arbitrary-alignment byte transfers from aligned word accesses, allowing several probe backends to share higher-level logic.
- **C1:** The [GDB implementation](https://github.com/cnlohr/ch32fun/blob/master/minichlink/minichgdb.c) saves and restores target registers around injected debug operations, manages shadow execution state, and handles software breakpoints over different instruction widths. A debugger must avoid corrupting the state it is observing.

The repository documents the strongest GDB support around CH32V003; do not infer equal support for every chip usable with other parts of ch32fun.

### 8. [ch32-rs/wlink](https://github.com/ch32-rs/wlink)

**Language/role:** Rust; WCH-Link host library and command-line programmer for WCH RISC-V devices. The README explicitly warns that it is **not production ready**.

- **C1:** The [session/operations layer](https://github.com/ch32-rs/wlink/blob/main/src/operations.rs) bounds attach retries, compares expected and detected chips, and contains probe-firmware-specific guards against misidentification. These checks matter because selecting the wrong family can select the wrong programming behavior.
- **C2:** A session combines a probe, detected chip, speed, and per-chip initialization into reusable operations rather than making each CLI command reconstruct the exchange.
- The additional [reverse-engineered protocol notes](https://github.com/ch32-rs/wlink/blob/main/protocol.md) describe request, success, and error packets, DMI byte order, and protection behavior. They also mark unknown fields, making the limits of the protocol knowledge visible.

Study it as a compact implementation with explicit uncertainty, not as a universally validated WCH programming stack.

## Probe firmware and browser-facing debug stacks

### 9. [ARMmbed/DAPLink](https://github.com/ARMmbed/DAPLink)

**Language/role:** C; interface-MCU firmware providing CMSIS-DAP debugging, serial bridging, and drag-and-drop programming.

Its virtual mass-storage programmer illustrates the mismatch between an operating system's filesystem writes and a target flash transaction.

- **C1:** The [virtual-filesystem manager](https://github.com/ARMmbed/DAPLink/blob/main/source/daplink/drag-n-drop/vfs_manager.c) tracks stream opening/completion, partial transfers, timeouts, and disconnect/remount state. It uses thread assertions and mutex-protected state where USB processing and other activity meet.
- **C2:** The [virtual FAT implementation](https://github.com/ARMmbed/DAPLink/blob/main/source/daplink/drag-n-drop/virtual_fs.c) exposes callbacks for generated files and sector reads/writes, separating filesystem emulation from the programming stream.
- **C3:** This is a constrained virtual filesystem rather than a disk image held in RAM. Packed-layout checks and explicit directory/sector sizing show how the implementation controls storage overhead.

The documented virtual-filesystem restrictions are part of the architecture, not promises of arbitrary FAT filesystem behavior.

### 10. [raspberrypi/debugprobe](https://github.com/raspberrypi/debugprobe)

**Language/role:** C with RP-series PIO programs; CMSIS-DAP SWD and UART probe firmware for supported Raspberry Pi probe/Pico hardware.

- **C1:** The [SWD-to-PIO shim](https://github.com/raspberrypi/debugprobe/blob/master/src/sw_dp_pio.c) handles SWD turnaround, parity, acknowledgement variants, and the different recovery/data phases associated with WAIT, FAULT, and protocol errors.
- **C3:** Timing-sensitive pin transactions are delegated to PIO while the C layer retains CMSIS-DAP semantics. The shim also caches the configured clock rate to avoid repeatedly doing the conversion work.

This offers a relatively focused study of dividing responsibility between a CPU protocol implementation and a hardware state machine. The category fit is actual SWD probe firmware; the presence of CMSIS-DAP should not be read as a claim that every possible CMSIS-DAP transport is implemented.

### 11. [felias-fogg/dw-link](https://github.com/felias-fogg/dw-link)

**Language/role:** C++/Arduino; on-probe AVR debugWIRE GDB server and ISP programmer, notably usable with an Arduino Uno.

This is a separate firmware implementation from the host-side PyAvrOCD project.

- **C1:** The [firmware](https://github.com/felias-fogg/dw-link/blob/master/dw-link/dw-link.ino) separates breakpoint allocation, activation, presence in flash, and use of the hardware breakpoint. Updating flash-resident breakpoints is gated on the flash state; detachment must also clean up inserted break instructions.
- **C4:** The [changelog](https://github.com/felias-fogg/dw-link/blob/master/CHANGELOG.md) traces input-capture interrupt lifecycle and low-baud calibration fixes in 2023, compatibility with PyAvrOCD integration tests in 2025, and status-register/stack-pointer corrections for simulated instructions in 2026.

It is a useful small-memory counterpoint to desktop servers: packet buffers, breakpoint capacity, serial timing, and flash wear all affect debugger behavior.

### 12. [ARMmbed/dapjs](https://github.com/ARMmbed/dapjs)

**Language/role:** TypeScript; browser/Node host library for CMSIS-DAP access, including WebUSB-oriented workflows.

- **C2:** The repository separates transport, CMSIS-DAP proxy, Arm Debug Interface, processor operations, and DAPLink-specific functionality. The [ADI implementation](https://github.com/ARMmbed/dapjs/blob/master/src/dap/adi.ts) accepts either a transport or a proxy and composes reusable queued operations.
- **C1:** The same implementation splits block transfers at the target address register's auto-increment boundary and handles byte requests using aligned word transfers. Host-side chunking must preserve target address semantics, not just USB packet sizes.
- **C3:** Cached DP/AP selection and configuration reduce repeated debug-port writes.

The study opportunity is a layered asynchronous hardware API in a language often associated with user interfaces. Browser support should be checked against the actual application environment; this report does not infer current compatibility from old examples.

## MCU and nonvolatile-memory programmers

### 13. [avrdudes/avrdude](https://github.com/avrdudes/avrdude)

**Language/role:** C; AVR programming across many programmers, bootloaders, memory areas, and device families.

- **C2:** The [library header](https://github.com/avrdudes/avrdude/blob/main/src/libavrdude.h) defines substantial programmer, part, memory, cache, and callback structures. This shared vocabulary lets frontends and backends work with the same device model; it should not be confused with a promise of a permanently stable binary ABI.
- **C1:** The [AVR programming core](https://github.com/avrdudes/avrdude/blob/main/src/avr.c) handles memory-specific address calculations, programming enablement, TPI key/control sequences, polling, and error propagation. Flash, EEPROM, fuse, and other memory operations cannot be treated as interchangeable byte writes.

Study the tension between data-driven device definitions and cases that need explicit protocol logic. The code contains substantive programming machinery beneath the familiar CLI.

### 14. [flashrom/flashrom](https://github.com/flashrom/flashrom)

**Language/role:** C; firmware flash-chip probing, reading, erasing, writing, and verification across many programmer interfaces. This is an **official GitHub mirror**; the repository directs contributions to the coreboot review infrastructure.

- **C1:** The [programming core](https://github.com/flashrom/flashrom/blob/main/flashrom.c) models erase necessity according to write granularity and existing contents, including the one-way bit transitions of relevant flash technologies. It checks operation capabilities and safety status, verifies ranges, and registers restoration/shutdown actions.
- **C2:** Chip definitions, programmer capabilities, bus constraints, and selected image regions meet in common programming logic. This is reusable coordination across combinations of hardware, rather than a single-chip upload script.
- **C3:** The same erase-decision machinery identifies data that can be left unchanged or written without an unnecessary erase.

An experienced engineer can study how capability discovery and recovery obligations constrain an apparently simple “write this image” command.

### 15. [espressif/esptool](https://github.com/espressif/esptool)

**Language/role:** Python; ESP-family ROM/stub bootloader communication, image handling, flashing, and associated device utilities.

- **C1:** The [loader implementation](https://github.com/espressif/esptool/blob/master/esptool/loader.py) matches responses to operation codes, tolerates extra synchronization replies, interprets command status separately from payload data, and restores temporary serial timeouts. It contains explicit recovery for repeated unsupported-command responses.
- **C2:** A common loader model is specialized for chip families and combines command framing with selectable reset strategies, ROM behavior, and uploaded-stub behavior.
- **C3:** Transfer and erase timeouts account for operation size, while stub-assisted operations address limitations and performance costs of the ROM loader.

The target stub source now has a separate repository; this entry counts esptool's host implementation and integration, without treating bundled stub binaries as source code implemented here.

### 16. [esp-rs/espflash](https://github.com/esp-rs/espflash)

**Language/role:** Rust; ESP flashing library, command-line tool, and Cargo integration, counted together as one repository.

This is a separate Rust implementation, not an extra entry for a fork of esptool.

- **C2:** The [flasher module](https://github.com/esp-rs/espflash/blob/main/espflash/src/flasher/mod.rs) composes connection handling, chip-specific flash targets, image formats, and segments. A target follows begin/write-segment/finish operations, allowing the library and frontends to share the programming path.
- **C1:** It validates family-specific flash parameters and changes or rejects behavior under secure-download constraints. Verification and skipping operations must be reconciled with capabilities actually available in that mode.
- **C3:** The flasher exposes mechanisms to avoid unnecessary programming and applies operation-size-dependent timing.

Compare its typed component boundaries with esptool's class-based organization; neither entry implies that every supported chip has identical capabilities.

### 17. [microchip-pic-avr-tools/pymcuprog](https://github.com/microchip-pic-avr-tools/pymcuprog)

**Language/role:** Python; Microchip programming library and CLI for supported AVR/PIC devices and probes. PIC workflows may require device packs.

- **C2:** The [programmer layer](https://github.com/microchip-pic-avr-tools/pymcuprog/blob/main/pymcuprog/programmer.py) selects a nonvolatile-memory provider from the transport, device description, interface, and pack. It then exposes common setup, read, write, erase, and verification operations.
- **C1:** It rejects negative offsets, attempts to write read-only memories, and writes outside a memory region. Verification uses memory-specific masks to account for unimplemented bits and pads data to the mask width, rather than assuming every readback bit has ordinary byte-storage semantics.

This is a useful example of a vendor tool whose reusable Python API remains visible beneath its command-line interface. The bounds and masked verification rules are more instructive than its device count.

### 18. [shumatech/BOSSA](https://github.com/shumatech/BOSSA)

**Language/role:** C++; SAM-BA-based flash programmer for supported SAM Arm microcontrollers.

- **C2:** The [Flasher implementation](https://github.com/shumatech/BOSSA/blob/master/src/Flasher.cpp) separates the flash-device backend, SAM-BA connection, and progress/status observer. The orchestration can therefore be shared by user interfaces and device variants.
- **C3:** It chooses buffered writing when the connection advertises that capability and otherwise programs pages. Verification similarly uses a target checksum capability when available, with readback handling around mismatches.
- **C1:** Page-aligned offsets and flash geometry affect writes and verification; final buffered chunks require explicit padding and page rounding.

**Maintenance context:** the [GitHub metadata snapshot](https://api.github.com/repos/shumatech/BOSSA) reported its latest push in November 2023. Treat this as an older, substantive implementation; the repository also distinguishes families not tested on every release. No claim of current active maintenance is made.

### 19. [raspberrypi/picotool](https://github.com/raspberrypi/picotool)

**Language/role:** C++ with a C USB connection layer; RP2040/RP2350 image inspection, programming, and provisioning.

- **C1:** The [picoboot connection implementation](https://github.com/raspberrypi/picotool/blob/master/picoboot_connection/picoboot_connection.c) checks transfer lengths and tracks exclusive access and execute-in-place state. It invalidates optimistic state before transactions so a failure does not leave the host assuming the device still has the previous state.
- **C2:** Shared command framing and transport operations underpin memory, flash, reset, and OTP-related operations, while higher layers handle binary information and user commands.
- **C3:** It skips redundant execute-in-place transitions only when the cached state and exclusive ownership justify the shortcut.

Study how a small boot-ROM protocol becomes a broader tool without allowing state caching to silently override error handling.

### 20. [vdudouyt/stm8flash](https://github.com/vdudouyt/stm8flash)

**Language/role:** C; STM8 flash/EEPROM programming through ST-LINK and SWIM.

- **C1:** The [ST-LINK/V2 implementation](https://github.com/vdudouyt/stm8flash/blob/master/stlinkv2.c) distinguishes flash and EEPROM unlock sequences, option-byte programming, status polling, and device-dependent registers/block geometry. These are consequential protocol and nonvolatile-memory constraints.
- **C3:** It can compare blocks with existing device contents and program only changed blocks, reducing transfer work and unnecessary flash writes.

**Source caveat:** the inspected write loop contains an explicit author comment about a potential read beyond the input buffer when its length is not a multiple of the flash block size. This report does not independently establish whether every caller can reach that condition. The project is included as compact, substantive protocol code with a visible review concern, not as a blanket recommendation for unattended production use.

### 21. [dfu-programmer/dfu-programmer](https://github.com/dfu-programmer/dfu-programmer)

**Language/role:** C; Atmel-specific USB DFU programming for supported AVR, AVR32, XMEGA, and 8051-family devices.

- **C1:** The [Atmel protocol implementation](https://github.com/dfu-programmer/dfu-programmer/blob/master/src/atmel.c) handles memory-page selection, transfer limits, blocks that cannot cross a 64 KiB boundary, blank checking, and the distinction between USB errors and device DFU status.
- **C2:** A common memory-unit and block-transfer model supports flash, EEPROM, configuration, bootloader, and other device regions, while isolating differences such as AVR32 command headers. This is a substantive vendor protocol engine rather than a thin generic-DFU wrapper.

**Maintenance context:** the [GitHub metadata snapshot](https://api.github.com/repos/dfu-programmer/dfu-programmer) reported its latest push in January 2024. Its value here is established protocol implementation; this is not a claim of an ongoing rapid release cycle.

## SoC provisioning, recovery, and manufacturing

### 22. [nxp-mcuxpresso/spsdk](https://github.com/nxp-mcuxpresso/spsdk)

**Language/role:** Python; NXP Secure Provisioning SDK. The relevant subsystem is **McuBoot/device communication and programming**, not every cryptographic or packaging component in the SDK.

- **C2:** The [McuBoot client](https://github.com/nxp-mcuxpresso/spsdk/blob/master/spsdk/mboot/mcuboot.py) operates over a protocol interface and uses typed commands, responses, memory descriptions, and family/revision information. This permits provisioning workflows to reuse transport-independent device operations.
- **C1:** Command acceptance, a following data phase, and final status are separate events. The implementation distinguishes timeouts and data aborts, chunks data according to packet limits, and handles command-dependent expectations about a final response.

Study the lifecycle of a stateful programming command that can fail between phases. Inclusion of a “secure provisioning” SDK does not constitute an assessment of its complete security design.

### 23. [nxp-imx/mfgtools](https://github.com/nxp-imx/mfgtools)

**Language/role:** C++; UUU/libuuu, the Universal Update Utility for NXP i.MX USB download and manufacturing workflows.

- **C1:** The [USB hotplug/worker implementation](https://github.com/nxp-imx/mfgtools/blob/master/libuuu/usbhotplug.cpp) coordinates polling, worker threads, filters, timeouts, and device lifetime. It explicitly takes a libusb device reference before a worker outlives the enumerated device list and releases that reference afterward.
- **C3:** The [sparse-image implementation](https://github.com/nxp-imx/mfgtools/blob/master/libuuu/sparse.cpp) represents raw, fill, and omitted chunks, coalesces applicable chunks, and splits data to fit bounded download buffers. Together with the worker structure, this addresses large images and multiple devices through identifiable modules.

This is an important scale contrast with single-MCU flash utilities: enumeration changes, staged boot protocols, transfer representation, and concurrency become central. The sparse-parser inspection is not an adversarial-input audit.

### 24. [linux-sunxi/sunxi-tools](https://github.com/linux-sunxi/sunxi-tools)

**Language/role:** C with Arm target helpers; retain the **Allwinner FEL transport and flash-programming subsystem** of this broader tools repository.

- **C2:** The [FEL library](https://github.com/linux-sunxi/sunxi-tools/blob/master/fel_lib.c) packages USB handles, SoC information, framed transactions, partial-transfer handling, and chunked reads/writes behind reusable host operations.
- **C3:** The [SPI-flash programming implementation](https://github.com/linux-sunxi/sunxi-tools/blob/master/fel-spiflash.c) executes batches of commands on the target and bounds work by available SRAM. It selects erase sizes according to alignment and remaining length, reducing per-command host interaction.
- **C1:** Register differences across SoCs, erase alignment, and scratch-memory preservation are visible obligations. The normal path saves and restores SRAM used by temporary code; that observation is not a claim that every failure path restores all state.

Study how a recovery ROM becomes a transport for a more capable temporary programmer.

## FPGA programmers and extensible hardware instruments

### 25. [trabucayre/openFPGALoader](https://github.com/trabucayre/openFPGALoader)

**Language/role:** C++; multi-vendor FPGA configuration and attached-flash programming through multiple cables/probes.

- **C1:** The [JTAG engine](https://github.com/trabucayre/openFPGALoader/blob/master/src/jtag.cpp) handles instruction/data-register shifts through device chains. It inserts bypass bits before and after the selected device and changes TMS on the correct final bit when leaving a shift state.
- **C2:** The implementation selects among cable backends while preserving a common JTAG operation model; higher layers select devices and programming behavior. This makes cable, board, and silicon variation separable engineering concerns.
- **C3:** Buffered TMS transitions and grouped shifts reduce the cost of driving individual state changes through host interfaces.

The chain logic is particularly useful to study: correctness depends on the complete chain and exit state, not merely sending the selected FPGA's bitstream.

### 26. [GlasgowEmbedded/glasgow](https://github.com/GlasgowEmbedded/glasgow)

**Language/role:** Python/Amaranth host and gateware, plus firmware; programmable hardware interface platform. Retain its **programmer/debug applet framework and implemented programming protocols**.

- **C2:** The [applet framework](https://github.com/GlasgowEmbedded/glasgow/blob/main/software/glasgow/applet/__init__.py) separates build, setup, and execution, with assembly abstractions for hardware and simulation. Plugin metadata and testing helpers support many independently composed protocol implementations.
- **C1:** The [XC9500XL programmer](https://github.com/GlasgowEmbedded/glasgow/blob/main/software/glasgow/applet/program/xc9500xl/__init__.py) is substantive evidence beyond the platform description: it maps JEDEC fuse data to physical programming geometry and implements enable, erase, program, and verification behavior. Its explanatory notes distinguish established observations from reverse-engineering hypotheses.

Study how unusual device protocols can share a transport/gateware framework while retaining detailed device semantics. This entry counts the monorepo once, not each applet as a separate project.

### 27. [greatscottgadgets/greatfet](https://github.com/greatscottgadgets/greatfet)

**Language/role:** C firmware and Python host tools; GreatFET hardware interface platform, including external flash programmers and debug interfaces.

- **C2:** The [class/verb interface documentation](https://github.com/greatscottgadgets/greatfet/blob/main/docs/source/greatfet_classes.rst) specifies a namespace for firmware capabilities and commands, with classes covering SPI flash, JTAG-related interfaces, and other instruments. It provides a shared extension boundary between host and firmware.
- **C1:** The [SPI-flash programmer](https://github.com/greatscottgadgets/greatfet/blob/main/host/greatfet/programmers/spi_flash.py) distinguishes likely stuck-signal JEDEC responses from usable identification, derives device geometry, and makes fallback after failed topology discovery an explicit policy. A disconnected or floating wire must not silently become a plausible flash device.

The focused study topic is capability discovery and programmer composition across the host/firmware boundary, rather than the board's unrelated peripheral features.

## Coverage, search process, and limitations

Discovery used live web search across more than six distinct query families, followed by direct reads of repository pages, GitHub API metadata, source files, design notes, and changelogs. Search angles included:

1. Arm GDB servers, CMSIS-DAP hosts, and SWD/JTAG transaction architectures.
2. Probe firmware, RP2040 PIO probes, and TypeScript/WebUSB debug libraries.
3. AVR debugWIRE/UPDI, MSP430 debugger backends, and STM8/SWIM programmers.
4. SPI firmware flash tools, Atmel USB DFU, SAM-BA, and Raspberry Pi boot-ROM tools.
5. ESP ROM/stub loaders and independently implemented Rust flashing libraries.
6. WCH-Link and CH32 RISC-V programming/debugging implementations.
7. Multi-vendor FPGA/JTAG loaders and extensible Glasgow/GreatFET programmer frameworks.
8. NXP provisioning/manufacturing, Allwinner FEL, Rockchip recovery, and serial-ISP alternatives.

The final recovery/manufacturing queries added UUU and sunxi-tools; other later searches increasingly returned already covered projects, vendor forks, packaging repositories, or smaller alternatives without comparably strong inspected evidence. The list extends beyond 25 because probe firmware, desktop libraries, small protocol implementations, and multi-device manufacturing tools expose materially different engineering problems.

**Important exclusions:** [Black Magic Debug's former GitHub repository](https://github.com/blackmagic-debug/blackmagic) now announces a move to Codeberg and no longer provides the substantive source tree required for this GitHub-only selection. It was therefore excluded rather than described as an active GitHub implementation. [dw-gdbserver](https://github.com/felias-fogg/dw-gdbserver) identifies PyAvrOCD as its successor and was not counted as another independent current choice. Searches for generic dfu-util, UrJTAG, and xc3sprog surfaced upstream-hosting or fork/mirror-provenance issues; no insufficiently verified GitHub mirror was added merely to cover a familiar name. Generic HALs, IDE wrappers, board examples, bootloaders without a substantial host/probe programming component, and lists of tools were outside the selection.

**Limits of the evidence:** this was read-only source research. No candidate code was installed or executed, no attached hardware was tested, and source inspection does not prove advertised device coverage. Repository metadata establishes identity and snapshot status, not software quality. C1–C3 assignments are engineering judgments grounded in the linked mechanisms; C4 is used only where multi-year compatibility/correction evidence was actually read. The report does not promise stable APIs, uniformly safe failure recovery, or current maintenance for every project. The experimental status of wlink, older BOSSA/dfu-programmer activity, and the visible stm8flash buffer concern are material qualifications to selection.

