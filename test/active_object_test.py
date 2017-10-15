import pytest
from miros.event import ReturnStatus, Signal, signals, Event, return_status
from miros.activeobject import ActiveObject, spy_on, HsmTopologyException, ActiveFabric
from miros.activeobject import LockingDeque

import pprint
def pp(item):
  print("")
  pprint.pprint(item)

Signal().append("A")
Signal().append("B")
Signal().append("C")
Signal().append("D")
Signal().append("E")
Signal().append("F")

################################################################################
#                          ActiveObject Graph G1                               #
################################################################################
'''
                     +-------------------------------- g1_s1 --------------+
   +---g1_s0------+  | *i/fifo(e)                                          |
   |+-g1_s01-----+|  |                      +---------g1_s22 ----------+   |
   ||e/fifo(a)   |+------c------------------>  *i/fifo(d)              |   |
   ||e/lifo(f)   ||  |                      |                          |   |
   ||e/recall()  <-e-+                      | +-------g1_s3 ---------+ |   |
   |+------------+|  |                      | | *i/defer(f)          | |   |
   |+------------+|  | +-------g1_s21----+  | |    +----g1_s32-----+ | |   |
   +-+------------+  | | +--g1_s211-----+|  | |    |  +-g1_s321--+ | | |   |
     |               | | |+-g1_s2111+   ||  | |    |  |          | | | |   |
     |               | | ||         |   ||  | |    |  |          | | | |   |
     |               | | ||         |   ||  | |    |  |          | | | |   |
     |               | | ||         |   ||  | |    |  |          | | | |   |
     |               | | ||         |   |+-------b---->          <----f----+
     |               | | ||         |   ||  | |    |  |          | | | |   |
     |               | | ||         |   ||  | |    |  |          | | | |   |
     +----------f--------->         |   ||  | |  +---->          | | | |   |
                     | | ||         |   ||  | |  | |  |          | | | |   |
                     | | |++--------+   ||  | |  | |  |          | | | +-d->
                     | | +-|------------+|  | |  | |  +----------+ | | |   |
                     | +---|-------------+  | |  | +---------------+ | |   |
                     |     |                | +--|-------------------+ |   |
                     |     +------------a--------+                     |   |
                     |                      +--------------------------+   |
                     |                                                     |
                     +-----------------------------------------------------+


This is used for testing the type E topology in the trans_ method of the HsmEventProcessor
class.
  * test_hsm_next_rtc - start in active_objects_graph_g1_s22
'''
@spy_on
def g1_s0_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.F):
    status = chart.trans(g1_s2111_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def g1_s01_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.post_fifo(Event(signal=signals.A))
    chart.post_lifo(Event(signal=signals.F))
    chart.recall()
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    status = chart.trans(g1_s22_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s0_active_objects_graph
  return status

@spy_on
def g1_s1_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    chart.post_fifo(Event(signal=signals.E))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.F):
    status = chart.trans(g1_s321_active_objects_graph)
  elif(e.signal == signals.E):
    status = chart.trans(g1_s01_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def g1_s21_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(g1_s321_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s1_active_objects_graph
  return status

@spy_on
def g1_s211_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s21_active_objects_graph
  return status

@spy_on
def g1_s2111_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(g1_s321_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s211_active_objects_graph
  return status

@spy_on
def g1_s22_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.post_fifo(Event(signal=signals.D))
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.D):
    status = chart.trans(g1_s1_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s1_active_objects_graph
  return status

@spy_on
def g1_s3_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.defer(Event(signal=signals.F))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s22_active_objects_graph
  return status

@spy_on
def g1_s32_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s3_active_objects_graph
  return status

@spy_on
def g1_s321_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s32_active_objects_graph
  return status

@pytest.fixture
def fabric_fixture(request):
  yield
  # shut down the active fabric for the next test
  ActiveFabric().stop()
  ActiveFabric().clear()

@pytest.mark.ao
def test_import(fabric_fixture):
  ao = ActiveObject()
  assert(ao != None)

@pytest.mark.ao
def test_start_stop(fabric_fixture):
  ao = ActiveObject()
  ao.start_at(g1_s22_active_objects_graph)
  assert(ao.thread.is_alive() == True)
  ao.stop()
  assert( ao.spy_full() == \
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s22_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:top',
     'ENTRY_SIGNAL:top',
     'ENTRY_SIGNAL:g1_s1_active_objects_graph',
     'ENTRY_SIGNAL:g1_s22_active_objects_graph',
     'INIT_SIGNAL:g1_s22_active_objects_graph',
     'POST_FIFO:D',
     'D:g1_s22_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s22_active_objects_graph',
     'EXIT_SIGNAL:g1_s22_active_objects_graph',
     'INIT_SIGNAL:g1_s1_active_objects_graph',
     'POST_FIFO:E',
     '<- Queued:(1) Deferred:(0)',
     'E:g1_s1_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s01_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s0_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:top',
     'EXIT_SIGNAL:g1_s1_active_objects_graph',
     'ENTRY_SIGNAL:g1_s0_active_objects_graph',
     'ENTRY_SIGNAL:g1_s01_active_objects_graph',
     'POST_FIFO:A',
     'POST_LIFO:F',
     'INIT_SIGNAL:g1_s01_active_objects_graph',
     '<- Queued:(2) Deferred:(0)',
     'F:g1_s01_active_objects_graph',
     'F:g1_s0_active_objects_graph',
     'EXIT_SIGNAL:g1_s01_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s01_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s2111_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s0_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s211_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s21_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:top',
     'EXIT_SIGNAL:g1_s0_active_objects_graph',
     'ENTRY_SIGNAL:g1_s1_active_objects_graph',
     'ENTRY_SIGNAL:g1_s21_active_objects_graph',
     'ENTRY_SIGNAL:g1_s211_active_objects_graph',
     'ENTRY_SIGNAL:g1_s2111_active_objects_graph',
     'INIT_SIGNAL:g1_s2111_active_objects_graph',
     '<- Queued:(1) Deferred:(0)',
     'A:g1_s2111_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s321_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s2111_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s32_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s3_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s22_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:top',
     'EXIT_SIGNAL:g1_s2111_active_objects_graph',
     'EXIT_SIGNAL:g1_s211_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s211_active_objects_graph',
     'EXIT_SIGNAL:g1_s21_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s21_active_objects_graph',
     'ENTRY_SIGNAL:g1_s22_active_objects_graph',
     'ENTRY_SIGNAL:g1_s3_active_objects_graph',
     'ENTRY_SIGNAL:g1_s32_active_objects_graph',
     'ENTRY_SIGNAL:g1_s321_active_objects_graph',
     'INIT_SIGNAL:g1_s321_active_objects_graph',
     '<- Queued:(0) Deferred:(0)',
     'stop_active_object:g1_s321_active_objects_graph',
     'stop_active_object:g1_s32_active_objects_graph',
     'stop_active_object:g1_s3_active_objects_graph',
     'stop_active_object:g1_s22_active_objects_graph',
     'stop_active_object:g1_s1_active_objects_graph',
     'stop_active_object:top',
     '<- Queued:(0) Deferred:(0)']
     )
  ao.clear_spy()
  assert(ao.spy_full() == [])

@pytest.mark.ao
def test_start_stop(fabric_fixture):
  ao = ActiveObject()
  ao.start_at(g1_s22_active_objects_graph)
  assert(ao.thread.is_alive() == True)
  ao.stop()
  print(ao.trace())
  #pp(ao.spy_full())
