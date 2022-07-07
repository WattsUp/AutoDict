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
      "time": _TIMESTAMP.timetz(),
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

  def test_serialize(self):
    path = self._DATA_ROOT.joinpath("basic_exp.json")

    class DefaultExplicit(autodict.DefaultJSONDriver):
      """Test with only explicit serialization options
      """
      IMPLICIT_TYPES_SERIALIZE = {}

    d = DefaultExplicit.serialize(self.JSON_BASIC)
    self.assertIsJSONTypes(d)

    with open(path, "r", encoding="utf-8") as file:
      j = json.load(file)
      self.assertDictEqual(j, d)

    path = self._DATA_ROOT.joinpath("basic_imp.json")

    class DefaultImplicit(autodict.DefaultJSONDriver):
      """Test with only implicit serialization options
      """
      EXPLICIT_TYPES_SERIALIZE = {}

    d = DefaultImplicit.serialize(self.JSON_BASIC)
    self.assertIsJSONTypes(d)

    with open(path, "r", encoding="utf-8") as file:
      j = json.load(file)
      self.assertDictEqual(j, d)

    class UnknownType:
      pass

    o = UnknownType()
    self.assertRaises(TypeError, autodict.DefaultJSONDriver.serialize, o)

  def test_dump(self):
    path = self._TEST_ROOT.joinpath("basic.json")

    autodict.DefaultJSONDriver.dump(self.JSON_BASIC, path)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    path.unlink()

    with open(path, "w", encoding="utf-8") as file:
      autodict.DefaultJSONDriver.dump(self.JSON_BASIC, file)
    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      json.loads(s)  # No JSON errors

    s = autodict.DefaultJSONDriver.dumps(self.JSON_BASIC)
    json.loads(s)  # No JSON errors

  def test_deserialize(self):
    path = self._DATA_ROOT.joinpath("basic_exp.json")

    with open(path, "r", encoding="utf-8") as file:
      j = json.load(file)

      d = autodict.DefaultJSONDriver.deserialize(j)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(self.JSON_BASIC, d)

    path = self._DATA_ROOT.joinpath("basic_imp.json")

    with open(path, "r", encoding="utf-8") as file:
      j = json.load(file)

      d = autodict.DefaultJSONDriver.deserialize(j)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(self.JSON_BASIC, d)

    self.assertRaises(TypeError, autodict.DefaultJSONDriver.deserialize,
                      {"__type__": "Unknown"})

  def test_load(self):
    path = self._DATA_ROOT.joinpath("basic_exp.json")

    d = autodict.DefaultJSONDriver.load(path)
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(self.JSON_BASIC, d)

    with open(path, "r", encoding="utf-8") as file:
      d = autodict.DefaultJSONDriver.load(file)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(self.JSON_BASIC, d)

  def test_loads(self):
    path = self._DATA_ROOT.joinpath("basic_exp.json")

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      d = autodict.DefaultJSONDriver.loads(s)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(self.JSON_BASIC, d)


class TestJSONAutoDict(base.TestBase):
  """Test JSONAutoDict
  """

  def test_init(self):
    path = self._DATA_ROOT.joinpath("basic_exp.json")

    with autodict.JSONAutoDict(path, save_on_exit=False) as d:
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertIsInstance(d, autodict.JSONAutoDict)

      self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC, d)

    with autodict.JSONAutoDict(path,
                               save_on_exit=False,
                               driver=autodict.DefaultJSONDriver) as d:
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertIsInstance(d, autodict.JSONAutoDict)

      self.assertDictEqual(TestDefaultJSONDriver.JSON_BASIC, d)

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
