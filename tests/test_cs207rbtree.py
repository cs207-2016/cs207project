
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
import numpy as np
import random
import math
import datetime
import os

from context import *

'''
Functions Being Tested: Get
Summary: Basic Get Test
'''
def test_get():
    try:
        os.remove("/tmp/test2.dbdb")
    except:
        None
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
    try:
        os.remove("/tmp/test2.dbdb")
    except:
        None
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
Tree Properties Being Tested: Left Child < Parent
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
    try:
        os.remove("/tmp/test2.dbdb")
    except:
        None
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
    try:
        os.remove("/tmp/test2.dbdb")
    except:
        None
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
    try:
        os.remove("/tmp/test2.dbdb")
    except:
        None
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
    try:
        os.remove("/tmp/test2.dbdb")
    except:
        None
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

'''
Functions Being Tested: Get
Summary: Get KeyError Test
'''
def test_get_keyerror():
    try:
        os.remove("/tmp/test2.dbdb")
    except:
        None
    db = connect("/tmp/test2.dbdb")
    for i in range(97,108):
        db.set(i,chr(i))
    with raises(KeyError):
        db.get(5)
    db.close()

'''
Functions Being Tested: Get
Summary: Get KeyError Test 2
'''
def test_get_keyerror2():
    try:
        os.remove("/tmp/test2.dbdb")
    except:
        None
    db = connect("/tmp/test2.dbdb")
    for i in range(97,108):
        db.set(i,chr(i))
    try:
        db.get(5)
        result = True
    except:
        result = False
    assert result == False
    db.close()

'''
Functions Being Tested: rbtree -> get_All_LTE()
Summary: Test getting all Less than or Equal to (Keys)
'''
def test_db_get_All_LTE():
    dbName = "/tmp/test2.dbdb"
    if os.path.exists(dbName):
         os.remove(dbName)
    db = connect(dbName)
    db.set(4.4, "ts484.dat")
    db.set(0.0, "ts3.dat") #vantagePT
    db.set(1.3, "ts82.dat")
    db.set(2.9, "ts84.dat")
    db.set(2.3, "ts382.dat")
    db.set(2.1, "ts52.dat")
    db.set(1.8, "ts49.dat")
    db.set(1.1, "ts77.dat")
    db.set(5.3, "ts583.dat")
    keys, vals = db.get_All_LTE(2.9)
    assert keys == [2.1, 2.9, 2.3, 1.3, 1.8, 0.0, 1.1]
    db.commit()
    db.close()

'''
Functions Being Tested: rbtree -> get_All_LTE2()
Summary: Test getting all Less than or Equal to (Vals)
'''
def test_db_get_All_LTE2():
    dbName = "/tmp/test2.dbdb"
    if os.path.exists(dbName):
         os.remove(dbName)
    db = connect(dbName)
    db.set(4.4, "ts484.dat")
    db.set(0.0, "ts3.dat") #vantagePT
    db.set(1.3, "ts82.dat")
    db.set(2.9, "ts84.dat")
    db.set(2.3, "ts382.dat")
    db.set(2.1, "ts52.dat")
    db.set(1.8, "ts49.dat")
    db.set(1.1, "ts77.dat")
    db.set(5.3, "ts583.dat")
    keys, vals = db.get_All_LTE(2.9)
    assert vals == ['ts52.dat','ts84.dat','ts382.dat','ts82.dat','ts49.dat','ts3.dat','ts77.dat']
    db.commit()
    db.close()

'''
Functions Being Tested: rbtree -> connect, set, commit, close, get
Summary: Test set and get for a DB
'''
def test_db_get():
    dbName = "/tmp/test2.dbdb"
    if os.path.exists(dbName):
         os.remove(dbName)
    db = connect(dbName)
    db.set("rahul", "aged")
    db.set("pavlos", "aged")
    db.set("kobe", "stillyoung")
    db.commit()
    db.close()
    db = connect("/tmp/test2.dbdb")
    assert db.get("rahul") == "aged"
    db.commit()
    db.close()

'''
Functions Being Tested: rbtree -> set (override)
Summary: Test set (override) and get for a DB
'''
def test_db_set():
    dbName = "/tmp/test2.dbdb"
    if os.path.exists(dbName):
         os.remove(dbName)
    db = connect(dbName)
    db.set("rahul", "aged")
    db.set("pavlos", "aged")
    db.set("kobe", "stillyoung")
    db.commit()
    db.close()
    db = connect("/tmp/test2.dbdb")
    db.set("rahul", "young")
    db.get("rahul")
    assert db.get("rahul") == "young"
    db.commit()
    db.close()

'''
Functions Being Tested: get() -> Key Error
Summary: If key isn't there, raise KeyError
'''
def test_db_get_error():
    dbName = "/tmp/test2.dbdb"
    if os.path.exists(dbName):
         os.remove(dbName)
    db = connect(dbName)
    db.set(4.4, "ts484.dat")
    with raises(KeyError):
        db.get(3.9)
    db.commit()
    db.close()
