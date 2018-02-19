import pytest
from miros.event import signals, Event, return_status
from miros.hsm   import InstrumentedHsmEventProcessor, spy_on
import pprint
from miros.hsm import stripped

def pp(item):
  print("")
  pprint.pprint(item)


################################################################################
#                               Trace Graph A1                                 #
################################################################################
# The following state chart is used to test the spy on topology A
#
#                             +- graph_a1_s1 -+
#                             |               +-----+
#                             |               |     a
#                             |               <-----+
#                             +---------------+
#
# This is used for testing the type A topology in the trans_ method of the HsmEventProcessor
# class.
#   * test__trace_topology_a_1 (diagram)
#   * test__trace_topology_a_2 (diagram)

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
  assert(start_trace.signal is None)
  assert(start_trace.end_state == 'trace_graph_a1_s1')
  trans_trace = chart.full.trace[1]
  trans_trace.start_state == 'trace_graph_a1_s1'
  trans_trace.end_state == 'trace_graph_a1_s1'
  trans_trace.signal == 'A'


################################################################################
#                               Trace Graph G1                                 #
################################################################################
# The following state chart is used to test topology G
#
#                   +-------------------------------- g1_s1 --------------+
#    +---g1_s0---+  | e/ print("ultimate hook")                           |
#    |+-g1_s01--+|  |                      +---------g1_s22 ----------+   |
#    ||         ++-----c------------------->                          |   |
#    ||         ||  |                      | +-------g1_s3 ---------+ |   |
#    |+---------+|  | +-------g1_s21----+  | |    +----g1_s32-----+ | |   |
#    +-----------+  | | +--g1_s211-----+|  | |    |  +-g1_s321--+ | | |   |
#                   | | |+-g1_s2111+   ||  | |    |  |          | | | |   |
#                   | | ||         |   ||  | |    |  |          | | | |   |
#                   | | ||         |   |+-------b---->          | | | |   |
#                   | | ||         |   ||  | |    |  |          | | | |   |
#                   | | ||         |   ||  | |    |  |          | | | |   |
#                   | | ||         |   ||  | |  +---->          | | | |   |
#                   | | ||         |   ||  | |  | |  |          | | | |   |
#                   | | |++--------+   ||  | |  | |  |          | | | +-d->
#                   | | +-|------------+|  | |  | |  +----------+ | | |   |
#                   | +---|-------------+  | |  | +---------------+ | |   |
#                   |     |                | +--|-------------------+ |   |
#                   |     +------------a--------+                     |   |
#                   |                      +--------------------------+   |
#                   |                                                     |
#                   +-----------------------------------------------------+
#
#
# This is used for testing the type E topology in the trans_ method of the HsmEventProcessor
# class.
#   * test_trace_topology_g1_1 - start in graph_g1_s211 (diagram -> a)
#   * test_trace_topology_g1_2 - start in graph_g1_s211 (diagram -> b)
#   * test_trace_topology_g1_3 - start in graph_g1_s01  (diagram -> a)
#   * test_trace_topology_g1_4 - start in graph_g1_s321 (diagram -> d)
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
    # print("handled")
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
  # pp(chart.full.spy)
  # pp(chart.full.trace)
  assert(len(chart.full.trace) == 2)
  start_trace = chart.full.trace[0]
  assert(start_trace.start_state == 'top')
  assert(start_trace.signal is None)
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
  # pp(chart.full.spy)
  # pp(chart.full.trace)
  # assert(chart.full.spy == expected_behavior)
  # assert(len(chart.full.trace) == 1)


@pytest.mark.trace
def test_trace_on_start():
  from miros.activeobject import Factory
  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def bb_handler(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.BB):
      chart.scribble(e.payload)
      status = chart.trans(fc)
    return status

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  # The following state chart is used to test topology C
  # in a multichart situation, statechart built using the factory
  #
  #        +------------------ fc ---------------+
  #        |   +----- fc1----+   +-----fc2-----+ |
  #        | * |             |   |             | +----+
  #        | | |             +-a->             | |    |
  #        | +->             <-a-+             | |    BB
  #        |   |             |   |             | |    |
  #        |   |             |   |             | <----+
  #        |   +-------------+   +-------------+ |
  #        +-------------------------------------+
  #

  c_chart = Factory('c_chart')
  fc = c_chart.create(state='fc'). \
        catch(signal=signals.INIT_SIGNAL, handler=trans_to_fc1). \
        catch(signal=signals.BB, handler=bb_handler). \
        to_method()

  fc1 = c_chart.create(state='fc1'). \
        catch(signal=signals.a, handler=trans_to_fc2). \
        to_method()

  fc2 = c_chart.create(state='fc2'). \
        catch(signal=signals.a, handler=trans_to_fc1). \
        to_method()

  c_chart.nest(fc,  parent=None). \
          nest(fc1, parent=fc). \
          nest(fc2, parent=fc)

  c_chart.start_at(fc)
  target = "[2017-12-07 12:08:41.154109] [c_chart] e->start_at() top->fc1"
  with stripped(target) as stripped_target, stripped(c_chart.trace()) as stripped_trace_result:
    assert(stripped_target == stripped_trace_result[0])

