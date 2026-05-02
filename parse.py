import re

with open("dump.txt", "r") as f:
    lines = f.readlines()

current_packet = []
packet_time = ""
for line in lines:
    if line.startswith("1"): # Timestamp line like 14:43:48.882565 IP ...
        if current_packet:
            # Reconstruct payload
            hex_str = "".join(current_packet)
            # UDP payload starts at offset 28 bytes (56 hex chars)
            payload = hex_str[56:]
            print(f"{packet_time} Payload (len {len(payload)//2}): {payload}")
            current_packet = []
        packet_time = line.split(" ")[0]
    elif line.startswith("	0x"): # Hex line like "\t0x0000:  4500 007c ..."
        parts = line.strip().split(" ")
        for part in parts[1:]:
            if re.match(r"^[0-9a-fA-F]{4}$", part):
                current_packet.append(part)

if current_packet:
    hex_str = "".join(current_packet)
    payload = hex_str[56:]
    print(f"{packet_time} Payload (len {len(payload)//2}): {payload}")
