import pytest
from miros.event import *

def test_ordered_dict_with_params():
  od = OrderedDictWithParams()
  assert(od!=None)

def test_state_returns():
  state_returns = ReturnStatus()
  assert(state_returns.SUPER == 1)
  assert(state_returns.TRAN_XP == 13)
  state_returns.append('RET_ZZ')
  assert(state_returns.RET_ZZ == 14)

def test_signal():
  signals = Signal()
  assert(signals.ENTRY_SIGNAL == 1)
  assert(signals.REFLECTION_SIGNAL == 4)
  signals.append('BAKE')
  assert(signals.BAKE == 6)
  assert(signals['BAKE'] == 6)

def test_signal():
  signals = SignalSource()
  assert(signals.ENTRY_SIGNAL == 1)
  assert(signals.REFLECTION_SIGNAL == 4)
  signals.append('BAKE')
  assert(signals.BAKE >= 6)
  assert(signals.is_inner_signal(1) == True)
  assert(signals.is_inner_signal(5) == True)
  assert(signals.is_inner_signal(6) == False)
  assert(signals.is_inner_signal('ENTRY_SIGNAL') == True)
  assert(signals.is_inner_signal('SEARCH_FOR_SUPER_SIGNAL') == True)
  assert(signals.is_inner_signal('BAKE') == False)
  assert(signals.is_inner_signal('NOT_THERE') == False)

def test_event():
  signals = SignalSource()
  event   = Event(signal=signals.ENTRY_SIGNAL)
  assert(event.signal == 1)
  assert(event.signal_name == "ENTRY_SIGNAL")
  event = Event(signal="BOB")
  assert(event.signal >= 6)
  assert(event.signal_name == "BOB")

def test_signal_singletons():
  '''The signals object from the event.py class is the growing signals enumeration'''
  local_signals = SignalSource()
  e = Event(signal = "MARY")
  assert(e.signal_name == "MARY")
  assert(signals.MARY > local_signals.REFLECTION_SIGNAL)
  e = Event(signal = "JANE")
  assert(e.signal_name == "JANE")
  assert(signals.JANE > signals.REFLECTION_SIGNAL)

  # we expect the local_signals class not to have to MANY enum
  with pytest.raises(KeyError) as excinfo:
    local_signals.MARY

@pytest.mark.test
def test_enum_2():
  ee = Signal2()
  assert( ee.ENTRY_SIGNAL == 1 )
  Signal2.BOB = Signal2.__next__()
  Signal2.append("MARY")
  assert( ee.BOB == 6 )
  assert(Signal2.MARY == 7)
  Signal3.Mary = Signal3.__next__()
  Signal3.Bob = Signal3.__next__()
  ef = Signal3()
  assert(ef.Bob == 7)
