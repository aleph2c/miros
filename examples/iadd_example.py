class IntFeeder(int):
  def __new__(cls, value):
    return int.__new__(cls, value)

class FeedStock(IntFeeder):
  def __iadd__(self, other):
    print("locking in __iadd__")
    if hasattr(super(), '__iadd__'):
      print("here")
      return super(FeedStock, self).__iadd__(other)
    else:
      return self + other

class NameInClassSpace1():

  def __init__(self):
    self._name = FeedStock(0)

  def __get__(self, instance, owner):
    print('getting1 ', self._name)
    return self._name

  def __set__(self, instance, name):
    print('setting1 ', name)
    self._name = name

  def __delete__(self, instance):
    print('deleting1 ', self._name)
    del self._name

class NameInClassSpace1Sub():
  name = NameInClassSpace1()

class NameInClassSpace2(object):

  def __init__(self):
    self._name = FeedStock(0)

  def fget(self):
    print('locking and getting ', self._name)
    return self._name

  def fset(self, name):
    print('locking and setting ', name)
    self._name = name

  def fdel(self):
    print('deleting ', self._name)
    del self._name

  name = property(fget, fset, fdel, doc="")

user = NameInClassSpace1Sub()
user.name = 1
user.name += 1
user.name
del user.name
import pdb; pdb.set_trace()
a = NameInClassSpace2()
print("")
a.name += 1
#user = Forced()
#user.name2.name = 1
#user.name2.name += 1
#del user.name2.name

