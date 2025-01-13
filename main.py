import socket
from UDPServer import UDPServer


def client_listener():
    # Create a socket for UDP communication
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the client to a specific port
    client_socket.bind((IP, PORT))
    print(f'{client_socket.getsockname()}')
    while True:
        # Receive data from the server
        data, address = client_socket.recvfrom(1024)
        if data:
            print(f"Received packet from {address}")
            print(f"Data: {data}")


if __name__ == "__main__":
    IP = str(input("Enter IP Address: "))
    SUBNET = str(input("Enter Subnet: "))
    PORT = int(input("Enter Port: "))

    # Test UDP server
    server = UDPServer(IP, 54321, 54322, SUBNET, PORT)
    server()

    # Test:
    client_listener()
