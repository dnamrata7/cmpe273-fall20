# Class Project

You will be buliding a distributed key-value datastore using ZeroMQ as transport protocol.

[ Node-0 ] 
[ Node-1 ]
[ Node-2 ]
[ Node-3 ]

### Cluster Adjustment

- Add Node-4


- Remove Node-0 


_How to launch server cluster_

> Format: python server_consumer.py {num_node}

```
pipenv run python server_consumer.py 4
```

_How to run client_

> Format: python client_producer.py {num_node}

```
pipenv run python client_producer.py 4
```
## Phase 1

The scope of phase 1 is to shard (PUT) the data into a list of servers. No retrieval is required.

### Consistent hashing


### HRW hashing

## Phase 2

In the phase 2, you will be adding retrieval GET by Id/key and GET all operations in both client and server sides. In addtion, the PUT method will get modified to work with new interface.

### PUT

_JSON Request Payload_

```json
{
    "op": "PUT",
    "key": "key",
    "value": "value"
}
```


### GET by key

_JSON Request Payload_

```json
{
    "op": "GET_ONE",
    "key": "key"
}
```

_JSON Response Payload_

```json
{
    "key": "key",
    "value": "value"
}
```

### GET All

_JSON Request Payload_

```json
{
    "op": "GET_ALL",
}
```

_JSON Response Payload_

```json
{
    "collection": [
        {
            "key": "key1",
            "value": "value1"
        },
        {
            "key": "key2",
            "value": "value2"
        }
    ]
}
```

### Cluster Membership

In order to dynamically control the node membership, your system will integrate with [Consul](https://www.consul.io/).

In the phase 1, we collected cluster size from the command line and mapped to nodes using this scheme of 

```python
server_port = "200{}".format(each_server)
```

In the phase 2, both client and server will no longer read the initial cluster size from the command line. Instead, you will be 
loading from Consul.

First, each node will be registered to the membership in Consul during the server boot up. Upon the server shut down, the node will be 
removed from the membership.

Similarly on the client side, you will first lookup the membership from Consul and then the data will be sharded across different nodes.

### Cluster Adjustment

Adding and removing nodes will be supported in the consistent hashing mode only and node rebalancing--moving data from one node to another--will 
be handled on the client side by sending the _remove_ and _add_ signals to Consul. 

_Steps to remove node_

- Pick a node to be removed.
- Re-balance data to the other nodes.
- After removal is done, send _remove_ signal to Consul.

_Steps to add node_

- Send _add_ signal to Consul.
- Server will get a push notification about the membership changes.
- Launch a new server process based on the node information given by Consul.
- Re-balance existing data to the new node.

### Steps for running the application
1. Initialize consul server agent using command line.
2. Add initial cluster size in key value store of master agent using key cluster_size.
3. Run server_consumer program
4. Wait till all the servers specified as per cluster_size are running
5. Run client_producer program

