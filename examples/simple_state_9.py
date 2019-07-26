# simple_state_9.py
import re
import time
import logging
from functools import partial

from miros import Event
from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status

@spy_on
def outer_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.scribble("hello from outer_state")
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.scribble("init")
    status = chart.trans(inner_state)
  elif(e.signal == signals.Hook):
    chart.scribble("run some code, but don't transition")
    status = return_status.HANDLED
  elif(e.signal == signals.Reset):
    chart.scribble("resetting the chart")
    status = chart.trans(outer_state)
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.scribble("exiting outer_state")
    status = return_status.HANDLED
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def inner_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.scribble("hello from inner_state")
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.scribble("exiting inner_state")
    status = return_status.HANDLED
  else:
    chart.temp.fun = outer_state
    status = return_status.SUPER
  return status
    
class ActiveObjectInstrumentToLog(ActiveObject):

  def __init__(self, name, filename=None):
    super().__init__(name)
    if filename is None:
      filename = 'simple_state_9.log'

    logging.basicConfig(
      format='%(asctime)s %(levelname)s:%(message)s',
      filename=filename,
      level=logging.DEBUG)

    # ActiveObject has a register_live_trace_callback and a
    # register_live_spy_callback interface, which can be used to
    # change the live_trace and live_spy behavior.  To use these
    # registration methods, you write a function which accepts a
    # string argument, provide this function as the input argument
    # to the registration method and your custom function will
    # stored, and then called each time a trace/spy string is
    # generated from within the ActiveObject's instrumentation
    # functions.  By providing your own functions, you can log
    # trace/spy information, or send it out over the network or do
    # whatever you like with it.

    # The register functions do not accept methods, they only accept
    # functions that take a single argument.  So we use the
    # functool.partial to create a function with the self baked into
    # it before it is passed into the register function. This way
    # when miros calls this function with a string, we do not get a
    # runtime error resulting from sending our customer function it
    # too few arguments.
    self.register_live_spy_callback(partial(self.spy_callback))
    self.register_live_trace_callback(partial(self.trace_callback))

  def trace_callback(self, trace):
    '''trace without datetime-stamp'''
    trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
    logging.debug("T: " + trace_without_datetime)

  def spy_callback(self, spy):
    '''spy with machine name pre-pended'''
    logging.debug("S: [{}] {}".format(self.name, spy))

if __name__ == '__main__':

  ao1 = ActiveObjectInstrumentToLog("ao1")
  ao1.live_trace = True
  ao1.live_spy = True

  ao2 = ActiveObjectInstrumentToLog("ao2")
  ao2.live_trace = True
  ao2.live_spy = True

  ao1.start_at(outer_state)
  ao1.post_fifo(Event(signal=signals.Hook))
  ao1.post_fifo(Event(signal=signals.Reset))

  ao2.start_at(inner_state)
  ao2.post_fifo(Event(signal=signals.Hook))
  ao2.post_fifo(Event(signal=signals.Reset))

  # let the threads catch up before we exit main
  time.sleep(0.01)

