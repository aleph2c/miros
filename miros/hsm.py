import sys
import traceback
from miros.event import signals, return_status, Event
import pprint
def pp(item):
  print()
  pprint.pprint(item)
# this_function_name = sys._getframe().f_code.co_name

def spy_on(fn):
  def spy_wrapped(chart, e):
    # Add the spy object if it doesn't exist already
    if hasattr(chart, 'spy') == False:
      chart.augment(name='spy', other=chart.spy_log)
    name = fn.__name__

    # Place what is happening within the spy
    if(e.signal == signals.ENTRY_SIGNAL):
      chart.spy.append("{}:{}".format(e.signal_name, name))
    elif(e.signal == signals.EXIT_SIGNAL):
      chart.spy.append("{}:{}".format(e.signal_name, name))
    elif(e.signal == signals.INIT_SIGNAL):
      chart.spy.append("{}:{}".format(e.signal_name, name))
    elif(e.signal == signals.REFLECTION_SIGNAL):
      # We are no longer going to return a ReturnStatus object
      # instead we write the function name as a string
      status = name
    else:
      chart.spy.append("{}:{}".format(e.signal_name, name))
    # now call the original handler
    status = fn(chart, e)
    return status
  return spy_wrapped

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
    self.state   = HsmAttr()
    self.temp    = HsmAttr()
    self.spy_log = []

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
    functions into a tpath variable.  Once this tpath is discovered, it calls the
    entry actions on each of the tpath items. Then it calls the init actions on
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
    tpath, outermost, max_index = [None], self.state.fun, 0
    assert(self.temp.fun != None and outermost == self.top)

    # We will continue searching the chart until it stops requesting transitions
    while(True): # outer while
      tpath[0], e, index = self.temp.fun, Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL), 0
      previous_super = None
      while(self.temp.fun != outermost):
        index      += 1
        r           = self.temp.fun(self, e)
        if( previous_super == self.temp.fun ):
          raise(HsmTopologyException(topological_error))
        if index > max_index:
          tpath.append(self.temp.fun)
          max_index = index
        else:
          tpath[index] = self.temp.fun
        previous_super = self.temp.fun

      self.temp.fun = tpath[0]
      # Now that we know what the tpaths are, starting for the outermost state,
      # enter each state until we reach our target state
      e = Event(signal=signals.ENTRY_SIGNAL)
      self.temp.fun = tpath[0]
      while(True): # inner while
        # pre-decrement to remove outermost from our entry list
        index -= 1
        entery_fn = tpath[index]
        r = entery_fn(self,e)
        if(index == 0):
          break # inner while break condition

      # Now send it the init event, the init event could change our
      # self.temp.fun if it needs to transition. This means that we might have to
      # repeat the work done above.  Reset our outermost state to this state and
      # continue to delve into the chart
      outermost = tpath[0]
      e = Event(signal=signals.INIT_SIGNAL)
      r = outermost(self,e)

      if r != return_status.TRAN:
        break # outer while break condition

    self.state.fun = outermost
    self.temp.fun  = outermost

  def dispatch(self,e,spy=None,trace=None):
    '''dispatches an event to a HSM.

    Processing an event represents one run-to-completion (RTC) step.

    Args:
      e (Event): The event to be dispatched to the hsm object

    Returns:
      None

    Example:
      chart = Hsm()
      signals.append("A")
      chart.start_at(dispatch_graph_a1_s1)
      chart.dispatch(Event(signal=signals.A)

    Raises:
      HsmTopologyException: if a state function handler is malformed

    Useful mnemonics:

    S (source)           Which state is the source of the arrow in the diagram?
                         This variable is not actually defined, but it is
                         referenced in the comments with adjacent diagrams to keep
                         things clear.

                         Example:
                           S == dispatch_graph_f1_s0
                           # in the follow state function
                           def dispatch_graph_f1_s0(chart, e):
                             .
                             elif(e.signal == signals.C):
                               chart.trans(dispatch_graph_f1_s22)
                             .

    T (target)           What is the source aiming at?  Which state is pointed
                         to by the arrow in the diagram?  This variable is not
                         actually defined, but it is referenced in the comments.

                         This will be state handler that was an argument of the
                         trans call:

                         Example:
                           T == dispatch_graph_f1_s22
                           # in the follow state function
                           def dispatch_graph_f1_s0(chart, e):
                             .
                             elif(e.signal == signals.C):
                               chart.trans(dispatch_graph_f1_s22)
                             .

    S->super             The super state of S, the state in which S is wrapped
                         within.
    S->super->super..    The super..super state of S

    T->super             The super state of T, the state in which T is wrapped
                         within.
    T->super->super..    The super..super state of T

    self.state.fun       The current state before the dispatch occurred

    self.temp.fun        Before the search begins, this is T, but gets overwritten
                         during the search process by:
                           * any call to trans within state function will change
                             this.
                           * any call with a super signal will change this.

    lca                  least common ancestor.  The most outward state that S and
                         T have in common.  It is used to determine when we have
                         constructed the correct entry path to the target, called
                         the tpath.

    tpath                A list of state functions that are found during the
                         trans_ process.  If you call this list backwards,
                         starting from ip you will correctly enter toward T for
                         a given state chart topology.

    ip                   An index into the tpath.  All elements between 0 and ip
                         in the tpath are valid entry handlers which will be used
                         to approach T.

    iq                   Sometimes a bool indicating if the lac has been found,
                         sometimes a shadow of the ip index used to discover
                         which topology the statechart is configured in.  Only
                         used in more advanced topologies.

    topology             A graph characteristic that is shared well enough across
                         a set of graphs that part of this search algorithm can be
                         used to move from the S to the T.  There are 8 different
                         topologies, labeled topology_a..topology_h.  If you
                         would like to know more about them, reference the tests
                         directory where they are drawn or the trans_ method which
                         also has them described as diagrams in the comments.
    '''
    tpath     = [None,None,None]
    t,s,v,ip  = None,None,None, 0
    max_index = 2

    entry_e, exit_e, super_e, init_e =                       \
              Event(signal=signals.ENTRY_SIGNAL),            \
              Event(signal=signals.EXIT_SIGNAL),             \
              Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL), \
              Event(signal=signals.INIT_SIGNAL)


    # To begin with we assume that no action will occur and the T state is just
    # our current state.
    #
    # t contains T
    t = self.state.fun

    # Our contract
    assert(t != None)
    assert(t == self.state.fun)

    # Determine if the chart can take action based on the event provided as
    # an argument to the method
    while(True):
      # if looped, place the super state into the s
      s = self.temp.fun
      # Event e was provided by the client, so we need to search outward in our
      # chart until we find a state that handles it, a state that handles it
      # will not return a return_state.SUPER status
      r = s(self, e)
      if r == None:
        raise(HsmTopologyException( \
            "state handler {} is not returning a valid status".format(s)))
      if(r != return_status.SUPER):
        # S in now stored in s
        break;

    # If we found a state that indicates that some action is required we
    # can now take action
    if(r >= return_status.TRAN):
      # tpath[0] contains T
      # tpath[1] contains t, self.state.fun (starting state)
      # tpath[2] contains S
      tpath[0], tpath[1], tpath[2] = self.temp.fun, t, s

      # Starting at our current state, move out to the S state, eventually
      # settling self.temp.fun on S, run all of the exit handlers we recurse
      # outward.
      #
      # t contains our current state at the start of the loop, then it is given
      # the self.state.fun->super.. Upon each iteration as it is passed the value
      # of self.temp.fun
      #
      # s contains S
      #
      # Note: This code and the topology_d code in trans_ allow provide the
      #       topology_h algorithm
      while(t != s):
        r = t(self, exit_e)
        if r == None:
          raise(HsmTopologyException( \
              "state handler {} is not returning a valid status".format(t)))
        if(r == return_status.HANDLED):
          t(self, super_e)
        t = self.temp.fun

      # navigate all supported topologies
      # tpath will be over-written with entry values
      # ip will indicate at which point we should begin an entry path
      ip = self.trans_(tpath,max_index)

      # transition to history spy stuff placed here

      # If our trans_ method indicated that we need to enter into a state(s) we
      # do so now.  The tpath lower indexes contain inner states while the
      # higher indexes contain outer states.  So, we enter our outer states to
      # get toward the desired inner state.
      while(ip >= 0):
        tpath[ip](self, entry_e)
        ip -= 1

      # tpath[0] contains T
      # t is now set to T
      # self.temp.fun is set to T
      t, self.temp.fun = tpath[0], tpath[0]

      # We have entered T, now we need to work with its 'init' signal
      while(t(self, init_e) == return_status.TRAN):
        tpath[0], ip = self.temp.fun, 0
        self.temp.fun(self, super_e)

        while(self.temp.fun != t):
          ip += 1
          if ip > max_index:
            tpath.append(self.temp.fun)
            max_index = ip
          else:
            tpath[ip] = self.temp.fun
          self.temp.fun(self, super_e)

        self.temp.fun = tpath[0]

        while(True):
          tpath[ip](self, entry_e)
          ip -= 1
          if(ip == 0):
            break
        t = tpath[0]

    elif(r == return_status.HANDLED): # trans handled
      # This is the ultimate hook pattern
      pass
    else:
      pass
      # ignore the event since our chart doesn't handle it

    # t contains T
    self.state.fun = t
    self.temp.fun  = t

  def trans(self,fn):
    '''sets a new function target and returns that transition required by engine'''
    self.temp.fun = fn
    return return_status.TRAN

  def trans_(self, tpath, max_index):
    '''execute a transition sequence in a hsm

    A helper function for the ```dispatch```.  It navigates through the possible
    supported topologies, navigating the chart just up to the point of entering
    the target hierarchy.  The target entry path is placed into the provided
    tpath list, and the depth of the entry path is provided as an output of the
    method.

    Args:
      tpath:      a list which will be populated with the entry path required
                  for the dispatch method to enter the T (target) state.

      max_index:  The maximum index used within the tpath list up until this
                  point.  If more space is required, an append is used to extend
                  the length of the tpath list, otherwise an element is assigned
                  to a given index location.

    Returns:
      ip:         An index into the tpath.  All elements between 0 and ip in the
                  tpath are valid entry handlers which will be used to approach T.

    If you don't understand what S/T are, read all of the mnemonics described in
    the ```dispatch``` docstring.

    To understand beyond this point you must first know what happens with
    the tpath, ip and iq. Consider this example:

     +-------- s1---------+
     | +-------s2-------+ |
     | | +-----s3-----+ | |
     | | | +---s4---+ | | |
     | | | | +-s5-+ | | | |
     | | | | T    | | | | | S
     | | | | +----+ | | | | top is the lca
     | | | +--------+ | | |
     | | +------------+ | |
     | +-+--------------+ |
     ++------------------++

    As trans_ searches, it will place state handlers into the tpath array
    These state handlers will be used to enter toward the target state once
    the lca has been found.

                useful data <-+-> garbage data
                              |   collected in search
           +----+----+----+---+----+-----+-----+
    tpath: | s5 | s4 | s3 |s2 | s1 | top | s21 |
           +----+----+----+---+-/--+-----+-----+
                                |
                                +-- ip == 4

    The method that called trans_ already has a reference to the tpath so it
    doesn't need to be returned.  However, ip does need to be returned at it
    represents which state handlers will be entered.

    Returning the above from this method will tell ```dispatch``` to
    enter s1, enter s2, enter s3, enter s4, enter s5.

    iq is a bool, it represents if we have found the lca of S and T.  It is only
    used later in the method and it is not used outside of the method, so we
    only it when needed by the search.  It leave comments in the code describing
    its state, so you can understand what is going on.

    When the method begins t == T and s == S but these variable are then clobbered
    in the search and over-written with new meanings.  Their new meanings will
    be described in the comments where they are used, we will always draw our
    attention back to S and T and how they relate to a diagram.
    '''

    ip, iq = -1, 0 # no entry, no lca found
    # S is in tpath[2]
    # T is in tpath[0]
    t, s = tpath[0], tpath[2]
    entry_e, exit_e, super_e, init_e =                       \
              Event(signal=signals.ENTRY_SIGNAL),            \
              Event(signal=signals.EXIT_SIGNAL),             \
              Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL), \
              Event(signal=signals.INIT_SIGNAL)
    # +-S-T-+
    # |     +-+
    # |     | |
    # |     <-+
    # +-lca-+
    # (a) check source == target
    # pytest -m topology_a -s
    if(s == t):
      s(self, exit_e) # exit the source
      ip = 0          # enter the target
      # iq = 1
    else:
      t(self,super_e)
      t = self.temp.fun
      # +--S-lca-+
      # | +-T--+ |
      # | |    <-+
      # | +----+ |
      # +--------+
      # t now contains T->super
      # s contains S
      # (b) check S == T->super
      # pytest -m topology_b -s
      if (s == t):
        ip = 0 # enter the target
        # iq = 1
      else:
        # find the super state of the source
        s(self, super_e)
        #  +-----lca-----+
        #  | +-S-+ +-T-+ |
        #  | |   | |   | |
        #  | |   +->   | |
        #  | |   | |   | |
        #  | +---+ +---+ |
        #  +-------------+
        # t now contains T->super
        # self.temp.fun contains S->super
        # (c) check S->super == T->super
        # pytest -m topology_c -s
        if(self.temp.fun == t):
          s(self, exit_e)
          ip = 0
          # iq = 1
        else:
          # +--T-lca-+
          # | +-S--+ |
          # | |    +->
          # | +----+ |
          # +--------+
          # self.temp.fun contains S->super
          # tpath[0] contains T
          # (d) check S->super == T
          # pytest -m topology_d -s
          if(self.temp.fun == tpath[0]):
            # leave ip as -1, that way no entry will occur
            s(self,exit_e)
            # iq = 1
          else:
            #  +--------S-lca-----+
            #  |+---------------+ |
            #  ||       .       | |
            #  ||   +-------+   | |
            #  ||   | +-T-+ |   | |
            #  || . | |   <-- . --+
            #  ||   | +---+ |   | |
            #  ||   +-------+   | |
            #  ||       .       | |
            #  |+---------------+ |
            #  +------------------+
            # (e) check S == T->super->super..
            # pytest -m topology_e -s
            iq, ip = 0,1     # LCA not found yet, enter T and T->super
            tpath[1] = t     # tpath[1] contains T->super
            t = self.temp.fun  # t contains S->super
            r = tpath[1](self, super_e)

            if r == None:
              raise(HsmTopologyException( \
                  "state handler {} is not returning a valid status".format(tpath[1])))

            while(r == return_status.SUPER):
              ip += 1
              # store our entry tpath
              if ip > max_index:
                tpath.append(self.temp.fun)
                max_index = ip
              else:
                tpath[ip] = self.temp.fun

              if(self.temp.fun == s): # if we have found S
                iq =  1
                ip -= 1 # don't enter S since we are coming at it from the
                        # inside
                r = return_status.HANDLED # terminate the loop
              else:
                r = self.temp.fun(self,super_e)

            if(iq==0):
              # s contains S
              # set self.temp.fun to S->super
              s(self, exit_e)
              # If our previous search failed, the tpath is filled
              # with the entire state hierarchy.  So, we start on the
              # outside of the graph, and work our way in, checking if
              # S->super is the same as T->super->super..
              #
              # At this point of the search, the tpath has been filled
              # with the super states of our target and iq is a bool. If
              # it is 0 we must consider topology f:
              #    +---------------------------+
              #    |+-----------lca-----------+|
              #    ||      +--S--+            ||
              #    ||      |     +----------+ ||
              #    ||      +-----+          | ||
              #    ||+------------------+   | ||
              #    |||+---------------+ |   | ||
              #    ||||       .       | |   | ||
              #    ||||   +-------+   | |   | ||
              #    ||||   | +-T-+ |   | |   | ||
              #    |||| . | |   <-- . ------+ ||
              #    ||||   | +---+ |   | |     ||
              #    ||||   +-------+   | |     ||
              #    ||||       .       | |     ||
              #    |||+---------------+ |     ||
              #    ||+------------------+     ||
              #    |+-------------------------+|
              #    +---------------------------+
              # pytest -m topology_f -s
              # (f) check is S->super == T->super->super..
              # t contains S->super
              # tpath contains entry function handlers to get to T
              # tpath[ip] contains T->super->super..
              iq = ip
              r  = return_status.IGNORED
              while(True):
                if(t==tpath[iq]): # is this the lca?
                  r = return_status.HANDLED
                  ip = iq-1 # do not enter the lca
                  iq = -1
                else:
                  iq -= 1
                if(iq < 0):
                  break
            if(r != return_status.HANDLED):
              # +----------------------------+
              # |+----------lca-------------+|
              # || +-------------------+    ||
              # || | +---------------+ |    ||
              # || | |       .       | |    ||
              # || | |   +-------+   | |    ||
              # || | |   | +-S-+ |   | |    ||
              # || | | . | |   +-- . -----+ ||
              # || | |   | +---+ |   | |  | ||
              # || | |   +-------+   | |  | ||
              # || | |       .       | |  | ||
              # || | +---------------+ |  | ||
              # || +-------------------+  | ||
              # ||                        | ||
              # || +-------------------+  | ||
              # || | +---------------+ |  | ||
              # || | |       .       | |  | ||
              # || | |   +-------+   | |  | ||
              # || | |   | +-T-+ |   | |  | ||
              # || | | . | |   <-- . -----+ ||
              # || | |   | +---+ |   | |    ||
              # || | |   +-------+   | |    ||
              # || | |       .       | |    ||
              # || | +---------------+ |    ||
              # || +-------------------+    ||
              # |+--------------------------+|
              # +----------------------------+
              # (g) check each S->super->super.. == T->super->super
              # t contains S->super
              # tpath contains entry function handlers to get to T
              # ip initially will have the index equal to the maximum depth of
              # the chart relative to T, minus 1.
              r = return_status.IGNORED
              while(True):
                if(t(self, exit_e)==return_status.HANDLED):
                  t(self, super_e)
                # t contains S->super->super..
                t = self.temp.fun
                iq = ip
                while(True):
                  if(t==tpath[iq]): # is this the lca?
                    r = return_status.HANDLED
                    ip = iq-1 # do not enter the lca
                    iq = -1
                  else:
                    iq -= 1
                  if(iq <0):
                    break
                if(r == return_status.HANDLED):
                  break;

    return ip

  def is_in(self,fn_state_handler):
    '''tests if a hsm is in a given state'''
    result = False
    super_e = Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL)
    while(True):
      if(self.temp.fun == fn_state_handler):
        result = True
        r = return_status.IGNORED
      else:
        r = self.temp.fun(self, super_e)
      if(r == return_status.IGNORED):
        break
    self.temp.fun = self.state.fun # set our temp back to what it should be
    return result


  def child_state(self,fn_parent_state_handler):
    '''finds the child state of a given parent

    This method will only return a child state of a given handler, if the system
    is in a substate of the state being called.

    +---------- graph_e1_s1 -----------+
    | +-------- graph_e1_s2 -------+   |
    | | +------ graph_e1_s3 -----+ |   |
    | | | +---- graph_e1_s4 ---+ | |   |
    | | | |  +- graph_e1_s5 -+ | | |   |
    | | | |  |               | | | |   |
    | +-b->  |               <-----a---+
    | | | |  |               | | | |   |
    | | +c>  +---------------+ | | |   |
    +d> | +--------------------+ | |   |
    | | +------------------------+ |   |
    | +----------------------------+   |
    +----------------------------------+

    chart = Hsm()
    chart.start_at(child_state_graph_e1_s5)
    chart.child_state(graph_e1_s5) #=> graph_e1_s5
    chart.child_state(graph_e1_s4) #=> graph_e1_s5
    chart.child_state(graph_e1_s3) #=> graph_e1_s4
    chart.dispatch(event=Event(signal=signals.D)

    # chart now in state graph_e1_s2
    chart.child_state(graph_e1_s5) #=> <CRASH!>
    chart.child_state(graph_e1_s2) #=> graph_e1_s2
    chart.child_state(graph_e1_s1) #=> graph_e1_s2 # which is wrong

    '''
    super_e   = Event(signal = signals.SEARCH_FOR_SUPER_SIGNAL)
    confirmed = False
    child     = self.state.fun
    self.temp.fun = self.state.fun
    while(True):
      if(self.temp.fun == fn_parent_state_handler):
        confirmed = True
        r = return_status.IGNORED
      else:
        child = self.temp.fun
        r = self.temp.fun(self, super_e)
      if(r == return_status.IGNORED):
        break;
    self.temp.fun = self.state.fun
    assert(confirmed == True)
    return child

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

