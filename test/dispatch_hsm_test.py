import pytest
from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import reflect, Hsm, HsmTopologyException
import pprint
def pp(item):
  pprint.pprint(item)
################################################################################
#                             Dispatch Graph A1                                #
################################################################################
'''           The following state chart is used to test topology A

                            +- graph_a1_s1 -+
                            |               +-----+
                            |               |     |
                            |               |     a
                            |               |     |
                            |               <-----+
                            +---------------+     

This is used for testing the type A topology in the trans_ method of the Hsm
class.
  * test_trans_topology_a_1 (diagram)
'''
def dispatch_graph_a1_s1(chart, e):
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
    status = chart.trans(dispatch_graph_a1_s1)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status
################################################################################
#                             Dispatch Graph B1                                #
################################################################################
'''           The following state chart is used to test topology B 

                       +------- graph_b1_s1 -----------+
                       |  +---- graph_b1_s2 -------+   |       
                       |  |  +- graph_b1_s3 -+     |   |       
                       |  |  |               |   +-+   |       
                       |  |  |               <-b-+ <-a-+       
                       |  |  +---------------+     |   |       
                       |  +------------------------+   |       
                       +-------------------------------+     

This is used for testing the type A topology in the trans_ method of the Hsm
class.
  * test_trans_topology_b1_1 (diagram)
  * test_trans_topology_b2_2 (diagram)
'''
def dispatch_graph_b1_s1(chart, e):
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
    status = chart.trans(dispatch_graph_b1_s2)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_b1_s2(chart, e):
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
  elif(e.signal == signals.B):
    status = chart.trans(dispatch_graph_b1_s3)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_b1_s1
  return status

def dispatch_graph_b1_s3(chart, e):
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
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_b1_s2
  return status
################################################################################
#                               Dispatch Graph n                                #
################################################################################
'''           The following state chart is used for the init test
      +------------------------------ s1 ------------------------------+
      |     +-------------------------s2-------------------------+     +-----+
      |  *  | *  +--------------------s3---------------------+   |     |     a
      |  |  | +-->                                           +   |     |     |
      |  +-->    +-------------------------------------------+   |     |     |
      |     +----------------------------------------------------+     <-----+
      +----------------------------------------------------------------+     
'''

def dispatch_graph_n_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_n_s2)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    status = chart.trans(dispatch_graph_n_s1)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_n_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_n_s3)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_n_s1
  return status

def dispatch_graph_n_s3(chart, e):
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
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_n_s2
  return status

@pytest.fixture
def spy_chart(request):
  chart = Hsm()
  spy   = []
  chart.augment(other=spy, name="spy")
  signals.append("A")
  signals.append("B")
  yield chart
  del spy
  del chart

# grep test name to view diagram
@pytest.mark.dispatch
def test1_trans_topology_a(spy_chart):
  chart = spy_chart
  expected_behavior = \
 ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_a1_s1',
  'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  'INIT_SIGNAL:dispatch_graph_a1_s1',
  'EXIT_SIGNAL:dispatch_graph_a1_s1',
  'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  'INIT_SIGNAL:dispatch_graph_a1_s1']

  chart.start_at(dispatch_graph_a1_s1)
  event_a  = Event(signal=signals.A)
  chart.dispatch(e=event_a)
  assert(chart.spy == expected_behavior)

# grep test name to view diagram
@pytest.mark.dispatch
def test_trans_topology_a_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
 ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_a1_s1',
  'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  'INIT_SIGNAL:dispatch_graph_a1_s1',
  'EXIT_SIGNAL:dispatch_graph_a1_s1',
  'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  'INIT_SIGNAL:dispatch_graph_a1_s1']

  chart.start_at(dispatch_graph_a1_s1)
  event_a  = Event(signal=signals.A)
  chart.dispatch(e=event_a)
  assert(chart.spy == expected_behavior)

@pytest.mark.dispatch
def test_trans_topology_b1_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s1',
     'ENTRY_SIGNAL:dispatch_graph_b1_s1',
     'ENTRY_SIGNAL:dispatch_graph_b1_s2',
     'INIT_SIGNAL:dispatch_graph_b1_s2',
     'A:dispatch_graph_b1_s2',
     'EXIT_SIGNAL:dispatch_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s1',
     'ENTRY_SIGNAL:dispatch_graph_b1_s2',
     'INIT_SIGNAL:dispatch_graph_b1_s2']
  chart.start_at(dispatch_graph_b1_s2)
  event_a  = Event(signal=signals.A)
  chart.dispatch(e=event_a)
  assert(chart.spy == expected_behavior)

@pytest.mark.dispatch
def test_trans_topology_b1_2(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s1',
     'ENTRY_SIGNAL:dispatch_graph_b1_s1',
     'ENTRY_SIGNAL:dispatch_graph_b1_s2',
     'ENTRY_SIGNAL:dispatch_graph_b1_s3',
     'INIT_SIGNAL:dispatch_graph_b1_s3',
     'B:dispatch_graph_b1_s3',
     'EXIT_SIGNAL:dispatch_graph_b1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s2',
     'ENTRY_SIGNAL:dispatch_graph_b1_s3',
     'INIT_SIGNAL:dispatch_graph_b1_s3']
  chart.start_at(dispatch_graph_b1_s3)
  event_a  = Event(signal=signals.B)
  chart.dispatch(e=event_a)
  assert(chart.spy == expected_behavior)
