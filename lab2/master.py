import zmq
import time

# Setup ZMQ socket
context = zmq.Context()
sock = context.socket(zmq.PUSH)
sock.bind("tcp://127.0.0.1:1234")


# Iterate over the grid, send each piece of computation to a worker.
for p in range(10001):
    print("sending work p=%d" % (p))
    sock.send(str(p).encode())
    