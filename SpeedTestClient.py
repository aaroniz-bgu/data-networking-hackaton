import threading
import socket
import struct
import time

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

    def __call__(self, *args, **kwargs):
        self.initial_port += 1
        self.search_offers(self.initial_port - 1)

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
                print('All transfers complete, listening to offer requests')

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
        # Helper variables
        con_num = sock_port - self.initial_port + 1

        # Create the socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', sock_port))

        # Connect and send request to host:
        connect_address = (address[0], host_port)
        sock.connect(connect_address)
        sock.send(bytes(f'{self.file_size}\n', "utf-8"))

        # Count time:
        start_time = time.perf_counter()

        # Wait for response:
        buf_size = max(self.file_size, BUFFER_SIZE)
        data = sock.recv(buf_size)
        data = data.decode("utf-8").strip()

        # print statistics:
        total_time = float(time.perf_counter() - start_time)
        speed = float(self.file_size) / total_time
        print(f'TCP Connection #{con_num: .4f} finished, total time: {total_time: .4f}, '
              f'seconds, total speed: {speed: .4f} bps')

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
        # Helper variables
        con_num = sock_port - self.initial_port - self.available_tcp_connections + 1
        recv = 0
        smax = 0

        # Sending the request
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.bind(('', sock_port))
        request = struct.pack('!IBQ', COOKIE, REQUEST_MSG, self.file_size)
        client_socket.sendto(request, address)
        client_socket.settimeout(BUFFER_SIZE // 200)  # for buff size 1024 we wait max of 5 seconds

        # Count the number of segments received, max number of segments possible and the time we started
        start_time = time.perf_counter()

        # Start listening:
        while True:
            # Listen for incoming requests:
            try:
                data, _ = client_socket.recv(BUFFER_SIZE)
            except socket.timeout:
                # if timeout had been reached
                break

            # Unpack data:
            data = struct.unpack('!IBQQ', data)

            if data[0] != COOKIE or data[1] != RESPONSE_MSG:
                continue  # not a valid message

            # Update the smax
            if smax == 0:
                smax = float(data[2])
            recv += 1

            if smax == data[3]:
                break

        if smax == 0:
            smax = float('inf')
        elapsed = time.perf_counter() - start_time
        speed = (float(recv) * float(self.file_size) / smax) / elapsed
        percentage = float(recv) / smax

        print(f'UDP transfer #{con_num: .4f} finished, total time: {elapsed: .4f} seconds, '
              f'total speed: {speed: .4f} bps, percentage of packets received successfully: {percentage: .4f}%')


if __name__ == '__main__':
    tcp_conns = int(input('How many TCP Connections would you like have?: '))
    udp_conns = int(input('How many UDP Connections would you like have?: '))
    init_port = int(input('The initial port which will be given to each connection in sequence: '))
    file_size = int(input('What is the file size you\'d like to receive?: '))

    print('Starting client...')
    client = SpeedTestClient(tcp_conns, udp_conns, file_size, init_port)
    client()
