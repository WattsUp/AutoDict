"""Dictionary that automatically adds children dictionaries as necessary
"""

from __future__ import annotations

import json
import os
import pathlib
from typing import Callable


class AutoDict(dict):
  """Dictionary that automatically adds children dictionaries as necessary
  """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self["__type__"] = "AutoDict"

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
    if isinstance(self[first_key], AutoDict):
      return self[first_key].contains(*keys)
    if len(keys) == 1:
      return keys[0] in self[first_key]
    return keys in self[first_key]

  def __contains__(self, o: object) -> bool:
    if isinstance(o, list):
      return self.contains(*o)
    return super().__contains__(o)

  @staticmethod
  def decoder(data: dict) -> object:
    """Decode a dictionary object into the appropriate class type

    Args:
      data: dictionary representation of object

    Returns:
      class representation of object
    """
    if "__type__" in data:
      t = data["__type__"]
      if t == "AutoDict":
        return AutoDict(data)
      raise TypeError(f'AutoDict decoder cannot decode __type__="{t}"')
    return data


class JSONAutoDict(AutoDict):
  """AutoDict with json file compatibility/autosaving
  """

  def __init__(self,
               path: str,
               *,
               save_on_exit: bool = False,
               encoder: json.JSONEncoder = None,
               decoder: Callable = AutoDict.decoder,
               **kwargs) -> None:
    """Initialize JSONAutoDict

    Args:
      path: path to json file
      save_on_exit: True will save file when object is closed, False will not
      encoder: JSONEncoder used to serialize the object
      decoder: object_hook used to deserialize the object

      other arguments passed to AutoDict.__init__
    """
    super().__init__(**kwargs)
    self._save_on_exit = save_on_exit
    self._encoder = encoder
    self._decoder = decoder

    self._path = path
    if os.path.exists(path):
      with open(path, "r", encoding="utf-8") as file:
        data = json.load(file, object_hook=self._decoder)
        for k, v in data.items():
          self[k] = v

  def save(self, indent: int = 2) -> None:
    """Write AutoDict to file

    Args:
      indent: Indentation parameter passed to json.dump
    """
    pathlib.Path(self._path).parent.mkdir(parents=True, exist_ok=True)
    with open(self._path, "w", encoding="utf-8") as file:
      json.dump(dict(self), file, cls=self._encoder, indent=indent)

  def __enter__(self) -> AutoDict:
    """Enter ContextManager
    Returns:
      self
    """
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
    """Exit ContextManager
    """
    if self._save_on_exit:
      self.save()
      self._save_on_exit = False

  def __del__(self) -> None:
    """Object destructor
    """
    if self._save_on_exit:
      self.save()
