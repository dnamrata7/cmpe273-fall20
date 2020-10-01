import zmq

# Setup ZMQ socket.
context = zmq.Context()
sock = context.socket(zmq.PULL)
sock.bind("tcp://127.0.0.1:5558")

# Display the square root results
while True:
    result = sock.recv_json()
    num=int(result['num'])
    square_root = float(result['square_root'])
    print("Square root of number %d = %f" % (num,square_root))
