.. called from quickstart.rst

.. code-block:: python

  from miros import ActiveObject
  from miros import signals
  from miros import Event
  from miros import return_status
  from miros import spy_on
  import time

  # This part of the code maps to the top part (non-state-machine) part of the
  # statechart diagram
  class SelfPayingToasterOven(ActiveObject):
    '''Class that holds the attributes and worker methods used by our toaster
       oven statechart'''

    def __init__(self, bitcoin_address):
      super().__init__("toaster_{}".format(bitcoin_address[0:5]))
      self.history = None
      self.bitcoin_address = bitcoin_address

      self.red_light_off()
      self.white_light_off()
      self.bitcoin_miner_off()
      self.heating_element_off()

    def red_light_on(self):
      print("turning red light on")

    def red_light_off(self):
      print("turning red light off")

    def white_light_on(self):
      print("turning white light on")

    def white_light_off(self):
      print("turning white light off")

    def bitcoin_miner_on(self):
      print("turning bitcoin miner on")

    def bitcoin_miner_off(self):
      print("turning bitcoin miner off")

    def heating_element_on(self):
      print("turning heating element on")

    def heating_element_off(self):
      print("turning heating element off")


  # The state-machine part of the statechart
  @spy_on
  def door_closed(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.white_light_off()
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = oven.trans(off)
    elif(e.signal == signals.Off):
      status = oven.trans(off)
    elif(e.signal == signals.Bake):
      status = oven.trans(baking)
    elif(e.signal == signals.Toast):
      status = oven.trans(toasting)
    elif(e.signal == signals.Open):
      status = oven.trans(door_open)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

  @spy_on
  def heating(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.red_light_on()
      oven.bitcoin_miner_on()
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.red_light_off()
      oven.bitcoin_miner_off()
      status = return_status.HANDLED
    else:
      oven.temp.fun = door_closed
      status = return_status.SUPER
    return status

  @spy_on
  def baking(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      oven.heating_element_on()
      oven.history = baking
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      oven.heating_element_off()
      status = return_status.HANDLED
    else:
      oven.temp.fun = heating
      status = return_status.SUPER
    return status

  @spy_on
  def toasting(oven, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
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
      oven.white_light_on()
      status = return_status.HANDLED
    elif(e.signal == signals.Close):
      status = oven.trans(oven.history)
    else:
      oven.temp.fun = oven.top
      status = return_status.SUPER
    return status

  if __name__ == "__main__":

    # make our toaster oven with our account information
    toaster = SelfPayingToasterOven('142x5ZhQEMk5LLjXGZeiTBWpv2oxQpfaHJ')

    # turn on our instrumentation so that we can test if our design is working
    toaster.live_trace = True

    # Start our toaster oven in the off state
    toaster.start_at(off)

    # Let's Bake
    toaster.post_fifo(Event(signal=signals.Bake))

    # Let's Toast
    toaster.post_fifo(Event(signal=signals.Toast))

    # Let's Open the door to our toaster oven
    toaster.post_fifo(Event(signal=signals.Open))

    # Let's Close the door
    toaster.post_fifo(Event(signal=signals.Close))

    # The toaster is running in a different thread than our main program
    # So wait a bit so that it can catch up before we close out this program
    time.sleep(0.1)

