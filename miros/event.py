
from collections import OrderedDict
class OrderedDictWithParams(OrderedDict):
  """
  If your subclass has the following init:
    def __init__(self,*args,**kwargs):

      self['RET_SUPER']     = 1
      self['RET_SUPER_SUB'] = 2
      self['RET_UNHANDLED'] = 3
      selfwrite_keys_to_attributes()

    Any object constructed from it will have to following attributes:
      obj = <name_of_subclass>
      obj.RET_SUPER     => 1
      obj.RET_SUPER_SUB => 2
      obj.RET_UNHANDLED => 3
  
    To post-pend an item to the object which will also have a named parameter:
      obj = <name_of_subclass>
      obj.append("NEW_NAMED_ATTRIBUTE")
      ob.NEW_NAMED_ATTRIBUTE => 4

  """

  def write_keys_to_attributes(self):
    for key in self.keys():
      exec("{0}.{1} = property(lambda self: self['{1}'])".format(self.__class__.__name__,key))

  def append(self,string):
    if string in self:
      return
    else:
      self[string] = len(self) + 1
      exec("{0}.{1} = property(lambda self: self['{1}'])".format(self.__class__.__name__,string))

class StateReturns(OrderedDictWithParams):

  """
  A class which contains all of the state returns type

  To append a return type
    state_returns = StateReturns()

  To get the number:
    state_returns.RET_SUPER => 1

  To add a return:
    state_returns.append('RET_ZZ')
    state_returns.RET_ZZ => 12

  """
  def __init__(self,*args,**kwargs):

    self['RET_SUPER']     = 1
    self['RET_SUPER_SUB'] = 2
    self['RET_UNHANDLED'] = 3
    
    # handled and do not need to be bubbled up
    self['RET_HANDLED']   = 4
    self['RET_IGNORED']   = 5

    # entry/exit
    self['RET_ENTRY']     = 6
    self['RET_EXIT']      = 7

    # no side effects 
    self['RET_NULL']      = 8

    #transitions need to execute
    self['RET_TRAN']      = 9
    self['RET_TRAN_INIT'] = 10
    self['RET_TRAN_HIST'] = 11
    self['RET_TRAN_EP']   = 12
    self['RET_TRAN_XP']   = 13

    self.write_keys_to_attributes()
    
class Signal(OrderedDictWithParams):
  """
  A class which contains all of the state signal types

  To get the basic system signals:
    signals = Signal()

  To append a new signal
    signals = Signal.append('OVEN_OFF')

  To get the number:
    signal.ENTRY_SIGNAL => 1
    signal['OVEN_OFF']  => 12
    signal.OVER_OFF     => 12

  """
  def __init__(self,*args,**kwargs):

    self['ENTRY_SIGNAL']      = 1
    self['EXIT_SIGNAL']       = 2
    self['INIT_SIGNAL']       = 3
    self['REFLECTION_SIGNAL'] = 4

    self.write_keys_to_attributes()

signals_exist = 'signals' in locals()
if signals_exist == False:
  signals = Signal()

class Event(OrderedDictWithParams):
  """
    An event should be constructed, used, then garbage collected.  An event is a
    temporary thing.  However if an event uses a signal that hasn't been seen
    before, that signal will be added to the list of global signals as a new
    enumerated value.

    # Make an event (this should happen internally):
      e = Event(signal  = signals.ENTRY_SIGNAL) # existing signal
      assert( e.signal == signals.ENTRY_SIGNAL)
      assert( e.signal_name == 'ENTRY_SIGNAL')

    # Make an event, which will construct a signal internally:
      e = Event(signal  = 'OVEN_OFF', payload = 'any object can go here') # new signal
      assert(e.signal == 5) # if it is the first unseen signal in the system
      assert(e.signal_name == 'OVEN_OFF')
      assert(signals.OVER_OFF == 5)

  """
  def __init__(self, signal, payload=None):
    global signals
    if signal in signals.values():
      self.signal = signal
      for key, value in signals.items():
        if value == signal:
          self.signal_name = key
    elif isinstance(signal,str):
      signals.append(signal)
      self.signal_name = signal
      # over-write the signal string as the signal name 
      self.signal      = signals[signal]
    else:
      raise("signal must be of type string or Signal")

  def __del__(self):
    print("delete event")


