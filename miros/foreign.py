class Hsm():
  '''
  Provides an object that can be filled with the trace/spy information coming
  from another statechart on a different host.
  '''
  def __init__(self):
    self.foreign_trace = []
    self.foreign_spy = []

  def trace(self):
    return self.foreign_trace

  def spy(self):
    return self.foreign_spy
    
