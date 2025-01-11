from constants import COOKIE, OFFER_MSG, REQUEST_MSG, RESPONSE_MSG
from AbstractServer import AbstractServer
import threading
import socket
import struct
import time

BROADCAST_IP = '255.255.255.255'


class UDPServer(AbstractServer):
    def __init__(self, port, tcp_port):
        # Ip, ports. (the tcp port is here for the offer packet)
        self.port = port
        self.tcp_port = tcp_port

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
        self.running = False
        self.offer_thread.join()
        self.clients_thread.join()
        self.server_socket.close()

    # This function will run in its own thread.
    def send_offer(self):
        """
        Send offer message, and calls self.send() which sends everyone their messages.
        """
        offer_packet = struct.pack('!IBHH', COOKIE, OFFER_MSG, self.port, self.tcp_port)
        while self.running:
            self.server_socket.sendto(offer_packet, (BROADCAST_IP, self.port))
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
        segments = file_size // 1011 + 1
        for i in range(segments):
            payload = struct.pack('!IBQQ', COOKIE, RESPONSE_MSG, segments - 1, i) + b"A" * 1011
            self.server_socket.sendto(payload, address)

    def serve(self):
        """
        Runs on the IO Thread
        The main server loop.
        """
        self.server_socket.bind(('', self.port))

        while self.running:
            # Get packets
            data, address = self.server_socket.recvfrom(1024)
            self.handle(data, address)

        # When server is closed, close the socket:
        self.server_socket.close()

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
