# NEORV32 Hello World on Tang Nano 9K (Windows Guide)

This is a working example of running a [NEORV32 RISC-V soft-core processor](https://github.com/stnolting/neorv32) on the [Tang Nano 9K FPGA](https://wiki.sipeed.com/hardware/en/tang/Tang-Nano-9K/Nano-9K.html) development board, built and uploaded entirely from **Windows**.

Based on [jimmyw/tang_nano_9k_neorv32](https://github.com/jimmyw/tang_nano_9k_neorv32) with fixes for Windows toolchain and binary format compatibility.

---

## Requirements

### Hardware
- Tang Nano 9K FPGA board
- USB cable

### Software
- [xPack RISC-V Embedded GCC](https://github.com/xpack-binaries/riscv-none-elf-gcc/releases) — RISC-V cross-compiler
- [w64devkit](https://github.com/skeeto/w64devkit/releases) — MinGW GCC for Windows (needed to build `image_gen`)
- [NEORV32 repository](https://github.com/stnolting/neorv32) — core library (clone separately)
- Python 3 + `pyserial` (`pip install pyserial`)

---

## Setup

### 1. Install xPack RISC-V GCC
Download and install from the [xPack releases page](https://github.com/xpack-binaries/riscv-none-elf-gcc/releases).
Make sure `riscv-none-elf-gcc` is in your PATH:
```powershell
riscv-none-elf-gcc --version
```

### 2. Install w64devkit
Download `w64devkit-x64-*.7z.exe` from [releases](https://github.com/skeeto/w64devkit/releases), extract to `D:\w64devkit`.
Add to PATH for the current session:
```powershell
$env:PATH = "D:\w64devkit\bin;" + $env:PATH
gcc --version
```

### 3. Clone NEORV32 library
Download the [NEORV32 repository](https://github.com/stnolting/neorv32) and extract to `D:\neorv32`.

### 4. Fix missing elf.h (Windows only)
`image_gen.c` requires `elf.h` which is Linux-only. Download it manually:
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/bminor/glibc/master/elf/elf.h" -OutFile "D:\w64devkit\include\elf.h"
```

### 5. Update NEORV32_HOME in makefile
Edit `makefile` line 30:
```makefile
NEORV32_HOME ?= D:/neorv32
```

---

## Build

```powershell
# Add w64devkit to PATH first
$env:PATH = "D:\w64devkit\bin;" + $env:PATH

# Build raw binary
make bin

# Convert to legacy bootloader format (0x4788CAFE signature)
py make_exe.py neorv32_raw_exe.bin neorv32_exe_old.bin
```

> **Why not `make exe`?**
> `make exe` produces `neorv32_exe.bin` but newer NEORV32 versions use a `NEO!` executable
> signature. The modified bootloader in this project expects the legacy `0x4788CAFE` signature.
> `make bin` gives us the raw binary, and `make_exe.py` repackages it with the correct
> header (signature + size + checksum).

---

## Upload

Reset the board (unplug/replug USB), then immediately run:

```powershell
py uart_upload.py COM4 neorv32_exe_old.bin
```

Replace `COM4` with your actual serial port. To find it:
```powershell
Get-WMIObject Win32_SerialPort | Select Name, DeviceID
```

### Expected output
```
Aborting autoboot...
CMD:>
Erasing flash memory...
...
Uploading executable... X X X X ... OK
CMD:>
Booting application... OK
```

Then on your serial terminal (115200 baud):
```
Booting from 0x00000000...
[NEORV32 logo]
Hello Jimmy! :)
```

---

## Files

| File | Description |
|------|-------------|
| `main.c` | Hello World application source |
| `makefile` | Build configuration (set NEORV32_HOME) |
| `uart_upload.py` | Fixed UART upload script for Windows |
| `make_exe.py` | Converts raw binary to legacy bootloader format |
| `.gitignore` | Excludes build artifacts |

---

## Bootloader Command Reference

The modified bootloader accepts these commands over UART:

| Command | Action |
|---------|--------|
| `space` | Abort autoboot sequence |
| `d` | Dump flash |
| `e` | Erase flash |
| `u` | Upload executable via UART |
| `x` | Execute application |

---

## Troubleshooting

**`ERR_EXE` during upload** — Binary signature mismatch. Use `make_exe.py` to convert the raw binary.

**`elf.h: No such file or directory`** — Follow Step 4 above to add `elf.h` to w64devkit.

**`gcc` not found** — Add `D:\w64devkit\bin` to PATH before running make.

**Bootloader not responding** — Reset the board and run the upload script immediately after.

---

## Credits
- [jimmyw/tang_nano_9k_neorv32](https://github.com/jimmyw/tang_nano_9k_neorv32) — Original project
- [stnolting/neorv32](https://github.com/stnolting/neorv32) — NEORV32 RISC-V Processor
