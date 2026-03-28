import struct
import sys

# Eski NEORV32 bootloader formatı: 0x4788CAFE signature
# Header: [signature 4B] [size 4B] [checksum 4B] [data ...]

def make_exe(raw_bin_path, output_path):
    with open(raw_bin_path, 'rb') as f:
        data = f.read()

    # 4 byte'a hizala
    while len(data) % 4 != 0:
        data += b'\x00'

    size = len(data)
    signature = 0x4788CAFE

    # Checksum hesapla (32-bit word toplamı, complement)
    checksum = 0
    for i in range(0, size, 4):
        word = struct.unpack_from('<I', data, i)[0]
        checksum = (checksum + word) & 0xFFFFFFFF
    checksum = ((~checksum) + 1) & 0xFFFFFFFF

    # Header + data yaz
    with open(output_path, 'wb') as f:
        f.write(struct.pack('<I', signature))
        f.write(struct.pack('<I', size))
        f.write(struct.pack('<I', checksum))
        f.write(data)

    print(f"Done! {output_path}")
    print(f"  Size:     {size} bytes")
    print(f"  Checksum: 0x{checksum:08X}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python make_exe.py <neorv32_raw_exe.bin> <neorv32_exe.bin>")
        sys.exit(1)
    make_exe(sys.argv[1], sys.argv[2])
