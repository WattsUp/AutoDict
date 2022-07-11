"""JSONDriver that uses the orjson library
"""

from __future__ import annotations

import io
import os
from typing import Callable, Union

try:
  import orjson
except ImportError as e:
  raise ImportError("Cannot use OrjsonDriver without orjson installed") from e

from autodict.implementation import AutoDict
from autodict.json_drivers import base


class OrjsonDriver(base.JSONDriver):
  """JSONDriver that uses the orjson library
  """

  TYPES_SERIALIZE = {}

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
      s = orjson.dumps(obj, default=cls.default)
    else:
      s = orjson.dumps(obj, default=cls.default, option=orjson.OPT_INDENT_2)
    if isinstance(fp, (str, os.PathLike)):
      with open(fp, "wb") as file:
        file.write(s)
    else:
      if isinstance(fp, io.TextIOBase):
        fp.write(s.decode(encoding="utf-8"))
      else:
        fp.write(s)

  @classmethod
  def dumps(cls, obj: AutoDict, indent: int = None) -> str:
    if indent is None:
      return orjson.dumps(obj, default=cls.default)
    return orjson.dumps(obj, default=cls.default, option=orjson.OPT_INDENT_2)

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
    # orjson is faster but doesn't make upgrading to AutoDicts fast
    # if isinstance(fp, (str, os.PathLike)):
    #   with open(fp, "rb") as file:
    #     return cls.upgrade_dicts(orjson.loads(file.read()))
    # fp: Union[io.BytesIO, io.StringIO]
    # return cls.upgrade_dicts(orjson.loads(fp.read()))

  @classmethod
  def loads(cls, s: Union[str, bytes]) -> AutoDict:
    return base.DefaultJSONDriver.loads(s)
    # orjson is faster but doesn't make upgrading to AutoDicts fast
    # return cls.upgrade_dicts(orjson.loads(s))
