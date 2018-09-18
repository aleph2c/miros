# file named toaster_oven_2.py
from miros import ActiveObject
from miros import return_status
from miros import Event
from miros import signals
from miros import spy_on
import time

class ToasterOven(ActiveObject):
  def __init__(self, name):
    super().__init__(name)

  def light_on(self):
    print("light_on")

  def light_off(self):
    print("light_on")

  def heater_on(self):
    print("heater_on")

  def heater_off(self):
    print("heater_off")

@spy_on
def door_closed(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.light_off()
    status = return_status.HANDLED
  elif(e.signal == signals.Baking):
    status = oven.trans(baking)
  elif(e.signal == signals.Toasting):
    status = oven.trans(toasting)
  elif(e.signal == signals.INIT_SIGNAL):
    status = oven.trans(toasting)
  elif(e.signal == signals.Off):
    status = oven.trans(off)
  else:
    oven.temp.fun = oven.top
    status = return_status.SUPER
  return status

@spy_on
def heating(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.heater_on()
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    oven.heater_off()
    status = return_status.HANDLED
  else:
    oven.temp.fun = door_closed
    status = return_status.SUPER
  return status

@spy_on
def baking(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    print("baking")
    status = return_status.HANDLED
  else:
    oven.temp.fun = heating
    status = return_status.SUPER
  return status

@spy_on
def toasting(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    print("toasting")
    status = return_status.HANDLED
  else:
    oven.temp.fun = heating
    status = return_status.SUPER
  return status

@spy_on
def off(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    print("off")
    status = return_status.HANDLED
  else:
    oven.temp.fun = door_closed
    status = return_status.SUPER
  return status

if __name__ == "__main__":
  oven = ToasterOven(name="oven")
  oven.live_trace = True
  oven.start_at(off)
  # toast something
  oven.post_fifo(Event(signal=signals.Toasting))
  # bake something
  oven.post_fifo(Event(signal=signals.Baking))
  # turn the oven off
  oven.post_fifo(Event(signal=signals.Off))
  time.sleep(0.01)

