import pytest
from miros.event import ReturnStatus, Signal, signals, Event, return_status
from miros.activeobject import ActiveObject, spy_on, HsmTopologyException, ActiveFabric

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
    status = chart.trans(active_objects_graph_g1_s2111)
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
    status = chart.trans(active_objects_graph_g1_s22)
  else:
    status, chart.temp.fun = return_status.SUPER, active_objects_graph_g1_s0
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
    status = chart.trans(active_objects_graph_g1_s321)
  elif(e.signal == signals.E):
    status = chart.trans(active_objects_graph_g1_s01)
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
    status = chart.trans(active_objects_graph_g1_s321)
  else:
    status, chart.temp.fun = return_status.SUPER, active_objects_graph_g1_s1
  return status

@spy_on
def g1_s211_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, active_objects_graph_g1_s21
  return status

@spy_on
def g1_s2111_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(active_objects_graph_g1_s321)
  else:
    status, chart.temp.fun = return_status.SUPER, active_objects_graph_g1_s211
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
    status = chart.trans(active_objects_graph_g1_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, active_objects_graph_g1_s1
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
    status, chart.temp.fun = return_status.SUPER, active_objects_graph_g1_s22
  return status

@spy_on
def g1_s32_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, active_objects_graph_g1_s3
  return status

@spy_on
def g1_s321_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, active_objects_graph_g1_s32
  return status

@pytest.fixture
def fabric(request):
  yield None
  print("turning off test")
  #af = ActiveFabric()
  #af.clear()

@pytest.mark.ao
def test_import(fabric):
  pass
  #ao = ActiveObject()
  #assert(ao != None)

@pytest.mark.ao
def test_start_state(fabric):
  pass
  #ao = ActiveObject()
  #ao.start_at(g1_s1_active_objects_graph)
  #pp(ao.spy_rtc())

