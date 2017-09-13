import pytest
from miros.event import OrderedDictWithParams, ReturnStatus, Signal, Event, signals

def test_ordered_dict_with_params():
  od = OrderedDictWithParams()
  assert(od!=None)

def test_state_returns():
  state_returns = ReturnStatus()
  assert(state_returns.RET_SUPER == 1)
  assert(state_returns.RET_TRAN_XP == 13)
  state_returns.append('RET_ZZ')
  assert(state_returns.RET_ZZ == 14)

def test_signal():
  signals = Signal()
  assert(signals.ENTRY_SIGNAL == 1)
  assert(signals.REFLECTION_SIGNAL == 4)
  signals.append('BAKE')
  assert(signals.BAKE == 6)
  assert(signals['BAKE'] == 6)

def test_event():
  signals = Signal()
  event   = Event(signal=signals.ENTRY_SIGNAL)
  assert(event.signal == 1)
  assert(event.signal_name == "ENTRY_SIGNAL")
  event = Event(signal="BOB")
  assert(event.signal == 6)
  assert(event.signal_name == "BOB")

def test_signal_singletons():
  '''The signals object from the event.py class is the growing signals enumeration'''
  local_signals = Signal()
  e = Event(signal = "MARY")
  assert(e.signal_name == "MARY")
  assert(signals.MARY > local_signals.REFLECTION_SIGNAL)
  e = Event(signal = "JANE")
  assert(e.signal_name == "JANE")
  assert(signals.JANE > signals.REFLECTION_SIGNAL)

  # we expect the local_signals class not to have to MANY enum
  with pytest.raises(KeyError) as excinfo:
    local_signals.MARY
