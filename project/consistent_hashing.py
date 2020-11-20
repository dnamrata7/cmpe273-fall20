import hashlib
from bisect import bisect, bisect_left, bisect_right

class ConsistentHashing:
    def __init__(self):
        self.positions = []                 # positions of the nodes in ring or hash space
        self.nodes = []                     # nodes present in the ring. nodes[i] is present at index positions[i]
        self.ring_size = 2**256             # total places in the ring


    def get_hash_value(self,key: str, ring_size: int):
        hash = hashlib.md5()
        hash.update(bytes(key.encode('utf-8')))
        return int(hash.hexdigest(), 16) % ring_size

    # adds new node and returns the position in the ring
    def add_node(self, node):

        # Ring space exhausted
        if len(self.positions) == self.ring_size:
            raise Exception("Ring space is full")

        node_hash = self.get_hash_value(node, self.ring_size)

        # index for the node to be added
        index = bisect(self.positions, node_hash)

        # node already present
        if index > 0 and self.positions[index - 1] == node_hash:
            raise Exception("Collision")

        self.nodes.insert(index, node)
        self.positions.insert(index, node_hash)

        return node_hash
    

    # returns node for given object
    def get_node(self, item: str) -> str:

        key = self.get_hash_value(item, self.ring_size)

        # find the first node to the right of this key in circular manner.
        index = bisect_right(self.positions, key) % len(self.positions)

        # return the node present at the index
        return self.nodes[index]

        
            

    