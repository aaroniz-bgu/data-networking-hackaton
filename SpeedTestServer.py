import time

from AbstractServer import AbstractServer
from TCPServer import TCPServer
from UDPServer import UDPServer
from concurrent import futures

PENDING = 0
RUNNING = 1
STOPPED = 2


class SpeedTestServer(AbstractServer):
    def __init__(self, ip: str, udp_port: int, tcp_port: int,
                 mask: str, broadcast_port: int, workers: int = 4):
        """
        The API to work with the speed test server.

        This server has two channels, TCP and UDP. The UDP is broadcasting and can handle clients too.

        The server manages a total of `tcp_workers` + 3 threads. Where 2 threads are for the UDP and 1 is for the TCP.

        :param ip: Server IP address
        :param udp_port: Port fot the UDP Channel
        :param tcp_port: Port fot the TCP Channel
        :param mask: Subnet mask for the broadcasting feature
        :param broadcast_port: The port which clients must listen to in-order to receive offers
        :param tcp_workers: How many TCP workers to use to handle clients
        """
        super().__init__()
        self._ip = ip
        self._udp_port = udp_port
        self._tcp_port = tcp_port
        self.executor = futures.ThreadPoolExecutor(max_workers=workers)

        self.udp_server = UDPServer(ip, udp_port, tcp_port, mask, broadcast_port, self.executor)
        self.tcp_server = TCPServer(ip, tcp_port, self.executor)

        self.started = False

    def __call__(self, *args, **kwargs):
        self.start()

    def start(self):
        if self.started:
            return

        self.udp_server.start()
        self.tcp_server.start()
        self.started = True

    def serve(self):
        """
        No reason to call this function here.
        """
        self.start()

    def stop(self):
        self.udp_server.stop()
        self.tcp_server.stop()
        print("Server stopped.")
        # We're not resetting self.started since this is a one-time use object


if __name__ == '__main__':
    _ip = input("Server IP address: ")
    _udp_port = int(input("Server UDP port (must be unique and <=2^16): "))
    _tcp_port = int(input("Server TCP port (must be unique and <=2^16): "))
    _mask = input("Subnet mask for the broadcasting feature (Must): ")
    _broadcast_port = int(input("Broadcast port (which will be used by listening clients): "))
    _workers = int(input("How many workers to use to handle clients for each channel?: "))

    server = SpeedTestServer(_ip, _udp_port, _tcp_port, _mask, _broadcast_port, _workers)
    # server = SpeedTestServer('172.20.10.11', 7777,7778,'255.255.255.240', 7779)
    state = PENDING
    # server()
    # time.sleep(5)
    # server.stop()

    while state != STOPPED:
        if state == PENDING and input("Do you want to start server? (Y/N): ").lower() == 'y':
            server()
            print("TYPE \'q\' to stop the server.")
        elif state == RUNNING and input().lower() == 'q':
            server.stop()
            state = STOPPED
