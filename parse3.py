import re
import struct

with open("dump.txt", "r") as f:
    lines = f.readlines()

current_packet = []
packet_time = ""
packets = []
for line in lines:
    if line.startswith("1"):
        if current_packet:
            hex_str = "".join(current_packet)
            payload = bytes.fromhex(hex_str[56:])
            packets.append((packet_time, payload))
            current_packet = []
        packet_time = line.split(" ")[0]
    elif line.startswith("	0x"):
        parts = line.strip().split(" ")
        for part in parts[1:]:
            if re.match(r"^[0-9a-fA-F]{4}$", part):
                current_packet.append(part)

if current_packet:
    hex_str = "".join(current_packet)
    payload = bytes.fromhex(hex_str[56:])
    packets.append((packet_time, payload))

print(f"Total packets: {len(packets)}")

for i in range(0, len(packets), 50):
    p = packets[i][1]
    if len(p) >= 24:
        seq = struct.unpack("<I", p[12:16])[0]
        v1, v2, v3, v4 = p[20:24]
        print(f"{packets[i][0]}: seq={seq}, joy=({v1}, {v2}, {v3}, {v4})")
    else:
        print(f"{packets[i][0]}: short packet {p.hex()}")

