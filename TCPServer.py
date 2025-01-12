from constants import COOKIE, OFFER_MSG
from AbstractServer import AbstractServer
import threading
import socket
import struct
import queue
import time

class TCPServer(AbstractServer):
    def __init__(self, host: str, port: int):
        self.host = host  # IP address of the server
        self.port = port  # Port number for the TCP server
        self.server_socket = None
        self.running = False

    def start(self):
        """Initialize and start the server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen(5)
        print(f"Server started, listening on IP address {self.host}")
    def serve(self):
        """Main loop for accepting client connections."""
        self.running = True
        print("Server is now serving...")
        while self.running:
            try:
                # Accept a client connection
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection received from {client_address}")

                # Start a new thread to handle the client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            except Exception as e:
                if not self.running:
                    break  # Exit loop if the server is stopping
                print(f"Error accepting connection: {e}")
