# simple_state_14.py
import re
import time
import logging
from functools import partial

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status

class F1(Factory):

  def __init__(self, name, log_file_name=None,
      live_trace=None, live_spy=None):

    super().__init__(name)

    self.live_trace = \
      False if live_trace == None else live_trace
    self.live_spy = \
      False if live_spy == None else live_spy

    self.times_in_inner = 0

    self.log_file_name = \
      'simple_state_14.log' if log_file_name == None else log_file_name

    # clear our log every time we run this program
    with open(self.log_file_name, "w") as fp:
      fp.write("")

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
      catch(signal=signals.Send_Broadcast, \
        handler=self.outer_state_send_broadcast). \
      catch(signal=signals.BROADCAST, \
        handler=self.outer_state_broadcast). \
      catch(signal=signals.Reset,
        handler=self.outer_state_reset). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.outer_state_exit_signal). \
      to_method()

    self.middle_state = self.create(state="middle_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.middle_state_entry_signal). \
      catch(signal=signals.Ready,
        handler=self.middle_state_ready). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.middle_state_exit_signal). \
      to_method()

    self.inner_state = self.create(state="inner_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.inner_state_entry_signal). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.inner_state_exit_signal). \
      to_method()

    self.nest(self.outer_state, parent=None). \
      nest(self.middle_state, parent=self.outer_state). \
      nest(self.inner_state, parent=self.middle_state)

  def trace_callback(self, trace):
    '''trace without datetime-stamp'''
    trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
    logging.debug("T: " + trace_without_datetime)

  def spy_callback(self, spy):
    '''spy with machine name pre-pended'''
    logging.debug("S: [{}] {}".format(self.name, spy))
  
  def outer_state_entry_signal(self, e):
    self.subscribe(Event(signal=signals.BROADCAST))
    self.scribble("hello from outer_state")
    status = return_status.HANDLED
    return status

  def outer_state_init_signal(self, e):
    self.scribble("init")
    status = self.trans(self.middle_state)
    return status

  def outer_state_hook(self, e):
    status = return_status.HANDLED
    self.scribble("run some code, but don't transition")
    return status

  def outer_state_send_broadcast(self, e):
    status = return_status.HANDLED
    self.publish(Event(signal=signals.BROADCAST))
    return status

  def outer_state_broadcast(self, e):
    status = return_status.HANDLED
    self.scribble("received broadcast")
    return status

  def outer_state_reset(self, e):
    status = self.trans(self.outer_state)
    return status

  def outer_state_exit_signal(self, e):
    status = return_status.HANDLED
    self.scribble("exiting the outer_state")
    return status

  def middle_state_entry_signal(self, e):
    status = return_status.HANDLED
    self.scribble("arming one-shot")
    self.post_fifo(Event(signal=signals.Ready),
      times=1,
      period=1.0,
      deferred=True)
    return status

  def middle_state_ready(self, e):
    status = self.trans(self.inner_state)
    return status

  def middle_state_exit_signal(self, e):
    status = return_status.HANDLED
    self.cancel_events(Event(signal=signals.Ready))
    return status

  def inner_state_entry_signal(self, e):
    status = return_status.HANDLED
    self.times_in_inner += 1
    self.scribble(
      "hello from inner_state {}".format(self.times_in_inner))
    return status

  def inner_state_exit_signal(self, e):
    status = return_status.HANDLED
    self.scribble("exiting inner_state")
    return status

class F2(F1):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def inner_state_entry_signal(self, e):
    status = return_status.HANDLED
    self.scribble("hello from new inner_state")
    return status

  def inner_state_exit_signal(self, e):
    status = return_status.HANDLED
    self.scribble("exiting new inner_state")
    return status

if __name__ == '__main__':

  f1 = F1(
    "f1",
    live_trace=True,
    live_spy=True,
  )

  f2 = F2(
    "f2",
    live_trace=True,
    live_spy=True,
  )

  f1.start_at(f1.outer_state)
  f1.post_fifo(Event(signal=signals.Hook))
  f1.post_fifo(
    Event(signal=signals.Reset),
    times=1,
    period=2.0,
    deferred=True
    )

  f2.start_at(f2.inner_state)
  f2.post_fifo(Event(signal=signals.Hook))
  f2.post_fifo(Event(signal=signals.Reset))
  f1.post_fifo(Event(signal=signals.Send_Broadcast))

  # delay long enough so we can see how the program behaves in time
  time.sleep(4.00)



