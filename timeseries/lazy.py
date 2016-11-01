class LazyOperation():
    def __init__(self, function, *args, **kwargs):
        '''Inits a LazyOperation that stores the provided function and arguments'''
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def eval(self):
        '''Recursively evaluates all of the lazy arguments'''
        new_args = [a.eval() if isinstance(a,LazyOperation) else a for a in self._args]
        new_kwargs = {k:v.eval() if isinstance(v,LazyOperation) else v for k,v in self._kwargs}
        return self._function(*new_args, **new_kwargs)

def lazy(function):
    '''A decorator to create a lazy version of a function. Stores the function
    and arguments in a thunk for later evaluation'''
    def create_thunk(*args, **kwargs):
        return LazyOperation(function, *args, **kwargs)
    return create_thunk

@lazy
def lazy_add(a,b):
    '''Lazy addition. Stores arguments and function for later evaluation'''
     return a+b

@lazy
def lazy_mul(a,b):
    '''Lazy multiplication. Stores arguments and function for later evaluation'''
     return a*b
