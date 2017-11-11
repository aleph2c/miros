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

import time
from miros.hsm import spy_on, pp
from miros.activeobject import ActiveObject
from miros.event import signals, Event, return_status


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
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    d(chart)
    status = chart.trans(s21_state)
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


if __name__ == "__main__":
  ao = ActiveObject(name="T_question")
  ao.start_at(s11_state)

  ao.clear_spy()
  ao.post_fifo(Event(signal=signals.T))
  time.sleep(0.2)
  pp(ao.spy())
