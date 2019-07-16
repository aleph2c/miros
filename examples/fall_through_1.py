import time

from miros import Event
from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status

@spy_on
def a0(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.INIT_SIGNAL):
    status = chart.trans(a2)
  elif(e.signal == signals.Bubbling):
    print(
      "finally hooked by a0, but state remains as {}".
      format(chart.state_name))
    status = return_status.HANDLED
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def a1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.Bubbling):
    print("caught and released by a1")
  else:
    chart.temp.fun = a0
    status = return_status.SUPER
  return status

@spy_on
def a2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.Bubbling):
    print("caught and released by a2")
  else:
    chart.temp.fun = a1
    status = return_status.SUPER
  return status

if __name__ == "__main__":
  ao = ActiveObject('fall_through')
  ao.live_trace = True
  ao.start_at(a0)
  ao.post_fifo(Event(signal=signals.Bubbling))
  time.sleep(0.1)

