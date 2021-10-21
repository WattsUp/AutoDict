"""Test module project_template.math
"""

import unittest

from project_template import math

class TestMathMethods(unittest.TestCase):

  def test_add_int(self):
    self.assertEqual(math.add_int(1, 4), 5)
    self.assertNotEqual(math.add_int(-1, 4), 5)
