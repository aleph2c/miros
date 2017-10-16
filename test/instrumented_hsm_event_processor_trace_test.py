import pytest
from miros.event import ReturnStatus, Signal, signals, Event, return_status
from miros.hsm   import InstrumentedHsmEventProcessor, HsmTopologyException, spy_on
import pprint
def pp(item):
  print("")
  pprint.pprint(item)

signals.append("A")
signals.append("B")
signals.append("C")
signals.append("D")
signals.append("E")
signals.append("F")
signals.append("G")

################################################################################
#                               Trace Graph A1                                 #
################################################################################
'''    The following state chart is used to test the spy on topology A

                            +- graph_a1_s1 -+
                            |               +-----+
                            |               |     a
                            |               <-----+
                            +---------------+

This is used for testing the type A topology in the trans_ method of the HsmEventProcessor
class.
  * test__trace_topology_a_1 (diagram)
  * test__trace_topology_a_2 (diagram)
'''
@spy_on
def trace_graph_a1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(trace_graph_a1_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@pytest.mark.trace
def test_trace_topology_a_1():
  chart = InstrumentedHsmEventProcessor()
  chart.start_at(trace_graph_a1_s1)
  chart.dispatch(Event(signal=signals.A))
  pp(chart.full.trace)
  assert(len(chart.full.trace) == 2)
  start_trace = chart.full.trace[0]
  assert(start_trace.start_state == 'top')
  assert(start_trace.signal == None)
  assert(start_trace.end_state == 'trace_graph_a1_s1')
  trans_trace = chart.full.trace[1]
  trans_trace.start_state == 'trace_graph_a1_s1'
  trans_trace.end_state == 'trace_graph_a1_s1'
  trans_trace.signal == 'A'

################################################################################
#                               Trace Graph G1                                 #
################################################################################
'''           The following state chart is used to test topology G

                  +-------------------------------- g1_s1 --------------+
   +---g1_s0---+  | e/ print("ultimate hook")                           |
   |+-g1_s01--+|  |                      +---------g1_s22 ----------+   |
   ||         ++-----c------------------->                          |   |
   ||         ||  |                      | +-------g1_s3 ---------+ |   |
   |+---------+|  | +-------g1_s21----+  | |    +----g1_s32-----+ | |   |
   +-----------+  | | +--g1_s211-----+|  | |    |  +-g1_s321--+ | | |   |
                  | | |+-g1_s2111+   ||  | |    |  |          | | | |   |
                  | | ||         |   ||  | |    |  |          | | | |   |
                  | | ||         |   |+-------b---->          | | | |   |
                  | | ||         |   ||  | |    |  |          | | | |   |
                  | | ||         |   ||  | |    |  |          | | | |   |
                  | | ||         |   ||  | |  +---->          | | | |   |
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
  * test_trace_topology_g1_1 - start in graph_g1_s211 (diagram -> a)
  * test_trace_topology_g1_2 - start in graph_g1_s211 (diagram -> b)
  * test_trace_topology_g1_3 - start in graph_g1_s01  (diagram -> a)
  * test_trace_topology_g1_4 - start in graph_g1_s321 (diagram -> d)
'''
@spy_on
def trace_graph_g1_s0(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def trace_graph_g1_s01(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    status = chart.trans(trace_graph_g1_s22)
  else:
    status, chart.temp.fun = return_status.SUPER, trace_graph_g1_s0
  return status

@spy_on
def trace_graph_g1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.E):
    print("handled")
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def trace_graph_g1_s21(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(trace_graph_g1_s321)
  else:
    status, chart.temp.fun = return_status.SUPER, trace_graph_g1_s1
  return status

@spy_on
def trace_graph_g1_s211(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, trace_graph_g1_s21
  return status

@spy_on
def trace_graph_g1_s2111(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(trace_graph_g1_s321)
  else:
    status, chart.temp.fun = return_status.SUPER, trace_graph_g1_s211
  return status

@spy_on
def trace_graph_g1_s22(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.D):
    status = chart.trans(trace_graph_g1_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, trace_graph_g1_s1
  return status

@spy_on
def trace_graph_g1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, trace_graph_g1_s22
  return status

@spy_on
def trace_graph_g1_s32(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, trace_graph_g1_s3
  return status

@spy_on
def trace_graph_g1_s321(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, trace_graph_g1_s32
  return status

@pytest.mark.trace
@pytest.mark.topology_g
def test_trace_topology_g1_1():
  chart = InstrumentedHsmEventProcessor()
  chart.start_at(trace_graph_g1_s2111)
  chart.dispatch(Event(signal=signals.A))
  pp(chart.full.spy)
  pp(chart.full.trace)
  #assert(chart.full.spy == expected_behavior)
  assert(len(chart.full.trace) == 2)
  start_trace = chart.full.trace[0]
  assert(start_trace.start_state == 'top')
  assert(start_trace.signal == None)
  assert(start_trace.end_state == 'trace_graph_g1_s2111')
  trans_trace = chart.full.trace[1]
  trans_trace.start_state == 'trace_graph_g1_s2111'
  trans_trace.end_state == 'ttrace_graph_g1_s321'
  trans_trace.signal == 'A'

@pytest.mark.trace
@pytest.mark.topology_g
def test_trace_topology_g1_2():
  chart = InstrumentedHsmEventProcessor()
  chart.start_at(trace_graph_g1_s2111)
  chart.dispatch(Event(signal=signals.E))
  pp(chart.full.spy)
  pp(chart.full.trace)
  #assert(chart.full.spy == expected_behavior)
  assert(len(chart.full.trace) == 1)
