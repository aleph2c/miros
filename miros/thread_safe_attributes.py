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
   
  def is_not_atomic(self, previous_line):
    is_not_atomic = True
    # search for '+=', '-=' ... '<<=', '**='
    is_not_atomic &= re.search(r'([+-/*@^&|<>%]=)|([/<>*]{2}=)', previous_line) is not None
    return is_not_atomic

  def request_for_lock(self, previous_line):
    request_for_lock = False
    # search for _, _lock = ...
    if '_lock' in previous_line:
      request_for_lock |= re.search(r'_, _lock[ ]+=', previous_line) is not None
    return request_for_lock

  def __get__(self, instance, owner):
    #print("get acquiring lock")
    self._lock.acquire(blocking=True)
    self._is_atomic = True
    previous_frame = inspect.currentframe().f_back
    fdata = FrameData(*inspect.getframeinfo(previous_frame))
    previous_line = fdata.lines[0]
    if self.is_not_atomic(previous_line):
      #print('{} not atomic'.format(fdata.lines[0]))
      self._is_atomic = False
    else:
      #print('{} is atomic'.format(fdata.lines[0]))
      #print("get releasing lock")
      self._lock.release()
    if self.request_for_lock(previous_line):
      #print("providing lock")
      return self._value, self._lock
    else:
      return self._value

  def __set__(self, instance, value):
    if self._is_atomic:
      #print("set aquiring lock")
      self._lock.acquire(blocking=True)
    else:
      #print("set continuing non atomic operation")
      pass
    self._value = value
    self._is_atomic = True
    #print("set releasing lock")
    self._lock.release()

class MetaThreadSafeAttributes(type):

  def __init__(cls, *args, **kwargs):
    '''Build thread safe attributes'''
    if hasattr(cls, '_attributes'):
      for name in list(set(cls._attributes)):
        setattr(cls, name, ThreadSafeAttribute(initial_value=0))
    super().__init__(*args, **kwargs)
