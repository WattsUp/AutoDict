"""Test module autodict
"""

from tests import base

import autodict
from autodict.implementation import AutoDict


class TestAutoDict(base.TestBase):
  """Test AutoDict
  """

  def test_plain(self):
    key = self.gen_string()
    value = self.gen_string(min_length=40, max_length=50)

    plain = {key: value}
    a = AutoDict(plain)
    self.assertDictEqual(a.plain(), plain)

  def test_str(self):
    key = self.gen_string()
    value = self.gen_string(min_length=40, max_length=50)

    plain = {key: value}
    a = AutoDict(plain)
    self.assertEqual(str(a), str(plain))

  def test_manual_save(self):
    key = self.gen_string()
    value = self.gen_string(min_length=40, max_length=50)
    path = self._TEST_ROOT.joinpath("autodict.json")

    # ContextManager
    with autodict.JSONAutoDict(path, save_on_exit=False) as c:
      c[key] = value
    c = None
    self.assertFalse(path.exists())

    # No ContextManager
    c = autodict.JSONAutoDict(path, save_on_exit=False)
    c[key] = value
    c = None
    self.assertFalse(path.exists())

    # Unknown encoding type
    class _UnrecognizedClass:
      pass

    c = autodict.JSONAutoDict(path, save_on_exit=False)
    c[key] = _UnrecognizedClass()
    self.assertRaises(TypeError, c.save)
    c = None
    path.unlink()

    # Unknown decoding type
    c = autodict.JSONAutoDict(path, save_on_exit=False)
    c[key] = {"__type__": "_UnrecognizedClass"}
    c.save()
    c = None
    self.assertRaises(TypeError,
                      autodict.JSONAutoDict,
                      path,
                      save_on_exit=False)

  def test_auto_save(self):
    section = self.gen_string()
    key = self.gen_string()
    value = self.gen_string(min_length=40, max_length=50)
    path = self._TEST_ROOT.joinpath("autodict.json")

    # ContextManager
    with autodict.JSONAutoDict(path, save_on_exit=True) as c:
      c[key] = {key: value}
      c[section][section][key] = value
    self.assertIsInstance(c[key], dict)
    self.assertIsInstance(c[section], autodict.AutoDict)
    c = None
    self.assertTrue(path.exists())

    with autodict.JSONAutoDict(path, save_on_exit=True) as c:
      self.assertIsInstance(c[key], dict)
      self.assertIsInstance(c[section], autodict.AutoDict)
    c = None
    path.unlink()

    # No ContextManager
    c = autodict.JSONAutoDict(path, save_on_exit=True)
    c[key] = {key: value}
    c[section][section][key] = value
    c = None
    self.assertTrue(path.exists())

  def test_contains(self):
    section = self.gen_string()
    key = self.gen_string()
    value = self.gen_string(min_length=40, max_length=50)
    path = self._TEST_ROOT.joinpath("autodict.json")

    # No ContextManager
    c = autodict.JSONAutoDict(path, save_on_exit=True)
    c[key] = {key: value}
    c[section][section][key] = value

    self.assertIn(key, c)
    self.assertNotIn(value, c)
    self.assertTrue(c.contains(section, section, key))
    self.assertFalse(c.contains(section, key, key))
    self.assertIn([key, key], c)
    self.assertNotIn([key, key, key], c)
    c = None
