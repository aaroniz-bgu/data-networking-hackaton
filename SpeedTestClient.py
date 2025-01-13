import socket
import struct
import threading
from constants import *


class SpeedTestClient(object):
    def __init__(self, available_tcp_connections: int, available_udp_connections: int,
                 file_size: int, initial_port: int):
        self.available_tcp_connections = available_tcp_connections
        self.available_udp_connections = available_udp_connections
        self.threads = []
        self.file_size = file_size
        self.initial_port = initial_port
        return

    def search_offers(self, listen_port: int):
        """Listen for UDP broadcast offers and parse them."""
        try:
            offer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            offer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            offer_socket.bind(('', listen_port))

            while True:
                data, address = offer_socket.recvfrom(BUFFER_SIZE)
                # The received data is def not an offer
                if len(data) != 9:
                    continue
                # Use struct to parse the data
                data = struct.unpack('!IBHH', data)
                # Check that the offer is valid:
                if data[0] != COOKIE or data[1] != OFFER_MSG:
                    continue

                # Handle TCP, UDP:
                self.handle_tcp(address, data[3], self.initial_port)
                self.handle_udp(address, data[2], self.initial_port + self.available_tcp_connections)
                # Join all the threads, waiting for data to be received:
                for thread in self.threads:
                    thread.join()
                # Continue...

        except Exception as e:
            print(f"Failed while searching for offers: \n{e}")
        return

    def handle_tcp(self, address, host_port, init_port):
        for i in range(self.available_tcp_connections):
            # Create the threads and start them:
            thread = threading.Thread(target=self.tcp_conn, name=f'tcp_conn{i}',
                                      args=(address, host_port, init_port + i))
            thread.start()
            # So we could join them later.
            self.threads.append(thread)

    def tcp_conn(self, address, host_port, sock_port):
        # Create the socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', sock_port))
        # Connect and send request to host:
        sock.connect((address, host_port))
        sock.send(bytes(f'{self.file_size}\n', "utf-8"))
        # Wait for response:
        data = sock.recv(BUFFER_SIZE)
        data = data.decode("utf-8").strip()
        # Sanity check:
        if len(data) != self.file_size:
            print(f'The file received in {threading.current_thread().name} was smaller than requested')

    def handle_udp(self, address, port, init_port):
        for i in range(self.available_udp_connections):
            thread = threading.Thread(
                target=self.udp_conn,
                name=f'udp_conn{i}',
                args=(address, port, init_port + i)
            )
            thread.start()
            self.threads.append(thread)

    def udp_conn(self, address, port, sock_port):
        pass
