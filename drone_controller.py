import socket
import time
import struct

DRONE_IP = "192.168.169.1"
DRONE_PORT = 8800

def create_control_packet(seq_num):
    # Base 88-byte control packet extracted from the pcap logs
    # Joystick values are idle (Roll: 128, Pitch: 128, Yaw: 129, Throttle: 64)
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
    # 4-byte stop sequence extracted from the end of the logs
    return bytes.fromhex("ef000400")

def main():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"Connecting to Drone at {DRONE_IP}:{DRONE_PORT}...")
    seq_num = 1950 # Start sequence number
    
    try:
        # Start the drone and keep connection alive for 5 seconds
        print("Sending start/control commands...")
        for _ in range(150): # ~30 packets a second = 5 seconds
            packet = create_control_packet(seq_num)
            sock.sendto(packet, (DRONE_IP, DRONE_PORT))
            seq_num += 1
            time.sleep(0.03) # 30ms delay between packets
            
        print("Stopping drone...")
        # Send the stop packets
        for _ in range(5):
            sock.sendto(create_stop_packet(), (DRONE_IP, DRONE_PORT))
            time.sleep(0.1)
            
        print("Done.")
        
    except KeyboardInterrupt:
        print("\nInterrupted, stopping drone...")
        # Ensure we send the stop packet if the user cancels the script (Ctrl+C)
        for _ in range(5):
            sock.sendto(create_stop_packet(), (DRONE_IP, DRONE_PORT))

if __name__ == "__main__":
    main()
