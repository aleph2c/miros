import pytest
from miros.event import OrderedDictWithParams, StateReturns, Signal, Event

def test_ordered_dict_with_params():
  od = OrderedDictWithParams()
  assert(od!=None)

def test_state_returns():
  state_returns = StateReturns()
  assert(state_returns.RET_SUPER == 1)
  assert(state_returns.RET_TRAN_XP == 13)
  state_returns.append('RET_ZZ')
  assert(state_returns.RET_ZZ == 14)

def test_signal():
  signals = Signal()
  assert(signals.ENTRY_SIGNAL == 1)
  assert(signals.REFLECTION_SIGNAL == 4)
  signals.append('BAKE')
  assert(signals.BAKE == 5)
  assert(signals['BAKE'] == 5)

def test_event():
  signals = Signal()
  event   = Event(signal=signals.ENTRY_SIGNAL)
  assert(event.signal == 1)
  assert(event.signal_name == "ENTRY_SIGNAL")
  event = Event(signal="BOB")
  assert(event.signal == 5)
  assert(event.signal_name == "BOB")
