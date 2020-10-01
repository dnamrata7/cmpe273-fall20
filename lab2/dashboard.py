import zmq

# Total number of computations.
total = 10001

# Setup ZMQ socket.
context = zmq.Context()
sock = context.socket(zmq.PULL)
sock.bind("tcp://127.0.0.1:5558")

# Accumulate the results until we know all computations are done.
results = []
num_processed = 0
while num_processed < total:
    root = sock.recv()
    results.append(root)
    num_processed += 1
    print("Square root of number %f" % (root))
