import time
from miros import spy_on
from miros import ActiveObject
from miros import signals, Event, return_status

class RelayDriverStub():
  def __init__(self):
    self._open = True

  def is_open(self):
    return self._open

  def is_closed(self):
    if self._open:
      result = False
    else:
      result = True
    return result

  def initiate_close(self):
    # hardware driver would do this
    pass

  def initiate_open(self):
    # hardware driver would do this
    pass

class AbbBreaker(ActiveObject):
  def __init__(self, name='abb_breaker', relay_driver=None):
    super().__init__(name)
    self._local = False
    self._open  = True
    self.history = None
    self.relay_driver = relay_driver

  def is_local(self):
    return self._local

  def is_open(self):
    return self._open

  def close(self):
    self._open = False

  def open(self):
    self._open = True

  def local(self):
    self._local = True
    self.post_fifo(Event(signal=signals.Local))

  def remote(self):
    self._local = False
    self.post_fifo(Event(signal=signals.Remote))

  def close_failed(self):
    self.post_fifo(Event(signal=signals.Failed_Closing))

  def open_failed(self):
    self.post_fifo(Event(signal=signals.Failed_Opening))

@spy_on
def circuit_breaker_outer_state(self, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.INIT_SIGNAL):
    if self.is_local():
      status = self.trans(mode_error)
    else:
      if self.is_open():
        status = self.trans(breaker_open)
      else:
        status = self.trans(breaker_closed)
  elif(e.signal == signals.Clock_Tick):
    # check hardware, issue events to this chart if needed
    status = return_status.HANDLED
  elif(e.signal == signals.Close_Command or
       e.signal == signals.Breaker_Closed):
    status = self.trans(breaker_closed)
  elif(e.signal == signals.Open_Command or
       e.signal == signals.Breaker_Opened or
       e.signal == signals.Breaker_Tripped):
    status = self.trans(breaker_open)
  elif(e.signal == signals.Local):
    self._local = True
    status = self.trans(mode_error)
  elif(e.signal == signals.Reset_Equipment_Error):
    status = self.trans(self.history)
  else:
    self.temp.fun = self.top
    status = return_status.SUPER
  return status

@spy_on
def breaker_open(self, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    self.history = breaker_open
    self.relay_driver.initiate_open()
    self.post_fifo(
      Event(signal=signals.Test_Relay_Hardware),
      period=1.0,
      deferred=True)
    status = return_status.HANDLED
  elif(e.signal == signals.Test_Relay_Hardware):
    if self.relay_driver.is_closed():
      self.open_failed()
    status = return_status.HANDLED
  elif(e.signal == signals.Failed_Opening):
    status = self.trans(breaker_error)
  elif(e.signal == signals.Closed):
    status = self.trans(breaker_closed)
  elif(e.signal == signals.Failed_Opening):
    status = self.trans(equipment_error)
  elif(e.signal == signals.EXIT_SIGNAL):
    self.cancel_events(Event(signals.Test_Relay_Hardware))
    status = return_status.HANDLED
  else:
    self.temp.fun = circuit_breaker_outer_state
    status = return_status.SUPER
  return status

@spy_on
def breaker_closed(self, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    self.history = breaker_closed
    self.relay_driver.initiate_close()
    self.post_fifo(
      Event(signal=signals.Test_Relay_Hardware),
      period=1.0,
      deferred=True)
    status = return_status.HANDLED
  elif(e.signal == signals.Test_Relay_Hardware):
    if self.relay_driver.is_open():
      self.close_failed()
    status = return_status.HANDLED
  elif(e.signal == signals.Tripped or
       e.signal == signals.Opened):
    status = self.trans(breaker_open)
  elif(e.signal == signals.Failed_Closing):
    status = self.trans(equipment_error)
  elif(e.signal == signals.EXIT_SIGNAL):
    self.cancel_events(Event(signals.Test_Relay_Hardware))
    status = return_status.HANDLED
  else:
    self.temp.fun = circuit_breaker_outer_state
    status = return_status.SUPER
  return status

@spy_on
def breaker_error(self, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    print("Turn on Equipment Error Light")
    status = return_status.HANDLED
  if(e.signal == signals.Remote):
    self._local = False
    status = self.trans(circuit_breaker_outer_state)
  elif(e.signal == signals.Breaker_Closed or
       e.signal == signals.Close_Command or
       e.signal == signals.Open_Command or
       e.signal == signals.Breaker_Tripped or
       e.signal == signals.Breaker_Opened):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    print("Turn off Equipment Error Light")
    status = return_status.HANDLED
  else:
    self.temp.fun = circuit_breaker_outer_state
    status = return_status.SUPER
  return status

@spy_on
def equipment_error(self, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.Remote):
    self._local = False
    status = return_status.HANDLED
  if(e.signal == signals.Local):
    self._local = True
    status = return_status.HANDLED
  else:
    self.temp.fun = breaker_error
    status = return_status.SUPER
  return status


@spy_on
def mode_error(self, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.Reset_Equipment_Error):
    status = return_status.HANDLED
  else:
    self.temp.fun = breaker_error
    status = return_status.SUPER
  return status

# Jeff:

# When you do this in Python, you are saying, "if I am running this file
# directory from the command line, run the following code, if I am including
# this file from another file DO NOT run this code.  This is how a lot of fast
# code tests of a files are done... you put this at the bottom of your file to test
# your code as you work on it.

if __name__ == "__main__":
  # Create a fake relay driver
  relay_driver = RelayDriverStub()

  # Create a hardware issue
  relay_driver._open = False

  # Create the breaker statechart and turn on some of it's instrumentation
  # This is an example of an aggregate, "has a" relationship in UML, see class
  # part of the diagram
  breaker = AbbBreaker(name='abb_breaker', relay_driver=relay_driver)
  breaker.live_trace = True
  breaker.start_at(circuit_breaker_outer_state)
  time.sleep(2)

  # Clear our hardware issue and "press" the Reset_Equipment_Error button
  # this tests the reset to deep history feature
  relay_driver._open = True
  breaker.post_fifo(Event(signals.Reset_Equipment_Error))
  time.sleep(2)

  # Set the breaker to Local and see what happens
  breaker.post_fifo(Event(signals.Local))
  time.sleep(2)

  # Send a Reset_Equipment_Error signal and confirm nothing happens
  print("sending Reset_Equipment_Error, it should be ignored")
  breaker.post_fifo(Event(signals.Reset_Equipment_Error))
  print("nothing should have happened")

  # send a Remote signal and the breaker should re-initialize
  breaker.post_fifo(Event(signals.Remote))
  time.sleep(2)

  # send a closed event, the hardware should enter error state
  # because our breaker is still open
  breaker.post_fifo(Event(signals.Closed))
  time.sleep(2)

  # adjust the hardware so that it is closed, the reset the equipment error it
  # should go back into the breaker closed state
  # this tests the reset to deep history feature
  relay_driver._open = False
  breaker.post_fifo(Event(signals.Reset_Equipment_Error))
  time.sleep(2)

