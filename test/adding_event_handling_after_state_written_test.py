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
#        +------------------- c2_s1 -----------+
#        |   +------ c2_s2-+   +------ c2_s3-+ |
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
def c2_s1(chart, e):

  with chart.signal_callback(e, c2_s1) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    with chart.parent_callback() as parent:
      status, chart.temp.fun = return_status.SUPER, parent

  return status


@spy_on
def c2_s2(chart, e):
  with chart.signal_callback(e, c2_s2) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    with chart.parent_callback() as parent:
      status, chart.temp.fun = return_status.SUPER, parent

  return status


@spy_on
def c2_s3(chart, e):
  with chart.signal_callback(e, c2_s3) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    with chart.parent_callback() as parent:
      status, chart.temp.fun = return_status.SUPER, parent

  return status


@pytest.fixture
def augmenting_state_methods_after_creation_and_test(request):

  def trans_to_c2_s1(chart, e):
    return chart.trans(c2_s1)

  def trans_to_c2_s3(chart, e):
    return chart.trans(c2_s3)

  def trans_to_c2_s2(chart, e):
    return chart.trans(c2_s2)

  def handled(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(c2_s1, signals.BB, trans_to_c2_s1)
  ao.register_signal_callback(c2_s1, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(c2_s1, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(c2_s1, signals.INIT_SIGNAL,  trans_to_c2_s2)
  ao.register_parent(c2_s1, ao.top)

  ao.register_signal_callback(c2_s2, signals.A, trans_to_c2_s3)
  ao.register_signal_callback(c2_s2, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(c2_s2, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(c2_s2, signals.INIT_SIGNAL,  handled)
  ao.register_parent(c2_s2, c2_s1)

  ao.register_signal_callback(c2_s3, signals.A, trans_to_c2_s2)
  ao.register_signal_callback(c2_s3, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(c2_s3, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(c2_s3, signals.INIT_SIGNAL,  handled)
  ao.register_parent(c2_s3, c2_s1)

  ao.start_at(c2_s2)
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.BB))
  time.sleep(0.50)

  yield(ao)


@pytest.mark.post_add
def test_post_addition_of_signal_handling(augmenting_state_methods_after_creation_and_test):

  ao = augmenting_state_methods_after_creation_and_test

  assert(ao.spy() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:c2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:c2_s1',
     'ENTRY_SIGNAL:c2_s1',
     'ENTRY_SIGNAL:c2_s2',
     'INIT_SIGNAL:c2_s2',
     '<- Queued:(0) Deferred:(0)',
     'A:c2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:c2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:c2_s2',
     'EXIT_SIGNAL:c2_s2',
     'ENTRY_SIGNAL:c2_s3',
     'INIT_SIGNAL:c2_s3',
     '<- Queued:(2) Deferred:(0)',
     'A:c2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:c2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:c2_s3',
     'EXIT_SIGNAL:c2_s3',
     'ENTRY_SIGNAL:c2_s2',
     'INIT_SIGNAL:c2_s2',
     '<- Queued:(1) Deferred:(0)',
     'BB:c2_s2',
     'BB:c2_s1',
     'EXIT_SIGNAL:c2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:c2_s2',
     'EXIT_SIGNAL:c2_s1',
     'ENTRY_SIGNAL:c2_s1',
     'INIT_SIGNAL:c2_s1',
     'SEARCH_FOR_SUPER_SIGNAL:c2_s2',
     'ENTRY_SIGNAL:c2_s2',
     'INIT_SIGNAL:c2_s2',
     '<- Queued:(0) Deferred:(0)'])


@pytest.mark.post_add
def test_creating_functions_from_a_template():

  tc2_s1 = state_method_template('tc2_s1')
  tc2_s2 = state_method_template('tc2_s2')
  tc2_s3 = state_method_template('tc2_s3')

  def trans_to_c2_s1(chart, e):
    return chart.trans(tc2_s1)

  def trans_to_c2_s3(chart, e):
    return chart.trans(tc2_s3)

  def trans_to_c2_s2(chart, e):
    return chart.trans(tc2_s2)

  def handled(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(tc2_s1, signals.BB, trans_to_c2_s1)
  ao.register_signal_callback(tc2_s1, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(tc2_s1, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(tc2_s1, signals.INIT_SIGNAL,  trans_to_c2_s2)
  ao.register_parent(tc2_s1, ao.top)

  ao.register_signal_callback(tc2_s2, signals.A, trans_to_c2_s3)
  ao.register_signal_callback(tc2_s2, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(tc2_s2, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(tc2_s2, signals.INIT_SIGNAL,  handled)
  ao.register_parent(tc2_s2, tc2_s1)

  ao.register_signal_callback(tc2_s3, signals.A, trans_to_c2_s2)
  ao.register_signal_callback(tc2_s3, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(tc2_s3, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(tc2_s3, signals.INIT_SIGNAL,  handled)
  ao.register_parent(tc2_s3, tc2_s1)

  ao.start_at(tc2_s2)

  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.BB))
  time.sleep(0.50)
  pp(ao.spy())

  # create a set of functions
  # manually wrap them with the spy
  # link them up (move test code into fixture)
  # begin the text


@pytest.mark.post_add
def test_to_s():
  tc2_s1 = state_method_template('tc2_s1')
  tc2_s2 = state_method_template('tc2_s2')
  tc2_s3 = state_method_template('tc2_s3')

  def trans_to_c2_s1(chart, e):
    return chart.trans(tc2_s1)

  def trans_to_c2_s3(chart, e):
    return chart.trans(tc2_s3)

  def trans_to_c2_s2(chart, e):
    return chart.trans(tc2_s2)

  def handled(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(tc2_s1, signals.BB, trans_to_c2_s1)
  ao.register_signal_callback(tc2_s1, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(tc2_s1, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(tc2_s1, signals.INIT_SIGNAL,  trans_to_c2_s2)
  ao.register_parent(tc2_s1, ao.top)

  # commented out line needed for test to work
  ao.register_signal_callback(tc2_s2, signals.A, trans_to_c2_s3)
  # ao.register_signal_callback(tc2_s2, signals.ENTRY_SIGNAL, handled)
  ao.register_signal_callback(tc2_s2, signals.EXIT_SIGNAL,  handled)
  ao.register_signal_callback(tc2_s2, signals.INIT_SIGNAL,  handled)
  ao.register_parent(tc2_s2, tc2_s1)

  # commented out lines needed for test to work
  ao.register_signal_callback(tc2_s3, signals.A, trans_to_c2_s2)
  ao.register_signal_callback(tc2_s3, signals.ENTRY_SIGNAL, handled)
  # ao.register_signal_callback(tc2_s3, signals.EXIT_SIGNAL,  handled)
  # ao.register_signal_callback(tc2_s3, signals.INIT_SIGNAL,  handled)
  ao.register_parent(tc2_s3, tc2_s1)

  expected_tc2_s1_as_flat_code = \
'''
def tc2_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = handled(chart, e)
  elsif(e.signal == signals.INIT_SIGNAL):
    status = trans_to_c2_s2(chart, e)
  elsif(e.signal == signals.BB):
    status = trans_to_c2_s1(chart, e)
  elsif(e.signal == signals.EXIT_SIGNAL):
    status = handled(chart, e)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status
'''
  assert(ao.to_code(tc2_s1) == expected_tc2_s1_as_flat_code)

  expected_tc2_s2_as_flat_code = \
'''
def tc2_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elsif(e.signal == signals.INIT_SIGNAL):
    status = handled(chart, e)
  elsif(e.signal == signals.A):
    status = trans_to_c2_s3(chart, e)
  elsif(e.signal == signals.EXIT_SIGNAL):
    status = handled(chart, e)
  else:
    status, chart.temp.fun = return_status.SUPER, tc2_s1
  return status
'''

  assert(ao.to_code(tc2_s2) == expected_tc2_s2_as_flat_code)
  expected_tc2_s3_as_flat_code = \
'''
def tc2_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = handled(chart, e)
  elif(e.signal == signals.INIT_SIGNAL):
    status = return_status.HANDLED
  elsif(e.signal == signals.A):
    status = trans_to_c2_s2(chart, e)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, tc2_s1
  return status
'''
  assert(ao.to_code(tc2_s3) == expected_tc2_s3_as_flat_code)

