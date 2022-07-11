"""Test module json_drivers.orjson
"""

import datetime
import json
import time

from tests import base
from tests.json_drivers.test_base import TestDefaultJSONDriver

import autodict
from autodict.json_drivers import orjson


class TestOrjsonDriver(base.TestBase):
  """Test OrjsonDriver
  """

  def test_default(self):

    class UnknownType:
      pass

    o = UnknownType()
    self.assertRaises(TypeError, orjson.OrjsonDriver.default, o)

    class Driver(orjson.OrjsonDriver):
      TYPES_SERIALIZE = {
          datetime.datetime: lambda t: t.isoformat(),
          UnknownType: lambda _: "123"
      }

    result = Driver.default(o)
    self.assertEqual(result, "123")

  def test_dump(self):
    path = self._TEST_ROOT.joinpath("basic.json")

    orjson.OrjsonDriver.dump(TestDefaultJSONDriver.JSON_BASIC, path)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    orjson.OrjsonDriver.dump(TestDefaultJSONDriver.JSON_BASIC, str(path))
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    with open(path, "w", encoding="utf-8") as file:
      orjson.OrjsonDriver.dump(TestDefaultJSONDriver.JSON_BASIC, file)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    with open(path, "wb") as file:
      orjson.OrjsonDriver.dump(TestDefaultJSONDriver.JSON_BASIC, file, indent=2)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

  def test_dumps(self):
    s = orjson.OrjsonDriver.dumps(TestDefaultJSONDriver.JSON_BASIC)
    json.loads(s)  # No JSON errors

    s = orjson.OrjsonDriver.dumps(TestDefaultJSONDriver.JSON_BASIC, indent=2)
    json.loads(s)  # No JSON errors

  def test_upgrade_dicts(self):
    key = self.gen_string()
    value = self.gen_string()
    d = {key: value}

    result = orjson.OrjsonDriver.upgrade_dicts(d)
    self.assertIsInstance(result, autodict.AutoDict)

    result = orjson.OrjsonDriver.upgrade_dicts(key)
    self.assertEqual(result, key)

    l = [d, d]

    result = orjson.OrjsonDriver.upgrade_dicts(l)
    self.assertIsInstance(result, list)
    self.assertIsInstance(result[0], autodict.AutoDict)

  def test_load(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    d = orjson.OrjsonDriver.load(path)
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

    d = orjson.OrjsonDriver.load(str(path))
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

    with open(path, "r", encoding="utf-8") as file:
      d = orjson.OrjsonDriver.load(file)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

  def test_loads(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      d = orjson.OrjsonDriver.loads(s)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

  def test_speed_load(self):
    path = self._DATA_ROOT.joinpath("basic.json")
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
    path_large = self._DATA_ROOT.joinpath("basic_large.json")
    with open(path_large, "r", encoding="utf-8") as file:
      s_large = file.read()

    n = 1000

    start = time.perf_counter()
    for _ in range(n):
      _ = autodict.DefaultJSONDriver.loads(s)
    _ = autodict.DefaultJSONDriver.loads(s_large)
    elapsed_default = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(n):
      _ = orjson.OrjsonDriver.loads(s)
    _ = orjson.OrjsonDriver.loads(s_large)
    elapsed_orjson = time.perf_counter() - start

    self.log_speed(elapsed_default, elapsed_orjson)

  def test_speed_dump(self):
    path = self._TEST_ROOT.joinpath("basic_large.json")

    d = autodict.AutoDict()
    n = 10000
    for i in range(n):
      d[str(i)] = TestDefaultJSONDriver.JSON_BASIC
      d["list"] = [TestDefaultJSONDriver.JSON_BASIC] * n

    start = time.perf_counter()
    autodict.DefaultJSONDriver.dump(d, path)
    elapsed_default = time.perf_counter() - start

    path.unlink()

    start = time.perf_counter()
    orjson.OrjsonDriver.dump(d, path)
    elapsed_orjson = time.perf_counter() - start

    self.log_speed(elapsed_default, elapsed_orjson)
