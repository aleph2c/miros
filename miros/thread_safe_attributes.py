# to test this:
# pytest -s -m thread_safe_attributes
import re
import time
import logging
from collections import deque
from functools import partial
from collections import namedtuple

class ThreadSafeAttribute:

  def __init__(self, initial_value=None):
    self._initial_value = initial_value
    self._value = deque(maxlen=1)
    self._value.append(self._initial_value)

  def __get__(self, obj, objtype):
    return self._value[-1]

  def __set__(self, obj, val):
    self._value.append(val)

class MetaThreadSafeAttributes(type):

  def __init__(cls, *args, **kwargs):
    '''Build thread safe attributes'''
    if hasattr(cls, '_attributes'):
      for name in list(set(cls._attributes)):
        setattr(cls, name, ThreadSafeAttribute(initial_value=0))
    super().__init__(*args, **kwargs)
