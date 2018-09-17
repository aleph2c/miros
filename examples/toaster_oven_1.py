# file named toaster_oven_1.py
from miros import ActiveObject
from miros import return_status
from miros import Event
from miros import signals
from miros import spy_on
import time

class ToasterOven(ActiveObject):
  def __init__(self, name):
    super().__init__(name)

@spy_on
def some_state_to_prove_this_works(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    print("hello world")
    status = return_status.HANDLED
  else:
    oven.temp.fun = oven.top
    status = return_status.SUPER
  return status

if __name__ == "__main__":
  oven = ToasterOven(name="oven")
  oven.live_trace = True
  oven.start_at(some_state_to_prove_this_works)

  time.sleep(0.1)
