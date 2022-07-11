"""JSONDriver that uses the ujson library
"""

from __future__ import annotations

import datetime
import io
import os
from typing import Callable, Union
import uuid

try:
  import ujson
except ImportError as e:
  raise ImportError("Cannot use UltraJSONDriver without ujson installed") from e

from autodict.implementation import AutoDict
from autodict.json_drivers import base


class UltraJSONDriver(base.JSONDriver):
  """JSONDriver that uses the ujson library
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
        ujson.dump(obj, file, indent=indent, default=cls.default)
    else:
      if isinstance(fp, io.TextIOBase):
        ujson.dump(obj, fp, indent=indent, default=cls.default)
      else:
        s = ujson.dumps(obj, indent=indent, default=cls.default)
        fp.write(s.encode(encoding="utf-8"))

  @classmethod
  def dumps(cls, obj: AutoDict, indent: int = None) -> str:
    if indent is None:
      indent = 0
    return ujson.dumps(obj, indent=indent, default=cls.default)

  @classmethod
  def upgrade_dicts(
      cls, obj: Union[dict, list, str, int, float]
  ) -> Union[dict, list, str, int, float, AutoDict]:
    """Traverse an object and upgrade the dicts to AutoDicts

    Args:
      obj: JSON basic type object

    Returns:
      Appropriate Python object

    Raises:
      TypeError upon decoding error
    """
    if isinstance(obj, dict):
      for k, v in obj.items():
        obj[k] = cls.upgrade_dicts(v)
      return AutoDict(obj)
    if isinstance(obj, list):
      for i, v in enumerate(obj):
        obj[i] = cls.upgrade_dicts(v)
      return obj
    return obj

  @classmethod
  def load(cls, fp: Union[str, os.PathLike, io.IOBase]) -> AutoDict:
    return base.DefaultJSONDriver.load(fp)
    # ujson is faster but doesn't make upgrading to AutoDicts fast
    # if isinstance(fp, (str, os.PathLike)):
    #   with open(fp, "rb") as file:
    #     return cls.upgrade_dicts(ujson.loads(file.read()))
    # fp: Union[io.BytesIO, io.StringIO]
    # return cls.upgrade_dicts(ujson.loads(fp.read()))

  @classmethod
  def loads(cls, s: Union[str, bytes]) -> AutoDict:
    return base.DefaultJSONDriver.loads(s)
    # ujson is faster but doesn't make upgrading to AutoDicts fast
    # return cls.upgrade_dicts(ujson.loads(s))
