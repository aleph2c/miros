# internal_signals_1.py
import time

from miros import spy_on
from miros import Event
from miros import signals
from miros import ActiveObject
from miros import return_status

@spy_on
def a(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    print("'a' entered")
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    print("'a' exited")
    status = return_status.HANDLED
  # need to add an external signal so we can cause exits
  # for our demo
  elif(e.signal == signals.Reset):
    status = chart.trans(a)
  elif(e.signal == signals.INIT_SIGNAL):
    print_string  = "code to run after 'a' entered "
    print_string += "and we have settled into 'a', "
    print_string += "the INIT_SIGNAL wants us to "
    print_string += "transition into 'a1'"
    print(print_string)
    status = chart.trans(a1)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def a1(chart, e):
  if(e.signal == signals.ENTRY_SIGNAL):
    print("'a1' entered")
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    print("'a1' exited")
    status = return_status.HANDLED
  else:
    chart.temp.fun = a
    status = return_status.SUPER
  return status

if __name__ == "__main__":
  # simple hook example 2
  ao = ActiveObject(name="she2")
  ao.live_trace = True
  ao.start_at(a1)
  ao.post_fifo(Event(signal=signals.SIGNAL_NAME))
  ao.post_fifo(Event(signal=signals.Reset))
  # starting another thread, let it run for a moment before we shut down
  time.sleep(0.01)  
