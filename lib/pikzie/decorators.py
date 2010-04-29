# Copyright (C) 2009-2010  Kouhei Sutou <kou@clear-code.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = ["metadata", "bug", "priority", "data"]

def override_setter(container, name, value):
    container[name] = value

def append_setter(container, name, value):
    if container.get(name) is None:
        container[name] = []
    container[name].append(value)

def metadata(name, value, setter=None):
    """Set metadata to a method."""
    if setter is None:
        setter = override_setter
    def decorator(function):
        if not hasattr(function, metadata.container_key):
            setattr(function, metadata.container_key, {})
        setter(getattr(function, metadata.container_key), name, value)
        return function
    return decorator
metadata.container_key = "__metadata__"

def bug(id):
    """Set Bug ID to a method."""
    return metadata("bug", id)

def priority(priority):
    """Set priority of test."""
    return metadata("priority", priority)

def data(label, value):
    """Set test data."""
    return metadata("data", {"label": label, "value": value}, append_setter)
