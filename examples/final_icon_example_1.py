# final_icon_example_1.py
import time

from miros import spy_on
from miros import Event
from miros import signals
from miros import ActiveObject
from miros import return_status

@spy_on
def outer_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.condition = False if chart.condition == None else chart.condition
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    if chart.condition:
      status = chart.trans(inner_state)
    else:
      chart.scribble("run code, but don't transition out of outer_state")
      status = return_status.HANDLED
  elif(e.signal == signals.Retry):
    chart.condition = False if chart.condition else True
    status = chart.trans(outer_state)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def inner_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  else:
    chart.temp.fun = outer_state
    status = return_status.SUPER
  return status

if __name__ == "__main__":
  ao = ActiveObject('final_icon')
  ao.augment( name='condition', other=None)
  ao.live_spy = True
  ao.start_at(outer_state)
  ao.post_fifo(Event(signal=signals.Retry))
  ao.post_fifo(Event(signal=signals.Retry))
  time.sleep(0.01)

