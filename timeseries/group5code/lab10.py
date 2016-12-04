import os
import struct
import portalocker
import pickle
import uuid

class Color(object):
    '''The Color class implemented using Python.
       The Color object includes two colors: RED and BLACK.
    '''
    RED = 0
    BLACK = 1



class ValueRef(object):
    '''This is the ValueRef class implemented using Python.
       ValueRef is a reference to a string value on disk.

       Implements:
           object

       Attributes:
           referent: the value to store.
           address: the address to store at.

       Methods:
           __init__: The constructor to initialize a ValueRef object.
           address: The function to return ValueRef's address.
           prepare_to_store: The function that is later implemented in class inheriting from ValueRef.
           referent_to_bytes: The function that converts referent to bytes.
           bytes_to_referent: The function that converts bytes back to referent.
           get: The function that reads bytes for value from disk.
           store: The function that stores bytes for value to disk.
    '''
    def __init__(self, referent=None, address=0):
        '''The constructor to initialize a ValueRef object.
           Param:
               referent: the value to store.
               address: the address to store at.
        '''
        self._referent = referent #value to store
        self._address = address #address to store at

    @property
    def address(self):
        '''The function to return ValueRef's address.
           Return:
               ValueRef's address.
        '''
        return self._address

    def prepare_to_store(self, storage):
        '''The function that is later implemented in class inheriting from ValueRef.
           Param:
               storage: the place to store.
        '''
        pass

    @staticmethod
    def referent_to_bytes(referent):
        '''The function that converts referent to bytes.
           Param:
               referent: the value to store and convert.
           Return:
               a bytes representation of the referent.
        '''
        return referent.encode('utf-8')

    @staticmethod
    def bytes_to_referent(bytes):
        '''The function that converts bytes back to referent.
           Param:
               bytes: a bytes representation of the referent.
           Return:
               the value converted back from the bytes.
        '''
        return bytes.decode('utf-8')

    def get(self, storage):
        '''The function that reads bytes for value from disk.
           Param:
               storage: the place that the value will be got.
           Return:
               the value got from disk.
        '''
        if self._referent is None and self._address:
            self._referent = self.bytes_to_referent(storage.read(self._address))
        return self._referent

    def store(self, storage):
        '''The function that stores bytes for value to disk.
           Param:
               storage: the place to store the value.
        '''
        #called by BinaryNode.store_refs
        if self._referent is not None and not self._address:
            self.prepare_to_store(storage)
            self._address = storage.write(self.referent_to_bytes(self._referent))



class RBNodeRef(ValueRef):
    '''This is the RBNodeRef class implemented using Python.
       RBNodeRef is a reference to a redblacktree node.

       Implements:
           ValueRef

       Methods:
          prepare_to_store: The function that have a node store its refs.
          referent_to_bytes: The function that uses pickle to convert node to string.
          bytes_to_referent: The function that unpickles string to get a node object.
    '''
    #calls the BinaryNode's store_refs
    def prepare_to_store(self, storage):
        '''The function that have a node store its refs.
           Param:
               storage: the place to store.
        '''
        if self._referent:
            self._referent.store_refs(storage)

    @staticmethod
    def referent_to_bytes(referent):
        '''The function that uses pickle to convert node to string.
           Param:
               referent: the node to store and convert.
           Return:
               a string representation of the node.
        '''
        return pickle.dumps({
            'left': referent.left_ref.address,
            'key': referent.key,
            'value': referent.value_ref.address,
            'right': referent.right_ref.address,
            'color': referent.color,
        })

    @staticmethod
    def bytes_to_referent(string):
        '''The function that unpickles string to get a node object.
           Param:
               string: a string representation of the node.
           Return:
               a RBNode recovered from the string representation of the node.
        '''
        d = pickle.loads(string)
        return RBNode(
            RBNodeRef(address=d['left']),
            d['key'],
            ValueRef(address=d['value']),
            RBNodeRef(address=d['right']),
            d['color'],
        )



class RBNode(object):
    '''The RBNode class implemented using Python.
       RBNode is the node in RedBlackTree.

       Implements:
           object

       Attributes:
           left_ref: RBNodeRef, the left child of the RBNode.
           key: the key of RBNode that is used in comparision in operations of redblacktree.
           value_ref: RBNodeRef, the value of the RBNode.
           right_ref: RBNodeRef, the right child of the RBNode.
           color: color of the RBNode.

       Methods:
           __init__: The constructor to initialize a RBNode object.
           from_node: The function that clones a node with some changes from another one.
           store_refs: The method for a RBNode to store all of its stuff.
           blacken: The function to blacken the RBNode if it is red.
           is_red(self): The method to check is a node is a red node.
    '''
    @classmethod
    def from_node(cls, node, **kwargs):
        '''The function that clones a node with some changes from another one.
           Param:
               node: the node to clone from.
           Return:
               a RBNode initialized from another one.
        '''
        return cls(
            left_ref=kwargs.get('left_ref', node.left_ref),
            key=kwargs.get('key', node.key),
            value_ref=kwargs.get('value_ref', node.value_ref),
            right_ref=kwargs.get('right_ref', node.right_ref),
            color = kwargs.get('color', node.color),
        )

    def __init__(self, left_ref, key, value_ref, right_ref, color):
        '''The constructor to initialize a RBNode object.
           Param:
               left_ref: RBNodeRef, the left child of the RBNode.
               key: the key of RBNode that is used in comparision in operations of redblacktree.
               value_ref: RBNodeRef, the value of the RBNode.
               right_ref: RBNodeRef, the right child of the RBNode.
               color: color of the RBNode.
        '''
        self.left_ref = left_ref
        self.key = key
        self.value_ref = value_ref
        self.right_ref = right_ref
        self.color = color

    def store_refs(self, storage):
        '''The method for a RBNode to store all of its stuff.
           Param:
               storage: the place to store the RBNode's stuff.
        '''
        self.value_ref.store(storage)
        #calls BinaryNodeRef.store. which calls
        #BinaryNodeRef.prepate_to_store
        #which calls this again and recursively stores
        #the whole tree
        self.left_ref.store(storage)
        self.right_ref.store(storage)

    def blacken(self):
        '''The function to blacken the RBNode if it is red.
           Return:
               The original RBNode if it was black;
               or the new blackened RBNode.
        '''
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
        '''The method to check is a node is a red node.
           Return:
               boolean, whether or not the node is a red one.
        '''
        return self.color == Color.RED



class RedBlackTree(object):
    '''The RedBlackTree class implemented by Python.
       The RedBlackTree is a balanced tree.

       Implements:
           object

       Attributes:

           storage: the place to store the RedBlackTree stuff.
           _tree_ref: reference to RedBlackTree.


       Methods:

           __init__: The constructor to initialize a RedBlackTree object.
           _refresh_tree_ref: The funtion to get reference to new tree if it has changed.
           commit: The function that commit changes to disk so that the changes are final.
           _follow: The function to get a node from a reference.
           get: The function that gets value for a key.
           set: The function that sets a new value in the tree.

           _insert: The function that insert a new node creating a new path from root.
           update: The function to find the insertion point.
           balance: The function to make the RedBlackTree balanced using rotate_left and rotate_right.
           rotate_left: The function that rotates the given node to left.
           rotate_right: The function that rotates the given node to right.
           recolored: The function that blacken the children of the node, and make the node itself red.
           find_all_smaller: The function to get a list of values that are smaller than the given one.
           inorder: The function to do an inorder traversal of the RedBlackTree.
    '''
    def __init__(self, storage):
        '''The constructor to initialize a RedBlackTree object.
           Param:
               storage: the place to store the RedBlackTree stuff.
        '''
        self._storage = storage
        self._refresh_tree_ref()

    def commit(self):
        '''The funtion to get reference to new tree if it has changed.
        '''
        #triggers BinaryNodeRef.store
        self._tree_ref.store(self._storage)
        #make sure address of new tree is stored
        self._storage.commit_root_address(self._tree_ref.address)

    def _refresh_tree_ref(self):
        '''The funtion to get reference to new tree if it has changed.
        '''
        self._tree_ref = RBNodeRef(
            address=self._storage.get_root_address())

    def get(self, key):
        '''The function that gets value for a key.
           Param:
               key: the key for getting the corresponding to the key.
        '''
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
        '''The function that sets a new value in the tree.
           Param:
               key: the key to set value with.
               value: the value to be set.
        '''
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
        '''The function that insert a new node creating a new path from root.
           Param:
               node: the root of the subRedBlackTree to insert.
               key: the key of the node to insert.
               value_ref: the value_ref of the node to insert.
           Return:
               return a new copy of the RedBlackTree after insertion after blacken.
        '''
        #create a tree ifnthere was none so far
        new_node = self._follow(self.update(node, key, value_ref))
        return RBNodeRef(referent = new_node.blacken())

    def update(self, node, key, value_ref):
        '''The function to find the insertion point.
           Param:
               node: the root of the subRedBlackTree to insert.
               key: the key of the node to insert.
               value_ref: the value_ref of the node to insert.
           Return:
               return a new copy of the RedBlackTree after insertion.
        '''
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


    def _follow(self, ref):
        '''The function to get a node from a reference.
           Param:
               ref: the RBNodeRef to get node from.
        '''
        #calls BinaryNodeRef.get
        return ref.get(self._storage)

    def rotate_left(self, node):
        '''The function that rotates the given node to left.
           Param:
               node: the RBNode to rotate to left.
           Return:
               RBNode after rotation to left.
        '''
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
        '''The function that rotates the given node to right.
           Param:
               node: the RBNode to rotate to right.
           Return:
               RBNode after rotation to right.
        '''
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
        '''The function that blacken the children of the node, and make the node itself red.
           Param:
               node: the node to recolor.
           Return:
               the RBNode after recolor.
        '''
        return RBNode(
            left_ref = RBNodeRef(referent = self._follow(node.left_ref).blacken()),
            key = node.key,
            value_ref = node.value_ref,
            right_ref = RBNodeRef(referent = self._follow(node.right_ref).blacken()),
            color=Color.RED,
        )

    def balance(self, node):
        '''The function to make the RedBlackTree balanced using rotate_left and rotate_right.
           Param:
               node: the root of the subRedBlackTree to be balanced.
           Return:
               the subRedBlackTree after balanced.
        '''
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

    def find_all_smaller(self, val):
        '''The function to get a list of values that are smaller than the given one.
           Param:
               val: the value to compare with.
           Return:
               a list of values that are smaller than the given one.
        '''
        smaller_list = []
        if not self._storage.locked:
            self._refresh_tree_ref()
        #get the top level node
        root = self._tree_ref
        self.inorder(root, smaller_list, val)
        return smaller_list

    def inorder(self, root, smaller_list, val):
        '''The function to do an inorder traversal of the RedBlackTree.
           Param:
               root: the root of the RedBlackTree.
               smaller_list: a list of values that are smaller than the given one.
               val: the value to compare with.
        '''
        node = self._follow(root)
        if node is not None :
            self.inorder(node.left_ref, smaller_list, val)
            if node.key > val:
                return
            smaller_list.append(self._follow(node.value_ref))
            self.inorder(node.right_ref, smaller_list, val)


class Storage(object):
    '''The Storage class implemented using Python.
       Storage is used to store things.


       Implements:

           object


       Attributes:

          _f: file name
          locked: whether the storage is locked.


       Methods:


           __init__: The constructor to initialize an area on the disk for storage.
           _ensure_superblock: The function that guarantee that the next write will start on a sector boundary.
           lock: if not locked, lock the file for writing.
           unlock: Flush the already written part on to the disk first, then unlock the file.
           _seek_end: Seeking the place where lastly written.
           _seek_superblock: go to beginning of file which is on sec boundary.
           _bytes_to_integer: The function that convert bytes to integer.
           _integer_to_bytes: The function that convert integer to bytes.
           _read_integer: Read bytes from storage and then convert to integer.
           _write_integer: The function that writes an integer to dist.
           write: The function to write data to disk, returning the adress at which you wrote it.
           read: The function to read data from the given address.
           commit_root_address: The function to commit root address.
           get_root_address: The function to get root address.
           close: The function to close storage.
           closed: The function to check whether the storage is closed.
    '''
    SUPERBLOCK_SIZE = 4096
    INTEGER_FORMAT = "!Q"
    INTEGER_LENGTH = 8

    def __init__(self, f):
        '''The constructor to initialize an area on the disk for storage.
           Param:
               f: the file name.
        '''
        self._f = f
        self.locked = False
        #we ensure that we start in a sector boundary
        self._ensure_superblock()

    def _ensure_superblock(self):
        '''The function that guarantee that the next write will start on a sector boundary.
        '''
        self.lock()
        self._seek_end()
        end_address = self._f.tell()
        if end_address < self.SUPERBLOCK_SIZE:
            self._f.write(b'\x00' * (self.SUPERBLOCK_SIZE - end_address))
        self.unlock()

    def lock(self):
        '''if not locked, lock the file for writing.
        '''
        if not self.locked:
            portalocker.lock(self._f, portalocker.LOCK_EX)
            self.locked = True
            return True
        else:
            return False

    def unlock(self):
        '''Flush the already written part on to the disk first, then unlock the file.
        '''
        if self.locked:
            self._f.flush()
            portalocker.unlock(self._f)
            self.locked = False

    def _seek_end(self):
        '''Seeking the place where lastly written.
        '''
        self._f.seek(0, os.SEEK_END)

    def _seek_superblock(self):
        '''go to beginning of file which is on sec boundary.
        '''
        self._f.seek(0)

    def _bytes_to_integer(self, integer_bytes):
        '''The function that convert bytes to integer.
           Param:
               integer_bytes: the bytes needed to be converted.
        '''
        return struct.unpack(self.INTEGER_FORMAT, integer_bytes)[0]

    def _integer_to_bytes(self, integer):
        '''The function that convert integer to bytes.
           Param:
               integer: the integer to be converted.
        '''
        return struct.pack(self.INTEGER_FORMAT, integer)

    def _read_integer(self):
        '''Read bytes from storage and then convert to integer.
        '''
        return self._bytes_to_integer(self._f.read(self.INTEGER_LENGTH))

    def _write_integer(self, integer):
        '''The function that writes an integer to dist.
           Param:
               integer: the integer to write.
        '''
        self.lock()
        self._f.write(self._integer_to_bytes(integer))

    def write(self, data):
        '''The function to write data to disk, returning the adress at which you wrote it.
           Param:
               data: the data to write.
        '''
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
        '''The function to read data from the given address.
           Param:
               address: the address to read data from.
        '''
        self._f.seek(address)
        length = self._read_integer()
        data = self._f.read(length)
        return data

    def commit_root_address(self, root_address):
        '''The function to commit root address.
           Param:
               root_address: the root_address to be commited.
        '''
        self.lock()
        self._f.flush()
        #make sure you write root address at position 0
        self._seek_superblock()
        #write is atomic because we store the address on a sector boundary.
        self._write_integer(root_address)
        self._f.flush()
        self.unlock()

    def get_root_address(self):
        '''The function to get root address.
           Return:
               root_address.
        '''
        #read the first integer in the file
        #your code here
        self._seek_superblock()
        root_address = self._read_integer()
        return root_address

    def close(self):
        '''The function to close storage.
        '''
        self.unlock()
        self._f.close()

    @property
    def closed(self):
        '''The function to check whether the storage is closed.
        '''
        return self._f.closed





class DBDB(object):
    '''The DBDB class implemented using Python.
       DBDB is a Python library that implements a simple key/value database


       Implements:

           object


       Attributes:

           _storage: the storage object used to store.
           _tree: the RedBlackTree data structure that backs the DBDB.


       Methods:
           __init__: The constructor to initialize a DBDB object.
           _assert_not_closed: The function to assert that the storage is already closed.
           close: The function to close the storage.
           commit: The function to commit the RedBlackTree.
           get: The function to get the value associated with the key.
           set: The function to set the value associated the key given.
           find_all_smaller: The function to get a list of values that are smaller than the given one.
    '''
    def __init__(self, f):
        '''The constructor to initialize a DBDB object.
           Param:
               f: the file name to store things.
        '''
        self._storage = Storage(f)
        self._tree = RedBlackTree(self._storage)

    def _assert_not_closed(self):
        '''The function to assert that the storage is already closed.
        '''
        if self._storage.closed:
            raise ValueError('Database closed.')

    def close(self):
        '''The function to close the storage.
        '''
        self._storage.close()

    def commit(self):
        '''The function to commit the RedBlackTree.
        '''
        self._assert_not_closed()
        self._tree.commit()

    def get(self, key):
        '''The function to get the value associated with the key.
           Param:
               key: the key for which to get value.
           Return:
               the value associated with the key.
        '''
        self._assert_not_closed()
        return self._tree.get(key)

    def set(self, key, value):
        '''The function to set the value associated the key given.
            Param:
                key: the key for which to set value.
                value: the value associated with the key given.
            Return
        '''
        self._assert_not_closed()
        return self._tree.set(key, value)

    def find_all_smaller(self, val):
        '''The function to get a list of values that are smaller than the given one.
           Param:
               val: the value to be compared with.
           Return:
               a list of values that are smaller than the given one.
        '''
        self._assert_not_closed()
        return self._tree.find_all_smaller(val)


'''
    def delete(self, key):
        self._assert_not_closed()
        return self._tree.delete(key)
'''


def connect(dbname):
    '''The function to connect to the database.
    '''
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
