
import time

from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status

@spy_on
def outer_state(chart, e):
  status = return_status.UNHANDLED
  # the event process automatically sends
  # an event named ENTRY_SIGNAL when a state is entered
  if(e.signal == signals.ENTRY_SIGNAL):
    print("hello from outer_state")
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    print("init")
    status = chart.trans(inner_state)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def inner_state(chart, e):
  status = return_status.UNHANDLED
  # the event process automatically sends
  # an event named ENTRY_SIGNAL when a state is entered
  if(e.signal == signals.ENTRY_SIGNAL):
    print("hello from inner_state")
    status = return_status.HANDLED
  else:
    chart.temp.fun = outer_state
    status = return_status.SUPER
  return status

if __name__ == '__main__':
  ao = ActiveObject('ao')
  ao.live_trace = True
  ao.start_at(outer_state)
  time.sleep(0.01)
