
''''

Authors:
Sophie Hilgard
Ryan Lapcevic
Anthony Soroka
Ariel Herbert-Voss
Yamini Bansal

Date: 28 Oct 2016
Course: Project CS 207
Document: test_cs207rbtree.py
Summary: Testing RBTree Class

Example:
    Example how to run this test
        $ source activate py35
        $ py.test test_cs207rbtree.py

'''



from pytest import raises
from cs207rbtree import *
import numpy as np
import random
import math
import datetime
import os



'''
Functions Being Tested: Get
Summary: Basic Get Test
'''
def test_get():
    os.remove("/tmp/test2.dbdb")
    db = connect("/tmp/test2.dbdb")
    for i in range(97,108):
        db.set(i,chr(i))
    value = db.get(97)
    assert value == 'a'
    db.close()

'''
Functions Being Tested: Commit
Summary: Basic Commit Test
'''
def test_commit():
    os.remove("/tmp/test2.dbdb")
    db = connect("/tmp/test2.dbdb")
    for i in range(97,108):
        db.set(i,chr(i))
    db.commit()
    db.close()
    db = connect("/tmp/test2.dbdb")
    value = db.get(98)
    assert value == 'b'
    db.close()

'''
Tree Properties Being Tested: Right Child > Parent
Summary: Testing Tree GT Property
'''
def test_gt():
    db = connect("/tmp/test2.dbdb")
    for i in range(97,108):
        db.set(i,chr(i))
    for i in range(119,109,-1):
        db.set(i,chr(i))
    tree = db._tree
    node = tree._follow(tree._tree_ref)
    while node!=None:
        next_node = tree._follow(node.right_ref)
        if next_node!=None:
            assert next_node.key > node.key
        node = next_node
    db.close()

'''
Tree Properties Being Tested: Left Child > Parent
Summary: Testing Tree LT Property
'''
def test_lt():
    db = connect("/tmp/test2.dbdb")
    for i in range(97,108):
        db.set(i,chr(i))
    for i in range(119,109,-1):
        db.set(i,chr(i))
    tree = db._tree
    node = tree._follow(tree._tree_ref)
    while node!=None:
        next_node = tree._follow(node.left_ref)
        if next_node!=None:
            assert next_node.key < node.key
        node = next_node
    db.close()

'''
Tree Properties Being Tested: Okasaki Case 1 Rotation
Summary: Testing Okasaki Rebalance 1
'''
def test_ok1():
    os.remove("/tmp/test2.dbdb")
    db = connect("/tmp/test2.dbdb")
    db.set(3,'c')
    db.set(1,'a')
    db.set(2,'b')
    tree = db._tree
    node = tree._follow(tree._tree_ref)
    assert node.key==2
    left_node = tree._follow(node.left_ref)
    assert left_node.key==1
    right_node = tree._follow(node.right_ref)
    assert right_node.key==3
    assert left_node.color == Color.BLACK
    assert right_node.color == Color.BLACK
    db.close()

'''
Tree Properties Being Tested: Okasaki Case 2 Rotation
Summary: Testing Okasaki Rebalance 2
'''
def test_ok2():
    os.remove("/tmp/test2.dbdb")
    db = connect("/tmp/test2.dbdb")
    db.set(3,'c')
    db.set(2,'b')
    db.set(1,'a')
    tree = db._tree
    node = tree._follow(tree._tree_ref)
    assert node.key==2
    left_node = tree._follow(node.left_ref)
    assert left_node.key==1
    right_node = tree._follow(node.right_ref)
    assert right_node.key==3
    assert left_node.color == Color.BLACK
    assert right_node.color == Color.BLACK
    db.close()

'''
Tree Properties Being Tested: Okasaki Case 3 Rotation
Summary: Testing Okasaki Rebalance 3
'''
def test_ok3():
    os.remove("/tmp/test2.dbdb")
    db = connect("/tmp/test2.dbdb")
    db.set(1,'a')
    db.set(2,'b')
    db.set(3,'c')
    tree = db._tree
    node = tree._follow(tree._tree_ref)
    assert node.key==2
    left_node = tree._follow(node.left_ref)
    assert left_node.key==1
    right_node = tree._follow(node.right_ref)
    assert right_node.key==3
    assert left_node.color == Color.BLACK
    assert right_node.color == Color.BLACK
    db.close()

'''
Tree Properties Being Tested: Okasaki Case 4 Rotation
Summary: Testing Okasaki Rebalance 4
'''
def test_ok4():
    os.remove("/tmp/test2.dbdb")
    db = connect("/tmp/test2.dbdb")
    db.set(1,'a')
    db.set(3,'c')
    db.set(2,'b')
    tree = db._tree
    node = tree._follow(tree._tree_ref)
    assert node.key==2
    left_node = tree._follow(node.left_ref)
    assert left_node.key==1
    right_node = tree._follow(node.right_ref)
    assert right_node.key==3
    assert left_node.color == Color.BLACK
    assert right_node.color == Color.BLACK
    db.close()
