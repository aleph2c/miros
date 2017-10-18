import pytest
from miros.event import ReturnStatus, Signal, signals, Event, return_status
from miros.activeobject import ActiveObject, spy_on, HsmTopologyException, ActiveFabric
from miros.activeobject import LockingDeque
import pprint
def pp(item):
  pprint.pprint(item)

signals.append("W")
signals.append("R")
################################################################################
#                             simple_example_1                                 #
################################################################################
'''           The following state chart is used to test an example

                     +------- outer -----------+
                     |  +---- middle ------+   +----+
                     |  |  +- inner ---+   |   |    |
                     |  |  |           <-* <-W-+    R
                     |  |  +-----------+   |   |    |
                     |  +------------------+   <----+
                     +-------------------------+    

This is used for testing the type B topology in the trans_ method of the Hsm
class.
'''
@spy_on
def outer(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.W):
    status = chart.trans(middle)
  elif(e.signal == signals.R):
    status = chart.trans(outer)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def middle(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = chart.trans(inner)
  else:
    status, chart.temp.fun = return_status.SUPER, outer
  return status

@spy_on
def inner(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
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
  assert( ao.spy_full() == \
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:outer',
     'SEARCH_FOR_SUPER_SIGNAL:top',
     'ENTRY_SIGNAL:top',
     'ENTRY_SIGNAL:outer',
     'INIT_SIGNAL:outer',
     '<- Queued:(0) Deferred:(0)']
  )
  pp(ao.spy_full())
  print(ao.trace())
  event_w = Event(signal=signals.W)
  ao.clear_trace()
  ao.post_fifo(event_w)
  import time
  time.sleep(0.1)
  pp(ao.spy_rtc())
  print(ao.trace())

  # chart = spy_chart
  # expected_behavior = \
  #['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_a1_s1',
  # 'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  # 'INIT_SIGNAL:dispatch_graph_a1_s1',
  # 'EXIT_SIGNAL:dispatch_graph_a1_s1',
  # 'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  # 'INIT_SIGNAL:dispatch_graph_a1_s1']

  # chart.start_at(dispatch_graph_a1_s1)
  # event  = Event(signal=signals.A)
  # chart.dispatch(e=event)
  # assert(chart.spy_log == expected_behavior)

