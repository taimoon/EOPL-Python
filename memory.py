from dataclasses import dataclass
the_store = []

@dataclass
class Immutable:
    val:None

def empty_store():
    return []

def get_store():
    return the_store

def init_store():
    global the_store
    the_store = empty_store()

def is_reference(id):
    return isinstance(id,int)

def newref(val):
    the_store.append(val)
    ref = len(the_store) - 1
    return ref

def deref(ref):
    return the_store[ref]

def setref(ref,val):
    the_store[ref] = val