# simple_state_8.py
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
    print("{}: hello from outer_state".format(chart.name))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    print("{}: init".format(chart.name))
    status = chart.trans(inner_state)
  elif(e.signal == signals.Hook):
    print("{}: run some code, but don't transition".format(chart.name))
    status = return_status.HANDLED
  elif(e.signal == signals.Reset):
    print("{}: resetting the chart".format(chart.name))
    status = chart.trans(outer_state)
  elif(e.signal == signals.EXIT_SIGNAL):
    print("{}: exiting outer_state".format(chart.name))
    status = return_status.HANDLED
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def inner_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    print("{}: hello from inner_state".format(chart.name))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    print("{}: exiting inner_state".format(chart.name))
    status = return_status.HANDLED
  else:
    chart.temp.fun = outer_state
    status = return_status.SUPER
  return status

if __name__ == '__main__':
  ao1 = ActiveObject("ao1")
  ao1.live_trace = True
  ao1.start_at(outer_state)
  ao1.post_fifo(Event(signal=signals.Hook))
  ao1.post_fifo(Event(signal=signals.Reset))

  ao2 = ActiveObject("ao2")
  ao2.live_trace = True
  ao2.start_at(inner_state)
  ao2.post_fifo(Event(signal=signals.Hook))
  ao2.post_fifo(Event(signal=signals.Reset))
  # let the thread catch up before we exit main
  time.sleep(0.01)

