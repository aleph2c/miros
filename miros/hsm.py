# -*- coding: utf-8 -*-
import re
import sys
import pprint
import inspect
import traceback  # try not use this if you can avoid it (it's fragile)
from copy         import copy
from functools    import wraps
from datetime     import datetime as stdlib_datetime
from contextlib   import contextmanager
from collections  import namedtuple, deque
from miros.event  import signals, return_status, Event
"""
This module provides a hierarchical state machine event class (HsmEventProcessor), and an
instrumented hierarchical state machine class (InstrumentedHsmEventProcessor).  The
InstrumentedHsmEventProcessor is inherited from the HsmEventProcessor, and it provides two different views
into the workings of your state machine:

  * spy   -> complete record of all search, transitions and hooks
  * trace -> only provides information about state transition (no hook
             information)

To define an HsmEventProcessor, you would create a number of methods outside of this class,
then inject them into the HsmEventProcessor, by calling the 'start_at' method.

Example::


                       +------- graph_b1_s1 -----s-----+
                       |  +---- graph_b1_s2 -----t-+   |
                       |  |  +- graph_b1_s3 -+     |   |
                       |  |  |               |   +-+   |
                       |  |  |               <-b-+ <-a-+
                       |  |  +---------------+     |   |
                       |  +------------------------+   |
                       +-------------------------------+

  # To create this cart, we
  # 1) import the required items from miros:
  from miros.event import ReturnStatus, signals, Event, return_status
  from miros.hsm   import InstrumentedHsmEventProcessor, HsmTopologyException, spy_on

  # 2) create the three different states:
  @spy_on
  def graph_b1_s1(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.A):
      status = chart.trans(graph_b1_s2)
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

  # define an inner state who's super state is graph_b1_s1
  @spy_on
  def graph_b1_s2(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.B):
      status = chart.trans(graph_b1_s3)
    else:
      status, chart.temp.fun = return_status.SUPER, graph_b1_s1
    return status

  # define an inner state who's super state is graph_b1_s2
  @spy_on
  def graph_b1_s3(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, graph_b1_s2
    return status

  # 3) Create an HsmEventProcessor, in this case we make one that is instrumented (a bit
  # slower than a plain HsmEventProcessor, but we can use it to see what happened)
  chart = InstrumentedHsmEventProcessor()

  # 4) Start the chart in the state we desire
  chart.start_at(graph_b1_s1)

  # 5) Send an Event(s) to the chart:
  chart.dispatch(Event(signal=signals.A)

  # 6) Look at what happened
  import pprint
  def pp(item):
    pprint.pprint(item)
  pp(chart.full.spy)
                     # ['START',
                     #  'SEARCH_FOR_SUPER_SIGNAL:graph_b1_s2',
                     #  'SEARCH_FOR_SUPER_SIGNAL:graph_b1_s1',
                     #  'ENTRY_SIGNAL:graph_b1_s1',
                     #  'ENTRY_SIGNAL:graph_b1_s2',
                     #  'INIT_SIGNAL:graph_b1_s2',
                     #  'A:graph_b1_s2',
                     #  'A:graph_b1_s1',
                     #  'EXIT_SIGNAL:graph_b1_s2',
                     #  'SEARCH_FOR_SUPER_SIGNAL:graph_b1_s2',
                     #  'SEARCH_FOR_SUPER_SIGNAL:graph_b1_s2',
                     #  'ENTRY_SIGNAL:graph_b1_s2',
                     #  'INIT_SIGNAL:graph_b1_s2']

  # 7) If you need these transitions to happen very quickly, create a chart
  # using the HsmEventProcessor class instead of the InstrumentedHsmEventProcessor class
  chart = InstrumentedHsmEventProcessor()
  chart.start_at(graph_b1_s1)
  chart.dispatch(Event(signal=signals.A) # same transitions with no trace or spy
                                         # features

"""


def pp(item):
  pprint.pprint(item)


SpyTuple = namedtuple('SpyTuple', ['signal',    'state',
                                   'hook',      'start',
                                   'internal',  'post_lifo',
                                   'post_fifo', 'post_defer',
                                   'recall',    'datetime'])

def spy_tuple(signal     = None,
              state      = None,
              hook       = False,
              start      = False,
              internal   = False,
              post_lifo  = False,
              post_fifo  = False,
              post_defer = False,
              recall     = False,
              datetime   = None,
              ):
  '''This is making it possible to have default settings in the SpyTuple,
     any attribute you need to over-write you can over-write by calling this
     function with it's name filled in with what you would like.'''
  if datetime is None:
    datetime = stdlib_datetime.now()
  return SpyTuple(signal=signal,
                  state=state,
                  start=start,
                  hook=hook,
                  internal=internal,
                  post_lifo=post_lifo,
                  post_fifo=post_fifo,
                  post_defer=post_defer,
                  recall=recall,
                  datetime=datetime
                  )


def spy_on(fn):
  '''Instrument a state handling method'''
  @wraps(fn)
  def _spy_on(chart, *args):
    chart.spied_on = True
    if len(args) == 1:
      e = args[0]
    else:
      e = args[-1]

    name = fn.__name__
    chart.state_name = name
    chart.state_fn = fn

    if not chart.instrumented:
      # call the original handler
      return fn(chart, e)
    
    # if the chart is not instrumented, don't try to wrap it
    if hasattr(chart, 'rtc') is False:
      # call the original handler and exit
      status = fn(chart, e)
      return status

    if(e.signal == signals.REFLECTION_SIGNAL):
      # We are no longer going to return a ReturnStatus object
      # instead we write the function name as a string
      status = name
      return status
    else:
      chart.rtc.spy.append("{}:{}".format(e.signal_name, name))

    # call the original handler
    status = fn(chart, e)

    if(signals.is_inner_signal(e.signal_name) is not True):
        # We have found a hook
        if(status is return_status.HANDLED):
          chart.rtc.spy.append("{}:{}:HOOK".format(e.signal_name, name))
          sr = spy_tuple(signal=e.signal_name, state=name, hook=True)
        else:
          sr = spy_tuple(signal=e.signal_name, state=name)
    else:
      sr = spy_tuple(signal=e.signal_name, state=name, hook=True, internal=True)
    chart.rtc.tuples.append(sr)
    return status
  return _spy_on


def state_method_template(name):
  '''
  Used to create state chart methods with the register_signal_callback and
  register_parent API
  '''

  def base_state_method(chart, e):
    with chart.signal_callback(e, name) as fn:
      if not inspect.ismethod(fn):
        status = fn(chart, e)
      else:
        status = fn(e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback(name) as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

  resulting_function = copy(base_state_method)
  resulting_function.__name__ = name
  resulting_function = spy_on(resulting_function)

  return resulting_function


# This is defined in the module name space so that inherited classes can access
# it
def spy_on_start(fn):
  '''instrument the on_start method into the spy log'''
  @wraps(fn)
  def _spy_on_start(self, initial_state):
    # if there is no decorator, the instrumentation is off
    if initial_state.__closure__ is None:
      self.instrumented = False
    else:
      # if there is a decorator check to see if it is a spy_on
      # decorator, if it isn't, the instrumentation is off
      m = re.search(r'spy_on', str(initial_state.__code__))
      if not m:
        self.instrumented = False

    if not self.instrumented:
      # fn is start_at
      return fn(self, initial_state)


    self.rtc.spy.append("START")
    sr = SpyTuple(
      signal="", state="",
      start=True, hook=False,
      internal=None, post_lifo=True,
      post_fifo=False, post_defer=False,
      recall=False, datetime=stdlib_datetime.now()
    )
    self.rtc.tuples.append(sr)
    # fn is start_at
    status = fn(self, initial_state)
    self.full.spy.extend(self.rtc.spy)
    return status
  return _spy_on_start


def append_fifo_to_spy(fn):
  @wraps(fn)
  def _append_fifo_to_spy(self, e):
    fn(self, e)
    if self.instrumented:
      self.rtc.spy.append("POST_FIFO:{}".format(e.signal_name))
  return _append_fifo_to_spy


# This is defined in the module name space so that inherited classes can access
# it
def trace_on_start(fn):
  '''instrument the on_start method into the trace log'''
  @wraps(fn)
  def _trace_on_start(self, initial_state):
    # fn is _spy_on_start
    status = fn(self, initial_state)
    if self.instrumented:
      if self.rtc.tuples[0].start:
        t = self.TraceTuple(
             datetime=stdlib_datetime.now(),
             start_state = 'top',
             signal      = None,
             payload     = None,
             end_state   =
               self.temp.fun(self,
                 Event(signal=signals.REFLECTION_SIGNAL))
           )
        self.full.trace.append(t)
    return status
  return _trace_on_start


def append_queue_reflection_after_start(fn):
  @wraps(fn)
  def _append_queue_reflection_after_start(self, initial_state):
    result = fn(self, initial_state)
    if self.instrumented:
      self.rtc.spy.append(self.queue_reflection())
      self.full.spy.append(self.queue_reflection())
    return result
  return _append_queue_reflection_after_start


class Attribute():
  def __init__(self):
    pass


class HsmTopologyException(Exception):
  pass


class HsmEventProcessor():
  SPY_RING_BUFFER_SIZE = 500
  TRC_RING_BUFFER_SIZE = 500
  RTC_RING_BUFFER_SIZE = 250

  def __init__(self):
    # making the name space common
    '''set initial state of the '''
    # used by the event processor
    self.state = Attribute()
    self.temp  = Attribute()
    self.event = Attribute()

    # this is useful if you instrument your event processor
    self.event.ignored = False

  def start_at(self, initial_state):
    '''
    hsm = HsmEventProcessor()
    # build it
    hsm.start(starting_state_function)
    '''
    if self.state is None:
      self.state = Attribute()

    if self.temp is None:
      self.temp  = Attribute()

    self.state.fun = self.top
    self.temp.fun  = initial_state
    self.init()
    self.state_name = self.state.fun.__name__
    self.state_fn = self.state.fun

  def top(self, *args):
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
    topological_error = "impossible chart topology for HsmEventProcessor.init, "
    topological_error += "see HsmEventProcessor.init doc string for details"

    e = Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL)
    tpath, outermost, max_index = [None], self.state.fun, 0

    # We will continue searching the chart until it stops requesting transitions
    while(True):  # outer while
      tpath[0], e, index = self.temp.fun, Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL), 0
      previous_super = None
      while(self.temp.fun != outermost):
        index      += 1
        r           = self.temp.fun(self, e)
        if(previous_super == self.temp.fun):
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
      while(True):  # inner while
        # pre-decrement to remove outermost from our entry list
        index -= 1
        entery_fn = tpath[index]
        r = entery_fn(self, e)
        if(index <= 0):
          break  # inner while break condition

      # Now send it the init event, the init event could change our
      # self.temp.fun if it needs to transition. This means that we might have to
      # repeat the work done above.  Reset our outermost state to this state and
      # continue to delve into the chart
      outermost = tpath[0]
      e = Event(signal=signals.INIT_SIGNAL)
      r = outermost(self, e)

      if r != return_status.TRAN:
        break  # outer while break condition

    self.state.fun = outermost
    self.temp.fun  = outermost

  def dispatch(self, e):
    '''dispatches an event to a HSM.

    Processing an event represents one run-to-completion (RTC) step.  This code
    is largely based on the same processor which was written by Miro Samek in
    his book titled, "Practical Statecharts in C/C++: Event Driven Programming
    for Embedded Systems."  If you need to add features or functions add them as
    wrappers in inherited classes.  Try not to change this code too much since
    it is beautifully documentated within the sited book.

    Args:
      e (Event): The event to be dispatched to the hsm object

    Returns:
      None

    Example::
      chart = HsmEventProcessor()
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

                         Example::
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

                         Example::
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
    tpath       = [None, None, None]
    t, s, ip    = None, None, 0
    max_index   = 2
    self.event.ignored = False

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
    assert(t is not None)
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
      if r is None:
        raise(HsmTopologyException(
            "state handler {} is not returning a valid status".format(s)))

      # if the event is unhandled due to a guard, send it a signal
      # which will force it to return the return_status.SUPER, as a
      # side effect, r will be set to the super state of the function 
      # being guarded
      if r == return_status.UNHANDLED:
        r = s(self, Event(signal=signals.EMPTY_SIGNAL))

      if(r != return_status.SUPER):
        # S in now stored in s
        break

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
        if r is None:
          raise(HsmTopologyException(
              "state handler {} is not returning a valid status".format(t)))
        if(r == return_status.HANDLED):
          t(self, super_e)
        t = self.temp.fun

      # navigate all supported topologies
      # tpath will be over-written with entry values
      # ip will indicate at which point we should begin an entry path
      ip = self.trans_(tpath, max_index)

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
          if(ip < 0):
            break
        t = tpath[0]

    elif(r is return_status.HANDLED):  # trans handled
      # This is the ultimate hook pattern
      pass
    elif(r is return_status.IGNORED):  # trans handled
      # The event was not handled by this HSM
      self.event.ignored = True
    else:
      pass

    # t contains T
    self.state.fun = t
    self.temp.fun  = t

    self.state_name = t.__name__
    self.state_fn = t

  def trans(self, fn):
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
    the tpath, ip and iq. Consider this example::

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
    the lca has been found::

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

    ip, iq = -1, 0  # no entry, no lca found
    # S is in tpath[2]
    # T is in tpath[0]
    t, s = tpath[0], tpath[2]

    exit_e, super_e =                                        \
              Event(signal=signals.EXIT_SIGNAL),             \
              Event(signal=signals.SEARCH_FOR_SUPER_SIGNAL)

    # +-S-T-+
    # |     +-+
    # |     | |
    # |     <-+
    # +-lca-+
    # (a) check source == target
    # pytest -m topology_a -s
    if(s is t):
      s(self, exit_e)  # exit the source
      ip = 0           # enter the target
      # iq = 1
    else:
      t(self, super_e)
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
      if (s is t):
        ip = 0  # enter the target
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
            s(self, exit_e)
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
            iq, ip = 0, 1    # LCA not found yet, enter T and T->super
            tpath[1] = t     # tpath[1] contains T->super
            t = self.temp.fun  # t contains S->super
            r = tpath[1](self, super_e)

            if r is None:
              raise(HsmTopologyException(
                  "state handler {} is not returning a valid status".format(tpath[1])))

            while(r == return_status.SUPER):
              ip += 1
              # store our entry tpath
              if ip > max_index:
                tpath.append(self.temp.fun)
                max_index = ip
              else:
                tpath[ip] = self.temp.fun

              if(self.temp.fun is s):  # if we have found S
                iq =  1
                ip -= 1  # don't enter S since we are coming at it from the
                         # inside
                r = return_status.HANDLED  # terminate the loop
              else:
                r = self.temp.fun(self, super_e)

            if(iq == 0):
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
                if(t is tpath[iq]):  # is this the lca?
                  r = return_status.HANDLED
                  ip = iq - 1  # do not enter the lca
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
                if(t(self, exit_e) == return_status.HANDLED):
                  t(self, super_e)
                # t contains S->super->super..
                t = self.temp.fun
                iq = ip
                while(True):
                  if(t == tpath[iq]):  # is this the lca?
                    r = return_status.HANDLED
                    ip = iq - 1  # do not enter the lca
                    iq = -1
                  else:
                    iq -= 1
                  if(iq < 0):
                    break
                if(r == return_status.HANDLED):
                  break
    return ip

  def is_in(self, fn_state_handler):
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
    self.temp.fun = self.state.fun  # set our temp back to what it should be
    return result

  def child_state(self, fn_parent_state_handler):
    '''finds the child state of a given parent

    This method will only return a child state of a given handler, if the system
    is in a substate of the state being called::

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

      chart = HsmEventProcessor()
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
        break
    self.temp.fun = self.state.fun
    assert(confirmed is True)
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
      alarm       = HsmEventProcessor(); alarm.name       = "alarm"
      time_keeper = HsmEventProcessor(); time_keeper.name = "time_keeper"
      alarm.augment(other=time_keeper, name="time_keeper")

      assert(alarm.time_keeper == time_keeper) # will be true

      inverter  = HsmEventProcessor(); inverter.name = "inverter"
      networker = HsmEventProcessor(); networker.name = "networker"
      inverter.augment(other=networker, name="net", relationship="mutual")

      assert(inverter.net == networker) # will be true
      assert(networker.inverter == inverter ) # will be true
    """

    relationship = None
    if("other" in kwargs):
      other = kwargs['other']
    if("name" in kwargs):
      name = kwargs['name']
    if("relationship" in kwargs):
      relationship = kwargs['relationship']

    if hasattr(self, name) is not True:
      setattr(self, name, other)
    else:
      pass
    if(relationship is not None and relationship == "mutual"):
      other.augment(other=self, name=self.name, relationship=None)


class InstrumentedHsmEventProcessor(HsmEventProcessor):
  '''

  '''

  def __init__(self):
    super().__init__()

    # by default we turn on instrumentation, but it can be turned off
    self.instrumented = True

    # used by spy/trace
    self.full  = Attribute()
    self.rtc   = Attribute()

    # used to build spy
    self.full.spy = deque(maxlen=HsmEventProcessor.SPY_RING_BUFFER_SIZE)

    # initialize this before start to give the ability to post items before 
    # the statechart is started
    self.init_rtc()

    # used to build trace
    self.full.trace = deque(maxlen=HsmEventProcessor.TRC_RING_BUFFER_SIZE)
    self.TraceTuple = namedtuple('TraceTuple',
                                            ['datetime',
                                             'start_state',
                                             'signal',
                                             'payload',
                                             'end_state'])

  def init_rtc(self):
    self.rtc.spy    = deque(maxlen=HsmEventProcessor.RTC_RING_BUFFER_SIZE)
    self.rtc.tuples = deque(maxlen=HsmEventProcessor.RTC_RING_BUFFER_SIZE)

  @trace_on_start
  @spy_on_start
  def start_at(self, initial_state):
    super().start_at(initial_state)

  def append_to_full_spy(fn):
    @wraps(fn)
    def _append_to_full_spy(self, e):
      if not self.instrumented:
        # fn is dispatch
        fn(self, e)
      else:
        self.rtc.spy.clear()
        # fn is dispatch
        fn(self, e)
        self.full.spy.extend(self.rtc.spy)
    return _append_to_full_spy

  def scribble(self, string):
    if self.instrumented:
      self.rtc.spy.append(string)

  def append_to_full_trace(fn):
    @wraps(fn)
    def is_signal_hooked(self):
      signal_name, hooked, dt = "", False, None
      for sr in self.rtc.tuples:
        if sr.internal is False and sr.recall is False:
          signal_name = sr.signal
          dt = sr.datetime
          if sr.hook:
            hooked  = True
            break
      return (signal_name, hooked, dt)

    def _append_to_full_trace(self, e):
      if not self.instrumented:
        # fn is append_to_full_spy
        fn(self, e)
      else:
        start_state = self.state.fun(self, Event(signal=signals.REFLECTION_SIGNAL))
        self.rtc.tuples.clear()
        # fn is append_to_full_spy
        fn(self, e)
        signal, hooked, dt = is_signal_hooked(self)
        if hooked is False and self.event.ignored is False:
          t = self.TraceTuple(
                datetime    = dt,
                start_state = start_state,
                signal      = signal,
                payload     = '',
                end_state   =
                  self.state.fun(
                    self, Event(signal=signals.REFLECTION_SIGNAL)))

          self.full.trace.append(t)
    return _append_to_full_trace

  @append_to_full_spy
  @append_to_full_trace
  def dispatch(self, e):
    super().dispatch(e)


class HsmWithQueues(InstrumentedHsmEventProcessor):
  '''An Hsm that can post to itself and run to complete on each all of next_rtc.'''
  QUEUE_SIZE = 500

  def __init__(self, maxlen=QUEUE_SIZE, instrumented=True, priority=1):
    super().__init__()

    if instrumented:
      # see what is going on
      self.instrumented = True
    else:
      # run as fast as possible
      self.instrumented = False

    self.spied_on = False

    self.queue       = deque(maxlen = self.__class__.QUEUE_SIZE)
    self.defer_queue = deque(maxlen = self.__class__.QUEUE_SIZE)
    self.live_spy    = False
    self.live_trace  = False
    self.name        = None

    self.live_spy_callback   = self.__class__.live_spy_callback_default
    self.live_trace_callback = self.__class__.live_trace_callback_default

    self.last_live_trace_datetime = len(self.full.trace)

  @staticmethod
  def live_spy_callback_default(spy_line):
    print(spy_line)

  @staticmethod
  def live_trace_callback_default(trace_line):
    print(trace_line.replace("\n", ""))

  def register_live_spy_callback(self, live_spy_callback):
    self.live_spy_callback = live_spy_callback

  def register_live_trace_callback(self, live_trace_callback):
    self.live_trace_callback = live_trace_callback

  def print_spy_after_at_start_if_live(fn):
    @wraps(fn)
    def _print_spy_if_live(self, initial_state):
      # fn is _print_trace_if_live
      result = fn(self, initial_state)
      if self.instrumented and self.live_spy:
        for line in self.rtc.spy.copy():
          self.live_spy_callback(line)
      return result
    return _print_spy_if_live

  def trace_tuple_to_formatted_string(self, tr):
    if self.name is None:
      name = 'None'
    else:
      name = self.name
    if tr.signal is None:
      signal = 'start_at'
    else:
      signal = tr.signal

    strace = "[{}] [{}] e->{}() {}->{}\n".format(
        stdlib_datetime.strftime(tr.datetime, "%Y-%m-%d %H:%M:%S.%f"),
        name,
        signal,
        tr.start_state,
        tr.end_state)
    return strace

  def print_trace_after_at_start_if_live(fn):
    @wraps(fn)
    def _print_trace_if_live(self, initial_state):
      tr = None
      # fn is next_rtc/start_at
      result = fn(self, initial_state)
      if self.instrumented and self.live_trace:
        strace = ""
        tr = self.full.trace[-1]
        strace  += self.trace_tuple_to_formatted_string(tr)
        self.live_trace_callback(strace)
      if tr is not None:
        self.last_live_trace_datetime = tr.datetime
      return result
    return _print_trace_if_live

  def print_spy_after_rtc_if_live(fn):
    @wraps(fn)
    def _print_spy_if_live(self):
      # fn is _print_trace_if_live
      result = fn(self)
      if self.instrumented and self.live_spy:
        for line in list(self.rtc.spy):
          self.live_spy_callback(line)
      return result
    return _print_spy_if_live

  def print_trace_after_rtc_if_live(fn):
    @wraps(fn)
    def _print_trace_if_live(self):
      tr = None
      # fn is next_rtc/start_at
      result = fn(self)
      if(self.instrumented and self.live_trace):
        tr = self.full.trace[-1]
        if tr.datetime != self.last_live_trace_datetime:
          strace = "\n"
          strace += self.trace_tuple_to_formatted_string(tr)
          self.live_trace_callback(strace)
      if tr is not None:
        self.last_live_trace_datetime = tr.datetime
      return result
    return _print_trace_if_live

  # print_spy_after_at_start_if_live calls print_trace_after_at_start_if_live
  # which calls append_queue_reflection_after_start which calls start_at.

  # append_queue_reflection_after_start does its work after start_at and
  # returns control to print_trace_after_at_start_if_live, which prints the
  # trace, then it returns control to print_spy_after_at_start_if_live which
  # prints the spy.
  @print_spy_after_at_start_if_live
  @print_trace_after_at_start_if_live
  @append_queue_reflection_after_start
  def start_at(self, initial_state):
    if self.instrumented:
      super().start_at(initial_state)
    else:
      HsmEventProcessor.start_at(self, initial_state)

  def current_state(self):
    if self.instrumented:
      cs = self.state.fun(self, Event(signals.REFLECTION_SIGNAL))
      return cs

  def dispatch(self, e):
    if self.instrumented:
      super().dispatch(e)
    else:
      HsmEventProcessor.dispatch(self, e)

  def queue_reflection(self):
    return "<- Queued:({}) Deferred:({})".format(len(self.queue), len(self.defer_queue))

  def append_lifo_to_spy(fn):
    @wraps(fn)
    def _append_lifo_to_spy(self, e):
      fn(self, e)
      if self.instrumented:
        self.rtc.spy.append("POST_LIFO:{}".format(e.signal_name))
    return _append_lifo_to_spy

  def append_defer_to_spy(fn):
    @wraps(fn)
    def _append_defer_to_spy(self, e):
      fn(self, e)
      if self.instrumented:
        self.rtc.spy.append("POST_DEFERRED:{}".format(e.signal_name))
    return _append_defer_to_spy

  def append_recall_to_spy(fn):
    @wraps(fn)
    def _append_recall_to_spy(self):
      if self.instrumented:
        if (len(self.defer_queue) != 0):
          sneak_peak = self.defer_queue[0]
          if sneak_peak is not None:
            sr = spy_tuple(signal=sneak_peak.signal_name, recall=True)
            self.rtc.spy.append("RECALL:{}".format(sneak_peak.signal_name))
            self.rtc.tuples.append(sr)
      e = fn(self)
      return e

    return _append_recall_to_spy

  def append_queue_reflection_to_spy(fn):
    @wraps(fn)
    def _append_queue_reflection_to_spy(self):
      # fn is _print_spy_if_live
      result = fn(self)
      if self.instrumented:
        self.rtc.spy.append(self.queue_reflection())
        self.full.spy.append(self.queue_reflection())
      return result
    return _append_queue_reflection_to_spy

  @append_fifo_to_spy
  def post_fifo(self, e):
    self.queue.append(e)

  @append_lifo_to_spy
  def post_lifo(self, e):
    self.queue.appendleft(e)

  @append_defer_to_spy
  def defer(self, e):
    self.defer_queue.append(e)

  @append_recall_to_spy
  def recall(self):
    e = None
    if(len(self.defer_queue) != 0):
      e = self.defer_queue.popleft()
      self.post_fifo(e)
    return e

  # print_spy_after_rtc_if_live calls print_trace_after_rtc_if_live which calls
  # append_queue_reflection_to_spy which calls next_rtc.

  # append_queue_reflection_to_spy does its work after next_rtc and returns
  # control to print_trace_after_rtc_if_live, which prints the trace, then it
  # returns control to print_spy_after_rtc_if_live which prints the spy.
  @print_spy_after_rtc_if_live
  @print_trace_after_rtc_if_live
  @append_queue_reflection_to_spy
  def next_rtc(self):
    if self.instrumented:
      self.rtc.spy.clear()
    action_taken = True
    if(len(self.queue) != 0):
      event = self.queue.popleft()
      self.dispatch(e=event)
    else:
      action_taken = False
    return action_taken

  def complete_circuit(self):
    action_taken = False
    while(len(self.queue) != 0):
      action_taken = self.next_rtc()
    return action_taken

  def clear_spy(self):
    if self.instrumented:
      self.full.spy.clear()

  def clear_trace(self):
    if self.instrumented:
      self.full.trace.clear()
      self.last_live_trace_datetime = stdlib_datetime.now()

  def trace(self):
    '''Output state transition information only:

    Example::
      print(chart.trace())
        [05:23:25.314420] [c] None: top->hsm_queues_graph_g1_s22
        [05:23:25.314420] [c] D: hsm_queues_graph_g1_s22->hsm_queues_graph_g1_s1
        [05:23:25.314420] [c] E: hsm_queues_graph_g1_s1->hsm_queues_graph_g1_s01
        [05:23:25.314420] [c] F: hsm_queues_graph_g1_s01->hsm_queues_graph_g1_s2111
        [05:23:25.314420] [c] A: hsm_queues_graph_g1_s2111->hsm_queues_graph_g1_s321
    '''
    if not self.instrumented:
      return None

    strace = "\n"
    for tr in self.full.trace:
      strace += self.trace_tuple_to_formatted_string(tr)
    return strace

  def spy_rtc(self):
    return list(self.rtc.spy)

  def spy_full(self):
    return list(self.full.spy)

  def spy(self):
    #if not self.instrumented or not self.spied_on:
    #  return None
    result = None
    if self.instrumented:
      result = self.spy_full()
    return result

  def register_signal_callback(self, state_method, signal, fn):
    '''
    Example 1:
      def for_A(chart, e):
        print("Ah!")
        return return_status.HANDLED

      def state_function(chart, e):
        status = return_status.UNHANDLED
        with chart.lookup(e) as fn:
          result = fn(chart, e)
        else:
          status, chart.temp.fun = return_status.SUPER, chart.top
      return status

      ao.register_for_lookup(state_function, signals.A, for_A)

    Example 2:
      # if you are using the function template provided by this module

    '''
    def handled(chart, e):
      return return_status.HANDLED

    # ensure that if the user doesn't explicitly define the behavior for
    # 'entry', 'init' and 'exit' that these internal signals are at least
    # blocked and not let out of the function to fall out of the current
    # state method
    if hasattr(self, '_lookup') is False:
      self._lookup = {}
      self.register_signal_callback(state_method, signals.ENTRY_SIGNAL, handled)
      self.register_signal_callback(state_method, signals.INIT_SIGNAL, handled)
      self.register_signal_callback(state_method, signals.EXIT_SIGNAL, handled)

    if state_method.__name__ in self._lookup:
      self._lookup[state_method.__name__][signal] = fn
    else:
      self._lookup[state_method.__name__] = {}
      self._lookup[state_method.__name__][signal] = fn

  def register_parent(self, state_method, parent_method):
    if hasattr(self, '_parents') is False:
      self._parents = {}

    self._parents[state_method.__name__] = parent_method

  @contextmanager
  def parent_callback(self, state_method=None):
    if state_method is None:
      state_method = traceback.extract_stack(None, 3)[0][2]
    yield(self._parents[state_method])

  @contextmanager
  def signal_callback(self, e, name):
    '''
    with self.lookup(chart, e) as fn:
      result = fn(chart, e)
    '''
    if callable(name):
      key = name.__name__
    else:
      key = name

    def nothing_registered_for_signal(self, e):
      return return_status.UNHANDLED

    fn = nothing_registered_for_signal
    if(key in self._lookup):
      if(e.signal in self._lookup[key]):
        fn = self._lookup[key][e.signal]
    yield(fn)

  def to_code(self, state_method_name):
    '''
    Provides the equivalent flat code for items that have been written to a
    state_method written from a template.  This may be useful for debugging
    your code when you have used the 'register_signal_callback' and
    'register_parent' methods of this class.


    '''
    If_Blob = namedtuple('IfLadder', ['priority', 'signal_name', 'callback'])
    entry_priority, init_priority, other_priority, exit_priority = 1, 2, 3, 4

    def get_priority(signal_name):
      if signal_name == 'ENTRY_SIGNAL':
        priority = entry_priority
      elif signal_name == 'INIT_SIGNAL':
        priority = init_priority
      elif signal_name == 'EXIT_SIGNAL':
        priority = exit_priority
      else:
        priority = other_priority
      return priority

    def create_unordered_if_ladder(state_method):
      ifs = []
      for signal in self._lookup[state_method]:
        fn_name = self._lookup[state_method][signal].__name__
        signal_name = signals.name_for_signal(signal)
        priority = get_priority(signal_name)
        if_ladder = If_Blob(priority=priority, signal_name=signal_name, callback=fn_name)
        ifs.append(if_ladder)
      return ifs

    def create_ordered_if_ladder(unordered_ifs):
      ifs = sorted(unordered_ifs, key=lambda if_: if_.priority)
      return ifs

    def fill_missing_ifs(ordered_ifs):
      full_ordered_ifs = []
      entry  = [item for item in ordered_ifs if item.priority == entry_priority]
      init   = [item for item in ordered_ifs if item.priority == init_priority]
      others = [item for item in ordered_ifs if item.priority == other_priority]
      exit   = [item for item in ordered_ifs if item.priority == exit_priority]

      if len(entry) != 0:
        full_ordered_ifs.extend(entry)
      else:
        full_ordered_ifs.append(If_Blob(priority=entry_priority, signal_name='ENTRY_SIGNAL', callback=None))

      if len(init) != 0:
        full_ordered_ifs.extend(init)
      else:
        full_ordered_ifs.append(If_Blob(priority=init_priority, signal_name='INIT_SIGNAL', callback=None))

      if len(others) != 0:
        full_ordered_ifs.extend(others)

      if len(exit) != 0:
        full_ordered_ifs.extend(exit)
      else:
        full_ordered_ifs.append(If_Blob(priority=exit_priority, signal_name='EXIT_SIGNAL', callback=None))

      return full_ordered_ifs

    if callable(state_method_name):
      state_method = state_method_name.__name__
    else:
      state_method = state_method_name

    unordered_ifs = create_unordered_if_ladder(state_method)
    ordered_ifs = create_ordered_if_ladder(unordered_ifs)
    ifs = fill_missing_ifs(ordered_ifs)

    # to make it easier to test this code, we will start the string with a line
    # break
    code = "\n@spy_on\n"
    for i, if_tuple in enumerate(ifs):
      if i == 0:
        code += "def {}(chart, e):\n".format(state_method)
        code += "  status = return_status.UNHANDLED\n"
        if if_tuple.callback is None or if_tuple.callback == 'handled':
          code += "  if(e.signal == signals.{}):\n".format(if_tuple.signal_name)
          code += "    status = return_status.HANDLED\n"
        else:
          code += "  if(e.signal == signals.{}):\n".format(if_tuple.signal_name)
          code += "    status = {}(chart, e)\n".format(if_tuple.callback)
      else:
        if if_tuple.callback is None or if_tuple.callback == 'handled':
          code += "  elif(e.signal == signals.{}):\n".format(if_tuple.signal_name)
          code += "    status = return_status.HANDLED\n"
        else:
          code += "  elif(e.signal == signals.{}):\n".format(if_tuple.signal_name)
          code += "    status = {}(chart, e)\n".format(if_tuple.callback)

    parent_name = self._parents[state_method].__name__
    if parent_name == 'top':
      parent_name = 'chart.top'
    code += "  else:\n"
    code += "    status, chart.temp.fun = return_status.SUPER, {}\n".format(parent_name)
    code += "  return status\n"

    return code


@contextmanager
def stripped(log):
  '''Context manager used to compared trace/spy logs stripped of their timestamps

  The timestamp and chart name are expected to be on the front end of the
  trace/spy, between []:

    [2017-11-05 15:17:39.424492] [75c8c] e->BATTERY_CHARGE() armed->armed

  becomes:

    [75c8c] e->BATTERY_CHARGE() armed->armed

  We want to strip off the timestamp so that we can use the instrumented log as
  a specification for our design, this should become clear in the examples.

  Example 1:
    timestamp_trace1 = ao.trace()
    timestamp_trace2 = ao.trace()  # same to make a point

    with stripped(timestamped_trace1) as twt, \
         stripped(timestamped_trace2) as otw:

      for target_item, other_item in zip(twt, owt):
        assert(target_item == other_item)

  Example 2:
    with stripped('[2017-11-05 15:17:39.424492] [75c8c] e->BATTERY_CHARGE() armed->armed') /
      as swt:
      assert(swt == '[75c8c] e->BATTERY_CHARGE() armed->armed')

  '''
  def item_without_timestamp(item):
    '''
    [2017-11-05 15:17:39.424492] [75c8c] e->BATTERY_CHARGE() armed->armed
    -------- removed -----------
                                ------------ captured -------------------
    OR

       [2017-11-05 15:17:39.424492] [75c8c] e->BATTERY_CHARGE() armed->armed
    ===-------- removed -----------
          (front spaces removed)   ------------ captured -------------------

    '''
    m = re.match(r"[ ]{0,}\[[0-9-:. ]+\] (.+)$", item)
    if(m is not None):
      without_time_stamp = m.group(1)
    else:
      without_time_stamp = item
    return without_time_stamp

  targets = log.splitlines()
  if len(targets) > 1:
    stripped_target = []
    for target_item in targets:
      target_item = target_item.strip()
      if len(target_item) != 0:
        stripped_target_item = item_without_timestamp(target_item)
        stripped_target.append(stripped_target_item)
    yield(stripped_target)
  else:
    target = log
    yield(item_without_timestamp(target))


