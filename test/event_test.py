import pytest
from miros.event import OrderedDictWithParams
from miros.event import ReturnStatus
from miros.event import SignalSource
from miros.event import Signal
from miros.event import signals
from miros.event import Event


@pytest.mark.event
def test_ordered_dict_with_params():
  od = OrderedDictWithParams()
  assert(od is not None)


@pytest.mark.event
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
  assert(signals.BAKE >= 6)
  assert(signals['BAKE'] >= 6)


def test_inner_signals():
  signals = SignalSource()
  assert(signals.ENTRY_SIGNAL == 1)
  assert(signals.REFLECTION_SIGNAL == 4)
  signals.append('BAKE')
  assert(signals.BAKE >= 6)
  assert(signals.is_inner_signal(1) is True)
  assert(signals.is_inner_signal(5) is True)
  assert(signals.is_inner_signal(6) is False)
  assert(signals.is_inner_signal('ENTRY_SIGNAL') is True)
  assert(signals.is_inner_signal('SEARCH_FOR_SUPER_SIGNAL') is True)
  assert(signals.is_inner_signal('BAKE') is False)
  assert(signals.is_inner_signal('NOT_THERE') is False)


def test_event():
  signals = SignalSource()
  event   = Event(signal=signals.ENTRY_SIGNAL)
  assert(event.signal is 1)
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


def test_automatic_construction_of_signals():
  '''We don't want to have to define a signal number and signal name twice, if
  it is referenced, it is invented'''
  e = Event(signal=signals.NOT_INVENTED_YET)
  assert(e.signal_name is 'NOT_INVENTED_YET')
