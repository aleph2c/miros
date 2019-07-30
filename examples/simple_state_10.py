# simple_state_10.py
import re
import time
import logging
from functools import partial

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status

class FactoryInstrumentationToLog(Factory):

  def __init__(self, name, log_file_name=None,
      live_trace=None, live_spy=None):

    super().__init__(name)

    self.live_trace = \
      False if live_trace == None else live_trace
    self.live_spy = \
      False if live_spy == None else live_spy

    self.log_file_name = \
      'simple_state_10.log' if log_file_name == None else log_file_name

    logging.basicConfig(
      format='%(asctime)s %(levelname)s:%(message)s',
      filename=self.log_file_name,
      level=logging.DEBUG)
  
    self.register_live_spy_callback(partial(self.spy_callback))
    self.register_live_trace_callback(partial(self.trace_callback))

    self.outer_state = self.create(state="outer_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.outer_state_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.outer_state_init_signal). \
      catch(signal=signals.Hook,
        handler=self.outer_state_hook). \
      catch(signal=signals.Reset,
        handler=self.outer_state_reset). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.outer_state_exit_signal). \
      to_method()

    self.inner_state = self.create(state="inner_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.inner_state_entry_signal). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.inner_state_exit_signal). \
      to_method()

    self.nest(self.outer_state, parent=None). \
      nest(self.inner_state, parent=self.outer_state)

  def trace_callback(self, trace):
    '''trace without datetime-stamp'''
    trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
    logging.debug("T: " + trace_without_datetime)

  def spy_callback(self, spy):
    '''spy with machine name pre-pended'''
    logging.debug("S: [{}] {}".format(self.name, spy))
  
  @staticmethod
  def outer_state_entry_signal(chart, e):
    chart.scribble("hello from outer_state")
    status = return_status.HANDLED
    return status

  @staticmethod
  def outer_state_init_signal(chart, e):
    chart.scribble("init")
    status = chart.trans(chart.inner_state)
    return status

  @staticmethod
  def outer_state_hook(chart, e):
    status = return_status.HANDLED
    chart.scribble("run some code, but don't transition")
    return status

  @staticmethod
  def outer_state_reset(chart, e):
    status = chart.trans(chart.outer_state)
    return status

  @staticmethod
  def outer_state_exit_signal(chart, e):
    status = return_status.HANDLED
    chart.scribble("exiting the outer_state")
    return status

  @staticmethod
  def inner_state_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.scribble("hello from inner_state")
    return status

  @staticmethod
  def inner_state_exit_signal(chart, e):
    status = return_status.HANDLED
    chart.scribble("exiting inner_state")
    return status

if __name__ == '__main__':

  f1 = FactoryInstrumentationToLog(
    "f1",
    live_trace=True,
    live_spy=True
  )

  f2 = FactoryInstrumentationToLog(
    "f2",
    live_trace=True,
    live_spy=True
  )

  f1.start_at(f1.outer_state)
  f1.post_fifo(Event(signal=signals.Hook))
  f1.post_fifo(Event(signal=signals.Reset))

  f2.start_at(f2.inner_state)
  f2.post_fifo(Event(signal=signals.Hook))
  f2.post_fifo(Event(signal=signals.Reset))

  # let the threads catch up before we exit main
  time.sleep(0.01)

