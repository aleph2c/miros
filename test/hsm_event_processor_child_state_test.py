
import pprint
import pytest
import traceback
from miros.event import signals, Event, return_status
from miros.hsm   import HsmEventProcessor


def pp(item):
  print("")
  pprint.pprint(item)


def reflect(hsm=None, e=None):
  '''
  This will return the callers function name as a string:
  Example:

    def example_function():
      return reflect()

    print(example_function) #=> "example_function"

  '''
  fnt  = traceback.extract_stack(None, 2)
  fnt1 = fnt[0]
  fnt2 = fnt1[2]
  return fnt2


################################################################################
#                            Child State Graph E1                              #
################################################################################
#
#                      +---------- graph_e1_s1 -----------+
#                      | +-------- graph_e1_s2 -------+   |
#                      | | +------ graph_e1_s3 -----+ |   |
#                      | | | +---- graph_e1_s4 ---+ | |   |
#                      | | | |  +- graph_e1_s5 -+ | | |   |
#                      | | | |  |               | | | |   |
#                      | +-b->  |               <-----a---+
#                      | | | |  |               | | | |   |
#                      | | +c>  +---------------+ | | |   |
#                      +d> | +--------------------+ | |   |
#                      | | +------------------------+ |   |
#                      | +----------------------------+   |
#                      +----------------------------------+
#
#   * test1_child_state_1 - start in graph_e1_s5 (diagram)
#   * test1_child_state_2 - start in graph_e1_s4 (diagram)
#   * test1_child_state_3 - start at graph_e1_s1 (diagram)
#
#
def child_state_graph_e1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  elif(e.signal == signals.A):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(child_state_graph_e1_s5)
  elif(e.signal == signals.D):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(child_state_graph_e1_s2)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


def child_state_graph_e1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  elif(e.signal == signals.B):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(child_state_graph_e1_s4)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status, chart.temp.fun = return_status.SUPER, child_state_graph_e1_s1
  return status


def child_state_graph_e1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  elif(e.signal == signals.C):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(child_state_graph_e1_s4)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status, chart.temp.fun = return_status.SUPER, child_state_graph_e1_s2
  return status


def child_state_graph_e1_s4(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status, chart.temp.fun = return_status.SUPER, child_state_graph_e1_s3
  return status


def child_state_graph_e1_s5(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status, chart.temp.fun = return_status.SUPER, child_state_graph_e1_s4
  return status


@pytest.fixture
def spy_chart(request):
  chart = HsmEventProcessor()
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
@pytest.mark.child_state
def test1_child_state_1(spy_chart):
  chart = spy_chart
  chart.start_at(child_state_graph_e1_s5)
  assert(chart.child_state(child_state_graph_e1_s5) == child_state_graph_e1_s5)
  assert(chart.child_state(child_state_graph_e1_s4) == child_state_graph_e1_s5)
  assert(chart.child_state(child_state_graph_e1_s3) == child_state_graph_e1_s4)
  chart.dispatch(Event(signals.D))
  assert(chart.child_state(child_state_graph_e1_s2) == child_state_graph_e1_s2)
  assert(chart.child_state(child_state_graph_e1_s1) == child_state_graph_e1_s2)

