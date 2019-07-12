import time

from miros import Event
from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status

@spy_on
def off(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.bake_pressed):
    status = chart.trans(heating)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def heating(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.off_pressed):
    status = chart.trans(off)
  elif(e.signal == signals.too_hot):
    status = chart.trans(idling)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def idling(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.too_cold):
    status = chart.trans(heating)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

if __name__ == "__main__":
  ao = ActiveObject('simple_fsm_2')
  ao.live_trace = True
  ao.start_at(off)
  ao.post_fifo(Event(signal=signals.bake_pressed))
  ao.post_fifo(Event(signal=signals.off_pressed))
  ao.post_fifo(Event(signal=signals.bake_pressed))
  ao.post_fifo(Event(signal=signals.too_hot))
  ao.post_fifo(Event(signal=signals.too_cold))
  time.sleep(0.01)
