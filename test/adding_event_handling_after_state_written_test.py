import time
import pytest

from miros.hsm import spy_on, pp
from miros.activeobject import ActiveObject, ActiveFabric
from miros.event import signals, Event, return_status


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
@spy_on
def c2_s1(chart, e):

  with chart.signal_callback(e) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    with chart.parent_callback() as parent:
      status, chart.temp.fun = return_status.SUPER, parent

  return status


@spy_on
def c2_s2(chart, e):
  with chart.signal_callback(e) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    with chart.parent_callback() as parent:
      status, chart.temp.fun = return_status.SUPER, parent

  return status


@spy_on
def c2_s3(chart, e):
  with chart.signal_callback(e) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    with chart.parent_callback() as parent:
      status, chart.temp.fun = return_status.SUPER, parent

  return status


@pytest.mark.post_add
def test_post_addition_of_signal_handling(fabric_fixture):

  def trans_to_c2_s1(chart, e):
    return chart.trans(c2_s1)

  def trans_to_c2_s3(chart, e):
    return chart.trans(c2_s3)

  def trans_to_c2_s2(chart, e):
    return chart.trans(c2_s2)

  def empty(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(c2_s1, signals.BB, trans_to_c2_s1)
  ao.register_signal_callback(c2_s1, signals.ENTRY_SIGNAL, empty)
  ao.register_signal_callback(c2_s1, signals.EXIT_SIGNAL,  empty)
  ao.register_signal_callback(c2_s1, signals.INIT_SIGNAL,  trans_to_c2_s2)
  ao.register_parent(c2_s1, ao.top)

  ao.register_signal_callback(c2_s2, signals.A, trans_to_c2_s3)
  ao.register_signal_callback(c2_s2, signals.ENTRY_SIGNAL, empty)
  ao.register_signal_callback(c2_s2, signals.EXIT_SIGNAL,  empty)
  ao.register_signal_callback(c2_s2, signals.INIT_SIGNAL,  empty)
  ao.register_parent(c2_s2, c2_s1)

  ao.register_signal_callback(c2_s3, signals.A, trans_to_c2_s2)
  ao.register_signal_callback(c2_s3, signals.ENTRY_SIGNAL, empty)
  ao.register_signal_callback(c2_s3, signals.EXIT_SIGNAL,  empty)
  ao.register_signal_callback(c2_s3, signals.INIT_SIGNAL,  empty)
  ao.register_parent(c2_s3, c2_s1)

  ao.start_at(c2_s2)
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.BB))
  time.sleep(0.50)

  pp(ao.spy())

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

