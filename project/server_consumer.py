import zmq
import sys
from  multiprocessing import Process

def server(port):
    context = zmq.Context()
    consumer = context.socket(zmq.PULL)
    consumer.connect(f"tcp://127.0.0.1:{port}")
    
    while True:
        raw = consumer.recv_json()
        key, value = raw['key'], raw['value']
        print(f"Server_port={port}:key={key},value={value}")
        # FIXME: Implement to store the key-value data.
        
        
if __name__ == "__main__":
    num_server = 1
    if len(sys.argv) > 1:
        num_server = int(sys.argv[1])
        print(f"num_server={num_server}")
        
    for each_server in range(num_server):
        server_port = "200{}".format(each_server)
        print(f"Starting a server at:{server_port}...")
        Process(target=server, args=(server_port,)).start()
    