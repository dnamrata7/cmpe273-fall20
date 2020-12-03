import zmq
import sys
from  multiprocessing import Process
import json
import consul
import docker
import time


dataDict ={}
docker_client = docker.from_env()
c=consul.Consul(host='0.0.0.0', dc ='dc1')


def register_with_consul(server_index,port):
    if(server_index==0):
        new_member = c.agent.members()[server_index]
        return(new_member['Name'],str(new_member['Addr']) )
    
    name = 'client-' + str(server_index)
    data_dir = '/tmp/' + name
    cmd = ' consul agent -node={} -retry-join=172.17.0.2 -data-dir={} -http-port={}'.format(name,data_dir,port)
    docker_client.containers.run(image = 'consul', name=name,command=cmd,remove=True,detach=True)
    time.sleep(2)
    new_member = c.agent.members()[server_index]
    return(new_member['Name'],str(new_member['Addr']))


def server(server_addr,port):
    context = zmq.Context()
    consumer = context.socket(zmq.REP)
    consumer.connect(f"tcp://127.0.0.1:{port}") 

    while True:
        raw = consumer.recv_json()
        op = raw['op']
        if op=='PUT':
            consumer.send_json(perform_put(raw))
            key, value =raw['key'], raw['value']
            print(f"Server:{port} key={key},value={value}")
        elif op=='GET_ONE':
            consumer.send_json(perform_get_by_key(raw))
        elif op=='GET_ALL':
            consumer.send_json(perform_get_all())
        else:
            print("Error : Invalid Operation")



def perform_put(request_data):
    # Implementation to store the key-value data on server.
    dataDict[request_data['key']]= request_data['value']
    response_data = {'status':'OK'}
    return response_data
    
def perform_get_by_key(request_data):
    key = request_data['key']
    value = dataDict[key]
    response_data={'key':key , 'value':value}
    return response_data

def perform_get_all():
    data_storage = []
    for key,value in dataDict.items():
        temp_dict = {}
        temp_dict['key'] = key
        temp_dict['value'] = value
        data_storage.append(temp_dict)
    response_data={'collection':data_storage}
    return response_data

if __name__ == "__main__":
    # num_server = 1
    # if len(sys.argv) > 1:
    #     num_server = int(sys.argv[1])
    #     print(f"num_server={num_server}")
        
    # for each_server in range(num_server):
    #     server_port = "200{}".format(each_server)
    #     print(f"Starting a server at:{server_port}...")
    #     Process(target=server, args=(server_port,)).start()
    
    master_data = c.agent.members()

    global num_server
    num_server = len(master_data)
    
    index,data = c.kv.get('cluster_size',index=None)
    cluster_size = int(data['Value'])
    print("Cluster size : ", cluster_size)

    cluster_addr = master_data[0]['Addr']
    master_port=master_data[0]['Port']
    cnt = 101

    for each_server in range(cluster_size):
        name, server_addr = register_with_consul(each_server,master_port+cnt)
        print("Starting node:{} at {}:{}...".format(name,server_addr,master_port+cnt))
        Process(target=server, args=(server_addr,master_port+cnt)).start()
        cnt += 101

    members_data = c.agent.members()

    # to keep checking the changes in membership
    while True: 
        if(num_server < len(members_data)):
            new_server_addr = members_data[num_server]['Addr']
            Process(target=server, args=(new_server_addr,master_port)).start()
            num_server = num_server + 1
        time.sleep(10)
  
    
    # num_server= int(c.kv.get('num_server'))
    # #num_server=int(members[0]['Tags']['expect'])
    # master_port=members[0]['Port']
    # master_address=members[0]['Addr']
    # master_dc = members[0]['Tags']['dc']

    # for each_server in range(num_server):
    #     #name = 'node' + str(each_server)
    #     port= master_port + each_server
    #     #c.agent.service.register(name=name,port=port,address=master_address)
    #     print(f"Starting a server at {master_address}:{port}...")
    #     Process(target=server, args=(port,each_server)).start()
        
    



    
   