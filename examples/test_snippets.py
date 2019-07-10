import time
from collections import namedtuple

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status

class InstrumentedFactory(Factory):
  def __init__(self, name, live_trace=None, live_spy=None):
    super().__init__(name)
    self.live_trace = False if live_trace == None else live_trace
    self.live_spy = False if live_spy == None else live_spy


class Bob(InstrumentedFactory):
  def __init__(self, name, a, b, live_trace=None, live_spy=None):
    '''comment'''
    super().__init__(name, live_trace, live_spy)

def guard():
  return True

@spy_on
def source_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.SIGNAL_NAME):
    if guard():
      chart.post_fifo(Event(signal=signals.EVT_A))
      status = chart.trans(target_state)
    else:
      status = return_status.HANDLED
  else:
    self.temp.fun = chart.top
    status = return_status.SUPER
  return status
 
@spy_on
def target_state(chart, e):
  self.temp.fun = chart.top
  status = return_status.SUPER
  return status

