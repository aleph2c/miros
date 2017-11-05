import pytest
import traceback
from miros.event import signals, return_status
from miros.hsm   import HsmEventProcessor, HsmTopologyException
import pprint


def pp(item):
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
#                                Init graph 1                                  #
################################################################################
# The following state chart is used for the init test
# +------------------------------------- d1 -------------------------------------+
# |                                                                              |
# |   +--------------------------------- d2 ---------------------------------+   |
# |(3)|                                                                      |   |
# | * |    +---------------------------- d3 ----------------------------+    |   |
# | | |    |                                                            |    |   |
# | | |    |                                                            |    |   |
# | +->  * |    +------- d31 -------+     +---------- d32 ---------+    |    |   |
# |   |  | |    | (2)               |     |                        |    |    |   |
# |   |  +->    | *  +-- d311 -+    |     |                        |    |    |   |
# |   |    |  * | |  |         |    |     |  *(4)                  |    |    |   |
# |   |    |  | | +-->   (1)   |    |     |  |                     |    |    |   |
# |   |    |  +->    +---------+    <--------+ (impossible init)   |    |    |   |
# |   |    |    |                   |     |                        |    |    |   |
# |   |    |    +-------------------+     +------------------------+    |    |   |
# |   |    |                                                            |    |   |
# |   |    +------------------------------------------------------------+    |   |
# |   |                                                                      |   |
# |   +----------------------------------------------------------------------+   |
# |                                                                              |
# +------------------------------------------------------------------------------+
# 
def init_graph_1_d1(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(init_graph_1_d2)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    chart.temp.fun = chart.top
    status = return_status.SUPER

  return status


def init_graph_1_d2(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(init_graph_1_d3)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    chart.temp.fun = init_graph_1_d1
    status = return_status.SUPER

  return status


def init_graph_1_d3(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(init_graph_1_d31)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    chart.temp.fun = init_graph_1_d2
    status = return_status.SUPER

  return status


def init_graph_1_d31(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED

  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(init_graph_1_d311)

  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)

  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    chart.temp.fun = init_graph_1_d3
    status = return_status.SUPER

  return status


def init_graph_1_d32(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    # impossible transition
    status = chart.trans(init_graph_1_d31)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    chart.temp.fun = init_graph_1_d3
    status = return_status.SUPER

  return status


def init_graph_1_d311(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
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
    chart.temp.fun = init_graph_1_d31
    status = return_status.SUPER

  return status


################################################################################
#                                Init graph 2                                  #
################################################################################
#  The following state chart is used for the init test
# +------------------------------------- d1 -------------------------------------+
# |                                                                              |
# |   +--------------------------------- d2 ---------------------------------+   |
# |(5)|                                                                      |   |
# | * |    +---------------------------- d3 ----------------------------+    |   |
# | | |    |                                                            |    |   |
# | | |    |                                                            |    |   |
# | | |    |    +------- d31 -------+     +---------- d32 ---------+    |    |   |
# | | |    |    |                   |     |                        |    |    |   |
# | | |    |    | *  +-- d311 -+    |     |                        |    |    |   |
# | +-----------> |  |         |    |     |  *                     |    |    |   |
# |   |    |    | +-->   (1)   |    |     |  |                     |    |    |   |
# |   |    |    |    +---------+    <--------+ (impossible init)   |    |    |   |
# |   |    |    |                   |     |                        |    |    |   |
# |   |    |    +-------------------+     +------------------------+    |    |   |
# |   |    |                                                            |    |   |
# |   |    +------------------------------------------------------------+    |   |
# |   |                                                                      |   |
# |   +----------------------------------------------------------------------+   |
# |                                                                              |
# +------------------------------------------------------------------------------+
#
def init_graph_2_d1(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(init_graph_2_d31)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    chart.temp.fun = chart.top
    status = return_status.SUPER

  return status


def init_graph_2_d2(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
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
    chart.temp.fun = init_graph_2_d1
    status = return_status.SUPER

  return status


def init_graph_2_d3(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
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
    chart.temp.fun = init_graph_2_d2
    status = return_status.SUPER

  return status


def init_graph_2_d31(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED

  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = chart.trans(init_graph_2_d311)

  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)

  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    chart.temp.fun = init_graph_2_d3
    status = return_status.SUPER

  return status


def init_graph_2_d32(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    # impossible transition
    status = chart.trans(init_graph_2_d31)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart, e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart, e)))
    chart.temp.fun = init_graph_2_d3
    status = return_status.SUPER

  return status


def init_graph_2_d311(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
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
    chart.temp.fun = init_graph_2_d31
    status = return_status.SUPER

  return status


@pytest.mark.init
def test_start_at_test_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
  ['SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d311',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d3',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d2',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d1',
   'ENTRY_SIGNAL:init_graph_1_d1',
   'ENTRY_SIGNAL:init_graph_1_d2',
   'ENTRY_SIGNAL:init_graph_1_d3',
   'ENTRY_SIGNAL:init_graph_1_d31',
   'ENTRY_SIGNAL:init_graph_1_d311',
   'INIT_SIGNAL:init_graph_1_d311']
  chart.start_at(init_graph_1_d311)
  # pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)


@pytest.mark.init
def test_start_at_test_2(spy_chart):
  chart = spy_chart
  expected_behavior = \
  ['SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d3',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d2',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d1',
   'ENTRY_SIGNAL:init_graph_1_d1',
   'ENTRY_SIGNAL:init_graph_1_d2',
   'ENTRY_SIGNAL:init_graph_1_d3',
   'ENTRY_SIGNAL:init_graph_1_d31',
   'INIT_SIGNAL:init_graph_1_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d311',
   'ENTRY_SIGNAL:init_graph_1_d311',
   'INIT_SIGNAL:init_graph_1_d311']
  chart.start_at(init_graph_1_d31)
  # pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)


@pytest.mark.init
def test_start_at_test_3(spy_chart):
  chart = spy_chart
  expected_behavior = \
  ['SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d1',
   'ENTRY_SIGNAL:init_graph_1_d1',
   'INIT_SIGNAL:init_graph_1_d1',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d2',
   'ENTRY_SIGNAL:init_graph_1_d2',
   'INIT_SIGNAL:init_graph_1_d2',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d3',
   'ENTRY_SIGNAL:init_graph_1_d3',
   'INIT_SIGNAL:init_graph_1_d3',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d31',
   'ENTRY_SIGNAL:init_graph_1_d31',
   'INIT_SIGNAL:init_graph_1_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_1_d311',
   'ENTRY_SIGNAL:init_graph_1_d311',
   'INIT_SIGNAL:init_graph_1_d311']
  chart.start_at(init_graph_1_d1)
  assert(chart.spy_log == expected_behavior)


@pytest.mark.init
def test_impossible_transition_start_at_test_4(spy_chart):
  chart = spy_chart
  with pytest.raises(HsmTopologyException):
    chart.start_at(init_graph_1_d32)


@pytest.mark.init
def test_impossible_transition_start_at_test_5(spy_chart):
  chart = spy_chart
  expected_behavior = \
  ['SEARCH_FOR_SUPER_SIGNAL:init_graph_2_d1',
   'ENTRY_SIGNAL:init_graph_2_d1',
   'INIT_SIGNAL:init_graph_2_d1',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_2_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_2_d3',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_2_d2',
   'ENTRY_SIGNAL:init_graph_2_d2',
   'ENTRY_SIGNAL:init_graph_2_d3',
   'ENTRY_SIGNAL:init_graph_2_d31',
   'INIT_SIGNAL:init_graph_2_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_graph_2_d311',
   'ENTRY_SIGNAL:init_graph_2_d311',
   'INIT_SIGNAL:init_graph_2_d311']
  chart.start_at(init_graph_2_d1)
  assert(chart.spy_log == expected_behavior)

