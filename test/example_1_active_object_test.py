import pytest
from miros import spy_on
from miros import signals, Event, return_status
from miros import ActiveObject
import pprint


def pp(item):
  pprint.pprint(item)


################################################################################
#                             simple_example_1                                 #
################################################################################
# The following state chart is used to test an example
#
#        +------- outer -----------+
#        |  +---- middle ------+   +----+
#        |  |  +- inner ---+   |   |    |
#        |  |  |           <-* <-W-+    R
#        |  |  +-----------+   |   |    |
#        |  +------------------+   <----+
#        +-------------------------+
#
# This is used for testing the type B topology in the trans_ method of the Hsm
# class.
@spy_on
def outer(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    # outer state custom entry code would go here
    status = return_status.HANDLED

  elif(e.signal == signals.EXIT_SIGNAL):
    # outer state custom exit code would go here
    status = return_status.HANDLED

  elif(e.signal == signals.WaitComplete):
    # we could write code which runs on the WaitComplete signal here
    status = chart.trans(middle)

  elif(e.signal == signals.ResetChart):
    # we could write code which runs on the ResetChart signal here
    status = chart.trans(outer)

  else:
    # this signal wasn't managed, pass a reference to the
    # method that is outside of us
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


@spy_on
def middle(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    # middle state custom entry code would go here
    status = return_status.HANDLED

  elif(e.signal == signals.EXIT_SIGNAL):
    # middle state custom exit code would go here
    status = return_status.HANDLED

  elif(e.signal == signals.INIT_SIGNAL):
    # middle state custom init code would go here
    status = chart.trans(inner)
  else:
    status, chart.temp.fun = return_status.SUPER, outer
  return status


@spy_on
def inner(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    # inner state custom entry code would go here
    status = return_status.HANDLED

  elif(e.signal == signals.EXIT_SIGNAL):
    # inner state custom exit code would go here
    status = return_status.HANDLED

  else:
    status, chart.temp.fun = return_status.SUPER, middle
  return status


# grep test name to view diagram
@pytest.mark.example
def test1_trans_topology_a():
  ao = ActiveObject()
  ao.start_at(outer)
  pp(ao.spy_full())
  assert(ao.spy_full() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:outer',
     'ENTRY_SIGNAL:outer',
     'INIT_SIGNAL:outer',
     '<- Queued:(0) Deferred:(0)']
  )
  pp(ao.spy_full())
  print(ao.trace())
  event_w = Event(signal=signals.WaitComplete)
  ao.clear_trace()
  ao.post_fifo(event_w)
  import time
  time.sleep(0.1)
  pp(ao.spy_rtc())
  print(ao.trace())

  # stop the threads
  ao.stop()

  # clear the spy and the trace
  ao.clear_spy()
  ao.clear_trace()

  # post a number of events and see what happens
  event_wait_complete = Event(signal=signals.WaitComplete)
  event_reset_chart = Event(signal=signals.ResetChart)
  ao.post_fifo(event_wait_complete)
  ao.post_fifo(event_reset_chart)
  ao.post_fifo(event_wait_complete)
  ao.post_fifo(event_reset_chart)
  time.sleep(0.3)
  print(ao.trace())
  pp(ao.spy_full())
