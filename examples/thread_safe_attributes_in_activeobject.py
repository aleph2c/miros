import time
import logging
from pathlib import Path

from miros import Event
from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status
from miros import ThreadSafeAttributes

logger = logging.getLogger('thread_safe_attributes')
log_file = str(Path('.') / 'thread_safe_attribute_activeobject.log')
f_handler = logging.FileHandler(log_file)
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

@spy_on
def c(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_1 = False
    chart.thread_safe_attr_2 = False
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.INIT_SIGNAL):
    status = chart.trans(c1)
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.B):
    chart.thread_safe_attr_1 = True
    status = chart.trans(c)
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def c1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_1 = True
    status = return_status.HANDLED
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.A):
    status = chart.trans(c2)
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.thread_safe_attr_1 = False
    status = return_status.HANDLED
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  else:
    chart.temp.fun = c
    status = return_status.SUPER
  return status

@spy_on
def c2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_2 = True
    status = return_status.HANDLED
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.A):
    status = chart.trans(c1)
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.thread_safe_attr_2 = False
    status = return_status.HANDLED
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  else:
    chart.temp.fun = c
    status = return_status.SUPER
  return status

class Example1(ThreadSafeAttributes, ActiveObject):
  _attributes = ['thread_safe_attr_1', 'thread_safe_attr_2']

  def __init__(self, name):
    super().__init__(name)
    self.register_live_spy_callback(spy_callback)

if __name__ == '__main__':
  ao = Example1('thread_safe_attribute_ao_demo') 
  ao.live_spy = True
  # Create the statechart thread and start it in state c
  ao.start_at(c)
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
