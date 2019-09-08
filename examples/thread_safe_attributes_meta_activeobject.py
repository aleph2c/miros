
import re
import time
import logging
from functools import partial
from collections import deque
from collections import namedtuple

from miros import Event
from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status
from miros import ActiveObjectWithAttributes
from miros import ThreadSafeAttributes

@spy_on
def c(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_1 = False
    chart.thread_safe_attr_2 = False
  elif(e.signal == signals.INIT_SIGNAL):
    status = chart.trans(c1)
  elif(e.signal == signals.B):
    chart.thread_safe_attr_1 = True
    status = chart.trans(c)
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
  elif(e.signal == signals.A):
    status = chart.trans(c2)
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.thread_safe_attr_1 = False
    status = return_status.HANDLED
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
  elif(e.signal == signals.A):
    status = chart.trans(c1)
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.thread_safe_attr_2 = False
    status = return_status.HANDLED
  else:
    chart.temp.fun = c
    status = return_status.SUPER
  return status

class Example(ThreadSafeAttributes, ActiveObject):
  _attributes = ['thread_safe_attr_1', 'thread_safe_attr_2']

  def __init__(self, name):
    super().__init__(name)

if __name__ == '__main__':
  
  ao = Example('ao')
  ao.thread_safe_attr_1 = False
  ao.thread_safe_attr_2 = True
  ao.live_trace = True
  ao.start_at(c)
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.B))
  time.sleep(0.01)
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.B))
  time.sleep(0.01)
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  time.sleep(0.01)

