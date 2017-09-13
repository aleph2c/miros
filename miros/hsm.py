import sys
import traceback
from miros.event import signals, return_status, Event
# this_function_name = sys._getframe().f_code.co_name

def reflect(hsm=None,e=None):
  '''
  This will return the callers function name as a string:
  Example:

    def example_function():
      return reflect()

    print(example_function) #=> "example_function"
  
  '''
  fnt  = traceback.extract_stack(None,2)
  fnt1 = fnt[0]
  fnt2 = fnt1[2]
  return fnt2

class HsmAttr():
  '''
  No clue yet
  '''
  def __init__(self):
    self.fun = None # state-handler function ? 
                    # signature (chart, event)

    self.act = None # action-handler function
                    # signature (chart, event)
class Hsm():

  def __init__(self):
    '''set initial state of the hsm'''
    self.state = HsmAttr()
    self.temp  = HsmAttr()

  def start_at(self, initial_state):
    '''
    hsm = Hsm()
    # build it
    hsm.start(starting_state_function)
    '''
    self.state.fun = self.top
    self.temp.fun  = initial_state
    self.init()


  def top(self,hsm, e):
    '''top most state given to all HSM; treat it as an outside function'''
    status = return_status.UNHANDLED
    return (None, status)

  def init(self):
    '''triggers the top-most initial transition in a HSM'''
    e = Event(signal=signals.SEARCH_SIGNAL)
    # Just into the transition using an empty signal
    # We will use the heirchy itself to tell use about the entry path into the
    # HSM
    (super_fn, r) = self.temp.fun(self, e)
    assert( r == return_status.RET_TRAN )

    while( True ):
      (super_fn, r) = super_fn(self, e)
      if r != return_status.RET_TRAN:
        break

  def dispatch(self, hsm, e):
    '''dispatches an event to a HSM.

     Processing an event represents one run-to-completion (RTC) step
     '''
    pass

  def trans(self, hsm, e):
    '''executes a transition sequence in a HSM'''
    pass

  def is_in(self,hsm,e):
    '''tests if a hsm is in a given state'''
    pass

  def child_state(hsm,e):
    '''finds the child state of a given parent'''
    pass

def ctor(hsm,e):
  pass



