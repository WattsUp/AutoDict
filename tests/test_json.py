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
  TARGET_BASIC = {
      "datetime": _TIMESTAMP,
      "datetime_exp": _TIMESTAMP,
      "date": _TIMESTAMP.date(),
      "date_exp": _TIMESTAMP.date(),
      "time": _TIMESTAMP.timetz(),
      "time_exp": _TIMESTAMP.timetz(),
      "name": "Whoami",
      "int": 123456789,
      "float": 1.23456789,
      "uuid": uuid.UUID("5d1e22eb-d9b2-48cd-b081-d1056d267f28"),
      "uuid_exp": uuid.UUID("5d1e22eb-d9b2-48cd-b081-d1056d267f28"),
      "list": [1, 2, 4, autodict.AutoDict(num=5)],
      "child": {
          "name": "Plain"
      },
      "other child": autodict.AutoDict(name="Not plain")
  }

  def test_deserialize(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    with open(path, "r", encoding="utf-8") as file:
      j = json.load(file)

      d = autodict.DefaultJSONDriver.deserialize(j)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(self.TARGET_BASIC, d)

    self.assertRaises(TypeError, autodict.DefaultJSONDriver.deserialize,
                      {"__type__": "Unknown"})

  def test_load(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    d = autodict.DefaultJSONDriver.load(path)
    self.assertIsInstance(d, autodict.AutoDict)
    self.assertDictEqual(self.TARGET_BASIC, d)

    with open(path, "r", encoding="utf-8") as file:
      d = autodict.DefaultJSONDriver.load(file)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(self.TARGET_BASIC, d)

  def test_loads(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    with open(path, "r", encoding="utf-8") as file:
      s = file.read()
      d = autodict.DefaultJSONDriver.loads(s)
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual(self.TARGET_BASIC, d)


class TestJSONAutoDict(base.TestBase):
  """Test JSONAutoDict
  """

  def test_init(self):
    path = self._DATA_ROOT.joinpath("basic.json")

    with autodict.JSONAutoDict(path, save_on_exit=False) as d:
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertIsInstance(d, autodict.JSONAutoDict)

      self.assertDictEqual(TestDefaultJSONDriver.TARGET_BASIC, d)

    with autodict.JSONAutoDict(path,
                               save_on_exit=False,
                               driver=autodict.DefaultJSONDriver) as d:
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertIsInstance(d, autodict.JSONAutoDict)

      self.assertDictEqual(TestDefaultJSONDriver.TARGET_BASIC, d)

    path = self._TEST_ROOT.joinpath("does not exist.json")
    with autodict.JSONAutoDict(path,
                               save_on_exit=False,
                               driver=autodict.DefaultJSONDriver) as d:
      self.assertIsInstance(d, autodict.AutoDict)
      self.assertDictEqual({}, d)
