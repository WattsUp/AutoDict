"""Test module json_drivers.rapidjson
"""

import json
import time

from tests import base
from tests.json_drivers.test_base import TestDefaultJSONDriver

import autodict
from autodict.json_drivers import rapidjson


class TestRapidJSONDriver(base.TestBase):
  """Test RapidJSONDriver
  """

  def test_default(self):
    result = rapidjson.RapidJSONDriver.default(
        TestDefaultJSONDriver.JSON_BASIC["date"])
    self.assertEqual(result,
                     TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED["date"])

    class UnknownType:
      pass

    o = UnknownType()
    self.assertRaises(TypeError, rapidjson.RapidJSONDriver.default, o)

  def test_dump(self):
    path = self._TEST_ROOT.joinpath("basic.json")

    rapidjson.RapidJSONDriver.dump(TestDefaultJSONDriver.JSON_BASIC, path)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    rapidjson.RapidJSONDriver.dump(TestDefaultJSONDriver.JSON_BASIC, str(path))
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    with open(path, "w", encoding="utf-8") as file:
      rapidjson.RapidJSONDriver.dump(TestDefaultJSONDriver.JSON_BASIC, file)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    with open(path, "wb") as file:
      rapidjson.RapidJSONDriver.dump(TestDefaultJSONDriver.JSON_BASIC,
                                     file,
                                     indent=2)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

  def test_dumps(self):
    s = rapidjson.RapidJSONDriver.dumps(TestDefaultJSONDriver.JSON_BASIC)
    json.loads(s)  # No JSON errors

    s = rapidjson.RapidJSONDriver.dumps(TestDefaultJSONDriver.JSON_BASIC,
                                        indent=2)
    json.loads(s)  # No JSON errors

  def test_object_hook(self):
    key = self.gen_string()
    value = self.gen_string()
    d = {key: value}

    result = autodict.DefaultJSONDriver.object_hook(d)
    self.assertIsInstance(result, autodict.AutoDict)

  def test_load(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    d = rapidjson.RapidJSONDriver.load(path)
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

    d = rapidjson.RapidJSONDriver.load(str(path))
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

    with open(path, "r", encoding="utf-8") as file:
      d = rapidjson.RapidJSONDriver.load(file)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

  def test_loads(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      d = rapidjson.RapidJSONDriver.loads(s)
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
      _ = rapidjson.RapidJSONDriver.loads(s)
    _ = rapidjson.RapidJSONDriver.loads(s_large)
    elapsed_rapidjson = time.perf_counter() - start

    self.log_speed(elapsed_default, elapsed_rapidjson)

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
    rapidjson.RapidJSONDriver.dump(d, path)
    elapsed_rapidjson = time.perf_counter() - start

    self.log_speed(elapsed_default, elapsed_rapidjson)
