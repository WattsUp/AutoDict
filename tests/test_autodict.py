"""Test module autodict
"""

from tests import base

import autodict


class TestAutoDict(base.TestBase):
  """Test AutoDict
  """

  def test_missing_children(self):
    key = self.gen_string()
    value = self.gen_string(min_length=40, max_length=50)

    d = autodict.AutoDict()
    self.assertNotIn(key, d)

    d[key][key][key] = value
    self.assertIsInstance(d[key], autodict.AutoDict)
    self.assertIsInstance(d[key][key], autodict.AutoDict)
    self.assertEqual(d[key][key][key], value)

  def test_comparison(self):
    key = self.gen_string()
    value = self.gen_string(min_length=40, max_length=50)

    plain = {key: value}
    d = autodict.AutoDict(plain)
    self.assertDictEqual(d, plain)

  def test_str(self):
    key = self.gen_string()
    value = self.gen_string(min_length=40, max_length=50)

    plain = {key: value}
    d = autodict.AutoDict(plain)
    self.assertEqual(str(d), str(plain))

  def test_contains(self):
    section = self.gen_string()
    key = self.gen_string()
    value = self.gen_string(min_length=40, max_length=50)

    d = autodict.AutoDict()
    d[key] = {key: value}
    d[section][section][key] = value

    self.assertIn(key, d)
    self.assertNotIn(value, d)
    self.assertTrue(d.contains(section, section, key))
    self.assertFalse(d.contains(section, key, key))
    self.assertIn([key, key], d)
    self.assertNotIn([key, key, key], d)
