# file named toaster_oven_2.py

import pprint
def pp(item):
  pprint.pprint(item)

from miros import ActiveObject
from miros import return_status
from miros import Event
from miros import signals
from miros import spy_on
import time

class ToasterOven(ActiveObject):
  def __init__(self, name):
    super().__init__(name)
    self.history = None

  def light_on(self):
    self.scribble("light_on")

  def light_off(self):
    self.scribble("light_off")

  def heater_on(self):
    self.scribble("heater_on")

  def heater_off(self):
    self.scribble("heater_off")

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
    status = oven.trans(off)
  elif(e.signal == signals.Off):
    status = oven.trans(off)
  elif(e.signal == signals.Door_Open):
    status = oven.trans(door_open)
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
    oven.scribble("baking")
    oven.history = baking
    status = return_status.HANDLED
  else:
    oven.temp.fun = heating
    status = return_status.SUPER
  return status

@spy_on
def toasting(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.scribble("toasting")
    oven.history = toasting
    status = return_status.HANDLED
  else:
    oven.temp.fun = heating
    status = return_status.SUPER
  return status

@spy_on
def off(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.scribble("off")
    oven.history = off
    status = return_status.HANDLED
  else:
    oven.temp.fun = door_closed
    status = return_status.SUPER
  return status

@spy_on
def door_open(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.light_on()
  elif(e.signal == signals.Door_Close):
    status = oven.trans(oven.history)
  else:
    oven.temp.fun = oven.top
    status = return_status.SUPER
  return status


if __name__ == '__main__':
  oven = ToasterOven(name="oven")
  oven.live_trace = True

  # start the oven
  oven.start_at(door_closed)

  # open the door
  oven.post_fifo(Event(signal=signals.Door_Open))

  # close the door
  oven.post_fifo(Event(signal=signals.Door_Close))

  # Bake something
  oven.post_fifo(Event(signal=signals.Baking))

  # open the door
  oven.post_fifo(Event(signal=signals.Door_Open))

  # Toast something
  oven.post_fifo(Event(signal=signals.Toasting))

  # open the door
  oven.post_fifo(Event(signal=signals.Door_Open))

  time.sleep(10.01)
