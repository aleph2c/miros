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

class Class2UsedToSolveProblem(Class1UsedToSolveProblem):
  def __init__(self, name):
    '''demonstration class showing how inheritance can
       overload methods of an another class, and indepentently attach
       to the statemachine used by the other class.

    **Args**:
       | ``name`` (string): the name to show up in the trace
    '''
    super().__init__(name)

  def method_1(self):
    print("method 1(overloaded) called")

  def method_2(self):
    print("method 2(overloaded) called")

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
  subclassed_ao1 = Class1UsedToSolveProblem('subclassed_ao1')
  subclassed_ao1.live_trace = True
  # this is the attachement point to the first object
  subclassed_ao1.start_at(outer_state)
  subclassed_ao1.post_fifo(Event(signal=signals.B))
  subclassed_ao1.post_fifo(Event(signal=signals.A))
  subclassed_ao1.post_fifo(Event(signal=signals.Hook))

  # the two statemachines will be running at the same time in different
  # threads, so we will delay so we don't end up with a confusing trace
  time.sleep(0.01)
  subsubclassed_ao2 = Class2UsedToSolveProblem('subsubclassed_ao2')
  subsubclassed_ao2.live_trace = True
  # this is the attachement point to the second object
  # (it uses the same statemachine as the first object)
  subsubclassed_ao2.start_at(outer_state)
  subsubclassed_ao2.post_fifo(Event(signal=signals.Hook))
  subsubclassed_ao2.post_fifo(Event(signal=signals.B))
  subsubclassed_ao2.post_fifo(Event(signal=signals.A))
  
  time.sleep(0.01)
