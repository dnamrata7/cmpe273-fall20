import zmq

# Setup ZMQ sockets.
context = zmq.Context()
sock_in = context.socket(zmq.PULL)
sock_in.connect("tcp://127.0.0.1:1234") #IP for worker
sock_out = context.socket(zmq.PUSH)
sock_out.connect("tcp://127.0.0.1:5558") # IP of dashboard

while True:
    num = int(sock_in.recv())
    square_root = num**0.5
    result={'num':num, 'square_root' : square_root}
    sock_out.send_json(result)
    print("Calculating & sending square root of number %d " % (num))