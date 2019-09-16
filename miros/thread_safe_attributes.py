# to test this:
# pytest -s -m thread_safe_attributes
import re
import inspect
from threading import RLock
from collections import namedtuple

FrameData = namedtuple('FrameData', [
  'filename', 
  'line_number',
  'function_name',
  'lines',
  'index'])

class ThreadSafeAttribute:

  def __init__(self, initial_value=None):
    self._initial_value = initial_value
    self._is_atomic = True
    self._lock = RLock()
    self._value = initial_value

  def __get__(self, instance, owner):
    self._is_atomic = True
    #print("get acquiring lock")
    self._lock.acquire(blocking=True)
    previous_frame = inspect.currentframe().f_back
    fdata = FrameData(*inspect.getframeinfo(previous_frame))
    if re.search(r'([+-/*@^&|<>%]=)|([/<>*]{2}=)', fdata.lines[0]) is not None:
      #print('{} not atomic'.format(fdata.lines[0]))
      self._is_atomic = False
    else:
      #print('{} is atomic'.format(fdata.lines[0]))
      #print("get releasing lock")
      self._lock.release()
    return self._value

  def __set__(self, instance, value):
    if not self._is_atomic:
      #print("set continuing non atomic operation")
      pass
    else:
      #print("set aquiring lock")
      self._lock.acquire(blocking=True)
    self._value = value
    #print("set releasing lock")
    self._is_atomic = True
    self._lock.release()

class MetaThreadSafeAttributes(type):

  def __init__(cls, *args, **kwargs):
    '''Build thread safe attributes'''
    if hasattr(cls, '_attributes'):
      for name in list(set(cls._attributes)):
        setattr(cls, name, ThreadSafeAttribute(initial_value=0))
    super().__init__(*args, **kwargs)
