import zmq
import time
import sys
from itertools import cycle
from consistent_hashing import ConsistentHashing
from hrw import HRWHashing
import consul
import docker

# intializations
docker_client = docker.from_env()
cst_hash = ConsistentHashing() 
hrw_hash = HRWHashing() 
c=consul.Consul(host='0.0.0.0', dc ='dc1')                           # accessing local consul instance

producers = {}

def create_clients(servers):
    context = zmq.Context()
    for server in servers:
        #print(f"Creating a server connection to {server}...")
        producer_conn = context.socket(zmq.REQ)
        producer_conn.bind(server)
        producers[server] = producer_conn
    return producers


def generate_data_round_robin(servers):
    print("Starting processing using round robin...")
    producers = create_clients(servers)
    pool = cycle(producers.values())
    for num in range(10):
        data = {'op':'PUT', 'key': f'key-{num}', 'value': f'value-{num}' }
        print(f"Sending data:{data}")
        current = next(pool)
        current.send_json(data)
        response=current.recv_json()
        time.sleep(1)
    print("Done")


def generate_data_consistent_hashing(servers):
    print("Starting processing using Consistent hashing...")

    if(len(servers) <= 0):
        print("ERROR : No server nodes present")
        return

    producers = create_clients(servers)
   
    
    for server in servers:
        cst_hash.add_node(server)

    for num in range(10):
        data = {'op':'PUT', 'key': f'key-{num}', 'value': f'value-{num}' }
        print(f"Sending data:{data}")
        producers[cst_hash.get_node(str(data))].send_json(data)
        response=producers[cst_hash.get_node(str(data))].recv_json()
        time.sleep(1)
    print("Done")
    
def generate_data_hrw_hashing(servers):
    print("Starting processing using HRW hashing...")
   
    if(len(servers) <= 0):
        print("ERROR : No server nodes present")
        return

    producers = create_clients(servers)

    for server in servers:
        hrw_hash.add_node(server)

    for num in range(10):
        data = {'op':'PUT', 'key': f'key-{num}', 'value': f'value-{num}' }
        print(f"Sending data:{data}")
        producers[hrw_hash.get_node(str(data))].send_json(data)
        response=producers[hrw_hash.get_node(str(data))].recv_json()
        time.sleep(1)
    print("Done")
    

# def add_node():


def remove_node(node_addr,node_name): 
    server = cst_hash.remove_node(node_addr)
    deleteted_server_data = perform_get_all_by_server(server)['collection']
    for item in deleteted_server_data:
        data = {'op':'PUT', 'key': item['key'], 'value': item['value'] }
        producers[cst_hash.get_node(str(data))].send_json()
        response = producers[cst_hash.get_node(str(data))].recv_json()
    c.agent.force_leave(node_name)

    

############ GET functionality for consitent hashing and HRW hashing #############
def perform_get_by_key_hrw(key,servers):
    data = {'op':'GET_ONE','key':key}
    producers = create_clients(servers)
    producers[hrw_hash.get_node(str(data))].send_json(data)
    response_data = producers[hrw_hash.get_node(str(data))].recv_json()
    print(response_data)

def perform_get_all(servers):
    data = {'op':'GET_ALL'}
    response_data = {}
    producers = create_clients(servers)
    for server in servers:
        producers[server].send_json(data)
        response_data.append(producers[server].recv_json())
    print(response_data)

def perform_get_all_by_server(index_server):
    data = {'op':'GET_ALL'}
    response_data = {}
    #producers = create_clients(servers)
    producers[index_server].send_json(data)
    response_data = producers[index_server].recv_json()
    return(response_data)

def perform_get_by_key_cst(key,servers):
    data = {'op':'GET_ONE','key':key}
    producers = create_clients(servers)
    producers[cst_hash.get_node(str(data))].send_json(data)
    response_data = producers[cst_hash.get_node(str(data))].recv_json()
    print(response_data)






if __name__ == "__main__":
    servers = []
    # num_server = 1
    # if len(sys.argv) > 1:
    #     num_server = int(sys.argv[1])
    #     print(f"num_server={num_server}")
        
    # for each_server in range(num_server):
    #     server_port = "200{}".format(each_server)
    #     servers.append(f'tcp://127.0.0.1:{server_port}')

    
   
    
    # getting all members in the cluster
    members = c.agent.members()
    cnt = 101

    for each_member in members:
        port = each_member['Port'] + cnt
        address = each_member['Addr']
        servers.append(f'tcp://127.0.0.1:{port}')
        cnt+=101
    
    generate_data_round_robin(servers)
    producers.clear()

    generate_data_consistent_hashing(servers)
    producers.clear()
    
    generate_data_hrw_hashing(servers)
    producers.clear()
    
    print('###########################################################')
    print("Get by key HRW test")
    perform_get_by_key_hrw('key-2',servers)
    producers.clear()

    print("Get by key Consistent hashing test")
    perform_get_by_key_cst('key-4',servers)
    producers.clear()

    print("Get all test")
    perform_get_all(servers)
    producers.clear()


