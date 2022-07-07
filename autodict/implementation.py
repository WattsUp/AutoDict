"""Dictionary that automatically adds children dictionaries as necessary
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import datetime
import io
import json
import os
import pathlib
import re
from typing import Callable, Union
import uuid


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


class JSONDriver(ABC):
  """Drivers to dump an AutoDict to json and load from json
  """

  @classmethod
  @abstractmethod
  def dump(cls,
           obj: AutoDict,
           fp: Union[os.PathLike, io.IOBase],
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
  def load(cls, fp: Union[os.PathLike, io.IOBase]) -> AutoDict:
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

  # Objects of these types will be serialized explicitly
  # i.e. key: value => key: {"__type__": "AutoDict", "v": value}
  EXPLICIT_TYPES_SERIALIZE = {
      datetime.datetime: ("datetime", lambda t: t.isoformat()),
      datetime.date: ("date", lambda t: t.isoformat()),
      datetime.time: ("time", lambda t: t.isoformat()),
      uuid.UUID: ("uuid", str)
  }

  EXPLICIT_TYPES_DESERIALIZE = {
      "datetime": datetime.datetime.fromisoformat,
      "date": datetime.date.fromisoformat,
      "time": datetime.time.fromisoformat,
      "uuid": uuid.UUID
  }

  # Objects of these types will be serialized implicitly
  # i.e. key: value => key: str(value)
  IMPLICIT_TYPES_SERIALIZE = {
      datetime.datetime: lambda t: t.isoformat(),
      datetime.date: lambda t: t.isoformat(),
      datetime.time: lambda t: t.isoformat(),
      uuid.UUID: str
  }

  IMPLICIT_TYPES_DESERIALIZE = {
      re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\+\d{2}:\d{2})?$"):
          datetime.datetime.fromisoformat,
      re.compile(r"^\d{4}-\d{2}-\d{2}$"):
          datetime.date.fromisoformat,
      re.compile(r"^\d{2}:\d{2}:\d{2}(\+\d{2}:\d{2})?$"):
          datetime.time.fromisoformat,
      re.compile(
          r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
          r"[0-9a-f]{4}-[0-9a-f]{12}$",
          flags=re.I):
          uuid.UUID
  }

  @classmethod
  def serialize(cls, obj: object) -> Union[str, dict, list, int, float]:
    """Serialize an object into a JSON basic type

    Args:
      obj: Object to serialize

    Returns:
      Serialized object in JSON basic types

    Raises:
      TypeError upon encoding error
    """
    if isinstance(obj, dict):
      # Process children
      d = {}
      for k, v in obj.items():
        d[k] = cls.serialize(v)

      if isinstance(obj, AutoDict):
        d["__type__"] = "AutoDict"
      return d
    if isinstance(obj, list):
      l = []
      for v in obj:
        l.append(cls.serialize(v))
      return l
    if isinstance(obj, (str, int, float)):
      return obj

    # Implicit has higher priority
    for t, op in cls.IMPLICIT_TYPES_SERIALIZE.items():
      op: Callable
      if isinstance(obj, t):
        return op(obj)

    for t, (type_str, op) in cls.EXPLICIT_TYPES_SERIALIZE.items():
      type_str: str
      op: Callable
      if isinstance(obj, t):
        return {"__type__": type_str, "v": op(obj)}

    raise TypeError(f"AutoDict encoder cannot encode type='{type(obj)}'")

  @classmethod
  def dump(cls,
           obj: AutoDict,
           fp: Union[os.PathLike, io.IOBase],
           indent: int = None) -> None:
    d = cls.serialize(obj)
    if isinstance(fp, os.PathLike):
      with open(fp, "w", encoding="utf-8") as file:
        json.dump(d, file, indent=indent)
    else:
      json.dump(d, fp, indent=indent)

  @classmethod
  def dumps(cls, obj: AutoDict, indent: int = None) -> str:
    d = cls.serialize(obj)
    return json.dumps(d, indent=indent)

  @classmethod
  def deserialize(cls, obj: Union[str, dict, list, int, float]) -> object:
    """Deserialize a JSON basic type into an appropriate Python object

    Args:
      obj: JSON basic type object

    Returns:
      Appropriate Python object

    Raises:
      TypeError upon decoding error
    """
    if isinstance(obj, dict):
      t = obj.pop("__type__", None)
      if t is not None and t != "AutoDict":
        class_type = cls.EXPLICIT_TYPES_DESERIALIZE.get(t, None)
        if class_type is None:
          raise TypeError(f"AutoDict decoder cannot decode __type__='{t}'")
        return class_type(obj["v"])

      # Process children
      for k, v in obj.items():
        obj[k] = cls.deserialize(v)
      if t is None:
        return obj
      return AutoDict(obj)
    elif isinstance(obj, list):
      # Process children
      for i, v in enumerate(obj):
        obj[i] = cls.deserialize(v)
      return obj
    elif isinstance(obj, str):
      # Could be an implicit type or a plain string
      for regex, op in cls.IMPLICIT_TYPES_DESERIALIZE.items():
        regex: re.Pattern
        op: Callable
        if regex.match(obj):
          return op(obj)
      return obj
    else:
      return obj

  @classmethod
  def load(cls, fp: Union[os.PathLike, io.IOBase]) -> AutoDict:
    if isinstance(fp, os.PathLike):
      with open(fp, "r", encoding="utf-8") as file:
        d = json.load(file)
    else:
      d = json.load(fp)
    return cls.deserialize(d)

  @classmethod
  def loads(cls, s: Union[str, bytes]) -> AutoDict:
    d = json.loads(s)
    return cls.deserialize(d)


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
    if os.path.exists(path):
      data = driver.load(path)
      for k, v in data.items():
        self[k] = v

  def save(self, indent: int = None) -> None:
    """Write AutoDict to file

    Args:
      indent: Indentation parameter passed to JSONDriver.dump
    """
    self._path.parent.mkdir(parents=True, exist_ok=True)
    self._driver.dump(self._path, self, indent=indent)

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
      self._save_on_exit = False
