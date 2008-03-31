def metadata(name, value):
    """Set metadata to a method."""
    def decorator(function):
        if not hasattr(function, metadata.container_key):
            setattr(function, metadata.container_key, {})
        getattr(function, metadata.container_key)[name] = value
        return function
    return decorator
metadata.container_key = "__metadata__"

def bug(id):
    """Set Bug ID to a method."""
    return metadata("bug", id)

def priority(priority):
    """Set priority of test."""
    return metadata("priority", priority)
