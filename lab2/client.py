import zmq
import sys

# ZeroMQ Context
context = zmq.Context()

# Define the socket using the "Context"
sock = context.socket(zmq.REQ)
sock.connect("tcp://127.0.0.1:1234")

# Send a "message" using the socket
sock.send("Hello".encode())
print(sock.recv().decode())