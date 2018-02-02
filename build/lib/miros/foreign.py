from collections  import deque
from miros.hsm import HsmEventProcessor, Attribute


class ForeignHsm():
  '''
  Provides an object that can be filled with the trace/spy information coming
  from another statechart on a different host.
  '''
  def __init__(self):
    self.foreign = Attribute()
    self.foreign.spy = deque(maxlen=HsmEventProcessor.SPY_RING_BUFFER_SIZE)
    self.foreign.trace = deque(maxlen=HsmEventProcessor.TRC_RING_BUFFER_SIZE)

  def clear_spy(self):
    self.foreign.spy.clear()

  def clear_trace(self):
    self.foreign.trace.clear()

  def trace(self):
    strace = ""
    for tr in self.foreign.trace:
      strace += tr
      strace += "\n"
    return strace

  def spy(self):
    return list(self.foreign.spy)

  def append_to_spy(self, item):
    self.foreign.spy.append(item)

  def append_to_trace(self, item):
    self.foreign.trace.append(item)

