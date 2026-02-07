"""Turns parsed list/dict containing UnresolvedXXX objects into list/dict of python native types."""

from ._lazy_resolver import merge
from ._resolver import resolve

__all__ = ("merge", "resolve")
