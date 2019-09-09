import re
import time
import logging
from pathlib import Path
from collections import deque
from collections import namedtuple

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status
from miros import ThreadSafeAttributes

logger = logging.getLogger('thread_safe_attributes')
log_file = str(Path('.') / 'thread_safe_attribute_factory.log')
f_handler = logging.FileHandler(log_file, "w")
f_handler.setLevel(logging.DEBUG)
f_format = logging.Formatter('%(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)

def spy_callback(spy):
  '''write spy to log'''
  logged_spy_message = "S: {}".format(spy)
  with open(log_file, "a+") as fp:
    fp.write(logged_spy_message+'\n')
  logging.debug(logged_spy_message)

class Example2(Factory):
  _attributes = ['thread_safe_attr_1', 'thread_safe_attr_2']

  def __init__(self, name, live_trace=None, live_spy=None):

    super().__init__(name=name)
    self.live_trace = False if live_trace == None else live_trace
    self.live_spy = False if live_spy == None else live_spy

    self.c = self.create(state="c"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.c_init_signal). \
      catch(signal=signals.B,
        handler=self.c_b). \
      to_method()

    self.c1 = self.create(state="c1"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c1_entry_signal). \
      catch(signal=signals.A,
        handler=self.c1_a). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.c1_exit_signal). \
      to_method()

    self.c2 = self.create(state="c2"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c2_entry_signal). \
      catch(signal=signals.A,
        handler=self.c2_a). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.c2_exit_signal). \
      to_method()

    self.nest(self.c, parent=None). \
         nest(self.c1, parent=self.c). \
         nest(self.c2, parent=self.c)

    self.register_live_spy_callback(spy_callback)

    self.start_at(self.c)

  def c_entry_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_1 = False
    self.thread_safe_attr_2 = False
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c_init_signal(self, e):
    status = self.trans(self.c1)
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c_b(self, e):
    self.thread_safe_attr_1 = True
    status = self.trans(self.c)
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c1_entry_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_1 = True
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c1_a(self, e):
    status = self.trans(self.c2)
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c1_exit_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_1 = False
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c2_entry_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_2 = True
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c2_a(self, e):
    status = self.trans(self.c1)
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c2_exit_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_2 = False
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

if __name__ == '__main__':
  ao = Example2('thread_safe_attribute_factory_demo', live_spy=True) 
  ao.live_spy = True
  # Create the statechart thread and start it in state c
  # Set the thread safe attributes while the statechart is starting is running
  # in another thread
  ao.thread_safe_attr_1 = False
  ao.thread_safe_attr_2 = True
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)

# the log file will look like this:
'''
S: START
S: SEARCH_FOR_SUPER_SIGNAL:c
S: ENTRY_SIGNAL:c
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: INIT_SIGNAL:c
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: SEARCH_FOR_SUPER_SIGNAL:c1
S: ENTRY_SIGNAL:c1
S: thread_safe_attr_1: True
S: thread_safe_attr_2: False
S: INIT_SIGNAL:c1
S: <- Queued:(0) Deferred:(0)
S: A:c1
S: thread_safe_attr_1: False
S: thread_safe_attr_2: True
S: SEARCH_FOR_SUPER_SIGNAL:c2
S: SEARCH_FOR_SUPER_SIGNAL:c1
S: EXIT_SIGNAL:c1
S: thread_safe_attr_1: False
S: thread_safe_attr_2: True
S: ENTRY_SIGNAL:c2
S: thread_safe_attr_1: False
S: thread_safe_attr_2: True
S: INIT_SIGNAL:c2
S: <- Queued:(0) Deferred:(0)
'''
