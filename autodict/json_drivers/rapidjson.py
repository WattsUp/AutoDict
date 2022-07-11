"""JSONDriver that uses the rapidjson library
"""

from __future__ import annotations

import datetime
import io
import os
from typing import Callable, Union
import uuid

try:
  import rapidjson
except ImportError as e:
  raise ImportError(
      "Cannot use RapidJSONDriver without rapidjson installed") from e

from autodict.implementation import AutoDict
from autodict.json_drivers import base


class RapidJSONDriver(base.JSONDriver):
  """JSONDriver that uses the rapidjson library
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
        rapidjson.dump(obj,
                       file,
                       indent=indent,
                       default=cls.default,
                       datetime_mode=rapidjson.DM_ISO8601,
                       uuid_mode=rapidjson.UM_CANONICAL)
    else:
      if isinstance(fp, io.TextIOBase):
        rapidjson.dump(obj,
                       fp,
                       indent=indent,
                       default=cls.default,
                       datetime_mode=rapidjson.DM_ISO8601,
                       uuid_mode=rapidjson.UM_CANONICAL)
      else:
        s = rapidjson.dumps(obj,
                            indent=indent,
                            default=cls.default,
                            datetime_mode=rapidjson.DM_ISO8601,
                            uuid_mode=rapidjson.UM_CANONICAL)
        fp.write(s.encode(encoding="utf-8"))

  @classmethod
  def dumps(cls, obj: AutoDict, indent: int = None) -> str:
    if indent is None:
      indent = 0
    return rapidjson.dumps(obj,
                           indent=indent,
                           default=cls.default,
                           datetime_mode=rapidjson.DM_ISO8601,
                           uuid_mode=rapidjson.UM_CANONICAL)

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
        return rapidjson.load(file, object_hook=cls.object_hook)
    return rapidjson.load(fp, object_hook=cls.object_hook)

  @classmethod
  def loads(cls, s: Union[str, bytes]) -> AutoDict:
    return rapidjson.loads(s, object_hook=cls.object_hook)
