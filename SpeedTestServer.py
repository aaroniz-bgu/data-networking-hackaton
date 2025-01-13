from AbstractServer import AbstractServer
from TCPServer import TCPServer
from UDPServer import UDPServer


class SpeedTestServer(AbstractServer):
    def __init__(self, ip: str, udp_port: int, tcp_port: int,
                 mask: str, broadcast_port: int, tcp_workers: int = 4):
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

        self.udp_server = UDPServer(ip, udp_port, tcp_port, mask, broadcast_port)
        self.tcp_server = TCPServer(ip, tcp_port, tcp_workers)

        self.started = False

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
        # We're not resetting self.started since this is a one-time use object
