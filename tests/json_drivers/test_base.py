"""Test module autodict
"""

import datetime
import json
import uuid

from tests import base

import autodict


class TestDefaultJSONDriver(base.TestBase):
  """Test DefaultJSONDriver
  """

  _TIMESTAMP = datetime.datetime(2000,
                                 9,
                                 1,
                                 21,
                                 55,
                                 2,
                                 tzinfo=datetime.timezone.utc)
  JSON_BASIC = autodict.AutoDict({
      "datetime": _TIMESTAMP,
      "date": _TIMESTAMP.date(),
      "time": _TIMESTAMP.time(),
      "name": "Whoami",
      "int": 123456789,
      "float": 1.23456789,
      "uuid": uuid.UUID("5d1e22eb-d9b2-48cd-b081-d1056d267f28"),
      "list": [1, 2, 4, autodict.AutoDict(num=5)],
      "child": {
          "name": "Plain"
      },
      "other child": autodict.AutoDict(name="Not plain")
  })

  JSON_BASIC_DESERIALIZED = autodict.AutoDict({
      "datetime": _TIMESTAMP.isoformat(),
      "date": _TIMESTAMP.date().isoformat(),
      "time": _TIMESTAMP.time().isoformat(),
      "name": "Whoami",
      "int": 123456789,
      "float": 1.23456789,
      "uuid": "5d1e22eb-d9b2-48cd-b081-d1056d267f28",
      "list": [1, 2, 4, autodict.AutoDict(num=5)],
      "child": autodict.AutoDict(name="Plain")
  })

  def test_default(self):
    result = autodict.DefaultJSONDriver.default(self.JSON_BASIC["date"])
    self.assertEqual(result, self.JSON_BASIC_DESERIALIZED["date"])

    class UnknownType:
      pass

    o = UnknownType()
    self.assertRaises(TypeError, autodict.DefaultJSONDriver.default, o)

  def test_dump(self):
    path = self._TEST_ROOT.joinpath("basic.json")

    autodict.DefaultJSONDriver.dump(self.JSON_BASIC, path)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    autodict.DefaultJSONDriver.dump(self.JSON_BASIC, str(path))
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    with open(path, "w", encoding="utf-8") as file:
      autodict.DefaultJSONDriver.dump(self.JSON_BASIC, file)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    with open(path, "wb") as file:
      autodict.DefaultJSONDriver.dump(self.JSON_BASIC, file, indent=2)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

  def test_dumps(self):
    s = autodict.DefaultJSONDriver.dumps(self.JSON_BASIC)
    json.loads(s)  # No JSON errors

    s = autodict.DefaultJSONDriver.dumps(self.JSON_BASIC, indent=2)
    json.loads(s)  # No JSON errors

  def test_object_hook(self):
    key = self.gen_string()
    value = self.gen_string()
    d = {key: value}

    result = autodict.DefaultJSONDriver.object_hook(d)
    self.assertIsInstance(result, autodict.AutoDict)

  def test_load(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    d = autodict.DefaultJSONDriver.load(path)
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(self.JSON_BASIC_DESERIALIZED, d)

    d = autodict.DefaultJSONDriver.load(str(path))
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(self.JSON_BASIC_DESERIALIZED, d)

    with open(path, "r", encoding="utf-8") as file:
      d = autodict.DefaultJSONDriver.load(file)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(self.JSON_BASIC_DESERIALIZED, d)

  def test_loads(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      d = autodict.DefaultJSONDriver.loads(s)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(self.JSON_BASIC_DESERIALIZED, d)


class TestJSONAutoDict(base.TestBase):
  """Test JSONAutoDict
  """

  def test_init(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    with autodict.JSONAutoDict(path, save_on_exit=False) as d:
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertIsInstance(d, autodict.JSONAutoDict)

      self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

    with autodict.JSONAutoDict(path,
                               save_on_exit=False,
                               driver=autodict.DefaultJSONDriver) as d:
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertIsInstance(d, autodict.JSONAutoDict)

      self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC_DESERIALIZED, d)

    path = self._TEST_ROOT.joinpath("does not exist.json")
    with autodict.JSONAutoDict(path,
                               save_on_exit=False,
                               driver=autodict.DefaultJSONDriver) as d:
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual({}, d)

  def test_save(self):
    path = self._TEST_ROOT.joinpath("basic.json")
    with autodict.JSONAutoDict(path,
                               save_on_exit=False,
                               driver=autodict.DefaultJSONDriver,
                               **TestDefaultJSONDriver.JSON_BASIC) as d:
      d.save(indent=None)

    self.assertTrue(path.exists())

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      self.assertNotIn("\n", s)

    path = self._TEST_ROOT.joinpath("folder/directory/basic.json")
    with autodict.JSONAutoDict(path,
                               save_on_exit=False,
                               driver=autodict.DefaultJSONDriver,
                               **TestDefaultJSONDriver.JSON_BASIC) as d:
      d.save(indent=2)

    self.assertTrue(path.exists())

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      self.assertIn("\n", s)
      self.assertIn("  ", s)

  def test_autosave(self):
    path = self._TEST_ROOT.joinpath("basic.json")
    with autodict.JSONAutoDict(path,
                               save_on_exit=True,
                               driver=autodict.DefaultJSONDriver,
                               **TestDefaultJSONDriver.JSON_BASIC) as d:
      d["key"] = "value"

    self.assertTrue(path.exists())

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      self.assertNotIn("\n", s)

    path.unlink()

    d = autodict.JSONAutoDict(path,
                              save_on_exit=True,
                              driver=autodict.DefaultJSONDriver,
                              **TestDefaultJSONDriver.JSON_BASIC)
    d = None

    self.assertTrue(path.exists())

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      self.assertNotIn("\n", s)

  def test_large(self):
    path = self._DATA_ROOT.joinpath("historical-events.json")
    with autodict.JSONAutoDict(path, save_on_exit=False) as d:
      self.assertIsInstance(d, autodict.JSONAutoDict)

    path = self._DATA_ROOT.joinpath("basic_large.json")
    with autodict.JSONAutoDict(path, save_on_exit=False) as d:
      self.assertIsInstance(d, autodict.JSONAutoDict)
