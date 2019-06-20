import time
import pytest
from miros import spy_on, pp
from miros import stripped
from miros import ActiveObject
from miros import signals, Event, return_status

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
    status = chart.trans(g1_s2111_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


@spy_on
def g1_s01_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.scribble("Demonstrating chart will react to F before A")
    chart.post_fifo(Event(signal=signals.A))
    chart.post_lifo(Event(signal=signals.F))
    chart.recall()
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    status = chart.trans(g1_s22_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s0_active_objects_graph
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
    status = chart.trans(g1_s321_active_objects_graph)
  elif(e.signal == signals.E):
    status = chart.trans(g1_s01_active_objects_graph)
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
    status = chart.trans(g1_s321_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s1_active_objects_graph
  return status


@spy_on
def g1_s211_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s21_active_objects_graph
  return status


@spy_on
def g1_s2111_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(g1_s321_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s211_active_objects_graph
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
    status = chart.trans(g1_s1_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s1_active_objects_graph
  return status


@spy_on
def g1_s3_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.scribble("defering event F to demonstrate how it will be recalled by another state")
    chart.defer(Event(signal=signals.F))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s22_active_objects_graph
  return status


@spy_on
def g1_s32_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s3_active_objects_graph
  return status


@spy_on
def g1_s321_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s32_active_objects_graph
  return status


@pytest.mark.spy
@pytest.mark.scribble
def test_graffiti_spy():
  ao = ActiveObject(name="scribbled_on")
  ao.start_at(g1_s22_active_objects_graph)
  time.sleep(0.2)
  pp(ao.spy())


'''
 +----------------------------- s -------------------------------+
 | +-------- s1 ---------+                 +-------- s2 -------+ |
 | | exit / b()          |                 | entry / c()       | |
 | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
 | |    | exit / a() |   |                 |  | entry / e()  | | |
 | |    |            |   |                 |  |              | | |
 | |    |            |   +- T [g()] / t() ->  |              | | |
 | |    +------------+   |                 |  +-----------/--+ | |
 | |                     |                 |   *-- / d() -+    | |
 | +---------------------+                 +-------------------+ |
 +---------------------------------------------------------------+

'''


@spy_on
def s_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


@spy_on
def s1_state(chart, e):
  def b(chart):
    chart.scribble("Running b()")

  def g(chart):
    chart.scribble("Running g() -- the guard, which return True")
    return True

  def t(chart):
    chart.scribble("Running t() -- funtion run on event")

  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    b(chart)
    status = return_status.HANDLED
  elif(e.signal == signals.T):
    if g(chart):
      t(chart)
      status = chart.trans(s2_state)
  else:
    status, chart.temp.fun = return_status.SUPER, s_state
  return status


@spy_on
def s11_state(chart, e):
  def a(chart):
    chart.scribble("Running a()")

  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    a(chart)
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, s1_state
  return status


@spy_on
def s2_state(chart, e):
  def c(chart):
    chart.scribble("running c()")

  def d(chart):
    chart.scribble("running d()")

  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    c(chart)
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    d(chart)
    status = chart.trans(s21_state)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, s_state
  return status


@spy_on
def s21_state(chart, e):
  def e_function(chart):
    chart.scribble("running e()")

  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    e_function(chart)
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, s2_state
  return status


@pytest.mark.spy
@pytest.mark.scribble
def test_scribble_to_learn_nature_of_event_processor():
  ao = ActiveObject(name="Testing")
  ao.start_at(s11_state)
  time.sleep(0.1)
  ao.post_fifo(Event(signal=signals.T))
  time.sleep(0.5)
  pp(ao.spy())
