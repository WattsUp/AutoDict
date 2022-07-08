"""Default JSONDriver that uses the built-in json library
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import datetime
import io
import json
import os
import pathlib
from typing import Callable, Union
import uuid

from autodict.implementation import AutoDict


class JSONDriver(ABC):
  """Drivers to dump an AutoDict to json and load from json
  """

  @classmethod
  @abstractmethod
  def dump(cls,
           obj: AutoDict,
           fp: Union[str, os.PathLike, io.IOBase],
           indent: int = None) -> None:
    """Dump AutoDict to a file

    Args:
      obj: AutoDict to dump
      fp: Path to file or object with a write() function
      indent: A number will pretty-print the JSON, None will not
    """
    pass  # pragma: no cover

  @classmethod
  @abstractmethod
  def dumps(cls, obj: AutoDict, indent: int = None) -> str:
    """Dump AutoDict to a file

    Args:
      obj: AutoDict to dump
      indent: A number will pretty-print the JSON, None will not

    Returns:
      JSON in a string
    """
    pass  # pragma: no cover

  @classmethod
  @abstractmethod
  def load(cls, fp: Union[str, os.PathLike, io.IOBase]) -> AutoDict:
    """Load a JSON file into an AutoDict

    Args:
      fp: Path to file or object with a read() function

    Returns:
      Loaded JSON object
    """
    pass  # pragma: no cover

  @classmethod
  @abstractmethod
  def loads(cls, s: Union[str, bytes]) -> AutoDict:
    """Load a JSON string into an AutoDict

    Args:
      s: JSON string to parse

    Returns:
      Loaded JSON object
    """
    pass  # pragma: no cover


class DefaultJSONDriver(JSONDriver):
  """Default JSONDriver that uses the built-in json library"""

  TYPES_SERIALIZE = {
      datetime.datetime: lambda t: t.isoformat(),
      datetime.date: lambda t: t.isoformat(),
      datetime.time: lambda t: t.isoformat(),
      uuid.UUID: str
  }

  @classmethod
  def default(cls, obj: object) -> Union[str, dict, list, int, float]:
    """Serialize an object into a JSON basic type

    Args:
      obj: Object to serialize

    Returns:
      Serialized object in JSON basic types

    Raises:
      TypeError upon encoding error
    """
    for t, op in cls.TYPES_SERIALIZE.items():
      op: Callable
      if isinstance(obj, t):
        return op(obj)

    raise TypeError(f"AutoDict encoder cannot encode type='{type(obj)}'")

  @classmethod
  def dump(cls,
           obj: AutoDict,
           fp: Union[str, os.PathLike, io.IOBase],
           indent: int = None) -> None:
    if isinstance(fp, (str, os.PathLike)):
      with open(fp, "w", encoding="utf-8") as file:
        json.dump(obj, file, indent=indent, default=cls.default)
    else:
      if isinstance(fp, io.TextIOBase):
        json.dump(obj, fp, indent=indent, default=cls.default)
      else:
        s = json.dumps(obj, indent=indent, default=cls.default)
        fp.write(s.encode(encoding="utf-8"))

  @classmethod
  def dumps(cls, obj: AutoDict, indent: int = None) -> str:
    return json.dumps(obj, indent=indent, default=cls.default)

  @classmethod
  def object_hook(cls, d: dict) -> object:
    """Object hook called when decoder encounters an object aka dict

    Args:
      d: JSON object literal

    Returns:
      Appropriate Python object

    Raises:
      TypeError upon decoding error
    """
    return AutoDict(d)

  @classmethod
  def load(cls, fp: Union[str, os.PathLike, io.IOBase]) -> AutoDict:
    if isinstance(fp, (str, os.PathLike)):
      with open(fp, "r", encoding="utf-8") as file:
        return json.load(file, object_hook=cls.object_hook)
    return json.load(fp, object_hook=cls.object_hook)

  @classmethod
  def loads(cls, s: Union[str, bytes]) -> AutoDict:
    return json.loads(s, object_hook=cls.object_hook)


class JSONAutoDict(AutoDict):
  """AutoDict with json file compatibility/autosaving
  """

  def __init__(self,
               path: str,
               *,
               save_on_exit: bool = True,
               driver: JSONDriver = None,
               **kwargs) -> None:
    """Initialize JSONAutoDict

    Args:
      path: path to json file
      save_on_exit: True will save file when object is closed, False will not
      driver: JSONDriver to serialize/deserialize the object, None will use the
        built-in json library via DefaultJSONDriver

      other arguments passed to AutoDict.__init__
    """
    super().__init__(**kwargs)
    self._save_on_exit = save_on_exit
    if driver is None:
      driver = DefaultJSONDriver
    self._driver = driver

    self._path = pathlib.Path(path)
    if self._path.exists():
      data = driver.load(self._path)
      for k, v in data.items():
        self[k] = v

  def save(self, indent: int = None) -> None:
    """Write AutoDict to file

    Args:
      indent: Indentation parameter passed to JSONDriver.dump
    """
    self._path.parent.mkdir(parents=True, exist_ok=True)
    self._driver.dump(self, self._path, indent=indent)

  def __enter__(self) -> JSONAutoDict:
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
      self._save_on_exit = False
