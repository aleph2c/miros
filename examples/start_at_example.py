import time
from miros import spy_on
from miros import ActiveObject
from miros import signals, Event, return_status

@spy_on
def c(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
    print("c1 entered")
  elif(e.signal == signals.INIT_SIGNAL):
    status = chart.trans(c1)
  elif(e.signal == signals.B):
    status = chart.trans(c)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def c1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.A):
    status = chart.trans(c2)
  else:
    chart.temp.fun = c
    status = return_status.SUPER
  return status

@spy_on
def c2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    print("c2 entered")
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(c1)
  else:
    chart.temp.fun = c
    status = return_status.SUPER
  return status

if __name__ == "__main__":
  ao = ActiveObject('start_example')
  print("calling: start_at(c2)")
  ao.start_at(c2)

  time.sleep(0.2)
  print(ao.trace()) # print what happened from the start_at call
  ao.clear_trace()  # clear our instrumentation

  print("sending B, then A, then A:")
  ao.post_fifo(Event(signal=signals.B))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.2)
  print(ao.trace()) # print what happened
