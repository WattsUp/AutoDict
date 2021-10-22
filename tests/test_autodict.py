"""Test module autodict
"""

import os
import pathlib
import random
import string
import unittest

import autodict
from autodict.implementation import AutoDict


def gen_string(min_length: int = 8, max_length: int = 12) -> str:
  """Generate a random string with letter, numbers, and symbols
  Args:
    min_length: minimum length of string
    max_length: maximum length of string
  Returns:
    str Random length string with random characters
  """
  allchar = string.ascii_letters + string.punctuation + string.digits
  return "".join(
      random.choice(allchar)
      for _ in range(random.randint(min_length, max_length)))


class TestAutoDict(unittest.TestCase):
  """Test AutoDict
  """

  _TEST_CONFIG = "testing.json"
  _TEST_ROOT = pathlib.Path(".test")

  def __clean_test_root(self):
    if self._TEST_ROOT.exists():
      for f in os.listdir(self._TEST_ROOT):
        os.remove(self._TEST_ROOT.joinpath(f))
      os.rmdir(self._TEST_ROOT)

  def test_plain(self):
    key = gen_string()
    value = gen_string(min_length=40, max_length=50)
    with autodict.JSONAutoDict(self._TEST_CONFIG, save_on_exit=True) as c:
      c["plain"]["key"] = key
      c["plain"]["value"] = value

    plain = {key: value}
    a = AutoDict(plain)
    self.assertDictEqual(a.plain(), plain)

  def test_str(self):
    key = gen_string()
    value = gen_string(min_length=40, max_length=50)
    with autodict.JSONAutoDict(self._TEST_CONFIG, save_on_exit=True) as c:
      c["str"]["key"] = key
      c["str"]["value"] = value

    plain = {key: value}
    a = AutoDict(plain)
    self.assertEqual(str(a), str(plain))

  def test_manual_save(self):
    self.__clean_test_root()

    key = gen_string()
    value = gen_string(min_length=40, max_length=50)
    path = str(self._TEST_ROOT.joinpath("autodict.json"))
    with autodict.JSONAutoDict(self._TEST_CONFIG, save_on_exit=True) as c:
      c["manual_save"]["key"] = key
      c["manual_save"]["value"] = value
      c["manual_save"]["path"] = path

    # ContextManager
    with autodict.JSONAutoDict(path, save_on_exit=False) as c:
      c[key] = value
    c = None
    self.assertFalse(os.path.exists(path))

    # No ContextManager
    c = autodict.JSONAutoDict(path, save_on_exit=False)
    c[key] = value
    c = None
    self.assertFalse(os.path.exists(path))

    # Unknown encoding type
    class _UnrecognizedClass:
      pass

    c = autodict.JSONAutoDict(path, save_on_exit=False)
    c[key] = _UnrecognizedClass()
    self.assertRaises(TypeError, c.save)
    c = None
    self.__clean_test_root()

    # Unknown decoding type
    c = autodict.JSONAutoDict(path, save_on_exit=False)
    c[key] = {"__type__": "_UnrecognizedClass"}
    c.save()
    c = None
    self.assertRaises(TypeError,
                      autodict.JSONAutoDict,
                      path,
                      save_on_exit=False)
    self.__clean_test_root()

  def test_auto_save(self):
    self.__clean_test_root()

    section = gen_string()
    key = gen_string()
    value = gen_string(min_length=40, max_length=50)
    path = str(self._TEST_ROOT.joinpath("autodict.json"))
    with autodict.JSONAutoDict(self._TEST_CONFIG, save_on_exit=True) as c:
      c["auto_save"]["section"] = section
      c["auto_save"]["key"] = key
      c["auto_save"]["value"] = value
      c["auto_save"]["path"] = path

    # ContextManager
    with autodict.JSONAutoDict(path, save_on_exit=True) as c:
      c[key] = {key: value}
      c[section][section][key] = value
    self.assertIsInstance(c[key], dict)
    self.assertIsInstance(c[section], autodict.AutoDict)
    c = None
    self.assertTrue(os.path.exists(path))

    with autodict.JSONAutoDict(path, save_on_exit=True) as c:
      self.assertIsInstance(c[key], dict)
      self.assertIsInstance(c[section], autodict.AutoDict)
    c = None
    self.__clean_test_root()

    # No ContextManager
    c = autodict.JSONAutoDict(path, save_on_exit=True)
    c[key] = {key: value}
    c[section][section][key] = value
    c = None
    self.assertTrue(os.path.exists(path))

    self.__clean_test_root()

  def test_contains(self):
    self.__clean_test_root()

    section = gen_string()
    key = gen_string()
    value = gen_string(min_length=40, max_length=50)
    path = str(self._TEST_ROOT.joinpath("autodict.json"))
    with autodict.JSONAutoDict(self._TEST_CONFIG, save_on_exit=True) as c:
      c["contains"]["section"] = section
      c["contains"]["key"] = key
      c["contains"]["value"] = value
      c["contains"]["path"] = path

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

    self.__clean_test_root()
