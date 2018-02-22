from collections import OrderedDict
from miros.singleton import SingletonDecorator


# Not intended for export
class OrderedDictWithParams(OrderedDict):
  '''
  If your subclass <name_of_subclass> has the following init:
    def __init__(self,*args,**kwargs):

      self['RET_SUPER']     = 1
      self['RET_SUPER_SUB'] = 2
      self['UNHANDLED']     = 3

    Any object constructed from it will have to following attributes:
      obj = <name_of_subclass>
      obj.RET_SUPER     => 1
      obj.RET_SUPER_SUB => 2
      obj.UNHANDLED     => 3

    To post-pend an item to the object which will also have a named parameter:
      obj = <name_of_subclass>
      obj.append("NEW_NAMED_ATTRIBUTE")
      ob.NEW_NAMED_ATTRIBUTE => 4

  This of this class as being an extensible ENUM which isn't immutable.  All of
  the enums are wrapped up within an OrderedDict, so you get all of it's methods
  as well as the clean interface to the attribute.
  '''

  def append(self, string):
    if string in self:
      return
    else:
      self[string] = len(self) + 1

  def __getattr__(self, item):
    return self[str(item)]


# Not intended for export
class ReturnStatusSource(OrderedDictWithParams):

  '''
  A class which contains all of the state returns codes

  To construct the object
    state_returns = ReturnCodes()

  To get the number:
    state_returns.RET_SUPER => 1

  To add a return code:
    state_returns.append('RET_ZZ')
    state_returns.RET_ZZ => 12

  '''
  def __init__(self, *args, **kwargs):

    self['SUPER']     = 1
    self['SUPER_SUB'] = 2
    self['UNHANDLED'] = 3

    # handled and do not need to be bubbled up
    self['HANDLED']   = 4
    self['IGNORED']   = 5

    # entry/exit
    self['ENTRY']     = 6
    self['EXIT']      = 7

    # no side effects
    self['NULL']      = 8

    # transitions need to execute
    self['TRAN']      = 9
    self['TRAN_INIT'] = 10
    self['TRAN_HIST'] = 11
    self['TRAN_EP']   = 12
    self['TRAN_XP']   = 13


# Not intended for export
class SignalSource(OrderedDictWithParams):
  '''
  A class which contains all of the state signal types

  To get the basic system signals:
    signals = Signal()

  To append a new signal
    signals = Signal.append('OVEN_OFF')

  To get the number:
    signal.ENTRY_SIGNAL => 1
    signal['OVEN_OFF']  => 12
    signal.OVER_OFF     => 12

  '''
  def __init__(self, *args, **kwargs):

    self['ENTRY_SIGNAL']            = 1
    self['EXIT_SIGNAL']             = 2
    self['INIT_SIGNAL']             = 3
    self['REFLECTION_SIGNAL']       = 4
    self['SEARCH_FOR_SUPER_SIGNAL'] = 5

  def append(self, string):
    if string in self:
      return
    else:
      self[string] = len(self) + 1

  def is_inner_signal(self, other):
    def is_number_an_internal_signal(number):
      result = False
      if number in list(self.values())[0:self.SEARCH_FOR_SUPER_SIGNAL]:
        result = True
      return result

    result = False
    if(isinstance(other, str)):
      try:
        other = self[other]
        result = is_number_an_internal_signal(other)
      except:
        pass
    elif(isinstance(other, int)):
      try:
        result = is_number_an_internal_signal(other)
      except:
        pass
    return result

  def name_for_signal(self, signal):
    '''
    get the name of a signal number as a string
    '''
    signal_name = list(self.keys())[list(self.values()).index(signal)]
    return signal_name

  def __getattr__(self, item):
    value = None
    try:
      value = self[str(item)]
    except:
      self.append(item)
      value = self[str(item)]

    return value


'''
Defining the signals used by this package and all of the packages that
reference it.  Think of this as a singleton or a growing enumeration.
'''
# Signal is a singleton
Signal = SingletonDecorator(SignalSource)
signals_exist = 'signals' in locals()
if signals_exist is False:
  signals = Signal()

# ReturnStatus is a singleton
ReturnStatus = SingletonDecorator(ReturnStatusSource)
status_exist = 'return_status' in locals()
if status_exist is False:
  return_status = ReturnStatus()


class Event(OrderedDictWithParams):
  '''
  An event should be constructed, used, then garbage collected.  An event is a
  temporary thing.  However if an event uses a signal that hasn't been seen
  before, that signal will be added to the list of global signals as a new
  enumerated value.

  # Make an event (this should happen internally):
    e = Event(signal=signals.ENTRY_SIGNAL) # existing signal
    assert(e.signal == signals.ENTRY_SIGNAL)
    assert(e.signal_name == 'ENTRY_SIGNAL')

  # Make an event, which will construct a signal internally:
    e = Event(signal ='OVEN_OFF', payload='any object can go here') # new signal
    assert(e.signal == 5) # if it is the first unseen signal in the system
    assert(e.signal_name == 'OVEN_OFF')
    assert(signals.OVER_OFF == 5)

  '''
  def __init__(self, signal, payload=None):
    global signals

    self.payload = payload

    if signal in signals.values():
      self.signal = signal
      for key, value in signals.items():
        if value == signal:
          self.signal_name = key
          break

    elif isinstance(signal, str):
      signals.append(signal)
      self.signal_name = signal
      # over-write the signal string as the signal name
      self.signal      = signals[signal]
    else:
      raise("signal must be of type string or Signal")

  def has_payload(self):
    result = True
    if self.payload is None:
      result = False
    return result
