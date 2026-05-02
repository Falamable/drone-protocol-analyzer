import socket
import time
import struct

DRONE_IP = "192.168.169.1"
DRONE_PORT = 8800

def set_joysticks(packet, roll=128, pitch=128, yaw=129, throttle_flags=0x40):
    # Set the joystick/flag bytes
    packet[20] = roll
    packet[21] = pitch
    packet[22] = yaw
    packet[23] = throttle_flags
    
    # The drone requires a checksum at byte 24
    # Checksum formula: (Roll ^ Pitch ^ Yaw ^ ThrottleFlags) ^ 0x80
    checksum = (roll ^ pitch ^ yaw ^ throttle_flags) ^ 0x80
    packet[24] = checksum

def create_control_packet(seq_num):
    # Base 88-byte control packet
    base_hex = (
        "ef025800020200010000000000000000" # Bytes 0-15 (Seq num will go in bytes 12-15)
        "08006680808081404199000000000000" # Bytes 16-31 (Joystick values at 20-23)
        "00000000000000000000000000000000" # Bytes 32-47
        "00000000000000000000000000000000" # Bytes 48-63
        "00000000000000000000000000000000" # Bytes 64-79
        "324b142d0000"                     # Bytes 80-87
    )
    packet = bytearray.fromhex(base_hex)
    
    # Update the sequence number (4 bytes, little-endian)
    packet[12:16] = struct.pack("<I", seq_num)
    
    return packet

def create_stop_packet():
    # 4-byte stop sequence
    return bytes.fromhex("ef000400")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Connecting to Drone at {DRONE_IP}:{DRONE_PORT}...")
    seq_num = 1950 
    
    try:
        print("1. Connecting... Sending idle commands.")
        for _ in range(30): # 1 second idle
            packet = create_control_packet(seq_num)
            set_joysticks(packet, 128, 128, 129, 0x40) # 0x40 is Idle
            sock.sendto(packet, (DRONE_IP, DRONE_PORT))
            seq_num += 1
            time.sleep(0.03)
            
        print("2. Sending UNLOCK/ARM command...")
        for _ in range(20): # ~0.6 seconds unlock
            packet = create_control_packet(seq_num)
            set_joysticks(packet, 128, 128, 129, 0x41) # 0x41 is the Unlock/Arm flag!
            sock.sendto(packet, (DRONE_IP, DRONE_PORT))
            seq_num += 1
            time.sleep(0.03)

        print("3. Motors should spin slowly. Waiting...")
        for _ in range(100): # ~3 seconds idle
            packet = create_control_packet(seq_num)
            set_joysticks(packet, 128, 128, 129, 0x40) # Back to idle
            sock.sendto(packet, (DRONE_IP, DRONE_PORT))
            seq_num += 1
            time.sleep(0.03)
            
        print("4. Sending TAKEOFF command...")
        for _ in range(35): # ~1 second takeoff command
            packet = create_control_packet(seq_num)
            set_joysticks(packet, 128, 128, 129, 0x42) # 0x42 is the Takeoff flag!
            sock.sendto(packet, (DRONE_IP, DRONE_PORT))
            seq_num += 1
            time.sleep(0.03)

        print("5. Drone should be hovering! Holding steady...")
        for _ in range(150): # ~4.5 seconds hovering
            packet = create_control_packet(seq_num)
            set_joysticks(packet, 128, 128, 129, 0x40) # Back to idle
            sock.sendto(packet, (DRONE_IP, DRONE_PORT))
            seq_num += 1
            time.sleep(0.03)
            
        print("Stopping drone...")
        for _ in range(5):
            sock.sendto(create_stop_packet(), (DRONE_IP, DRONE_PORT))
            time.sleep(0.1)
            
        print("Done.")
        
    except KeyboardInterrupt:
        print("\nInterrupted, stopping drone...")
        for _ in range(5):
            sock.sendto(create_stop_packet(), (DRONE_IP, DRONE_PORT))

if __name__ == "__main__":
    main()
