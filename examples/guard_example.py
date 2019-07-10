# guard_example.py
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
  print('some action')

@spy_on
def source_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.SIGNAL_NAME):
    if guard():
      action()
      chart.post_fifo(Event(signal=signals.EVT_A))
      status = chart.trans(target_state)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status
 
@spy_on
def target_state(chart, e):
  chart.temp.fun = chart.top
  status = return_status.SUPER
  return status

if __name__ == "__main__":
  # event arrow example
  ao = ActiveObject('eae')
  ao.live_trace = True
  ao.start_at(source_state)
  ao.post_fifo(Event(signal=signals.SIGNAL_NAME,
    payload=OptionalPayload(x='1')))
  time.sleep(0.01)

