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
class HsmTopologyException(Exception):
  pass

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

    '''
    topological_error = "impossible chart topology for Hsm.init, "
    topological_error += "see Hsm.init doc string for details"

    e = Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL)
    path, outermost, max_index = [None], self.state.fun, 0
    assert(self.temp.fun != None and outermost == self.top)

    # We will continue searching the chart until it stops requesting transitions
    while(True): # outer while
      path[0], e, index = self.temp.fun, Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL), 0
      previous_super = None
      while(self.temp.fun != outermost):
        index      += 1
        r           = self.temp.fun(self, e)
        if( previous_super == self.temp.fun ):
          raise(HsmTopologyException(topological_error))
        if index > max_index:
          path.append(self.temp.fun)
          max_index = index
        else:
          path[index] = self.temp.fun
        previous_super = self.temp.fun

      self.temp.fun = path[0]
      # Now that we know what the paths are, starting for the outermost state,
      # enter each state until we reach our target state
      e = Event(signal=signals.ENTRY_SIGNAL)
      self.temp.fun = path[0]
      while(True): # inner while
        # pre-decrement to remove outermost from our entry list
        index -= 1
        entery_fn = path[index]
        r = entery_fn(self,e)
        if(index == 0):
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

  def dispatch(self,e):
    '''dispatches an event to a HSM.

    Processing an event represents one run-to-completion (RTC) step
    '''
    t,s,v,ip     = None,None,None, 0
    path         = [None,None,None]
    max_index    = 0

    entry_e, exit_e, search_e, init_e =                      \
              Event(signal=signals.ENTRY_SIGNAL),            \
              Event(signal=signals.EXIT_SIGNAL),             \
              Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL), \
              Event(signal=signals.INIT_SIGNAL)

    t = self.state.fun # saving the current state function into our temporary
                       # variable

    assert(t != None)
    assert(t == self.state.fun)

    while(True):
      s = self.temp.fun
      # Event e was provided by the client, so we need to search outward in our
      # chart until we find a state that handles it, a state that handles it
      # will not return a return_state.SUPER status
      r = s(self, e)
      if(r != return_status.SUPER):
        break;

    # If we found a state that indicates that some action is required, we
    # process that action, by digging into the chart.
    if(r >= return_status.TRAN):
      path[0], path[1], path[2] = self.temp.fun, t, s
      t = self.temp.fun
      while(t != s):
        r = t(self, exit_e)
        if(r == return_status.HANDLED):
          t(self, search_e)

      # This hasn't been written yet (provides the lca - more will be written
      # shortly)
      ip = self.trans_(path,max_index)

      # transition to history spy stuff placed here

      # If our trans indicated that we need to enter our path information
      # we did it now.  The path lower indexes contain inner states while the
      # higher indexes contain outer states.  We enter our outer states to get
      # toward the desired inner state.
      while(ip >= 0):
        path[ip](self, entry_e)
        ip -= 1

      # We reset our temporary memory and target state method pointer will what
      # we are trying to get to (prior to running all of the init signals).  If
      # there are no handled init events in our target state, we are done our
      # work here.
      t, self.temp.fun = path[0], path[0]

      # Now that we have entered our target state, we have to see it has an init
      # signal that will take us deeper into the hsm.  If it does, continue to
      # transition until we settle to where we need to be
      while(t(self, init_e) == return_status.TRAN):
        path[0], ip = self.temp.fun, 0
        self.temp.fun(self, search_e)

        while(self.temp.fun != t):
          ip += 1
          if ip > max_index:
            path.append(self.temp.fun)
            max_index = ip
          else:
            path[ip] = self.temp.fun
          self.temp.fun(self, search_e)

        self.temp.fun = path[0]

        while(True):
          path[ip](self, entry_e)
          ip -= 1
          if(ip == 0):
            break
        t = path[0]

    elif(r == return_status.HANDLED): # trans handled
      pass
    else:
      pass
      # ignored

    self.state.fun = t
    self.temp.fun  = t

  def trans(self,fn):
    '''sets a new function target and returns that transition required by engine'''
    self.temp.fun = fn
    return return_status.TRAN

  def trans_(self, path, max_index):
    '''sets a new function target and returns that transition required by engine'''
    ip, iq = -1, 0
    t, s   = path[0], path[2]

    entry_e, exit_e, search_e, init_e =                      \
              Event(signal=signals.ENTRY_SIGNAL),            \
              Event(signal=signals.EXIT_SIGNAL),             \
              Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL), \
              Event(signal=signals.INIT_SIGNAL)

    # +------+
    # |      +----+
    # |      |    |
    # |      <----+
    # +------+
    if(s == t):
      s(self, exit_e)
      ip = 0
    else:
      # fill this in later
      pass

    return ip

  def is_in(self,hsm,e):
    '''tests if a hsm is in a given state'''
    pass

  def child_state(hsm,e):
    '''finds the child state of a given parent'''
    pass

  def augment(self, **kwargs):
    """Used to add attributes to an hsm object

    Args:
      kwargs['other'](Mandatory other object): An another object for which you would
      like to add as an attribute of this object.

      kwargs['name'](Mandatory): The name that you would like to call this
      attribute, this argument must be a string

      kwargs['relationship'](Optional): Indicates if you want to also add this
      object as an attribute to the other class, using this object's name.  This
      option will only work if the other object also has an augment method that
      acts exactly the same as this one.

      ``Examples``
      alarm       = Hsm(); alarm.name       = "alarm"
      time_keeper = Hsm(); time_keeper.name = "time_keeper"
      alarm.augment(other=time_keeper, name="time_keeper")

      assert(alarm.time_keeper == time_keeper) # will be true

      inverter  = Hsm(); inverter.name = "inverter"
      networker = Hsm(); networker.name = "networker"
      inverter.augment(other=networker, name="net", relationship="mutual")

      assert(inverter.net == networker) # will be true
      assert(networker.inverter == inverter ) # will be true
    """

    relationship = None
    if("other" in kwargs ):
      other = kwargs['other']
    if("name" in kwargs ):
      name = kwargs['name']
    if("relationship" in kwargs ):
      relationship = kwargs['relationship']

    if hasattr(self, name ) is not True:
      setattr(self, name, other)
    else:
      pass
    if( relationship != None and relationship == "mutual"):
      other.augment( other=self, name=self.name, relationship=None )



