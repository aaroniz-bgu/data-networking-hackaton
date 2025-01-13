from constants import COOKIE, OFFER_MSG, REQUEST_MSG, RESPONSE_MSG, BUFFER_SIZE
from AbstractServer import AbstractServer
import ipaddress
import threading
import socket
import struct
import time


def get_broadcast_ip(ip, subnet_mask):
    """
    To have a nice method to get the broadcast ip
    """
    network = ipaddress.IPv4Network(f"{ip}/{subnet_mask}", strict=False)
    return str(network.broadcast_address)


class UDPServer(AbstractServer):
    def __init__(self, ip: str, port: int, tcp_port: int, subnet_mask: str, broadcast_port: int):
        # Ips, ports. (the tcp port is here for the offer packet)
        self.ip = ip
        self.port = port
        self.tcp_port = tcp_port
        self.broadcast_port = broadcast_port
        self.broadcast_ip = get_broadcast_ip(ip, subnet_mask)

        # Creating the socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Multithreading & it's utils
        self.clients_thread = threading.Thread(target=self.serve, name='clients_thread')
        self.offer_thread = threading.Thread(target=self.send_offer, name='offer_thread')
        self.running = False

    def __call__(self, *args, **kwargs):
        self.start()

    def stop(self):
        """
        Stops the UDP server gracefully.
        """
        if not self.running:
            return

        self.running = False

        if not self.running:
            self.server_socket.close()

        self.offer_thread.join()
        self.clients_thread.join()

    # This function will run in its own thread.
    def send_offer(self):
        """
        Send offer message, and calls self.send() which sends everyone their messages.
        """
        offer_packet = struct.pack('!IBHH', COOKIE, OFFER_MSG, self.port, self.tcp_port)
        while self.running:
            self.server_socket.sendto(offer_packet, (self.broadcast_ip, self.broadcast_port))
            print('Sent offer message')
            time.sleep(1)

    def handle(self, unpacked_data, address):
        if len(unpacked_data) != 13:
            return

        # Do the unpacking of the packet:
        data = struct.unpack('!IBQ', unpacked_data)

        if data[0] != COOKIE or data[1] != REQUEST_MSG:
            print(f'Illegal request from {address[0]}:{address[1]}')
            return

        file_size = data[2]
        # each payload packet had 13 bytes for the protocol
        limit = BUFFER_SIZE - 13 + 1
        segments = file_size // limit
        for i in range(segments):
            payload = struct.pack('!IBQQ', COOKIE, RESPONSE_MSG, segments - 1, i) + b"A" * 1011
            self.server_socket.sendto(payload, address)

    def serve(self):
        """
        Runs on the IO Thread
        The main server loop.
        """
        self.server_socket.bind((self.ip, self.port))

        try:
            while self.running:
                # Get packets
                data, address = self.server_socket.recvfrom(BUFFER_SIZE)
                self.handle(data, address)
        except Exception as e:
            print(f'UDP Channel faced an error:\n{e}')
        finally:
            self.stop()

    def start(self):
        """
        Starts the server in its entirety.
        Creates IO and Offer threads.
        """
        self.running = True

        # Start the IO Thread
        self.clients_thread.start()

        time.sleep(5)

        # Start offer thread
        self.offer_thread.start()

        print(f'Server started, listening on IP address {self.server_socket.getsockname()[0]}')
