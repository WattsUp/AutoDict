"""Test module json_drivers.simplejson
"""

import json
import time

from tests import base
from tests.json_drivers.test_base import TestDefaultJSONDriver

import autodict
from autodict.json_drivers import simplejson


class TestSimpleJSONDriver(base.TestBase):
  """Test SimpleJSONDriver
  """

  def test_default(self):
    result = simplejson.SimpleJSONDriver.default(
        TestDefaultJSONDriver.JSON_BASIC["date"])
    self.assertEqual(result,
                     TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED["date"])

    class UnknownType:
      pass

    o = UnknownType()
    self.assertRaises(TypeError, simplejson.SimpleJSONDriver.default, o)

  def test_dump(self):
    path = self._TEST_ROOT.joinpath("basic.json")

    simplejson.SimpleJSONDriver.dump(TestDefaultJSONDriver.JSON_BASIC, path)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    simplejson.SimpleJSONDriver.dump(TestDefaultJSONDriver.JSON_BASIC,
                                     str(path))
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    with open(path, "w", encoding="utf-8") as file:
      simplejson.SimpleJSONDriver.dump(TestDefaultJSONDriver.JSON_BASIC, file)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    with open(path, "wb") as file:
      simplejson.SimpleJSONDriver.dump(TestDefaultJSONDriver.JSON_BASIC,
                                       file,
                                       indent=2)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

  def test_dumps(self):
    s = simplejson.SimpleJSONDriver.dumps(TestDefaultJSONDriver.JSON_BASIC)
    json.loads(s)  # No JSON errors

    s = simplejson.SimpleJSONDriver.dumps(TestDefaultJSONDriver.JSON_BASIC,
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

    d = simplejson.SimpleJSONDriver.load(path)
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

    d = simplejson.SimpleJSONDriver.load(str(path))
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

    with open(path, "r", encoding="utf-8") as file:
      d = simplejson.SimpleJSONDriver.load(file)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

  def test_loads(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      d = simplejson.SimpleJSONDriver.loads(s)
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
      _ = simplejson.SimpleJSONDriver.loads(s)
    _ = simplejson.SimpleJSONDriver.loads(s_large)
    elapsed_simplejson = time.perf_counter() - start

    self.log_speed(elapsed_default, elapsed_simplejson)

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
    simplejson.SimpleJSONDriver.dump(d, path)
    elapsed_simplejson = time.perf_counter() - start

    self.log_speed(elapsed_default, elapsed_simplejson)
