import time
from collections import deque

from miros import Event
from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status

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

class ThreadSafeAttributesInActiveObject(ActiveObject):
  def __init__(self, name):
    super().__init__(name)
    self._thread_safe_attr_1 = deque(maxlen=1)
    self._thread_safe_attr_1.append(False)
    self._thread_safe_attr_2 = deque(maxlen=1)
    self._thread_safe_attr_2.append(False)

  @property
  def thread_safe_attr_1(self):
    return self._thread_safe_attr_1[-1]

  @thread_safe_attr_1.setter
  def thread_safe_attr_1(self, value):
    self._thread_safe_attr_1.append(value)

  @property
  def thread_safe_attr_2(self):
    return self._thread_safe_attr_2[-1]

  @thread_safe_attr_2.setter
  def thread_safe_attr_2(self, value):
    self._thread_safe_attr_2.append(value)

if __name__ == '__main__':
  ao = ThreadSafeAttributesInActiveObject('tsao')
  ao.live_trace = True
  ao.start_at(c)
  ao.thread_safe_attr_1 = False
  ao.thread_safe_attr_2 = True
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.A))
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.B))
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.A))
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.B))
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  ao.post_fifo(Event(signal=signals.A))
  print("ao.thread_safe_attr_1: {}".format(ao.thread_safe_attr_1))
  print("ao.thread_safe_attr_2: {}".format(ao.thread_safe_attr_2))
  time.sleep(0.1)
