"""autodict

Dictionary that automatically adds children dictionaries as necessary
"""

from autodict import version

__version__ = version.version_full

from autodict.implementation import AutoDict
from autodict.json_drivers import *
