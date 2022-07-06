"""Test base class
"""

import os
import pathlib
import random
import string
import time
import unittest

import autodict

from tests import TEST_LOG


class TestBase(unittest.TestCase):
  """Test base class
  """

  _TEST_ROOT = pathlib.Path(".test")
  _DATA_ROOT = pathlib.Path(__file__).parent.joinpath("data")

  def __clean_test_root(self):
    if self._TEST_ROOT.exists():
      for f in os.listdir(self._TEST_ROOT):
        os.remove(self._TEST_ROOT.joinpath(f))

  def gen_string(self, min_length: int = 8, max_length: int = 12) -> str:
    """Generate a random string with letter, numbers, and symbols

    Args:
      min_length: minimum length of string
      max_length: maximum length of string

    Returns:
      str Random length string with random characters
    """
    all_char = string.ascii_letters + string.punctuation + string.digits
    return "".join(
        random.choice(all_char)
        for _ in range(random.randint(min_length, max_length)))

  def setUp(self):
    self.__clean_test_root()
    self._TEST_ROOT.mkdir(parents=True, exist_ok=True)
    self._test_start = time.perf_counter()

    # Remove sleeping by default, mainly in read hardware interaction
    self._original_sleep = time.sleep
    time.sleep = lambda *args: None

  def tearDown(self):
    duration = time.perf_counter() - self._test_start
    with autodict.JSONAutoDict(TEST_LOG) as d:
      d["methods"][self.id()] = duration
    self.__clean_test_root()

    # Restore sleeping
    time.sleep = self._original_sleep

  def log_speed(self, slow_duration, fast_duration):
    with autodict.JSONAutoDict(TEST_LOG) as d:
      d["speed"][self.id()] = {
          "slow": slow_duration,
          "fast": fast_duration,
          "increase": slow_duration / fast_duration
      }

  @classmethod
  def setUpClass(cls):
    print(f"{cls.__module__}.{cls.__qualname__}[", end="", flush=True)
    cls._CLASS_START = time.perf_counter()

  @classmethod
  def tearDownClass(cls):
    print("]done", flush=True)
    # time.sleep(10)
    duration = time.perf_counter() - cls._CLASS_START
    with autodict.JSONAutoDict(TEST_LOG) as d:
      d["classes"][f"{cls.__module__}.{cls.__qualname__}"] = duration
