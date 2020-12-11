import zmq
import pickle
import threading
import time

class GCounter(object):
    def __init__(self, i, n, zmq_port):
        self.i = i # server id
        self.n = n # number of servers
        self.xs = [0] * n
        self.zmq_port = zmq_port
        # TODO
        # You can assume all servers are running at host tcp://127.0.0.1:xxxx
        # Start a new ZMQ server instance or process.
        self.context = zmq.Context()
        #Using threads for each server
        threading.Thread(target=self._listen_merge_request_from_peer).start()
        

    def query(self):
        return sum(self.xs)

    def add(self, x):
        assert x >= 0
        self.xs[self.i] += x

    def merge(self, c):
        c_xs = c['xs']
        zipped = zip(self.xs, c_xs) 
        self.xs = [max(x, y) for (x, y) in zipped]
    
    def to_dict(self):
        return {
            'i': self.i,
            'n': self.n,
            'xs': self.xs
        }
        
    def _listen_merge_request_from_peer(self):
        # receive merge request from peer.
        # TODO
        sock_in = self.context.socket(zmq.PULL)
        addr = f"tcp://127.0.0.1:{self.zmq_port}"
        sock_in.connect(addr)
        while True:
            c = sock_in.recv_json()
            self.merge(c)

                


    def sync_to_peer(self, zmq_peer_port):
        peer = f"tcp://127.0.0.1:{zmq_peer_port}"
        print(f"Syncing to peer:{peer}")
        # send merge request to peer.
        # TODO
        push_sock = self.context.socket(zmq.PUSH)
        push_sock.bind(peer)
        data_string = self.to_dict()
        push_sock.send_json(data_string)
        time.sleep(1)
        
        