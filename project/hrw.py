import hashlib

def get_hash_value(key):
    hash = hashlib.md5()
    hash.update(bytes(key.encode('utf-8')))
    return int(hash.hexdigest(), 16) 
        
# Weight function referred from paper introducing HRW hashing : http://www.eecs.umich.edu/techreports/cse/96/CSE-TR-316-96.pdf
def get_weight(node, key):
    a = 1103515245
    b = 12345
    key_hash = get_hash_value(key)
    node_hash = get_hash_value(node)
    return (a * ((a * node_hash + b) ^ key_hash) + b) % (2**31)

class HRWHashing:

    def __init__(self, nodes=None):
        node_list = nodes or {}
        self.nodes = set(node_list)

    def add_node(self, node):
        self.nodes.add(node)

    # returns the node associated with the key
    def get_node(self, key):

        weights = []
        for node in self.nodes:
            weight = get_weight(node, key)
            weights.append((weight, node))

        wt , node = max(weights)                    
        return node
    
    

   