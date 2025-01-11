import socket

from UDPServer import UDPServer

# Test UDP server
server = UDPServer(7777, 9999)
server()

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(('192.168.56.1', 7779))
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.settimeout(10)
client.settimeout(2)  # Optional: 5 seconds timeout, can remove if you don't want a timeout
print("Client listening on port 7779...")
while True:
    try:
        # Receive data from the server (the broadcast)
        data, address = client.recvfrom(1024)  # Buffer size: 1024 bytes
        print(f"Received offer from {address}: {data}")
    except socket.timeout:
        print("No offers received within the timeout period.")
        break
