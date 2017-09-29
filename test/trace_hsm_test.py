import pytest
from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import reflect, Hsm, HsmTopologyException, spy_on
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

This is used for testing the type A topology in the trans_ method of the Hsm
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
    status = chart.trans(spy_graph_a1_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@pytest.mark.trace
def test_trace_topology_a_1():
  chart = Hsm()
  chart.start_at(trace_graph_a1_s1)
  pp(chart.full.trace)
  a = 1

  


