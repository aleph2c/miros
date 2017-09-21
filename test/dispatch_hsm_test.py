import pytest
from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import reflect, Hsm, HsmTopologyException
import pprint
def pp(item):
  pprint.pprint(item)
################################################################################
#                               Dispatch Graph 1                                #
################################################################################
'''           The following state chart is used for the init test
      +------------------------------ d1 ------------------------------+
      |                                                                +-----+
      |                                                                |     a
      |                                                                |     |
      |                                                                <-----+
      +----------------------------------------------------------------+     
'''
def dispatch_graph_1_d1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    status = chart.trans(dispatch_graph_1_d1)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status
################################################################################
#                               Dispatch Graph n                                #
################################################################################
'''           The following state chart is used for the init test
      +------------------------------ d1 ------------------------------+
      |     +-------------------------d2-------------------------+     +-----+
      |  *  | *  +--------------------d3---------------------+   |     |     a
      |  |  | +-->                                           +   |     |     |
      |  +-->    +-------------------------------------------+   |     |     |
      |     +----------------------------------------------------+     <-----+
      +----------------------------------------------------------------+     
'''

def dispatch_graph_n_d1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_n_d2)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    status = chart.trans(dispatch_graph_n_d1)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_n_d2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_n_d3)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_n_d1
  return status

def dispatch_graph_n_d3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_n_d2
  return status

@pytest.fixture
def spy_chart(request):
  chart = Hsm()
  spy   = []
  chart.augment(other=spy, name="spy")
  signals.append("A")
  yield chart
  del spy
  del chart

@pytest.mark.dispatch
def test_init_test_1(spy_chart):
  chart = spy_chart
  chart.start_at(dispatch_graph_1_d1)
  event_a  = Event(signal=signals.A)
  chart.dispatch(e=event_a)
  pp(chart.spy)
