import time
from collections import namedtuple

from miros import spy_on
from miros import Event
from miros import signals
from miros import ActiveObject
from miros import return_status

OptionalPayload = namedtuple('OptionalPayload', ['x'])

@spy_on
def a(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.SIGNAL_NAME):
    print("this code should never run")
    status = return_status.HANDLED
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def a1(chart, e):
  if(e.signal == signals.SIGNAL_NAME):
    status = return_status.HANDLED
  else:
    chart.temp.fun = a
    status = return_status.SUPER
  return status

@spy_on
def a11(chart, e):
  chart.temp.fun = a1
  status = return_status.SUPER
  return status

if __name__ == "__main__":
  # simple hook example 2
  ao = ActiveObject(name="she2")
  ao.live_trace = True
  ao.start_at(a11)
  ao.post_fifo(Event(signal=signals.SIGNAL_NAME))
  # starting another thread, let it run for a moment before we shut down
  time.sleep(0.01)  
  print(ao.state_name)
