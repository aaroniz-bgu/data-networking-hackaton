# Team Latency Zero
This project is our solution for the 2025, Data Networking Introductory course at the Ben Gurion University of the Negev.

This project is a weird implementation of a speed test done with a server which is implemented with both UDP and TCP. Clients receive offers to connect to the server through UDP broadcast. Clients listen on UDP sockets and search for servers, once a client have "accepted" an offer they connect via TCP/UDP to the server and perform the speed test. Clients also decide on the number of allowed connection they can make with each protocol.

### Team 
1. **Aaron Iziyaev**
2. **Adam Rammal** 

## Documentation
### AbstractServer.py
Contains the interface of the server internally. The server has three implementations for this class:
`UDPServer.py`, `TCPServer.py` and `SpeedTestServer.py`. Each has its own responsibility.

To be more specific, `SpeedTestServer.py` is just a wrapper which has two instances of `UDPServer.py` and `TCPServer.py`. It is delegating the work to those instances, and just provides a neat and concise interface to work with from the programmers side.

The API provided by this class is:
```python
def start(self):
    pass
def serve(self):
    pass
def stop(self):
    pass
```

### UDPServer.py
Let us first discover what are the requirements for the UDP server:
1. Broadcast offers every second on the broadcast IP address.
2. Receive requests to connect through UDP, if there are any such requests.

Notice that there are two concurrent missions that the UDP server must fulfill. To solve this issue, we will use two threads, one is for handling clients and connections and another one to send out messages as well as offers.
```python
import threading

clients_thread = threading.Thread(target=self.serve, name='clients_thread')
offer_thread = threading.Thread(target=self.send_offer, name='offer_thread')
```

### TCPServer.py