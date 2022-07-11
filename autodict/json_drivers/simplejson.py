"""JSONDriver that uses the simplejson library
"""

from __future__ import annotations

import datetime
import io
import os
from typing import Callable, Union
import uuid

try:
  import simplejson
except ImportError as e:
  raise ImportError(
      "Cannot use SimpleJSONDriver without simplejson installed") from e

from autodict.implementation import AutoDict
from autodict.json_drivers import base


class SimpleJSONDriver(base.JSONDriver):
  """JSONDriver that uses the simplejson library
  """

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
    if indent is None:
      indent = 0
    if isinstance(fp, (str, os.PathLike)):
      with open(fp, "w", encoding="utf-8") as file:
        simplejson.dump(obj, file, indent=indent, default=cls.default)
    else:
      if isinstance(fp, io.TextIOBase):
        simplejson.dump(obj, fp, indent=indent, default=cls.default)
      else:
        s = simplejson.dumps(obj, indent=indent, default=cls.default)
        fp.write(s.encode(encoding="utf-8"))

  @classmethod
  def dumps(cls, obj: AutoDict, indent: int = None) -> str:
    if indent is None:
      indent = 0
    return simplejson.dumps(obj, indent=indent, default=cls.default)

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
        return simplejson.load(file, object_hook=cls.object_hook)
    return simplejson.load(fp, object_hook=cls.object_hook)

  @classmethod
  def loads(cls, s: Union[str, bytes]) -> AutoDict:
    return simplejson.loads(s, object_hook=cls.object_hook)
