# simple_state_2.py
import time

from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status

@spy_on  # enables the live trace
def outer_state(chart, e):
  status = return_status.UNHANDLED
  # the event processor is asking us about events called INIT_SIGNAL
  if(e.signal == signals.INIT_SIGNAL):
    # we are transitioning to inner_state
    # we let the trans method, set temp.fun and our return status
    status = chart.trans(inner_state)
  # we do this for any other event
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on  # enables the live trace
def inner_state(chart, e):
  # we do this for all events
  chart.temp.fun = outer_state
  status = return_status.SUPER
  return status

if __name__ == '__main__':
  ao = ActiveObject('ao')
  ao.live_trace = True  # so we can see what is happening
  # Create a thread and start our state machine
  ao.start_at(outer_state)
  # Run our main program so that the state machine's thread
  # can do some stuff.
  # The state machine's thread will be stopped when our main thread stops
  time.sleep(0.01)

