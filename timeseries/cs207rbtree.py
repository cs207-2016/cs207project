import os
import struct
import portalocker
import pickle

class Storage(object):
    SUPERBLOCK_SIZE = 4096
    INTEGER_FORMAT = "!Q"
    INTEGER_LENGTH = 8

    def __init__(self, f):
        self._f = f
        self.locked = False
        #we ensure that we start in a sector boundary
        self._ensure_superblock()

    def _ensure_superblock(self):
        "guarantee that the next write will start on a sector boundary"
        self.lock()
        self._seek_end()
        end_address = self._f.tell()
        if end_address < self.SUPERBLOCK_SIZE:
            self._f.write(b'\x00' * (self.SUPERBLOCK_SIZE - end_address))
        self.unlock()

    def lock(self):
        "if not locked, lock the file for writing"
        if not self.locked:
            portalocker.lock(self._f, portalocker.LOCK_EX)
            self.locked = True
            return True
        else:
            return False

    def unlock(self):
        if self.locked:
            self._f.flush()
            portalocker.unlock(self._f)
            self.locked = False

    def _seek_end(self):
        self._f.seek(0, os.SEEK_END)

    def _seek_superblock(self):
        "go to beginning of file which is on sec boundary"
        self._f.seek(0)

    def _bytes_to_integer(self, integer_bytes):
        return struct.unpack(self.INTEGER_FORMAT, integer_bytes)[0]

    def _integer_to_bytes(self, integer):
        return struct.pack(self.INTEGER_FORMAT, integer)

    def _read_integer(self):
        return self._bytes_to_integer(self._f.read(self.INTEGER_LENGTH))

    def _write_integer(self, integer):
        self.lock()
        self._f.write(self._integer_to_bytes(integer))

    def write(self, data):
        "write data to disk, returning the adress at which you wrote it"
        #first lock, get to end, get address to return, write size
        #write data, unlock <==WRONG, dont want to unlock here
        #your code here
        self.lock()
        self._seek_end()
        object_address = self._f.tell()
        self._write_integer(len(data))
        self._f.write(data)
        return object_address

    def read(self, address):
        self._f.seek(address)
        length = self._read_integer()
        data = self._f.read(length)
        return data

    def commit_root_address(self, root_address):
        self.lock()
        self._f.flush()
        #make sure you write root address at position 0
        self._seek_superblock()
        #write is atomic because we store the address on a sector boundary.
        self._write_integer(root_address)
        self._f.flush()
        self.unlock()

    def get_root_address(self):
        #read the first integer in the file
        #your code here
        self._seek_superblock()
        root_address = self._read_integer()
        return root_address

    def close(self):
        self.unlock()
        self._f.close()

    @property
    def closed(self):
        return self._f.closed

class DBDB(object):

    def __init__(self, f):
        self._storage = Storage(f)
        self._tree = BinaryTree(self._storage)

    def _assert_not_closed(self):
        if self._storage.closed:
            raise ValueError('Database closed.')

    def close(self):
        self._storage.close()

    def commit(self):
        self._assert_not_closed()
        self._tree.commit()

    def get(self, key):
        self._assert_not_closed()
        return self._tree.get(key)

    def set(self, key, value):
        self._assert_not_closed()
        print(self._tree)
        return self._tree.set(key, value)

    def delete(self, key):
        self._assert_not_closed()
        return self._tree.delete(key)

class ValueRef(object):
    " a reference to a string value on disk"
    def __init__(self, referent=None, address=0):
        self._referent = referent #value to store
        self._address = address #address to store at

    @property
    def address(self):
        return self._address

    def prepare_to_store(self, storage):
        pass

    @staticmethod
    def referent_to_bytes(referent):
        return referent.encode('utf-8')

    @staticmethod
    def bytes_to_referent(bytes):
        return bytes.decode('utf-8')


    def get(self, storage):
        "read bytes for value from disk"
        if self._referent is None and self._address:
            self._referent = self.bytes_to_referent(storage.read(self._address))
        return self._referent

    def store(self, storage):
        "store bytes for value to disk"
        #called by BinaryNode.store_refs
        if self._referent is not None and not self._address:
            self.prepare_to_store(storage)
            self._address = storage.write(self.referent_to_bytes(self._referent))

class BinaryNodeRef(ValueRef):
    "reference to a btree node on disk"

    #calls the BinaryNode's store_refs
    def prepare_to_store(self, storage):
        "have a node store its refs"
        if self._referent:
            self._referent.store_refs(storage)

    @staticmethod
    def referent_to_bytes(referent):
        "use pickle to convert node to bytes"
        return pickle.dumps({
            'left': referent.left_ref.address,
            'key': referent.key,
            'value': referent.value_ref.address,
            'right': referent.right_ref.address,
            'color': referent.color,
        })

    @staticmethod
    def bytes_to_referent(string):
        "unpickle bytes to get a node object"
        d = pickle.loads(string)
        return BinaryNode(
            BinaryNodeRef(address=d['left']),
            d['key'],
            ValueRef(address=d['value']),
            BinaryNodeRef(address=d['right']),
            d['color'],
        )

class BinaryNode(object):
    @classmethod
    def from_node(cls, node, **kwargs):
        "clone a node with some changes from another one"
        return cls(
            left_ref=kwargs.get('left_ref', node.left_ref),
            key=kwargs.get('key', node.key),
            value_ref=kwargs.get('value_ref', node.value_ref),
            right_ref=kwargs.get('right_ref', node.right_ref),
            color=kwargs.get('color', node.color),
            #parent_ref=kwargs.get('parent', node.parent),
        )

    def __init__(self, left_ref, key, value_ref, right_ref, color): #, parent):
        self.left_ref = left_ref
        self.key = key
        self.value_ref = value_ref
        self.right_ref = right_ref
        self.color = color
        #self.parent = parent

    def is_red(self):
        return self.color == Color.RED

    def is_black(self):
        return self.color == Color.BLACK

    def store_refs(self, storage):
        "method for a node to store all of its stuff"
        self.value_ref.store(storage)
        #calls BinaryNodeRef.store. which calls
        #BinaryNodeRef.prepate_to_store
        #which calls this again and recursively stores
        #the whole tree
        self.left_ref.store(storage)
        self.right_ref.store(storage)

class Color(object):
    RED = 0
    BLACK = 1

class BinaryTree(object):
    "Immutable Binary Tree class. Constructs new tree on changes"
    def __init__(self, storage):
        self._storage = storage
        self._refresh_tree_ref()

    def commit(self):
        "changes are final only when committed"
        #triggers BinaryNodeRef.store
        self._tree_ref.store(self._storage)
        #make sure address of new tree is stored
        self._storage.commit_root_address(self._tree_ref.address)

    def _refresh_tree_ref(self):
        "get reference to new tree if it has changed"
        self._tree_ref = BinaryNodeRef(
            address=self._storage.get_root_address())

    def get(self, key):
        "get value for a key"
        #your code here
        #if tree is not locked by another writer
        #refresh the references and get new tree if needed
        if not self._storage.locked:
            self._refresh_tree_ref()
        #get the top level node

        # print (self._tree_ref)
        node = self._follow(self._tree_ref)
        # print (node)
        #traverse until you find appropriate node
        while node is not None:
            if key < node.key:
#                 print("searching left", node.key, key)
                node = self._follow(node.left_ref)
            elif key > node.key:
#                 print("searching right", node.key, key)
                node = self._follow(node.right_ref)
            else:
#                 print(node.key<key)
#                 print(node.key>key)
#                 print(node.key==key)
#                 print("found", node.key, key)
                return self._follow(node.value_ref)
        raise KeyError

    def set(self, key, value):
        "set a new value in the tree. will cause a new tree"
        #try to lock the tree. If we succeed make sure
        #we dont lose updates from any other process
        if self._storage.lock():
            self._refresh_tree_ref()
        #get current top-level node and make a value-ref
        # print ("tree ref, tree", self._tree_ref)
        node = self._follow(self._tree_ref)
        value_ref = ValueRef(value)
        #insert and get new tree ref
        # print (self._tree_ref, node, key, value_ref)
#         self._tree_ref = BinaryNodeRef(referent=self.blacken(self._insert(node, key, value_ref)))
        self._tree_ref = BinaryNodeRef(referent=self.blacken(self._follow(self._insert(node, key, value_ref))))
        # self.printTree()


    def _insert(self, node, key, value_ref):
        # print ("inserting at", node)
        "insert a new node creating a new path from root"
        #create a tree ifnthere was none so far
        if node is None:
            # print ("reached empty node", key, value_ref._referent)
            new_node = BinaryNode(
                BinaryNodeRef(), key, value_ref, BinaryNodeRef(), Color.RED)
#             return self.balance(self._follow(BinaryNodeRef(referent=new_node)))
            return BinaryNodeRef(referent = self.balance(self._follow(BinaryNodeRef(referent=new_node))))
        elif key < node.key:
            # print ("recursively inserting left", self, node.key, key, value_ref._referent)
            new_node = BinaryNode.from_node(
                node,
                left_ref=self._insert(
                    self._follow(node.left_ref), key, value_ref))
#             return BinaryNodeRef(referent = self.blacken(self.balance(self._follow(BinaryNodeRef(referent=new_node)))))
#             return BinaryNodeRef(referent=self.blacken(self.balance(new_node)))
#             return self.balance(new_node)
            return BinaryNodeRef(referent=self.balance(new_node))
        elif key > node.key:
            # print ("recursively inserting right", self, node.key, key, value_ref._referent)
            new_node = BinaryNode.from_node(
                node,
                right_ref=self._insert(
                    self._follow(node.right_ref), key, value_ref))
            return BinaryNodeRef(referent = self.balance(self._follow(BinaryNodeRef(referent=new_node))))
#             return BinaryNodeRef(referent=self.blacken(self.balance(new_node)))
#             return self.balance(new_node)
        else: #create a new node to represent this data
            new_node = BinaryNode.from_node(node, value_ref=value_ref)
#         return new_node
        return BinaryNodeRef(referent=new_node)

    def printTree(self):
        print ("printing tree")
        node = self._follow(self._tree_ref)
        self.printNode(node)
#         print (node.key, node.value_ref._referent, node.color)
#         while True:
#             next_node = self._follow(node.left_ref)
#             if next_node is None:
#                 return None
#             node = next_node
#             print (node.key, node.value_ref._referent, node.color)

    def printNode(self, node):
        print (node.key, node.value_ref._referent, node.color)
        left_node = self._follow(node.left_ref)
        right_node = self._follow(node.right_ref)
        if left_node is not None:
            print ("left of ", node.key)
            self.printNode(left_node)
        if right_node is not None:
            print ("right of ", node.key)
            self.printNode(right_node)

    def blacken(self, node):
        if node.is_red():
            return BinaryNode.from_node(node, color=Color.BLACK)
        return node

    def recolored(self, node):
        # print ("recoloring",node.key, node.color)
        new_node = BinaryNode.from_node(node, left_ref=BinaryNodeRef(
                                        referent=self.blacken(BinaryNode.from_node(self._follow(node.left_ref)))),
                                        right_ref=BinaryNodeRef(
                                        referent=self.blacken(BinaryNode.from_node(self._follow(node.right_ref)))),
                                        color=Color.RED)
        print (new_node.color)
        return BinaryNode.from_node(node, left_ref=BinaryNodeRef(
                                        referent=self.blacken(BinaryNode.from_node(self._follow(node.left_ref)))),
                                        right_ref=BinaryNodeRef(
                                        referent=self.blacken(BinaryNode.from_node(self._follow(node.right_ref)))),
                                        color=Color.RED)

    def is_empty(node):
        return False

    def rotate_left(self, node):
        right_node = self._follow(node.right_ref)
        left_node = self._follow(node.left_ref)
        right_left_node = self._follow(right_node.left_ref)
        return BinaryNode.from_node(right_node,
                                    left_ref=BinaryNodeRef(
                                        referent=BinaryNode.from_node(node,right_ref=right_node.left_ref)))

    def rotate_right(self, node):
        left_node = self._follow(node.left_ref)
        left_right_node = self._follow(left_node.right_ref)
        return BinaryNode.from_node(left_node,
                                    right_ref=BinaryNodeRef(
                                        referent=BinaryNode.from_node(node,left_ref=left_node.right_ref)))

    def balance(self, node):
        # print("balancing", node.key)
        if node.is_red():
            # print ("Red node, returning")
            return node

        if self._follow(node.left_ref) != None:
            if self._follow(node.left_ref).is_red():
                # print ("left: red")
                if self._follow(node.right_ref) != None:
                    if self._follow(node.right_ref).is_red():
                        return self.recolored(node)

                left_node = self._follow(node.left_ref)
                # print (node.key, node.value_ref._referent, node.color)
                # print (left_node.key, left_node.value_ref._referent, left_node.color)
        #         print (left_node.left_ref)
        #         print (self._follow(left_node.left_ref).key)
        #         self.printTree()
                if self._follow(left_node.left_ref) != None:
                    if self._follow(left_node.left_ref).is_red():
                        # print ("left, left: black, red")
                        # print ("node", node.key)
                        # print ("node right", node.right_ref)
                        new_node = self.recolored(self.rotate_right(node))
                        # print ("in balance", new_node.key, new_node.color)
            #             return self.recolored(self.rotate_right(node))
                        return new_node
                if self._follow(left_node.right_ref) != None:
                    if self._follow(left_node.right_ref).is_red():
#                         return self.balance(BinaryNode.from_node(
#                             node,
#                             left_ref=BinaryNodeRef(referent=self.rotate_left(self._follow(node.left_ref))),
#                             key=key, value_ref=value_ref))
                        return self.balance(BinaryNode.from_node(
                            node,
                            left_ref=BinaryNodeRef(referent=self.rotate_left(self._follow(node.left_ref)))))

        right_node = self._follow(node.right_ref)
        if self._follow(node.right_ref) != None:
            if self._follow(node.right_ref).is_red():
                if self._follow(right_node.right_ref)!= None:
                    if self._follow(right_node.right_ref).is_red():
                        return self.recolored(self.rotate_left(node))
                if self._follow(right_node.left_ref) != None:
                    if self._follow(right_node.left_ref).is_red():
#                         return self.recolored(self.rotate_left(BinaryNode.from_node(
#                         node,
#                         right_ref=BinaryNodeRef(referent=self.rotate_right(self._follow(node.right_ref))),
#                         key=key, value_ref=value_ref)))
                        return self.recolored(self.rotate_left(BinaryNode.from_node(
                        node,
                        right_ref=BinaryNodeRef(referent=self.rotate_right(self._follow(node.right_ref))))))
        return node

    def _follow(self, ref):
        "get a node from a reference"
        #calls BinaryNodeRef.get
        return ref.get(self._storage)

    def _find_max(self, node):
        while True:
            next_node = self._follow(node.right_ref)
            if next_node is None:
                return node
            node = next_node

def connect(dbname):
    try:
        f = open(dbname, 'r+b')
    except IOError:
        fd = os.open(dbname, os.O_RDWR | os.O_CREAT)
        f = os.fdopen(fd, 'r+b')
    return DBDB(f)
