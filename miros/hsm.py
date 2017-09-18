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
    status = return_status.IGNORED
    return status

  def init(self):
    '''triggers the top-most initial transition into a HSM

    This method is used at the beginning of an interaction with a statechart.
    It jumps into the initial state, then places all of the super state
    functions into a path variable.  Once this path is discovered, it calls the
    entry actions on each of the path items. Then it calls the init actions on
    the target, and if this init call requires a transition, it will perform all
    of the above actions again until the chart settles into its final initial
    state.

    This algorithm limits the design topology of your chart.  'init' signals
    that are going to be followed on the chart 'start_at' can only climb into
    the chart, they can not climb out.  If they do, this search routine will
    fail.

    TODO: Write about this limitation in the README.txt
    '''
    e = Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL)
    path, outermost, max_index = [None], self.state.fun, 0
    assert(self.temp.fun != None and outermost == self.top)

    # We will continue searching the chart until it stops requesting transitions
    while(True): # outer while
      path[0], e, index = self.temp.fun, Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL), 0

      while(self.temp.fun != outermost):
        index      += 1
        r           = self.temp.fun(self, e)
        if index > max_index:
          path.append(self.temp.fun)
          max_index = index
        else:
          path[index] = self.temp.fun
      self.temp.fun = path[0]
      # Now that we know what the paths are, starting for the outermost state,
      # enter each state until we reach our target state
      e = Event(signal=signals.ENTRY_SIGNAL)

      self.temp.fun = path[0]
      while(True): # inner while
        entery_fn = path[index]
        index -= 1
        r = entery_fn(self,e)
        if(index < 0):
          break # inner while break condition

      # Now send it the init event, the init event could change our
      # self.temp.fun if it needs to transition. This means that we might have to
      # repeat the work done above.  Reset our outermost state to this state and
      # continue to delve into the chart
      outermost = path[0]
      e = Event(signal=signals.INIT_SIGNAL)
      r = outermost(self,e)

      if r != return_status.TRAN:
        break # outer while break condition

    self.state.fun = outermost
    self.temp.fun  = outermost

  def dispatch(self, hsm, e):
    '''dispatches an event to a HSM.

     Processing an event represents one run-to-completion (RTC) step
     '''
    pass

  def trans(self, fn):
    '''sets a new function target and returns that transition required by engine'''
    self.temp.fun = fn
    return return_status.TRAN

  def is_in(self,hsm,e):
    '''tests if a hsm is in a given state'''
    pass

  def child_state(hsm,e):
    '''finds the child state of a given parent'''
    pass

def ctor(hsm,e):
  pass



