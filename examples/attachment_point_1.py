# attachment_point_1.py
import time

from miros import spy_on
from miros import Event
from miros import signals
from miros import ActiveObject
from miros import return_status

class Class1UsedToSolveProblem(ActiveObject):
  def __init__(self, name):
    '''demonstration class used to show 
       event processor attachment point on statechart diagram

    **Args**:
       | ``name`` (string): the name to show up in the trace
    '''
    super().__init__(name)
    self.attribute_1 = None
    self.attribute_2 = None

  def method_1(self):
    print("method 1 called")

  def method_2(self):
    print("method 2 called")

@spy_on
def outer_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.attribute_1 = True
    chart.attribute_2 = True
    status = return_status.HANDLED
  if(e.signal == signals.Hook):
    print('hook')
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = chart.trans(inner_state_1)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def inner_state_1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.method_1()
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(inner_state_2)
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.method_2()
    status = return_status.HANDLED
  else:
    chart.temp.fun = outer_state
    status = return_status.SUPER
  return status
    
@spy_on
def inner_state_2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.attribute_1 = True
    chart.attribute_2 = True
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(inner_state_1)
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.attribute_1 = False
    chart.attribute_2 = False
    status = return_status.HANDLED
  else:
    chart.temp.fun = outer_state
    status = return_status.SUPER
  return status

if __name__ == "__main__":
  subclassed_ao = Class1UsedToSolveProblem('subclassed_ao')
  subclassed_ao.live_trace = True
  # this is the attachement point where the event processor
  # is linking to the statemachine defined above as a set of 
  # functions which reference each other
  subclassed_ao.start_at(outer_state)
  subclassed_ao.post_fifo(Event(signal=signals.B))
  subclassed_ao.post_fifo(Event(signal=signals.A))
  subclassed_ao.post_fifo(Event(signal=signals.Hook))
  time.sleep(0.01)
