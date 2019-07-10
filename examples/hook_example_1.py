import time
from collections import namedtuple

from miros import spy_on
from miros import Event
from miros import signals
from miros import ActiveObject
from miros import return_status

OptionalPayload = namedtuple('OptionalPayload', ['x'])

def guard():
  return True

def action():
  print('hook code was run {}')

@spy_on
def a(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.SIGNAL_NAME):
    if guard():
      action()
    status = return_status.HANDLED
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def a1(chart, e):
  chart.temp.fun = a
  status = return_status.SUPER
  return status

if __name__ == "__main__":
  # simple hook example
  ao = ActiveObject(name="she")
  ao.live_trace = True
  ao.start_at(a1)
  ao.post_fifo(Event(signal=signals.SIGNAL_NAME, payload=OptionalPayload(x=2)))
  # starting another thread, let it run for a moment before we shut down
  time.sleep(0.01)  
  print(ao.state_name)
