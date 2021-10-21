"""Dictionary that automatically adds children dictionaries as necessary
"""

from __future__ import annotations

import json
import os
import pathlib
from typing import Any


class AutoDict(dict):
  """Dictionary that automatically adds children dictionaries as necessary
  """

  def __init__(self, *args: Any, **kwargs: Any):
    """Initialize AutoDict

    Args:
      arguments passed to dict.__init__
    """
    super().__init__(*args, **kwargs)
    self["__type__"] = "AutoDict"

  def __missing__(self, key: Any):
    """Called when a key does not exist in the dictionary

    Args:
      key: Index of item that does not exist
    
    Returns:
      New AutoDict created at key location
    """
    value = self[key] = AutoDict()
    return value


class AutoDictEncoder(json.JSONEncoder):
  """AutoDict JSON encoder
  """

  def default(self, o) -> dict:
    if isinstance(o, AutoDict):
      return dict(o)
    return json.JSONEncoder.default(self, o)

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
    return data


class JSONAutoDict(AutoDict):
  """AutoDict with json file compatibility/autosaving
  """

  def __init__(self,
               path: str,
               save_on_exit: bool = False,
               encoder: json.JSONEncoder = AutoDictEncoder,
               decoder: function = AutoDictEncoder.decoder,
               *args: Any,
               **kwargs: Any) -> None:
    """Initialize JSONAutoDict

    Args:
      path: path to json file
      save_on_exit: True will save file when object is closed, False will not
      encoder: JSONEncoder used to serialize the object
      decoder: object_hook used to deserialize the object

      other arguments passed to AutoDict.__init__
    """
    super().__init__(*args, **kwargs)
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
