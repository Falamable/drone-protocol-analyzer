# Reverse-Engineering My Drone: Physics Project 🚁

For my Physics project, I decided to do something a bit different: I reverse-engineered the communication protocol for my DMH002HW drone so I could write my own Python script to fly it!

This project helped me apply the theory I've been learning about **Networks (UDP/IP), Hexadecimal, Binary Data, and Programming** into a real-world scenario. Here's a breakdown of how I did it.

---

## 1. The Goal: Hacking the Drone

Normally, I fly the drone using the official app on my phone. The app sends invisible signals over Wi-Fi to control the drone. 

I wanted to replace the app with my own Python code. But to do that, I needed to intercept those signals and understand the "language" (or protocol) the app was using to speak to the drone.

## 2. The Method: Snooping with Wireshark

To figure out how the app worked, I set up an Android emulator on my PC, installed the official drone app, and connected to the drone's Wi-Fi. Then, I used a tool called **Wireshark** to record all the network traffic between the emulator and the drone. Wireshark acts like a wiretap, logging every single packet sent over the connection.

I saved this recording as a `.pcapng` file. By analyzing this file, I needed to answer three main questions:
1. **Where** is the data going? (IP Address & Port)
2. **How** is the data sent? (Protocol)
3. **What** is the data saying? (Payload)

## 3. The Discovery: Breaking the Code

After staring at a lot of network logs, I started to notice patterns and managed to decode the protocol!

### A. The Address Book (IP & Port)
- **Protocol:** The app uses **UDP** (User Datagram Protocol). In my AS Level syllabus, I learned that UDP is fast and doesn't wait for acknowledgements, unlike TCP. This makes perfect sense for flying a drone, where you need real-time control and zero lag.
- **Destination IP:** The drone acts as its own Wi-Fi router. Its IP address is `192.168.169.1`.
- **Port:** The drone listens for commands on Port `8800`.

### B. The Language (Hexadecimal Payloads)
Computers send data in binary, but Wireshark displays it in **Hexadecimal** (base-16) to make it easier to read. I noticed two main types of packets being sent:

#### 1. The "Start / Fly" Packets (88 bytes long)
While flying, the app sends a massive packet roughly every 30 milliseconds. If I stopped sending them, the drone assumed the connection was lost and hovered safely. 
Here is what the raw hex data looks like inside one of these packets:
```text
ef 02 58 00 02 02 00 01 00 00 00 00 [a6 07 00 00] 08 00 66 80 [80 80 81 40] 41 ... 
```
Here is how I decoded it:
- **`ef 02`**: This is a "magic number". It basically tells the drone, "Hey, this is a control packet!"
- **`58 00`**: The length of the packet (`0x58` in hex is 88 in decimal).
- **`[a6 07 00 00]`**: This is the **Sequence Number**. It increases by 1 for every single packet sent. It helps the drone ignore old, delayed packets.
- **`[80 80 81 40]`**: These are the actual **Joystick Values**! 
  - `0x80` is 128 in decimal. Since a byte goes from 0-255, 128 is the exact middle. This means the Pitch, Roll, and Yaw joysticks are perfectly centered. 
  - `0x40` is 64 in decimal. This represents the Throttle (altitude control) at the zero/idle position.

#### 2. The "Stop" Packets (4 bytes long)
When I closed the app or pressed stop, it sent a tiny 4-byte packet to immediately kill the connection:
```text
ef 00 04 00
```

## 4. The Solution: Writing the Python Script

Now that I knew the IP, the Port, and the exact Hexadecimal codes, I could use Python to build those identical packets and send them over Wi-Fi myself. 

Here is the Python script I wrote. It uses the `socket` library to connect to the drone, sends "idle" control commands for 5 seconds to keep it alive, and then cleanly shuts it down.

```python
import socket
import time
import struct

DRONE_IP = "192.168.169.1"
DRONE_PORT = 8800

def create_control_packet(seq_num):
    # This is the 88-byte hex payload I copied from Wireshark.
    # The joysticks are centered, and throttle is zero.
    base_hex = (
        "ef025800020200010000000000000000" # First 16 bytes
        "08006680808081404199000000000000" # Next 16 bytes (Joysticks are here!)
        "00000000000000000000000000000000" 
        "00000000000000000000000000000000" 
        "00000000000000000000000000000000" 
        "324b142d0000"                     # Last 6 bytes
    )
    # Convert the long string of hex into actual raw bytes
    packet = bytearray.fromhex(base_hex)
    
    # I used the 'struct' library to easily inject my increasing 
    # Sequence Number into bytes 12, 13, 14, and 15 in Little-Endian format.
    packet[12:16] = struct.pack("<I", seq_num)
    
    return packet

def create_stop_packet():
    # The simple 4-byte kill signal
    return bytes.fromhex("ef000400")

def main():
    # Create a UDP network socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"Connecting to Drone at {DRONE_IP}:{DRONE_PORT}...")
    seq_num = 1950 # Start sequence number
    
    try:
        # Send packets rapidly to keep the drone alive for 5 seconds
        print("Sending start/idle commands...")
        for _ in range(150): # 150 packets / 30 per second = 5 seconds
            packet = create_control_packet(seq_num)
            
            # Fire the packet over the Wi-Fi!
            sock.sendto(packet, (DRONE_IP, DRONE_PORT))
            
            seq_num += 1     # Increase the sequence number for the next loop
            time.sleep(0.03) # Wait 30 milliseconds before sending the next one
            
        print("Stopping drone...")
        # Send the kill signal multiple times to ensure it arrives
        for _ in range(5):
            sock.sendto(create_stop_packet(), (DRONE_IP, DRONE_PORT))
            time.sleep(0.1)
            
        print("Done.")
        
    except KeyboardInterrupt:
        print("\nInterrupted! Emergency Stop...")
        for _ in range(5):
            sock.sendto(create_stop_packet(), (DRONE_IP, DRONE_PORT))

if __name__ == "__main__":
    main()
```

### Next Steps for my Project
My next goal is to programatically control the Drone to understand the aero dynomics and flight path!

### Components used

* DHW002HW with Camara module (HW)
* Android Studio and Android Virtual Device Emulator
* WireShark
* Wifi UAV App
* Acer Laptop (HW)
* AntiGraviity

