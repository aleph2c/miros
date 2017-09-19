import pytest
from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import reflect, Hsm
import pprint
def pp(item):
  pprint.pprint(item)
################################################################################
#                                 Init test 1                                  #
################################################################################
'''           The following state chart is used for the init test
+------------------------------------- d1 -------------------------------------+
|                                                                              |
|   +--------------------------------- d2 ---------------------------------+   |
|   |                                                                      |   |
| * |    +---------------------------- d3 ----------------------------+    |   |
| | |    |                                                            |    |   |
| | |    |                                                            |    |   |
| +->  * |    +------- d31 -------+     +---------- d32 ---------+    |    |   |
|   |  | |    |                   |     |                        |    |    |   |
|   |  +->    | *  +-- d311 -+    |     |                        |    |    |   |
|   |    |  * | |  |         |    |     |  *                     |    |    |   |
|   |    |  | | +-->         |    |     |  |                     |    |    |   |
|   |    |  +->    +---------+    <--------+ (impossible init)   |    |    |   |
|   |    |    |                   |     |                        |    |    |   |
|   |    |    +-------------------+     +------------------------+    |    |   |
|   |    |                                                            |    |   |
|   |    +------------------------------------------------------------+    |   |
|   |                                                                      |   |
|   +----------------------------------------------------------------------+   |
|                                                                              |
+------------------------------------------------------------------------------+
'''

def init_test_1_d1(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(init_test_1_d2)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    chart.temp.fun = chart.top
    status = return_status.SUPER

  return status

def init_test_1_d2(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(init_test_1_d3)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    chart.temp.fun = init_test_1_d1
    status = return_status.SUPER

  return status

def init_test_1_d3(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(init_test_1_d31)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    chart.temp.fun = init_test_1_d2
    status = return_status.SUPER

  return status

def init_test_1_d31(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED

  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(init_test_1_d311)

  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)

  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    chart.temp.fun = init_test_1_d3
    status = return_status.SUPER

  return status

def init_test_1_d32(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(init_test_1_d31)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    chart.temp.fun = init_test_1_d3
    status = return_status.SUPER

  return status

def init_test_1_d311(chart, e):
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
    chart.temp.fun = init_test_1_d31
    status = return_status.SUPER

  return status

@pytest.fixture
def spy_chart(request):
  chart = Hsm()
  spy   = []
  chart.augment(other=spy, name="spy")
  yield chart
  del spy
  del chart

@pytest.mark.init
def test_init_test_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
  ['SEARCH_FOR_SUPER_SIGNAL:init_test_1_d311',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d3',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d2',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d1',
   'ENTRY_SIGNAL:init_test_1_d1',
   'ENTRY_SIGNAL:init_test_1_d2',
   'ENTRY_SIGNAL:init_test_1_d3',
   'ENTRY_SIGNAL:init_test_1_d31',
   'ENTRY_SIGNAL:init_test_1_d311',
   'INIT_SIGNAL:init_test_1_d311']
  chart.start_at(init_test_1_d311)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.init
def test_init_test_2(spy_chart):
  chart = spy_chart
  expected_behavior = \
  ['SEARCH_FOR_SUPER_SIGNAL:init_test_1_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d3',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d2',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d1',
   'ENTRY_SIGNAL:init_test_1_d1',
   'ENTRY_SIGNAL:init_test_1_d2',
   'ENTRY_SIGNAL:init_test_1_d3',
   'ENTRY_SIGNAL:init_test_1_d31',
   'INIT_SIGNAL:init_test_1_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d311',
   'ENTRY_SIGNAL:init_test_1_d311',
   'INIT_SIGNAL:init_test_1_d311']
  chart.start_at(init_test_1_d31)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.init
@pytest.mark.now
def test_init_test_2(spy_chart):
  chart = spy_chart
  expected_behavior = \
  ['SEARCH_FOR_SUPER_SIGNAL:init_test_1_d1',
   'ENTRY_SIGNAL:init_test_1_d1',
   'INIT_SIGNAL:init_test_1_d1',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d2',
   'ENTRY_SIGNAL:init_test_1_d2',
   'INIT_SIGNAL:init_test_1_d2',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d3',
   'ENTRY_SIGNAL:init_test_1_d3',
   'INIT_SIGNAL:init_test_1_d3',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d31',
   'ENTRY_SIGNAL:init_test_1_d31',
   'INIT_SIGNAL:init_test_1_d31',
   'SEARCH_FOR_SUPER_SIGNAL:init_test_1_d311',
   'ENTRY_SIGNAL:init_test_1_d311',
   'INIT_SIGNAL:init_test_1_d311']
  print("")
  chart.start_at(init_test_1_d1)
  assert(chart.spy == expected_behavior)
