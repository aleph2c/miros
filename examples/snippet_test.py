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

class ExampleChart(InstrumentedFactory):
  def __init__(self, name, live_trace=None, live_spy=None):
    '''comment'''
    super().__init__(name, live_trace, live_spy)

    self.outer_state = self.create(state="outer_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.outer_state_entry_signal). \
      to_method()

    nest(self.outer_state, parent=None). \

    
  def outer_state_entry_signal(self, e):
    status = return_status.HANDLED
    return status


