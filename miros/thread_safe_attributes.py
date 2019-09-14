# to test this:
# pytest -s -m thread_safe_attributes
import types
from threading import RLock

class ThreadSafeAttributeMixin():

  def __new__(cls, *args, **kwargs):
    try:
      return super().__new__(cls, *args, **kwargs)
    except:
      # immutable 
      return super().__new__(cls)

  def __init__(self, *args, **kwargs):
    try:
      # mutable
      super().__init__(*args, **kwargs)
    except:
      # immutable 
      super().__init__()

    if 'value' in kwargs:
      self._value = kwargs['value']

    if 'lock' in kwargs:
      self.lock = kwargs['lock']

  def __iadd__(self, other):
    with self.lock:
      return super().__iadd__(other)

  def __isub__(self, other):
    with self.lock:
      return super().__isub__(other)

  def __imul__(self, other):
    with self.lock:
      return super().__imul__(other)

  def __imatmul__(self, other):
    with self.lock:
      return super().__imatmul__(other)

  def __itruediv__(self, other):
    with self.lock:
      return super().__itruediv__(other)

  def __ifloordiv__(self, other):
    with self.lock:
      return super().__ifloordiv__(other)

  def __imod__(self, other):
    with self.lock:
      return super().__imod__(other)

  def __ilshift__(self, other):
    with self.lock:
      return super().__ilshift__(other)

  def __irshift__(self, other):
    with self.lock:
      return super().__irshift__(other)

  def __iand__(self, other):
    with self.lock:
      return super().__iand__(other)

  def __ixor__(self, other):
    with self.lock:
      return super().__ixor__(other)

  def __ior__(self, other):
    with self.lock:
      return super().__ior__(other)

class ThreadSafeAttribute(ThreadSafeAttributeMixin):

  def __init__(self, initial_value=0):
    self.lock = RLock()
    super().__init__(lock=self.lock)
    self.__coerse_object__(initial_value)

  def __coerse_object__(self, initial_value):
    cls_dict = dict(initial_value.__class__.__dict__)
    cls_dict.update(ThreadSafeAttributeMixin.__dict__)
    DynamicClass = types.new_class(
      'DynamicClass', 
      (ThreadSafeAttributeMixin, initial_value.__class__), 
      {}, 
      lambda ns: ns.update(cls_dict))
    DynamicClass.__module__ == __name__
    self._value_base_class = initial_value.__class__
    value = DynamicClass(initial_value)
    setattr(value, 'lock', self.lock)
    self._value = value
    self._value = ThreadSafeAttributeMixin()

  def __get__(self, obj, objtype):
    with self.lock:
      return self._value

  def __set__(self, obj, val):
    with self.lock:
      if not isinstance(val, self._value_base_class) or not issubclass(val.__class__, self._value_base_class):
        self.__coerse_object__(obj)
        self._value = val
      else:
        self._value = val

class MetaThreadSafeAttributes(type):

  def __init__(cls, *args, **kwargs):
    '''Build thread safe attributes'''
    if hasattr(cls, '_attributes'):
      for name in list(set(cls._attributes)):
        setattr(cls, name, ThreadSafeAttribute(initial_value=1))
    super().__init__(*args, **kwargs)
