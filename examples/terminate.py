import time
from miros import spy_on
from miros import ActiveObject
from miros import signals, Event, return_status

@spy_on
def some_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.Destroy_This_Chart):
    chart.stop()
    status = return_status.HANDLED
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

if __name__ == "__main__":
  ao = ActiveObject('some_state')
  ao.live_trace = True
  ao.start_at(some_state)
  time.sleep(2)
  ao.post_fifo(Event(signal=signals.Destroy_This_Chart))
  time.sleep(200)

