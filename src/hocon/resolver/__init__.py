"""Turns parsed list/dict containing UnresolvedXXX objects into list/dict of python native types."""

from ._resolver import resolve

__all__ = ("resolve",)
