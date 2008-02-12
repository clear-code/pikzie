def metadata(name, value):
    def decorator(function):
        if not hasattr(function, metadata.container_key):
            setattr(function, metadata.container_key, {})
        getattr(function, metadata.container_key)[name] = value
        return function
    return decorator
metadata.container_key = "__metadata__"

def bug(id):
    return metadata("bug", id)
