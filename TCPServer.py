from AbstractServer import AbstractServer
from constants import BUFFER_SIZE
import threading
import socket


class TCPServer(AbstractServer):
    def __init__(self, host: str, port: int, executor):
        """
        :param host: server ip
        :param port: server port
        :param max_workers: the number of workers, defaults to 1. The number of threads created by this server will be
        at most max_workers + 1.
        """
        self.host = host  # IP address of the server
        self.port = port  # Port number for the TCP server
        self.server_socket = None
        self.server_thread = threading.Thread(target=self.serve, name="tcp_thread")
        self.executor = executor
        self.running = False

    def __call__(self, *args, **kwargs):
        self.start()

    def start(self):
        """Initialize and start the server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        self.server_thread.start()
        print(f"TCP Channel: started, listening on IP address {self.host}")

    def serve(self):
        """Main loop for accepting client connections."""
        print(f"Server is now serving...")
        while self.running:
            try:
                # Accept a client connection
                client_socket, client_address = self.server_socket.accept()

                # Start a new thread to handle the client
                self.executor.submit(self.handle_client, client_socket, client_address)

            except Exception as e:
                if not self.running:
                    break  # Exit loop if the server is stopping
                print(f"TCP Channel: error accepting connection: {e}")

    def handle_client(self, client_socket, client_address):
        print(f"TCP Channel: connection received from {client_address}")
        """Handle a single client connection."""
        try:
            # Receive request from the client
            data = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
            if not data.isdigit() or int(data) <= 0:
                print(f"TCP Channel: invalid file size received from {client_address}: {data}")
                client_socket.sendall(b"Invalid file size\n")
                return

            # Compute the file
            file_size = int(data)
            file = "A" * file_size
            # Send to client
            client_socket.sendall(file.encode('utf-8'))

        except Exception as e:
            print(f"TCP Channel: error handling client: {e}")
        finally:
            # Step 4: Close the connection
            client_socket.close()
            print(f"TCP Channel: connection closed for {client_address}.")

    def stop(self):
        """Stop the server."""
        if not self.running:
            return

        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.executor.shutdown(wait=True)
