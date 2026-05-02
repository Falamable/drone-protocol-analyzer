import re

with open("dump.txt", "r") as f:
    lines = f.readlines()

current_packet = []
packet_time = ""
packets = []
for line in lines:
    if line.startswith("1"):
        if current_packet:
            hex_str = "".join(current_packet)
            payload = hex_str[56:]
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
    payload = hex_str[56:]
    packets.append((packet_time, payload))

# Let's count unique lengths and maybe diff the packets
import collections
counts = collections.defaultdict(int)
for t, p in packets:
    counts[len(p)//2] += 1

print(f"Total packets: {len(packets)}")
print(f"Lengths: {dict(counts)}")

print("First few packets:")
for i in range(10):
    if i < len(packets):
        print(f"{packets[i][0]}: {packets[i][1]}")

print("Last few packets:")
for i in range(max(0, len(packets)-10), len(packets)):
    print(f"{packets[i][0]}: {packets[i][1]}")

