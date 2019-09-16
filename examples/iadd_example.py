import re
import inspect
from threading import RLock
from collections import namedtuple

# __iadd__ has been removed from this example because it is not needed
# the data descriptor is more fundamental than the __iadd__, __iadd__ will call
# its __get__ and __set__ method.  If we lock across these methods we can avoid
# the complexity of having to write __iadd__ and it's family of magic methods.

# demonstration of how to make a thread safe attribute using a data descriptor

FrameData = namedtuple('FrameData', [
  'filename', 
  'line_number',
  'function_name',
  'lines',
  'index'])

class NameInClassSpace1(object):

  def __init__(self):
    self._name = 0
    self._is_atomic = True
    self._lock = RLock()

  def __get__(self, instance, owner):
    self._is_atomic = True
    print("get acquiring lock")
    self._lock.acquire(blocking=True)
    previous_frame = inspect.currentframe().f_back
    fdata = FrameData(*inspect.getframeinfo(previous_frame))
    if re.search(r'([+-/*@^&|<>%]=)|([/<>*]{2}=)', fdata.lines[0]) is not None:
      print('{} not atomic'.format(fdata.lines[0]))
      self._is_atomic = False
    else:
      print('{} is atomic'.format(fdata.lines[0]))
      print("get releasing lock")
      self._lock.release()
    return self._name

  def __set__(self, instance, value):
    if not self._is_atomic:
      print("set continuing non atomic operation")
    else:
      print("set aquiring lock")
      self._lock.acquire(blocking=True)
    self._name = value
    print("set releasing lock")
    self._lock.release()
    self._is_atomic = True

class NameInClassSpace2():
  name = NameInClassSpace1()

a = NameInClassSpace2()
a.name -= 1
a.name = 1
print("")
a.name *= 1
a.name = 1
print("")
#a.name @= 1
#a.name = 1
a.name /= 1
a.name = 1
print("")
a.name //= 1
a.name = 1
print("")
a.name %= 1
a.name = 1
print("")
a.name **= 1
a.name = 1
print("")
a.name <<= 1
a.name = 1
print("")
a.name >>= 1
a.name = 1
print("")
a.name &= 1
a.name = 1
print("")
a.name ^= 1
a.name = 1
print("")
a.name |= 1
a.name = 1
print("")

print("")
a.name = 3
print(a.name)
print("")
a.name += 1
print("")
a.name = 1
print("")

