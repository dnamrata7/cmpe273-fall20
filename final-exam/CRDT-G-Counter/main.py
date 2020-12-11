from gcounter import GCounter

def run():
    a = GCounter(0, 2, 2000)
    b = GCounter(1, 2, 3000)
    
    print(f"a-GCounter:query={a.query()}")
    a.add(1)
    print(f"a-GCounter:query={a.query()}")
    
    print(f"b-GCounter:query={b.query()}")
    b.add(2)
    print(f"b-GCounter:query={b.query()}")
    
    print(f"a-GCounter:{a.to_dict()}")
    print(f"b-GCounter:{b.to_dict()}")
    b.sync_to_peer(a.zmq_port)
    print(f"a-GCounter:{a.to_dict()}")
    print(f"b-GCounter:{b.to_dict()}")
    
    print(f"a-GCounter:query={a.query()}")
    
    b.add(4)
    print(f"b-GCounter:query={b.query()}")
    
    print(f"a-GCounter:{a.to_dict()}")
    print(f"b-GCounter:{b.to_dict()}")
   
    a.sync_to_peer(b.zmq_port)
    print(f"a-GCounter:{a.to_dict()}")
    print(f"b-GCounter:{b.to_dict()}")
    
    print(f"b-GCounter:query={b.query()}")
    

    
if __name__ == "__main__":
    run()