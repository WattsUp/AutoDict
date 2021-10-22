"""autodict

Dictionary that automatically adds children dictionaries as necessary
"""

from . import version

__version__ = version.version_full

__all__ = ['implementation']

from autodict.implementation import AutoDict, JSONAutoDict
