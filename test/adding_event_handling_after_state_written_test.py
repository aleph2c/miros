import time
import pytest

from miros.hsm import spy_on, pp, state_method_template
from miros.activeobject import ActiveObject
from miros.event import signals, Event, return_status
from copy import copy


# diagram for next set of state functions
#
#  The following state chart is used to test topology C
#
#        +------------------- s1 -----------+
#        |   +------ s2-+   +------ s3-+ |
#        | * |             |   |             | +----+
#        | | |             +-a->             | |    |
#        | +->             <-a-+             | |    bb
#        |   |             |   |             | |    |
#        |   |             |   |             | <----+
#        |   +-------------+   +-------------+ |
#        +-------------------------------------+
#
# This is used for testing the type C topology within another state, in the trans_
# method of the HsmEventProcessor class.
def state_method_template(name):

  def base_state_method(chart, e):
    with chart.signal_callback(e, name) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback(name) as parent:
        status, chart.temp.fun = return_status.SUPER, parent
    return status

  resulting_function = copy(base_state_method)
  resulting_function.__name__ = name
  resulting_function = spy_on(resulting_function)

  return resulting_function


@spy_on
def s1(chart, e):

  with chart.signal_callback(e, s1) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    with chart.parent_callback() as parent:
      status, chart.temp.fun = return_status.SUPER, parent

  return status


@spy_on
def s2(chart, e):
  with chart.signal_callback(e, s2) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    with chart.parent_callback() as parent:
      status, chart.temp.fun = return_status.SUPER, parent

  return status


@spy_on
def s3(chart, e):
  with chart.signal_callback(e, s3) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    with chart.parent_callback() as parent:
      status, chart.temp.fun = return_status.SUPER, parent

  return status


@pytest.fixture
def augmenting_state_methods_after_creation_and_test(request):

  def trans_to_s1(chart, e):
    return chart.trans(s1)

  def trans_to_c2_s3(chart, e):
    return chart.trans(s3)

  def trans_to_c2_s2(chart, e):
    return chart.trans(s2)

  def handled(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(s1, signals.BB, trans_to_s1)
  ao.register_signal_callback(s1, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(s1, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(s1, signals.INIT_SIGNAL,  trans_to_c2_s2)
  ao.register_parent(s1, ao.top)

  ao.register_signal_callback(s2, signals.A, trans_to_c2_s3)
  ao.register_signal_callback(s2, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(s2, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(s2, signals.INIT_SIGNAL,  handled)
  ao.register_parent(s2, s1)

  ao.register_signal_callback(s3, signals.A, trans_to_c2_s2)
  ao.register_signal_callback(s3, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(s3, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(s3, signals.INIT_SIGNAL,  handled)
  ao.register_parent(s3, s1)

  ao.start_at(s2)
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.BB))
  time.sleep(0.10)

  yield(ao)


@pytest.mark.post_add
def test_post_addition_of_signal_handling(augmenting_state_methods_after_creation_and_test):

  ao = augmenting_state_methods_after_creation_and_test

  assert(ao.spy() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:s2',
     'SEARCH_FOR_SUPER_SIGNAL:s1',
     'ENTRY_SIGNAL:s1',
     'ENTRY_SIGNAL:s2',
     'INIT_SIGNAL:s2',
     '<- Queued:(0) Deferred:(0)',
     'A:s2',
     'SEARCH_FOR_SUPER_SIGNAL:s3',
     'SEARCH_FOR_SUPER_SIGNAL:s2',
     'EXIT_SIGNAL:s2',
     'ENTRY_SIGNAL:s3',
     'INIT_SIGNAL:s3',
     '<- Queued:(2) Deferred:(0)',
     'A:s3',
     'SEARCH_FOR_SUPER_SIGNAL:s2',
     'SEARCH_FOR_SUPER_SIGNAL:s3',
     'EXIT_SIGNAL:s3',
     'ENTRY_SIGNAL:s2',
     'INIT_SIGNAL:s2',
     '<- Queued:(1) Deferred:(0)',
     'BB:s2',
     'BB:s1',
     'EXIT_SIGNAL:s2',
     'SEARCH_FOR_SUPER_SIGNAL:s2',
     'EXIT_SIGNAL:s1',
     'ENTRY_SIGNAL:s1',
     'INIT_SIGNAL:s1',
     'SEARCH_FOR_SUPER_SIGNAL:s2',
     'ENTRY_SIGNAL:s2',
     'INIT_SIGNAL:s2',
     '<- Queued:(0) Deferred:(0)'])


@pytest.mark.post_add
def test_creating_functions_from_a_template():

  ts1 = state_method_template('ts1')
  tc2_s2 = state_method_template('tc2_s2')
  tc2_s3 = state_method_template('tc2_s3')

  def trans_to_s1(chart, e):
    return chart.trans(ts1)

  def trans_to_c2_s3(chart, e):
    return chart.trans(tc2_s3)

  def trans_to_c2_s2(chart, e):
    return chart.trans(tc2_s2)

  def handled(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(ts1, signals.BB, trans_to_s1)
  ao.register_signal_callback(ts1, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(ts1, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(ts1, signals.INIT_SIGNAL,  trans_to_c2_s2)
  ao.register_parent(ts1, ao.top)

  ao.register_signal_callback(tc2_s2, signals.A, trans_to_c2_s3)
  ao.register_signal_callback(tc2_s2, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(tc2_s2, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(tc2_s2, signals.INIT_SIGNAL,  handled)
  ao.register_parent(tc2_s2, ts1)

  ao.register_signal_callback(tc2_s3, signals.A, trans_to_c2_s2)
  ao.register_signal_callback(tc2_s3, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(tc2_s3, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(tc2_s3, signals.INIT_SIGNAL,  handled)
  ao.register_parent(tc2_s3, ts1)

  ao.start_at(tc2_s2)

  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.BB))
  time.sleep(0.1)
  assert(ao.spy() == \
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:ts1',
     'ENTRY_SIGNAL:ts1',
     'ENTRY_SIGNAL:tc2_s2',
     'INIT_SIGNAL:tc2_s2',
     '<- Queued:(0) Deferred:(0)',
     'A:tc2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'EXIT_SIGNAL:tc2_s2',
     'ENTRY_SIGNAL:tc2_s3',
     'INIT_SIGNAL:tc2_s3',
     '<- Queued:(2) Deferred:(0)',
     'A:tc2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s3',
     'EXIT_SIGNAL:tc2_s3',
     'ENTRY_SIGNAL:tc2_s2',
     'INIT_SIGNAL:tc2_s2',
     '<- Queued:(1) Deferred:(0)',
     'BB:tc2_s2',
     'BB:ts1',
     'EXIT_SIGNAL:tc2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'EXIT_SIGNAL:ts1',
     'ENTRY_SIGNAL:ts1',
     'INIT_SIGNAL:ts1',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'ENTRY_SIGNAL:tc2_s2',
     'INIT_SIGNAL:tc2_s2',
     '<- Queued:(0) Deferred:(0)'])


@pytest.mark.post_add
def test_to_code():
  ts1 = state_method_template('ts1')
  tc2_s2 = state_method_template('tc2_s2')
  tc2_s3 = state_method_template('tc2_s3')

  def trans_to_s1(chart, e):
    return chart.trans(ts1)

  def trans_to_c2_s3(chart, e):
    return chart.trans(tc2_s3)

  def trans_to_c2_s2(chart, e):
    return chart.trans(tc2_s2)

  def handled(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(ts1, signals.BB, trans_to_s1)
  ao.register_signal_callback(ts1, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(ts1, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(ts1, signals.INIT_SIGNAL,  trans_to_c2_s2)
  ao.register_parent(ts1, ao.top)

  # commented out line needed for test to work
  ao.register_signal_callback(tc2_s2, signals.A, trans_to_c2_s3)
  ao.register_signal_callback(tc2_s2, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(tc2_s2, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(tc2_s2, signals.INIT_SIGNAL,  handled)
  ao.register_parent(tc2_s2, ts1)

  # commented out lines needed for test to work
  ao.register_signal_callback(tc2_s3, signals.A, trans_to_c2_s2)
  ao.register_signal_callback(tc2_s3, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(tc2_s3, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(tc2_s3, signals.INIT_SIGNAL,  handled)
  ao.register_parent(tc2_s3, ts1)

  expected_ts1_as_flat_code = \
'''
@spy_on
def ts1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = trans_to_c2_s2(chart, e)
  elif(e.signal == signals.BB):
    status = trans_to_s1(chart, e)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status
'''
  assert(ao.to_code(ts1) == expected_ts1_as_flat_code)

  expected_tc2_s2_as_flat_code = \
'''
@spy_on
def tc2_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = trans_to_c2_s3(chart, e)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, ts1
  return status
'''

  assert(ao.to_code(tc2_s2) == expected_tc2_s2_as_flat_code)
  expected_tc2_s3_as_flat_code = \
'''
@spy_on
def tc2_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = trans_to_c2_s2(chart, e)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, ts1
  return status
'''
  assert(ao.to_code(tc2_s3) == expected_tc2_s3_as_flat_code)

  ao.start_at(tc2_s2)

  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.BB))
  time.sleep(0.1)
  assert(ao.spy() == \
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:ts1',
     'ENTRY_SIGNAL:ts1',
     'ENTRY_SIGNAL:tc2_s2',
     'INIT_SIGNAL:tc2_s2',
     '<- Queued:(0) Deferred:(0)',
     'A:tc2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'EXIT_SIGNAL:tc2_s2',
     'ENTRY_SIGNAL:tc2_s3',
     'INIT_SIGNAL:tc2_s3',
     '<- Queued:(2) Deferred:(0)',
     'A:tc2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s3',
     'EXIT_SIGNAL:tc2_s3',
     'ENTRY_SIGNAL:tc2_s2',
     'INIT_SIGNAL:tc2_s2',
     '<- Queued:(1) Deferred:(0)',
     'BB:tc2_s2',
     'BB:ts1',
     'EXIT_SIGNAL:tc2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'EXIT_SIGNAL:ts1',
     'ENTRY_SIGNAL:ts1',
     'INIT_SIGNAL:ts1',
     'SEARCH_FOR_SUPER_SIGNAL:tc2_s2',
     'ENTRY_SIGNAL:tc2_s2',
     'INIT_SIGNAL:tc2_s2',
     '<- Queued:(0) Deferred:(0)'])
