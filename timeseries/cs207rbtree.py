import os
import struct
import portalocker
import pickle


class Storage(object):
    """Class to manage writing to file in consecutive blocks with locking"""
    SUPERBLOCK_SIZE = 4096
    INTEGER_FORMAT = "!Q"
    INTEGER_LENGTH = 8

    def __init__(self, f):
        """Initialize Storage block, Set Lock to False"""
        self._f = f
        self.locked = False
        # we ensure that we start in a sector boundary
        self._ensure_superblock()

    def _ensure_superblock(self):
        """Guarantee that the next write will start on a sector boundary"""
        self.lock()
        self._seek_end()
        end_address = self._f.tell()
        if end_address < self.SUPERBLOCK_SIZE:
            self._f.write(b'\x00' * (self.SUPERBLOCK_SIZE - end_address))
        self.unlock()

    def lock(self):
        """If storage is not already locked, lock the file for writing"""
        if not self.locked:
            portalocker.lock(self._f, portalocker.LOCK_EX)
            self.locked = True
            return True
        else:
            return False

    def unlock(self):
        """Unlock the file if it is currently locked"""
        if self.locked:
            self._f.flush()
            portalocker.unlock(self._f)
            self.locked = False

    def _seek_end(self):
        """Seek pointer to the end of the block"""
        self._f.seek(0, os.SEEK_END)

    def _seek_superblock(self):
        """Go to beginning of file which is on sector boundary"""
        self._f.seek(0)

    def _bytes_to_integer(self, integer_bytes):
        """Convert bytes to integer format"""
        return struct.unpack(self.INTEGER_FORMAT, integer_bytes)[0]

    def _integer_to_bytes(self, integer):
        """Convert integers to byte format"""
        return struct.pack(self.INTEGER_FORMAT, integer)

    def _read_integer(self):
        """Read an integer from file"""
        return self._bytes_to_integer(self._f.read(self.INTEGER_LENGTH))

    def _write_integer(self, integer):
        """Write an integer to file"""
        self.lock()
        self._f.write(self._integer_to_bytes(integer))

    def write(self, data):
        """Write data to disk, returning the address at which you wrote it"""
        # first lock, get to end, get address to return, write size
        self.lock()
        self._seek_end()
        object_address = self._f.tell()
        self._write_integer(len(data))
        self._f.write(data)
        return object_address

    def read(self, address):
        """Read data from address on disk"""
        self._f.seek(address)
        length = self._read_integer()
        data = self._f.read(length)
        return data

    def commit_root_address(self, root_address):
        """Write the root address at position 0 of the superblock"""
        self.lock()
        self._f.flush()
        # make sure you write root address at position 0
        self._seek_superblock()
        # write is atomic because we store the address on a sector boundary.
        self._write_integer(root_address)
        self._f.flush()
        self.unlock()

    def get_root_address(self):
        """Read in the root"""
        # read the first integer in the file
        self._seek_superblock()
        root_address = self._read_integer()
        return root_address

    def close(self):
        """Close the storage file"""
        self.unlock()
        self._f.close()

    @property
    def closed(self):
        """Check if file is closed"""
        return self._f.closed


class DBDB(object):
    """A Database that implements a simple key/value database.
    It lets you associate a key with a value, and store that association
    on disk for later retrieval."""

    def __init__(self, f):
        """Initialize the storage file and structure for the database"""
        self._storage = Storage(f)
        self._tree = BinaryTree(self._storage)

    def _assert_not_closed(self):
        """Check if the storage file is closed"""
        if self._storage.closed:
            raise ValueError('Database closed.')

    def close(self):
        """Close the storage file"""
        self._storage.close()

    def commit(self):
        """Check if the storage file is closed. If not, write database to file"""
        self._assert_not_closed()
        self._tree.commit()

    def get(self, key):
        """Retrieve the value associated with a key"""
        self._assert_not_closed()
        return self._tree.get(key)

    def set(self, key, value):
        """Set the value associated with a key"""
        self._assert_not_closed()
        print(self._tree)
        return self._tree.set(key, value)

    def delete(self, key):
        """Delete a key, value pair from the Database"""
        self._assert_not_closed()
        return self._tree.delete(key)


class ValueRef(object):
    """A reference to a string value on disk"""

    def __init__(self, referent=None, address=0):
        """Initialize with either or both the object to be stored
        and its disk address"""
        self._referent = referent  # value to store
        self._address = address  # address to store at

    @property
    def address(self):
        """Return the disk address of the object"""
        return self._address

    def prepare_to_store(self, storage):
        pass

    @staticmethod
    def referent_to_bytes(referent):
        """Encode string value as utf-8"""
        return referent.encode('utf-8')

    @staticmethod
    def bytes_to_referent(bytes):
        """Decode bytes to string value"""
        return bytes.decode('utf-8')

    def get(self, storage):
        """Read bytes for value from disk"""
        if self._referent is None and self._address:
            self._referent = self.bytes_to_referent(storage.read(self._address))
        return self._referent

    def store(self, storage):
        """Store bytes for value to disk"""
        # called by BinaryNode.store_refs
        if self._referent is not None and not self._address:
            self.prepare_to_store(storage)
            self._address = storage.write(self.referent_to_bytes(self._referent))


class BinaryNodeRef(ValueRef):
    """Reference to a Red-Black Binary Tree node on disk"""

    # calls the BinaryNode's store_refs
    def prepare_to_store(self, storage):
        "have a node store its refs"
        if self._referent:
            self._referent.store_refs(storage)

    @staticmethod
    def referent_to_bytes(referent):
        """Use pickle to convert node to bytes"""
        return pickle.dumps({
            'left': referent.left_ref.address,
            'key': referent.key,
            'value': referent.value_ref.address,
            'right': referent.right_ref.address,
            'color': referent.color,
        })

    @staticmethod
    def bytes_to_referent(string):
        """Unpickle bytes to get a node object"""
        d = pickle.loads(string)
        return BinaryNode(
            BinaryNodeRef(address=d['left']),
            d['key'],
            ValueRef(address=d['value']),
            BinaryNodeRef(address=d['right']),
            d['color'],
        )


class BinaryNode(object):
    """Represents a Node of a Red-Black Binary Tree"""

    @classmethod
    def from_node(cls, node, **kwargs):
        """Clone a node with some changes from another one"""
        return cls(
            left_ref=kwargs.get('left_ref', node.left_ref),
            key=kwargs.get('key', node.key),
            value_ref=kwargs.get('value_ref', node.value_ref),
            right_ref=kwargs.get('right_ref', node.right_ref),
            color=kwargs.get('color', node.color),
            # parent_ref=kwargs.get('parent', node.parent),
        )

    def __init__(self, left_ref, key, value_ref, right_ref, color):  # , parent):
        """Initialize a node with key, value, left and right children, and color"""
        self.left_ref = left_ref
        self.key = key
        self.value_ref = value_ref
        self.right_ref = right_ref
        self.color = color
        # self.parent = parent

    def is_red(self):
        """Return true if node is red"""
        return self.color == Color.RED

    def is_black(self):
        """Return true if node is black"""
        return self.color == Color.BLACK

    def store_refs(self, storage):
        """Method for a node to store all of its stuff"""
        self.value_ref.store(storage)
        # calls BinaryNodeRef.store. which calls
        # BinaryNodeRef.prepate_to_store
        # which calls this again and recursively stores
        # the whole tree
        self.left_ref.store(storage)
        self.right_ref.store(storage)


class Color(object):
    """Class which encodes the Red or Black parameter of a tree node"""
    RED = 0
    BLACK = 1


class BinaryTree(object):
    """Immutable Red-Black Binary Tree class. Constructs new tree on changes"""

    def __init__(self, storage):
        """Initialize tree with disk storage and tree node if it already exists"""
        self._storage = storage
        self._refresh_tree_ref()

    def commit(self):
        """Commit database changes to file, making them persistent"""
        # triggers BinaryNodeRef.store
        self._tree_ref.store(self._storage)
        # make sure address of new tree is stored
        self._storage.commit_root_address(self._tree_ref.address)

    def _refresh_tree_ref(self):
        """Get reference to new tree if it has changed"""
        self._tree_ref = BinaryNodeRef(
            address=self._storage.get_root_address())

    def get(self, key):
        """Get value associated with a key"""
        # if tree is not locked by another writer
        # refresh the references and get new tree if needed
        if not self._storage.locked:
            self._refresh_tree_ref()
        # get the top level node
        node = self._follow(self._tree_ref)
        # traverse until you find appropriate node
        while node is not None:
            if key < node.key:
                #                 print("searching left", node.key, key)
                node = self._follow(node.left_ref)
            elif key > node.key:
                #                 print("searching right", node.key, key)
                node = self._follow(node.right_ref)
            else:
                return self._follow(node.value_ref)
        raise KeyError

    def set(self, key, value):
        """Set a new value in the tree. Will cause a new tree"""
        # try to lock the tree. If we succeed make sure
        # we dont lose updates from any other process
        if self._storage.lock():
            self._refresh_tree_ref()
        # get current top-level node and make a value-ref
        node = self._follow(self._tree_ref)
        value_ref = ValueRef(value)
        # insert and get new tree ref
        # print (self._tree_ref, node, key, value_ref)
        self._tree_ref = BinaryNodeRef(referent=self.blacken(self._follow(self._insert(node, key, value_ref))))
        # self.printTree()

    def _insert(self, node, key, value_ref):
        """Insert a new node, creating a new path from root"""
        # create a tree ifnthere was none so far
        if node is None:
            # print ("reached empty node", key, value_ref._referent)
            new_node = BinaryNode(
                BinaryNodeRef(), key, value_ref, BinaryNodeRef(), Color.RED)
            #             return self.balance(self._follow(BinaryNodeRef(referent=new_node)))
            return BinaryNodeRef(referent=self.balance(self._follow(BinaryNodeRef(referent=new_node))))
        elif key < node.key:
            # print ("recursively inserting left", self, node.key, key, value_ref._referent)
            new_node = BinaryNode.from_node(
                node,
                left_ref=self._insert(
                    self._follow(node.left_ref), key, value_ref))
            return BinaryNodeRef(referent=self.balance(new_node))
        elif key > node.key:
            new_node = BinaryNode.from_node(
                node,
                right_ref=self._insert(
                    self._follow(node.right_ref), key, value_ref))
            return BinaryNodeRef(referent=self.balance(self._follow(BinaryNodeRef(referent=new_node))))
        else:  # create a new node to represent this data
            new_node = BinaryNode.from_node(node, value_ref=value_ref)
        return BinaryNodeRef(referent=new_node)

    def printTree(self):
        """Print a rough representation of the tree for error checking"""
        print("printing tree")
        node = self._follow(self._tree_ref)
        self.printNode(node)

    def printNode(self, node):
        """Recursively print nodes within the printTree function"""
        print(node.key, node.value_ref._referent, node.color)
        left_node = self._follow(node.left_ref)
        right_node = self._follow(node.right_ref)
        if left_node is not None:
            print("left of ", node.key)
            self.printNode(left_node)
        if right_node is not None:
            print("right of ", node.key)
            self.printNode(right_node)

    def blacken(self, node):
        """If a node is red, change its color to black"""
        if node.is_red():
            return BinaryNode.from_node(node, color=Color.BLACK)
        return node

    def recolored(self, node):
        """Recolor a node and its two children such that the parent is red
        and the children are black"""
        return BinaryNode.from_node(node, left_ref=BinaryNodeRef(
            referent=self.blacken(BinaryNode.from_node(self._follow(node.left_ref)))),
                                    right_ref=BinaryNodeRef(
                                        referent=self.blacken(BinaryNode.from_node(self._follow(node.right_ref)))),
                                    color=Color.RED)

    def is_empty(node):
        return False

    def rotate_left(self, node):
        """Perform an Okasaki left rotation"""
        right_node = self._follow(node.right_ref)
        left_node = self._follow(node.left_ref)
        right_left_node = self._follow(right_node.left_ref)
        return BinaryNode.from_node(right_node,
                                    left_ref=BinaryNodeRef(
                                        referent=BinaryNode.from_node(node, right_ref=right_node.left_ref)))

    def rotate_right(self, node):
        """Perform an Okasaki right rotation"""
        left_node = self._follow(node.left_ref)
        left_right_node = self._follow(left_node.right_ref)
        return BinaryNode.from_node(left_node,
                                    right_ref=BinaryNodeRef(
                                        referent=BinaryNode.from_node(node, left_ref=left_node.right_ref)))

    def balance(self, node):
        """Balance the tree after an insert"""
        if node.is_red():
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
                if self._follow(left_node.left_ref) != None:
                    if self._follow(left_node.left_ref).is_red():
                        # print ("left, left: black, red")
                        # print ("node", node.key)
                        # print ("node right", node.right_ref)
                        new_node = self.recolored(self.rotate_right(node))
                        return new_node
                if self._follow(left_node.right_ref) != None:
                    if self._follow(left_node.right_ref).is_red():
                        return self.balance(BinaryNode.from_node(
                            node,
                            left_ref=BinaryNodeRef(referent=self.rotate_left(self._follow(node.left_ref)))))

        right_node = self._follow(node.right_ref)
        if self._follow(node.right_ref) != None:
            if self._follow(node.right_ref).is_red():
                if self._follow(right_node.right_ref) != None:
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
        """Get a node from a reference"""
        # calls BinaryNodeRef.get
        return ref.get(self._storage)

    def _find_max(self, node):
        """Find the max value of the binary tree"""
        while True:
            next_node = self._follow(node.right_ref)
            if next_node is None:
                return node
            node = next_node


def connect(dbname):
    """Opens the database file (possibly creating it, 
    but never overwriting it) and returns an instance of DBDB"""
    try:
        f = open(dbname, 'r+b')
    except IOError:
        fd = os.open(dbname, os.O_RDWR | os.O_CREAT)
        f = os.fdopen(fd, 'r+b')
    return DBDB(f)
