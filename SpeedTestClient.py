import socket
import threading

class SpeedTestClient(object):
    def __init__(self, available_tcp_connections: int, available_udp_connections: int,
                 file_size: int, initial_port: int):
        self.available_tcp_connections = available_tcp_connections
        self.available_udp_connections = available_udp_connections
        self.tcp_threads = []
        self.udp_threads = []
        self.file_size = file_size
        self.initial_port = initial_port
        return

    def search_offers(self, listen_port: int):
        """Listen for UDP broadcast offers and parse them."""
        try:
            offer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            offer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            offer_socket.bind(('', listen_port))

            data, address = offer_socket.recvfrom(BUFFER_SIZE)

        except Exception as e:
            print(f"Failed to bind UDP socket on {listen_ip}:{listen_port}: {e}")
        return
