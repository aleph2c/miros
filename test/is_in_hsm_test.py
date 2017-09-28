import pytest
from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import reflect, Hsm, HsmTopologyException
import pprint
def pp(item):
  print("")
  pprint.pprint(item)
################################################################################
#                                Is_in Graph E1                                #
################################################################################
'''
                     +---------- graph_e1_s1 -----------+
                     | +-------- graph_e1_s2 -------+   |
                     | | +------ graph_e1_s3 -----+ |   |
                     | | | +---- graph_e1_s4 ---+ | |   |
                     | | | |  +- graph_e1_s5 -+ | | |   |
                     | | | |  |               | | | |   |
                     | +-b->  |               <-----a---+
                     | | | |  |               | | | |   |
                     | | +c>  +---------------+ | | |   |
                     +d> | +--------------------+ | |   |
                     | | +------------------------+ |   |
                     | +----------------------------+   |
                     +----------------------------------+

  * test1_is_in_1 - start in graph_e1_s5 (diagram)
  * test1_is_in_2 - start in graph_e1_s4 (diagram)
  * test1_is_in_3 - start at graph_e1_s1 (diagram)

'''
def is_in_graph_e1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(is_in_graph_e1_s5)
  elif(e.signal == signals.D):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(is_in_graph_e1_s2)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def is_in_graph_e1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.B):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(is_in_graph_e1_s4)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, is_in_graph_e1_s1
  return status

def is_in_graph_e1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.C):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(is_in_graph_e1_s4)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, is_in_graph_e1_s2
  return status

def is_in_graph_e1_s4(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, is_in_graph_e1_s3
  return status

def is_in_graph_e1_s5(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, is_in_graph_e1_s4
  return status

@pytest.fixture
def spy_chart(request):
  chart = Hsm()
  spy   = []
  chart.augment(other=spy, name="spy_log")
  signals.append("A")
  signals.append("B")
  signals.append("C")
  signals.append("D")
  signals.append("E")
  signals.append("F")
  yield chart
  del spy
  del chart

# grep test name to view diagram
@pytest.mark.is_in
def test1_is_in_1(spy_chart):
  chart = spy_chart
  chart.start_at(is_in_graph_e1_s5)
  assert(chart.is_in(is_in_graph_e1_s5) == True)
  assert(chart.is_in(is_in_graph_e1_s4) == True)
  assert(chart.is_in(is_in_graph_e1_s3) == True)
  assert(chart.is_in(is_in_graph_e1_s2) == True)
  assert(chart.is_in(is_in_graph_e1_s1) == True)

@pytest.mark.is_in
def test1_is_in_2(spy_chart):
  chart = spy_chart
  chart.start_at(is_in_graph_e1_s4)
  assert(chart.is_in(is_in_graph_e1_s5) == False)
  assert(chart.is_in(is_in_graph_e1_s4) == True)
  assert(chart.is_in(is_in_graph_e1_s3) == True)
  assert(chart.is_in(is_in_graph_e1_s2) == True)
  assert(chart.is_in(is_in_graph_e1_s1) == True)

@pytest.mark.is_in
def test1_is_in_2(spy_chart):
  chart = spy_chart
  expected_behavior = []
  chart.start_at(is_in_graph_e1_s1)
  assert(chart.is_in(is_in_graph_e1_s5) == False)
  assert(chart.is_in(is_in_graph_e1_s4) == False)
  assert(chart.is_in(is_in_graph_e1_s3) == False)
  assert(chart.is_in(is_in_graph_e1_s2) == False)
  assert(chart.is_in(is_in_graph_e1_s1) == True)
