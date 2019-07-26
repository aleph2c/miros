# simple_state_7.py
import time
from collections import namedtuple

from miros import Event
from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status

@spy_on
def outer_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.scribble("hello from outer_state")
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.scribble("init")
    status = chart.trans(inner_state)
  elif(e.signal == signals.Hook):
    chart.scribble("run some code, but don't transition")
    status = return_status.HANDLED
  elif(e.signal == signals.Reset):
    chart.scribble("resetting the chart")
    status = chart.trans(outer_state)
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.scribble("exiting outer_state")
    status = return_status.HANDLED
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def inner_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.scribble("hello from inner_state")
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.scribble("exiting inner_state")
    status = return_status.HANDLED
  else:
    chart.temp.fun = outer_state
    status = return_status.SUPER
  return status

if __name__ == '__main__':
  ao = ActiveObject("ao")
  ao.live_spy = True
  ao.live_trace = True
  ao.start_at(outer_state)
  ao.post_fifo(Event(signal=signals.Hook))
  ao.post_fifo(Event(signal=signals.Reset))
  # let the thread catch up before we exit main
  time.sleep(0.01)

