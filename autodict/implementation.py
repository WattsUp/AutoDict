"""Dictionary that automatically adds children dictionaries as necessary
"""

from __future__ import annotations


class AutoDict(dict):
  """Dictionary that automatically adds children dictionaries as necessary
  """

  def __missing__(self, key: object):
    """Called when a key does not exist in the dictionary

    Args:
      key: Index of item that does not exist

    Returns:
      New AutoDict created at key location
    """
    value = self[key] = AutoDict()
    return value

  def contains(self, *keys: object) -> bool:
    """Check for the presence of keys in dictionary

    Supply multiple keys to check children. Only descends other AutoDicts

    contains("level0", "level1", key) will return True when AutoDict is
    structured as follows:
    {"level0": {"level1": {"key": _ }}}

    Args:
      keys: one or more keys to check for (cascading levels)

    Returns:
      True when key(s) exist
    """
    first_key = keys[0]
    if len(keys) == 1:
      return super().__contains__(first_key)
    if not super().__contains__(first_key):
      return False
    keys = keys[1:]
    obj = self[first_key]
    if isinstance(obj, AutoDict):
      return obj.contains(*keys)
    if len(keys) == 1:
      return keys[0] in obj
    return keys in obj

  def __contains__(self, o: object) -> bool:
    if isinstance(o, list):
      return self.contains(*o)
    return super().__contains__(o)
