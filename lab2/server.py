import zmq

# ZeroMQ Context
context = zmq.Context()

# Define the socket using the "Context"
sock = context.socket(zmq.REP)
sock.bind("tcp://127.0.0.1:1234")

# Run a simple "Echo" server
while True:
    message = sock.recv()
    message = message.decode()
    reply_msg = "Echo: " + message
    sock.send(reply_msg.encode())
    print(reply_msg)