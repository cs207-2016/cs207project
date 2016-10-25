def lazy(function):
    def create_thunk(*args, **kwargs):
        return LazyOperation(function, *args, **kwargs)
    return create_thunk
