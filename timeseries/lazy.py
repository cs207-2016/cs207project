class LazyOperation():
    def __init__(self, function, *args, **kwargs):
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def eval(self):
        # Recursively eval() lazy args
        new_args = [a.eval() if isinstance(a,LazyOperation) else a for a in self._args]
        new_kwargs = {k:v.eval() if isinstance(v,LazyOperation) else v for k,v in self._kwargs}
        return self._function(*new_args, **new_kwargs)

    # Debug:
    def thunk_tree(self, indent='| '):
        s = indent[:-2]+'| ['+self._function.__name__+']\n'
        for a in self._args:
            if isinstance(a, LazyOperation):
                s += a.thunk_tree(indent=indent+'| ')
            else:
                s += indent+'| '+str(a)+'\n'
        for k,v in self._kwargs:
            if isinstance(a, LazyOperation):
                s += str(k)+'='+v.thunk_tree(indent=indent+'| ')
            else:
                s += indent+'| '+str(k)+'='+str(v)+'\n'
        return s

def lazy(function):
    def create_thunk(*args, **kwargs):
        return LazyOperation(function, *args, **kwargs)
    return create_thunk
