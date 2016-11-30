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







import pickle
class RBNodeRef(ValueRef):
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
        return RBNode(
            RBNodeRef(address=d['left']),
            d['key'],
            ValueRef(address=d['value']),
            RBNodeRef(address=d['right']),
            d['color'],
        )







class RBNode(object):
    @classmethod
    def from_node(cls, node, **kwargs):
        "clone a node with some changes from another one"
        return cls(
            left_ref=kwargs.get('left_ref', node.left_ref),
            key=kwargs.get('key', node.key),
            value_ref=kwargs.get('value_ref', node.value_ref),
            right_ref=kwargs.get('right_ref', node.right_ref),
            color = kwargs.get('color', node.color),
        )

    def __init__(self, left_ref, key, value_ref, right_ref, color):
        self.left_ref = left_ref
        self.key = key
        self.value_ref = value_ref
        self.right_ref = right_ref
        self.color = color


    def store_refs(self, storage):
        "method for a node to store all of its stuff"
        self.value_ref.store(storage)
        #calls BinaryNodeRef.store. which calls
        #BinaryNodeRef.prepate_to_store
        #which calls this again and recursively stores
        #the whole tree
        self.left_ref.store(storage)
        self.right_ref.store(storage)

    def blacken(self):
        if self.is_red():
            return self.from_node(
                self,
                color=Color.BLACK,
            )
        return self

    #def is_empty(self):
    #    return False

    #def is_black(self):
    #    return self.color == Color.BLACK

    def is_red(self):
        return self.color == Color.RED




import uuid


class Color(object):
    RED = 0
    BLACK = 1



class RedBlackTree(object):
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
        self._tree_ref = RBNodeRef(
            address=self._storage.get_root_address())

    def get(self, key):
        "get value for a key"
        #your code here
        #if tree is not locked by another writer
        #refresh the references and get new tree if needed
        if not self._storage.locked:
            self._refresh_tree_ref()
        #get the top level node
        node = self._follow(self._tree_ref)
        #traverse until you find appropriate node
        while node is not None:
            if key < node.key:
                node = self._follow(node.left_ref)
            elif key < node.key:
                node = self._follow(node.right_ref)
            else:
                return self._follow(node.value_ref)
        raise KeyError

    def set(self, key, value):
        "set a new value in the tree. will cause a new tree"
        #try to lock the tree. If we succeed make sure
        #we dont lose updates from any other process
        if self._storage.lock():
            self._refresh_tree_ref()
        #get current top-level node and make a value-ref
        node = self._follow(self._tree_ref)
        value_ref = ValueRef(value)
        #insert and get new tree ref
        self._tree_ref = self._insert(node, key, value_ref)


    def _insert(self, node, key, value_ref):
        "insert a new node creating a new path from root"
        #create a tree ifnthere was none so far
        new_node = self._follow(self.update(node, key, value_ref))
        return RBNodeRef(referent = new_node.blacken())

    def _follow(self, ref):
        "get a node from a reference"
        #calls BinaryNodeRef.get
        return ref.get(self._storage)

    '''
    def _find_max(self, node):
        while True:
            next_node = self._follow(node.right_ref)
            if next_node is None:
                return node
            node = next_node
    '''

    def rotate_left(self, node):
        return RBNode(
            RBNodeRef(
                referent = RBNode.from_node(node, right_ref = self._follow(node.right_ref).left_ref)
            ),
            self._follow(node.right_ref).key,
            self._follow(node.right_ref).value_ref,
            self._follow(node.right_ref).right_ref,
            self._follow(node.right_ref).color,
        )

    def rotate_right(self, node):
        return RBNode(
            self._follow(node.left_ref).left_ref,
            self._follow(node.left_ref).key,
            self._follow(node.left_ref).value_ref,
            RBNodeRef(
                referent = RBNode.from_node(node, left_ref = self._follow(node.left_ref).right_ref)
            ),
            color=self._follow(node.left_ref).color,
        )

    def recolored(self, node):
        return RBNode(
            left_ref = RBNodeRef(referent = self._follow(node.left_ref).blacken()),
            key = node.key,
            value_ref = node.value_ref,
            right_ref = RBNodeRef(referent = self._follow(node.right_ref).blacken()),
            color=Color.RED,
        )

    def balance(self, node):
        if node.is_red():
            return node
        node_left = self._follow(node.left_ref)
        node_right = self._follow(node.right_ref)
        if node_left is not None:
            left_left = self._follow(node_left.left_ref)
            left_right = self._follow(node_left.right_ref)
        else:
            left_left = None
            left_right = None

        if node_right is not None:
            right_left = self._follow(node_right.left_ref)
            right_right = self._follow(node_right.right_ref)
        else:
            right_left = None
            right_right = None

        if node_left is not None and node_left.is_red():
            if node_right is not None and node_right.is_red():
                return self.recolored(node)
            if left_left is not None and left_left.is_red():
                return self.recolored(self.rotate_right(node))
            if left_right is not None and left_right.is_red():
                new_node = RBNode.from_node(
                        node,
                        left_ref = RBNodeRef(referent = self.rotate_left(node_left)),
                        color = node.color,
                    )
                return self.recolored(self.rotate_right(new_node))
            return node

        if node_right is not None and node_right.is_red():
            if right_right is not None and right_right.is_red():
                return self.recolored(self.rotate_left(node))
            if right_left is not None and right_left.is_red():
                new_node = RBNode.from_node(
                        node,
                        right_ref = RBNodeRef(referent = self.rotate_right(node_right)),
                        color = node.color,
                    )
                return self.recolored(self.rotate_left(new_node))
        return node

    def update(self, node, key, value_ref):
        if node is None:
            new_node = RBNode(
                RBNodeRef(), key, value_ref, RBNodeRef(), Color.RED)
        elif key < node.key:
            new_node = RBNode.from_node(
                node,
                left_ref=self.update(
                    self._follow(node.left_ref), key, value_ref))
        elif key > node.key:
            new_node = RBNode.from_node(
                node,
                right_ref=self.update(
                    self._follow(node.right_ref), key, value_ref))
        else: #create a new node to represent this data
            new_node = RBNode.from_node(node, value_ref=value_ref)
        new_node = self.balance(new_node)
        return RBNodeRef(referent=new_node)

    def find_all_smaller(self, val):
        smaller_list = []
        if not self._storage.locked:
            self._refresh_tree_ref()
        #get the top level node
        root = self._tree_ref
        self.inorder(root, smaller_list, val)
        return smaller_list

    def inorder(self, root, smaller_list, val):
        node = self._follow(root)
        if node is not None :
            self.inorder(node.left_ref, smaller_list, val)
            if node.key > val:
                return
            smaller_list.append(self._follow(node.value_ref))
            self.inorder(node.right_ref, smaller_list, val)


import os
import struct

import portalocker


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
        self._tree = RedBlackTree(self._storage)

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
        return self._tree.set(key, value)

    def find_all_smaller(self, val):
        self._assert_not_closed()
        return self._tree.find_all_smaller(val)


'''
    def delete(self, key):
        self._assert_not_closed()
        return self._tree.delete(key)
'''






import os
def connect(dbname):
    try:
        f = open(dbname, 'r+b')
    except IOError:
        fd = os.open(dbname, os.O_RDWR | os.O_CREAT)
        f = os.fdopen(fd, 'r+b')
    return DBDB(f)





'''
class EmptyRBNode(RBNode):

    def __init__(self):
        self.color = Color.BLACK

    def is_empty(self):
        return True

    def update(self, node):
        return node

    def __len__(self):
        return 0
'''
